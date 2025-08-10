#!/usr/bin/env python3
"""
Final validation script for QuickPact MCP Server
Comprehensive tests before deployment
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING!")
        return False

def check_env_vars():
    """Check environment variables"""
    print("\n🔧 Environment Variables:")
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "AUTH_TOKEN": "Bearer token for MCP authentication",
        "MY_NUMBER": "Phone number for Puch AI validation"
    }
    
    all_good = True
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Don't print sensitive values, just confirm they exist
            print(f"✅ {var}: {'*' * len(value)} ({desc})")
        else:
            print(f"❌ {var}: NOT SET - {desc}")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check if all required dependencies can be imported"""
    print("\n📦 Dependencies:")
    
    required_modules = [
        ("fastmcp", "FastMCP framework"),
        ("dotenv", "Environment variable loading"),
        ("pydantic", "Data validation"),
        ("uvicorn", "ASGI server"),
        ("mcp", "Model Context Protocol"),
        ("httpx", "HTTP client for testing")
    ]
    
    all_good = True
    for module, desc in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: {desc}")
        except ImportError:
            print(f"❌ {module}: NOT INSTALLED - {desc}")
            all_good = False
    
    return all_good

def validate_server_code():
    """Basic validation of server code"""
    print("\n🐍 Server Code Validation:")
    
    try:
        # Try to import the server module
        import quickpact_mcp_server
        print("✅ Server module imports successfully")
        
        # Check if key components exist
        if hasattr(quickpact_mcp_server, 'mcp'):
            print("✅ MCP server instance exists")
        else:
            print("❌ MCP server instance not found")
            return False
            
        if hasattr(quickpact_mcp_server, 'agreements_db'):
            print("✅ Agreement database exists")
        else:
            print("❌ Agreement database not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Server code validation failed: {e}")
        return False

def check_deployment_files():
    """Check deployment configuration files"""
    print("\n🚀 Deployment Files:")
    
    files_to_check = [
        ("requirements.txt", "Python dependencies"),
        ("Procfile", "Railway/Heroku process definition"),
        ("runtime.txt", "Python runtime version"),
        ("railway.json", "Railway deployment configuration"),
        (".gitignore", "Git ignore rules"),
        ("README.md", "Documentation")
    ]
    
    all_good = True
    for file_path, desc in files_to_check:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    return all_good

def validate_requirements_txt():
    """Validate requirements.txt has all needed packages"""
    print("\n📋 Requirements Validation:")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        required_packages = ["fastmcp", "python-dotenv", "pydantic", "uvicorn", "mcp"]
        
        all_good = True
        for package in required_packages:
            if package in requirements:
                print(f"✅ {package} found in requirements.txt")
            else:
                print(f"❌ {package} missing from requirements.txt")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def validate_env_file():
    """Validate .env file format"""
    print("\n⚙️ Environment File Validation:")
    
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "AUTH_TOKEN=" in env_content:
            print("✅ AUTH_TOKEN defined in .env")
        else:
            print("❌ AUTH_TOKEN not found in .env")
            return False
            
        if "MY_NUMBER=" in env_content:
            print("✅ MY_NUMBER defined in .env")
        else:
            print("❌ MY_NUMBER not found in .env")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ .env file not found")
        return False

def run_all_checks():
    """Run all validation checks"""
    print("🔍 QuickPact MCP Server - Final Validation")
    print("=" * 50)
    
    checks = [
        check_deployment_files,
        validate_requirements_txt,
        validate_env_file,
        check_env_vars,
        check_dependencies,
        validate_server_code
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 ALL CHECKS PASSED! ✅")
        print("\n🚀 Ready for deployment!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Connect to Puch AI: /mcp connect <https_url> <auth_token>")
        print("3. Test in Puch AI environment")
        print("4. Submit to hackathon!")
        return True
    else:
        print("❌ SOME CHECKS FAILED!")
        print(f"\nPassed: {sum(results)}/{len(results)}")
        print("Please fix the issues above before deploying.")
        return False

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
