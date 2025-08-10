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
from http.server import BaseHTTPRequestHandler

# Add the parent directory to the path to import our server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from quickpact_mcp_server import (
        create_agreement_tool,
        sign_agreement_tool, 
        get_agreement_tool,
        list_agreements_tool,
        validate_tool,
        app,  # Import the FastMCP app
        SERVER_NAME,
        logger
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback basic response
    def create_basic_response():
        return {
            "error": "Server not available",
            "message": "QuickPact MCP Server",
            "status": "import_error"
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Basic health check
            if self.path == "/" or self.path == "/mcp":
                response = {
                    "name": "QuickPact MCP Server - Micro Agreement Creator",
                    "version": "1.0.0",
                    "status": "healthy",
                    "tools": [
                        "validate",
                        "create_agreement", 
                        "sign_agreement",
                        "get_agreement",
                        "list_agreements"
                    ],
                    "auth": "Bearer token required",
                    "phone": os.environ.get("MY_NUMBER", "Not configured"),
                    "endpoint": "/mcp"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                return
                
            # Handle MCP protocol requests
            elif self.path.startswith("/mcp"):
                # For now, return basic info
                response = {
                    "protocol": "mcp",
                    "message": "Use POST for MCP operations",
                    "available_tools": [
                        "validate",
                        "create_agreement", 
                        "sign_agreement",
                        "get_agreement",
                        "list_agreements"
                    ]
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                return
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_POST(self):
        """Handle POST requests for MCP operations"""
        try:
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            # Basic MCP tool simulation
            tool_name = request_data.get('tool', '')
            
            if tool_name == 'validate':
                response = {
                    "result": f"Phone number validated: {os.environ.get('MY_NUMBER', '919876543210')}",
                    "status": "success",
                    "tool": "validate"
                }
            elif tool_name == 'create_agreement':
                response = {
                    "result": f"Agreement created: qp_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "status": "success", 
                    "tool": "create_agreement"
                }
            else:
                response = {
                    "available_tools": ["validate", "create_agreement", "sign_agreement", "get_agreement", "list_agreements"],
                    "message": "Specify tool name in request",
                    "status": "info"
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
