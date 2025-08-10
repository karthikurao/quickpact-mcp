import asyncio
import json
import uuid
from datetime import datetime
from typing import Annotated
import os
import logging
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import TextContent, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load environment variables ---
load_dotenv()

# Support both AUTH_TOKEN and QUICKPACT_AUTH_TOKEN (for Vercel compatibility)
TOKEN = os.environ.get("AUTH_TOKEN") or os.environ.get("QUICKPACT_AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")

assert TOKEN is not None, "Please set AUTH_TOKEN or QUICKPACT_AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# --- Rich Tool Description model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None

# --- Agreement Data Models ---
class Agreement(BaseModel):
    id: str
    original_text: str
    party1: str
    party2: str
    terms: str
    deadline: str
    payment_amount: str | None = None
    payment_currency: str = "INR"
    deliverables: list[str] = []
    status: str = "draft"  # draft, signed, completed
    signatures: list[dict] = []
    created_at: str
    updated_at: str
    shareable_url: str | None = None

# In-memory storage (for demo purposes - use Firebase/Supabase in production)
agreements_db = {}

# --- Agreement Parser ---
class AgreementParser:
    @staticmethod
    def parse_agreement_text(text: str, party1: str = "", party2: str = "") -> dict:
        """Parse natural language agreement text into structured data"""
        
        # Extract payment information
        payment_patterns = [
            r'(?:pay|payment|₹|rs\.?|rupees?)\s*(?:₹|rs\.?)?\s*(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s*(?:₹|rs\.?|rupees?)',
        ]
        
        payment_amount = None
        for pattern in payment_patterns:
            match = re.search(pattern, text.lower())
            if match:
                payment_amount = match.group(1).replace(',', '')
                break
        
        # Extract deadline information
        deadline_patterns = [
            r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'by\s+(next\s+\w+)',
            r'by\s+(\w+day)',
            r'within\s+(\d+)\s+(day|week|month)s?',
            r'before\s+(.+?)(?:\.|,|$)',
            r'deadline[:\s]+(.+?)(?:\.|,|$)',
        ]
        
        deadline = "Not specified"
        for pattern in deadline_patterns:
            match = re.search(pattern, text.lower())
            if match:
                deadline = match.group(1)
                break
        
        # Extract deliverables/tasks
        deliverable_patterns = [
            r'(?:i\'ll|i\s+will)\s+(.+?)(?:\s+by|\s+for|,|\.|$)',
            r'(?:design|create|build|deliver|complete|help)\s+(.+?)(?:\s+by|\s+for|,|\.|$)',
        ]
        
        deliverables = []
        for pattern in deliverable_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                deliverable = match.group(0).strip()
                if deliverable and deliverable not in deliverables:
                    deliverables.append(deliverable)
        
        # Auto-detect parties if not provided
        if not party1 and not party2:
            if "i'll" in text.lower() or "i will" in text.lower():
                party1 = "Party 1"
            if "you'll" in text.lower() or "you will" in text.lower():
                party2 = "Party 2"
        
        return {
            "payment_amount": payment_amount,
            "deadline": deadline,
            "deliverables": deliverables if deliverables else ["Complete agreed task"],
            "party1": party1 or "Party 1",
            "party2": party2 or "Party 2"
        }

# --- MCP Server Setup ---
mcp = FastMCP(
    "QuickPact MCP Server - Micro Agreement Creator",
    auth=SimpleBearerAuthProvider(TOKEN),
)

# --- Tool: validate (required by Puch) ---
@mcp.tool
async def validate() -> str:
    """Validate bearer token and return phone number for Puch AI authentication"""
    return MY_NUMBER

# --- Tool: create_agreement ---
CREATE_AGREEMENT_DESCRIPTION = RichToolDescription(
    description="Create a structured micro-agreement from natural language input. Perfect for quick handshake deals, freelance work, small payments, and simple commitments.",
    use_when="Use when users want to create quick agreements like 'I'll design logo by Friday, you pay ₹2000' or any micro-contract between two parties.",
    side_effects="Creates a new agreement with unique ID, parses terms, and returns shareable link."
)

@mcp.tool(description=CREATE_AGREEMENT_DESCRIPTION.model_dump_json())
async def create_agreement(
    party1: Annotated[str, Field(description="Name or email of the first party (person offering service/work)")],
    party2: Annotated[str, Field(description="Name or email of the second party (person receiving service/making payment)")],
    terms: Annotated[str, Field(description="Plain text description of the agreement terms and conditions")],
    deadline: Annotated[str, Field(description="When the work should be completed (e.g., 'by Friday', 'next Monday', 'within 3 days')")],
) -> str:
    """Create a micro-agreement between two parties with AI-powered parsing"""
    
    try:
        # Input validation
        if not terms or len(terms.strip()) < 10:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Agreement terms must be at least 10 characters long"))
        
        if not party1 or not party1.strip():
            party1 = "Party 1"
        else:
            party1 = party1.strip()
            
        if not party2 or not party2.strip():
            party2 = "Party 2"
        else:
            party2 = party2.strip()
            
        if not deadline or not deadline.strip():
            deadline = "Not specified"
        else:
            deadline = deadline.strip()
        
        logger.info(f"Creating agreement between {party1} and {party2}")
        
        # Generate unique agreement ID
        agreement_id = f"qp_{uuid.uuid4().hex[:8]}"
        
        # Parse the agreement text for structured data
        parsed_data = AgreementParser.parse_agreement_text(terms, party1, party2)
        
        # Create agreement object
        agreement = Agreement(
            id=agreement_id,
            original_text=terms,
            party1=party1,
            party2=party2,
            terms=terms,
            deadline=deadline,
            payment_amount=parsed_data.get("payment_amount"),
            payment_currency="INR",
            deliverables=parsed_data.get("deliverables", []),
            status="draft",
            signatures=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            shareable_url=f"https://quickpact.app/agreement/{agreement_id}"
        )
        
        # Store in database (in-memory for demo)
        agreements_db[agreement_id] = agreement.model_dump()
        
        # Format response
        response = {
            "success": True,
            "agreement_id": agreement_id,
            "agreement": {
                "parties": f"{party1} ↔ {party2}",
                "terms": terms,
                "deadline": deadline,
                "payment": f"₹{parsed_data['payment_amount']}" if parsed_data.get("payment_amount") else "No payment specified",
                "deliverables": parsed_data.get("deliverables", []),
                "status": "Draft (awaiting signatures)",
                "created": agreement.created_at
            },
            "next_steps": [
                f"Share agreement ID '{agreement_id}' with both parties",
                "Each party should sign using the 'sign_agreement' tool",
                "Access via shareable link: " + agreement.shareable_url
            ],
            "shareable_url": agreement.shareable_url
        }
        
        return f"""
🎉 **Micro-Agreement Created Successfully!**

**Agreement ID**: `{agreement_id}`
**Parties**: {party1} ↔ {party2}
**Terms**: {terms}
**Deadline**: {deadline}
**Payment**: {"₹" + parsed_data['payment_amount'] if parsed_data.get('payment_amount') else "No payment specified"}

**Next Steps**:
1. Share this agreement ID with both parties
2. Each party signs using: `sign_agreement("{agreement_id}", "Your Name", "party1" or "party2")`
3. View anytime at: {agreement.shareable_url}

**Status**: Draft (awaiting signatures)
"""
        
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to create agreement: {str(e)}"))

# --- Tool: sign_agreement ---
SIGN_AGREEMENT_DESCRIPTION = RichToolDescription(
    description="Add a digital signature to an existing agreement by providing agreement ID, signer name, and role.",
    use_when="Use when a party wants to digitally sign an agreement that has been created.",
    side_effects="Adds timestamp signature to the agreement and updates status when all parties have signed."
)

@mcp.tool(description=SIGN_AGREEMENT_DESCRIPTION.model_dump_json())
async def sign_agreement(
    agreement_id: Annotated[str, Field(description="The unique ID of the agreement to sign")],
    signer_name: Annotated[str, Field(description="Full name of the person signing the agreement")],
    signer_role: Annotated[str, Field(description="Role of signer: 'party1', 'party2', or 'witness'")]
) -> str:
    """Sign an existing agreement with digital signature"""
    
    try:
        # Input validation
        if not agreement_id or not agreement_id.strip():
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Agreement ID is required"))
            
        if not signer_name or len(signer_name.strip()) < 2:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Signer name must be at least 2 characters long"))
            
        if signer_role not in ["party1", "party2", "witness"]:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="Signer role must be 'party1', 'party2', or 'witness'"))
        
        signer_name = signer_name.strip()
        agreement_id = agreement_id.strip()
        
        logger.info(f"Signing agreement {agreement_id} by {signer_name} as {signer_role}")
        
        # Check if agreement exists
        if agreement_id not in agreements_db:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Agreement '{agreement_id}' not found"))
        
        agreement = agreements_db[agreement_id]
        
        # Check if already signed by this role
        existing_signature = next((sig for sig in agreement["signatures"] if sig["role"] == signer_role), None)
        if existing_signature:
            return f"❌ Agreement '{agreement_id}' already signed by {signer_role}: {existing_signature['signer_name']}"
        
        # Add signature
        signature = {
            "signer_name": signer_name,
            "role": signer_role,
            "timestamp": datetime.now().isoformat(),
            "ip_address": "127.0.0.1"  # In production, capture real IP
        }
        
        agreement["signatures"].append(signature)
        agreement["updated_at"] = datetime.now().isoformat()
        
        # Update status based on signatures
        party_signatures = [sig for sig in agreement["signatures"] if sig["role"] in ["party1", "party2"]]
        if len(party_signatures) >= 2:
            agreement["status"] = "fully_signed"
        elif len(party_signatures) == 1:
            agreement["status"] = "partially_signed"
        
        # Save updated agreement
        agreements_db[agreement_id] = agreement
        
        return f"""
✅ **Agreement Signed Successfully!**

**Agreement ID**: `{agreement_id}`
**Signed by**: {signer_name} ({signer_role})
**Timestamp**: {signature['timestamp']}
**Status**: {agreement['status'].replace('_', ' ').title()}

**All Signatures**:
{chr(10).join([f"• {sig['signer_name']} ({sig['role']}) - {sig['timestamp']}" for sig in agreement['signatures']])}

**Agreement Status**: {"🎉 FULLY EXECUTED" if agreement['status'] == 'fully_signed' else "⏳ Awaiting more signatures"}
**View**: {agreement.get('shareable_url', f'https://quickpact.app/agreement/{agreement_id}')}
"""
        
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to sign agreement: {str(e)}"))

# --- Tool: get_agreement ---
GET_AGREEMENT_DESCRIPTION = RichToolDescription(
    description="Retrieve full details of an agreement by its ID, including parties, terms, signatures, and status.",
    use_when="Use when someone needs to view or review an existing agreement's details.",
    side_effects="Returns complete agreement information and current status."
)

@mcp.tool(description=GET_AGREEMENT_DESCRIPTION.model_dump_json())
async def get_agreement(
    agreement_id: Annotated[str, Field(description="The unique ID of the agreement to retrieve")]
) -> str:
    """Get details of an existing agreement"""
    
    try:
        if agreement_id not in agreements_db:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Agreement '{agreement_id}' not found"))
        
        agreement = agreements_db[agreement_id]
        
        # Format signatures
        signatures_text = ""
        if agreement["signatures"]:
            signatures_text = "\n**Signatures**:\n" + "\n".join([
                f"• {sig['signer_name']} ({sig['role']}) - {sig['timestamp']}" 
                for sig in agreement["signatures"]
            ])
        else:
            signatures_text = "\n**Signatures**: None yet"
        
        # Format payment
        payment_text = ""
        if agreement.get("payment_amount"):
            payment_text = f"\n**Payment**: ₹{agreement['payment_amount']} {agreement.get('payment_currency', 'INR')}"
        
        return f"""
📋 **Agreement Details**

**ID**: `{agreement_id}`
**Status**: {agreement['status'].replace('_', ' ').title()}
**Created**: {agreement['created_at']}

**Parties**:
• **Party 1**: {agreement['party1']}
• **Party 2**: {agreement['party2']}

**Terms**: {agreement['terms']}
**Deadline**: {agreement['deadline']}{payment_text}

**Deliverables**:
{chr(10).join([f"• {item}" for item in agreement.get('deliverables', [])])}
{signatures_text}

**Shareable URL**: {agreement.get('shareable_url', f'https://quickpact.app/agreement/{agreement_id}')}
"""
        
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to retrieve agreement: {str(e)}"))

# --- Tool: list_agreements ---
LIST_AGREEMENTS_DESCRIPTION = RichToolDescription(
    description="List all agreements in the system with optional filtering by status or party name.",
    use_when="Use when you need to see all agreements or find agreements by a specific person or status.",
    side_effects="Returns a summary list of agreements with basic details."
)

@mcp.tool(description=LIST_AGREEMENTS_DESCRIPTION.model_dump_json())
async def list_agreements(
    filter_party: Annotated[str | None, Field(description="Filter agreements by party name (optional)")] = None,
    filter_status: Annotated[str | None, Field(description="Filter by status: draft, partially_signed, fully_signed (optional)")] = None
) -> str:
    """List all agreements with optional filtering"""
    
    try:
        if not agreements_db:
            return "📭 **No agreements found**\n\nCreate your first agreement with the 'create_agreement' tool!"
        
        agreements = list(agreements_db.values())
        
        # Apply filters
        if filter_party:
            agreements = [
                a for a in agreements 
                if filter_party.lower() in a['party1'].lower() or filter_party.lower() in a['party2'].lower()
            ]
        
        if filter_status:
            agreements = [a for a in agreements if a['status'] == filter_status]
        
        if not agreements:
            return f"📭 **No agreements found** matching your filters\n\nFilter: Party='{filter_party}', Status='{filter_status}'"
        
        # Format list
        agreements_list = []
        for agreement in sorted(agreements, key=lambda x: x['created_at'], reverse=True):
            status_emoji = {
                'draft': '📝',
                'partially_signed': '⏳',
                'fully_signed': '✅'
            }.get(agreement['status'], '📄')
            
            payment_text = f" | ₹{agreement['payment_amount']}" if agreement.get('payment_amount') else ""
            
            agreements_list.append(
                f"{status_emoji} **{agreement['id']}** - {agreement['party1']} ↔ {agreement['party2']}{payment_text}"
            )
        
        return f"""
📚 **Agreements List** ({len(agreements)} total)

{chr(10).join(agreements_list)}

**Legend**: 📝 Draft | ⏳ Partially Signed | ✅ Fully Signed

Use `get_agreement("agreement_id")` for full details.
"""
        
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to list agreements: {str(e)}"))

# --- Tool: delete_agreement ---
DELETE_AGREEMENT_DESCRIPTION = RichToolDescription(
    description="Delete an agreement permanently (use with caution).",
    use_when="Use only when an agreement needs to be completely removed from the system.",
    side_effects="Permanently deletes the agreement - this action cannot be undone."
)

@mcp.tool(description=DELETE_AGREEMENT_DESCRIPTION.model_dump_json())
async def delete_agreement(
    agreement_id: Annotated[str, Field(description="The unique ID of the agreement to delete")],
    confirm: Annotated[bool, Field(description="Set to true to confirm deletion")] = False
) -> str:
    """Delete an agreement (requires confirmation)"""
    
    try:
        if not confirm:
            return f"⚠️ **Deletion requires confirmation**\n\nTo delete agreement '{agreement_id}', call again with confirm=true"
        
        if agreement_id not in agreements_db:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Agreement '{agreement_id}' not found"))
        
        agreement = agreements_db[agreement_id]
        del agreements_db[agreement_id]
        
        return f"""
🗑️ **Agreement Deleted**

**Deleted Agreement**: {agreement_id}
**Was between**: {agreement['party1']} ↔ {agreement['party2']}
**Status**: {agreement['status']}

This action cannot be undone.
"""
        
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to delete agreement: {str(e)}"))

# --- Run MCP Server ---
async def main():
    try:
        # Get port from environment variable (Railway/Vercel) or default to 8086
        port = int(os.environ.get("PORT", 8086))
        host = os.environ.get("HOST", "0.0.0.0")
        
        logger.info("🚀 QuickPact MCP Server starting")
        logger.info(f"🌐 Server URL: http://{host}:{port}")
        logger.info("🎯 Available tools: create_agreement, sign_agreement, get_agreement, list_agreements, validate")
        logger.info("� Use bearer token authentication with Puch AI")
        logger.info(f"📱 Phone validation: {MY_NUMBER}")
        logger.info("🔗 MCP Endpoint: /mcp")
        
        print("�🚀 QuickPact MCP Server starting")
        print(f"🌐 Server URL: http://{host}:{port}")
        print("🎯 Available tools: create_agreement, sign_agreement, get_agreement, list_agreements, validate")
        print("🔑 Use bearer token authentication with Puch AI")
        print("📱 Phone validation:", MY_NUMBER)
        print("🔗 MCP Endpoint: /mcp")
        
        await mcp.run_async("streamable-http", host=host, port=port)
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
