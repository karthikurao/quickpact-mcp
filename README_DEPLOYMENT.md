# 🚀 QuickPact MCP Server

**Micro Agreement Creator for Puch AI Hackathon**

## 🌟 Live Deployment

**🌐 Vercel**: https://quickpact-rjdk7s7fz-karthikrao.vercel.app/mcp

## 🔥 Features

- **5 MCP Tools**: create_agreement, sign_agreement, get_agreement, list_agreements, validate
- **Natural Language Processing**: Convert plain English to structured agreements
- **Digital Signatures**: Timestamped, immutable signing
- **Phone Validation**: Real identity verification
- **Bearer Token Authentication**: Secure Puch AI integration

## 🛠️ MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `validate` | Returns authenticated phone number | `919876543210` |
| `create_agreement` | Creates micro-agreement from natural language | "Pay ₹2000 for logo by Friday" |
| `sign_agreement` | Adds digital signature with timestamp | Signs with phone verification |
| `get_agreement` | Retrieves agreement by ID | Get `qp_abc12345` |
| `list_agreements` | Lists all agreements with filters | All signed agreements |

## 🔗 Connect to Puch AI

```bash
/mcp connect https://quickpact-rjdk7s7fz-karthikrao.vercel.app/mcp quickpact_supersecret_token_2025
```

## 🎯 Tech Stack

- **Framework**: FastMCP 2.11.2
- **Runtime**: Python 3.11
- **Deployment**: Vercel Serverless Functions
- **Authentication**: Bearer Token
- **Database**: In-memory (demo) → Firebase (production)

## 🏆 Hackathon Ready

Built for **Puch AI Hackathon Phase 1** - Ready for deployment and Phase 2 traction!

---

*Created with ❤️ for micro-agreements everywhere*
