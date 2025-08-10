# GitHub Repository Setup Instructions

## 🐙 Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `quickpact-mcp`
3. **Description**: `QuickPact MCP Server - Micro Agreement Creator for Puch AI`
4. **Make it Public** (for hackathon visibility)
5. **Don't initialize** (we have existing code)
6. **Click "Create repository"**

## 📤 Push Your Code

```bash
# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/quickpact-mcp.git

# Push to GitHub
git push -u origin master
```

## 🔗 Connect to Vercel via GitHub

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "New Project"**
3. **Import from GitHub**: Select `quickpact-mcp`
4. **Framework**: Leave as "Other"
5. **Root Directory**: `./` (default)
6. **Build Settings**: Use default
7. **Environment Variables**:
   - `QUICKPACT_AUTH_TOKEN` = `quickpact_supersecret_token_2025`
   - `MY_NUMBER` = `919876543210`
8. **Deploy**

## 🛡️ Disable Vercel Authentication

1. **In Vercel project settings**
2. **Go to "Security" tab**
3. **Vercel Authentication**: Set to "None"
4. **Save changes**

This will make your MCP server publicly accessible for Puch AI integration.

## ✅ Final Test

Your MCP server should be available at:
- `https://your-project.vercel.app/mcp`

Test with:
```bash
curl https://your-project.vercel.app/mcp
```

Expected response:
```json
{
  "name": "QuickPact MCP Server - Micro Agreement Creator",
  "tools": ["validate", "create_agreement", "sign_agreement", "get_agreement", "list_agreements"],
  "status": "healthy"
}
```
