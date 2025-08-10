"""
QuickPact MCP Server - Vercel Serverless Function
Micro Agreement Creator for Puch AI Integration
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify

# Set environment variables
os.environ['QUICKPACT_AUTH_TOKEN'] = os.environ.get('QUICKPACT_AUTH_TOKEN', 'quickpact_supersecret_token_2025')
os.environ['MY_NUMBER'] = os.environ.get('MY_NUMBER', '919876543210')

app = Flask(__name__)

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
                
                agreement = {
                    "id": agreement_id,
                    "description": description,
                    "parties": ["Party A", "Party B"],
                    "status": "draft",
                    "created_at": datetime.now().isoformat(),
                }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Agreement created successfully!\n\n**Agreement ID**: {agreement_id}\n**Description**: {description}\n**Status**: Draft\n\nUse `sign_agreement` to add digital signatures."
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

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handler():
    """Main Flask handler"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
    
    # Handle GET requests (health check)
    if request.method == 'GET':
        response_data = {
            "name": "QuickPact MCP Server - Micro Agreement Creator",
            "version": "1.0.0",
            "status": "healthy",
            "protocol": "MCP 1.0.0",
            "tools": ["validate", "create_agreement", "sign_agreement", "get_agreement", "list_agreements"],
            "auth": "Bearer token required",
            "phone": os.environ.get('MY_NUMBER', '919876543210'),
            "endpoint": "/api/mcp"
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    # Handle POST requests (MCP protocol)
    if request.method == 'POST':
        try:
            # Check authorization
            auth_header = request.headers.get('Authorization', '')
            expected_token = os.environ.get('QUICKPACT_AUTH_TOKEN', 'quickpact_supersecret_token_2025')
            
            if not auth_header.startswith('Bearer ') or auth_header[7:] != expected_token:
                response = jsonify({"error": "Unauthorized"})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.status_code = 401
                return response
            
            # Parse request body
            try:
                request_data = request.get_json()
                if not request_data:
                    raise ValueError("No JSON data")
            except Exception as e:
                response = jsonify({"error": "Invalid JSON"})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.status_code = 400
                return response
            
            # Handle MCP request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(handle_mcp_request(request_data))
            loop.close()
            
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": f"Internal server error: {str(e)}"
                }
            }
            response = jsonify(error_response)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.status_code = 500
            return response
    
    # Unsupported method
    response = jsonify({"error": "Method not allowed"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 405
    return response

# Vercel handler
def handler_func(request, context=None):
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=dict(request.headers),
        data=request.body if hasattr(request, 'body') else None
    ):
        response = app.full_dispatch_request()
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
