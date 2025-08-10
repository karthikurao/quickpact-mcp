# PowerShell script to deploy QuickPact MCP Server to Railway
Write-Host "🚀 Deploying QuickPact MCP Server to Railway..." -ForegroundColor Green

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Red
    npm install -g @railway/cli
}

# Check if logged in
$whoami = railway whoami 2>&1
if ($whoami -match "Unauthorized") {
    Write-Host "❌ Not logged into Railway. Please run 'railway login' first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logged in as: $whoami" -ForegroundColor Green

# Initialize if needed
Write-Host "🔧 Initializing Railway project..." -ForegroundColor Yellow
railway init

# Deploy the project
Write-Host "📦 Deploying to Railway..." -ForegroundColor Yellow
railway up

Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
Write-Host "🌐 Please set these environment variables in Railway dashboard:" -ForegroundColor Cyan
Write-Host "   AUTH_TOKEN = quickpact_supersecret_token_2025" -ForegroundColor White
Write-Host "   MY_NUMBER = 919876543210" -ForegroundColor White
Write-Host ""
Write-Host "🌍 Opening Railway dashboard..." -ForegroundColor Yellow
railway open

Write-Host "✅ Deployment complete! Set environment variables and redeploy." -ForegroundColor Green
