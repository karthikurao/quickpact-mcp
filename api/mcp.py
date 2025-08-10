"""
QuickPact MCP Server - Vercel Serverless Function
Micro Agreement Creator for Puch AI Integration
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# Set environment variables for compatibility
os.environ['QUICKPACT_AUTH_TOKEN'] = os.environ.get('QUICKPACT_AUTH_TOKEN', 'quickpact_supersecret_token_2025')
os.environ['MY_NUMBER'] = os.environ.get('MY_NUMBER', '919876543210')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MCP Protocol handler
async def handle_mcp_request(request_data: dict) -> dict:
    """Handle MCP protocol requests"""
    
    method = request_data.get('method', '')
    params = request_data.get('params', {})
    request_id = request_data.get('id', 1)
    
    try:
        if method == 'initialize':
            # MCP initialization handshake
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "1.0.0",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "QuickPact MCP Server - Micro Agreement Creator",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == 'tools/list':
            # List available tools
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "validate",
                            "description": "Validate phone number for Puch AI authentication",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "create_agreement",
                            "description": "Create a micro-agreement from natural language",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "description": {
                                        "type": "string",
                                        "description": "Natural language description of the agreement"
                                    }
                                },
                                "required": ["description"]
                            }
                        },
                        {
                            "name": "sign_agreement",
                            "description": "Add digital signature to an agreement",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "agreement_id": {
                                        "type": "string",
                                        "description": "ID of the agreement to sign"
                                    },
                                    "signer_phone": {
                                        "type": "string",
                                        "description": "Phone number of the signer"
                                    }
                                },
                                "required": ["agreement_id", "signer_phone"]
                            }
                        },
                        {
                            "name": "get_agreement",
                            "description": "Retrieve an agreement by ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "agreement_id": {
                                        "type": "string",
                                        "description": "ID of the agreement to retrieve"
                                    }
                                },
                                "required": ["agreement_id"]
                            }
                        },
                        {
                            "name": "list_agreements",
                            "description": "List all agreements with optional filters",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "status": {
                                        "type": "string",
                                        "description": "Filter by status (draft, signed, completed)"
                                    }
                                },
                                "required": []
                            }
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            # Call a specific tool
            tool_name = params.get('name', '')
            tool_args = params.get('arguments', {})
            
            if tool_name == 'validate':
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Phone number validated: {os.environ.get('MY_NUMBER', '919876543210')}"
                            }
                        ]
                    }
                }
            
            elif tool_name == 'create_agreement':
                description = tool_args.get('description', '')
                agreement_id = f"qp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Simple parsing
                parties = ["Party A", "Party B"]
                if "pay" in description.lower():
                    amount_start = description.lower().find("₹")
                    if amount_start == -1:
                        amount_start = description.lower().find("rs")
                    payment = "Amount specified in description"
                else:
                    payment = "No payment specified"
                
                agreement = {
                    "id": agreement_id,
                    "description": description,
                    "parties": parties,
                    "payment": payment,
                    "status": "draft",
                    "created_at": datetime.now().isoformat(),
                    "signed_by": []
                }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Agreement created successfully!\n\n**Agreement ID**: {agreement_id}\n**Description**: {description}\n**Status**: Draft\n**Parties**: {', '.join(parties)}\n\nUse `sign_agreement` to add digital signatures."
                            }
                        ]
                    }
                }
            
            elif tool_name == 'sign_agreement':
                agreement_id = tool_args.get('agreement_id', '')
                signer_phone = tool_args.get('signer_phone', '')
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Agreement {agreement_id} signed by {signer_phone} at {datetime.now().isoformat()}"
                            }
                        ]
                    }
                }
            
            elif tool_name == 'get_agreement':
                agreement_id = tool_args.get('agreement_id', '')
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Agreement {agreement_id} details would be shown here (demo mode)"
                            }
                        ]
                    }
                }
            
            elif tool_name == 'list_agreements':
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Demo agreements list:\n1. qp_demo_001 - Logo design agreement (Draft)\n2. qp_demo_002 - Payment for services (Signed)"
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def handler(request):
    """Main Vercel serverless function handler"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': ''
        }
    
    # Handle GET requests (health check)
    if request.method == 'GET':
        response = {
            "name": "QuickPact MCP Server - Micro Agreement Creator",
            "version": "1.0.0",
            "status": "healthy",
            "protocol": "MCP 1.0.0",
            "tools": ["validate", "create_agreement", "sign_agreement", "get_agreement", "list_agreements"],
            "auth": "Bearer token required",
            "phone": os.environ.get('MY_NUMBER', '919876543210'),
            "endpoint": "/api/mcp"
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(response, indent=2)
        }
    
    # Handle POST requests (MCP protocol)
    if request.method == 'POST':
        try:
            # Check authorization
            auth_header = request.headers.get('authorization', '')
            expected_token = os.environ.get('QUICKPACT_AUTH_TOKEN', 'quickpact_supersecret_token_2025')
            
            if not auth_header.startswith('Bearer ') or auth_header[7:] != expected_token:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({"error": "Unauthorized"})
                }
            
            # Parse request body
            try:
                if hasattr(request, 'body'):
                    body = request.body
                elif hasattr(request, 'get_body'):
                    body = request.get_body()
                else:
                    body = request.data if hasattr(request, 'data') else '{}'
                
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                
                request_data = json.loads(body)
            except (json.JSONDecodeError, AttributeError) as e:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({"error": "Invalid JSON"})
                }
            
            # Handle MCP request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(handle_mcp_request(request_data))
            loop.close()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32603,
                        "message": f"Internal server error: {str(e)}"
                    }
                })
            }
    
    # Unsupported method
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({"error": "Method not allowed"})
    }
