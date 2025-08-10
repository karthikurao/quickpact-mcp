# QuickPact MCP Server 🤝

A Model Context Protocol (MCP) server for creating micro-agreements between parties. Built for the Puch AI Hackathon.

## 🎯 What is QuickPact?

QuickPact allows users to create structured micro-agreements from natural language input. Perfect for:
- Freelance work agreements
- Small payments and services
- Quick handshake deals
- Simple commitments between parties

## 🚀 Live Demo

**MCP Server**: `https://quickpact-mcp.railway.app/mcp` (coming soon)
**Auth Token**: Contact for hackathon demo
**Phone**: 919876543210

## 🛠️ Available MCP Tools

### 1. `create_agreement`
Create a structured micro-agreement from natural language.

**Parameters:**
- `party1` (string): First party name/email
- `party2` (string): Second party name/email  
- `terms` (string): Agreement terms in plain English
- `deadline` (string): When work should be completed

**Example:**
```
create_agreement(
  party1="John Doe",
  party2="Jane Smith", 
  terms="I'll design a logo by Friday, you'll pay ₹2000",
  deadline="by Friday"
)
```

### 2. `sign_agreement`
Add digital signature to an existing agreement.

**Parameters:**
- `agreement_id` (string): Agreement ID to sign
- `signer_name` (string): Full name of signer
- `signer_role` (string): "party1", "party2", or "witness"

### 3. `get_agreement`
Retrieve full agreement details by ID.

**Parameters:**
- `agreement_id` (string): Agreement ID to retrieve

### 4. `list_agreements`
List all agreements with optional filtering.

**Parameters:**
- `filter_party` (string, optional): Filter by party name
- `filter_status` (string, optional): Filter by status

### 5. `validate`
Required tool for Puch AI authentication. Returns phone number.

## 🔧 Local Development

### Prerequisites
- Python 3.11+
- pip or uv

### Setup
```bash
# Clone the repository
git clone <repo-url>
cd quickpact-mcp

# Install dependencies
pip install fastmcp python-dotenv pydantic uvicorn

# Create .env file
cp .env.example .env
# Edit .env with your AUTH_TOKEN and MY_NUMBER

# Run the server
python quickpact_mcp_server.py
```

The server will start on `http://localhost:8086/mcp`

### Environment Variables
```bash
AUTH_TOKEN=your_secret_token_here
MY_NUMBER=919876543210
```

## 🌐 Connecting to Puch AI

1. Deploy your MCP server to a public HTTPS endpoint
2. In Puch AI chat, run:
   ```
   /mcp connect https://your-server.com/mcp YOUR_AUTH_TOKEN
   ```
3. Puch will validate using your phone number
4. Start using QuickPact tools in Puch AI!

## 📱 Usage Examples

### Creating an Agreement
```
User: "Create an agreement where I design a logo by Friday and they pay ₹2000"

Puch AI calls: create_agreement(
  party1="User",
  party2="Client",
  terms="I'll design a logo by Friday, you'll pay ₹2000", 
  deadline="by Friday"
)

Result: Agreement qp_abc123 created with structured terms
```

### Signing the Agreement
```
User: "Sign agreement qp_abc123 as John Doe for party1"

Puch AI calls: sign_agreement("qp_abc123", "John Doe", "party1")

Result: Digital signature added with timestamp
```

## 🎨 Features

- **AI-Powered Parsing**: Extracts parties, payments, deadlines from natural language
- **Digital Signatures**: Timestamped signatures with role verification
- **Shareable Links**: Each agreement gets a unique shareable URL
- **Status Tracking**: Draft → Partially Signed → Fully Signed
- **Payment Detection**: Automatically detects amounts and currencies
- **Deadline Parsing**: Understands various deadline formats

## 🏗️ Architecture

```
User Input → Puch AI → MCP Server → Agreement Parser → Database → Response
```

1. User describes agreement in natural language
2. Puch AI calls our MCP tools
3. Agreement parser extracts structured data
4. Stored with unique ID and shareable link
5. Parties can sign digitally
6. Immutable record with timestamps

## 📊 Hackathon Metrics

Track real-time usage on the Puch AI leaderboard:
- Number of agreements created
- Active users
- Signature completion rate
- Viral sharing metrics

## 🚀 Deployment

### Railway (Recommended)
1. Connect GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Manual Deployment
```bash
# Build and deploy to any Python hosting service
# Ensure HTTPS endpoint for Puch AI compatibility
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with local MCP server
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details

## 🎯 Hackathon Submission

- **Team**: QuickPact Team
- **Category**: MCP Server Extension
- **Focus**: Micro-agreements and digital handshakes
- **Traction Goal**: Get people actually using it for real agreements

---

**Built with ❤️ for the Puch AI Hackathon**
