# Test your deployed QuickPact MCP Server
Write-Host "🧪 Testing QuickPact MCP Server..." -ForegroundColor Green

# Get the Railway URL (you'll need to replace this with your actual URL)
$RAILWAY_URL = "https://your-service-name.up.railway.app"
$AUTH_TOKEN = "quickpact_supersecret_token_2025"

Write-Host "🔍 Testing MCP endpoint..." -ForegroundColor Yellow

# Test the validate tool (which returns your phone number)
try {
    $response = Invoke-RestMethod -Uri "$RAILWAY_URL/mcp" -Method GET -Headers @{
        "Authorization" = "Bearer $AUTH_TOKEN"
        "Content-Type" = "application/json"
    }
    Write-Host "✅ MCP Server is responding!" -ForegroundColor Green
    Write-Host "Response: $response" -ForegroundColor White
} catch {
    Write-Host "❌ Error connecting to MCP server:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 To connect to Puch AI, use:" -ForegroundColor Cyan
Write-Host "/mcp connect $RAILWAY_URL/mcp $AUTH_TOKEN" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Expected tools available:" -ForegroundColor Yellow
Write-Host "  - validate (returns phone: 919876543210)" -ForegroundColor White
Write-Host "  - create_agreement (creates micro-agreements)" -ForegroundColor White
Write-Host "  - sign_agreement (adds digital signatures)" -ForegroundColor White
Write-Host "  - get_agreement (retrieves agreement by ID)" -ForegroundColor White
Write-Host "  - list_agreements (lists all agreements)" -ForegroundColor White
