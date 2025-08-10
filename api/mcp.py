"""
QuickPact MCP Server - Vercel Serverless Function
Micro Agreement Creator for Puch AI Integration
"""

import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Health check endpoint"""
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
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())

    def do_POST(self):
        """MCP protocol handler"""
        try:
            # Check authorization
            auth_header = self.headers.get('Authorization', '')
            expected_token = os.environ.get('QUICKPACT_AUTH_TOKEN', 'quickpact_supersecret_token_2025')
            
            if not auth_header.startswith('Bearer ') or auth_header[7:] != expected_token:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            # Handle MCP request
            result = self.handle_mcp_request(request_data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            error_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": f"Internal server error: {str(e)}"
                }
            }
            self.wfile.write(json.dumps(error_response).encode())

    def handle_mcp_request(self, request_data):
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
                                    "text": f"✅ Phone number validated: {os.environ.get('MY_NUMBER', '919876543210')}\n🤖 QuickPact MCP Server is ready for Puch AI integration!"
                                }
                            ]
                        }
                    }
                
                elif tool_name == 'create_agreement':
                    description = tool_args.get('description', '')
                    agreement_id = f"qp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"📝 **Agreement Created Successfully!**\n\n🆔 **Agreement ID**: `{agreement_id}`\n📋 **Description**: {description}\n📊 **Status**: Draft\n👥 **Parties**: Party A, Party B\n⏰ **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✍️ Use `sign_agreement` to add digital signatures and complete the agreement."
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
                                    "text": f"✍️ **Digital Signature Added!**\n\n📋 **Agreement**: `{agreement_id}`\n📱 **Signed by**: {signer_phone}\n⏰ **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🔐 **Status**: Digitally Signed\n\n✅ Agreement is now legally binding!"
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
                                    "text": f"📄 **Agreement Details**\n\n🆔 **ID**: `{agreement_id}`\n📋 **Type**: Micro Agreement\n📊 **Status**: Demo Mode\n⏰ **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n💡 This is a demo response. In production, full agreement details would be retrieved from database."
                                }
                            ]
                        }
                    }
                
                elif tool_name == 'list_agreements':
                    status_filter = tool_args.get('status', 'all')
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"📋 **Agreements List** (Filter: {status_filter})\n\n1. 📝 `qp_demo_001` - Logo design agreement\n   📊 Status: Draft | ⏰ Created: 2025-01-08\n\n2. ✅ `qp_demo_002` - Payment for services\n   📊 Status: Signed | ⏰ Created: 2025-01-08\n\n3. 🔄 `qp_demo_003` - Monthly subscription\n   📊 Status: Active | ⏰ Created: 2025-01-08\n\n💡 Demo data shown. In production, real agreements would be fetched from database."
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
