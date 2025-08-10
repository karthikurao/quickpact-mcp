#!/usr/bin/env python3
"""
Test script for QuickPact MCP Server
Run this to test the server endpoints locally
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.environ.get("PORT", 8086))
BASE_URL = f"http://localhost:{PORT}"
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "quickpact_supersecret_token_2025")

async def test_mcp_server():
    """Test the MCP server endpoints"""
    
    print("🧪 Testing QuickPact MCP Server")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("\n1️⃣ Testing server health...")
        try:
            response = await client.get(f"{BASE_URL}/mcp")
            print(f"✅ Server is running: {response.status_code}")
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return
        
        # Test 2: Validate tool (required by Puch)
        print("\n2️⃣ Testing validate tool...")
        try:
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "validate",
                    "arguments": {}
                }
            }
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Validate tool works: {result}")
            else:
                print(f"❌ Validate failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Validate test failed: {e}")
        
        # Test 3: Create agreement
        print("\n3️⃣ Testing create_agreement tool...")
        try:
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "create_agreement",
                    "arguments": {
                        "party1": "Alice Johnson",
                        "party2": "Bob Smith",
                        "terms": "I'll design a logo by Friday, you'll pay ₹2000",
                        "deadline": "by Friday"
                    }
                }
            }
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(f"{BASE_URL}/mcp", json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agreement created successfully!")
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Extract agreement ID for next test
                if 'content' in result and result['content']:
                    content = result['content'][0]['text']
                    # Simple extraction of agreement ID from response
                    import re
                    agreement_id_match = re.search(r'qp_[a-f0-9]{8}', content)
                    if agreement_id_match:
                        agreement_id = agreement_id_match.group()
                        print(f"📋 Agreement ID: {agreement_id}")
                        
                        # Test 4: Sign agreement
                        print(f"\n4️⃣ Testing sign_agreement tool...")
                        sign_payload = {
                            "method": "tools/call",
                            "params": {
                                "name": "sign_agreement",
                                "arguments": {
                                    "agreement_id": agreement_id,
                                    "signer_name": "Alice Johnson",
                                    "signer_role": "party1"
                                }
                            }
                        }
                        
                        sign_response = await client.post(f"{BASE_URL}/mcp", json=sign_payload, headers=headers)
                        if sign_response.status_code == 200:
                            sign_result = sign_response.json()
                            print(f"✅ Agreement signed successfully!")
                            print(f"Sign response: {json.dumps(sign_result, indent=2)}")
                        else:
                            print(f"❌ Sign failed: {sign_response.status_code} - {sign_response.text}")
                        
                        # Test 5: Get agreement
                        print(f"\n5️⃣ Testing get_agreement tool...")
                        get_payload = {
                            "method": "tools/call",
                            "params": {
                                "name": "get_agreement",
                                "arguments": {
                                    "agreement_id": agreement_id
                                }
                            }
                        }
                        
                        get_response = await client.post(f"{BASE_URL}/mcp", json=get_payload, headers=headers)
                        if get_response.status_code == 200:
                            get_result = get_response.json()
                            print(f"✅ Agreement retrieved successfully!")
                            print(f"Get response: {json.dumps(get_result, indent=2)}")
                        else:
                            print(f"❌ Get agreement failed: {get_response.status_code} - {get_response.text}")
                        
                        # Test 6: List agreements
                        print(f"\n6️⃣ Testing list_agreements tool...")
                        list_payload = {
                            "method": "tools/call",
                            "params": {
                                "name": "list_agreements",
                                "arguments": {}
                            }
                        }
                        
                        list_response = await client.post(f"{BASE_URL}/mcp", json=list_payload, headers=headers)
                        if list_response.status_code == 200:
                            list_result = list_response.json()
                            print(f"✅ Agreements listed successfully!")
                            print(f"List response: {json.dumps(list_result, indent=2)}")
                        else:
                            print(f"❌ List agreements failed: {list_response.status_code} - {list_response.text}")
                
            else:
                print(f"❌ Create agreement failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Create agreement test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
    print("\nNext steps:")
    print("1. Deploy to Railway/Vercel for HTTPS")
    print("2. Connect to Puch AI with /mcp connect")
    print("3. Start creating real agreements!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
