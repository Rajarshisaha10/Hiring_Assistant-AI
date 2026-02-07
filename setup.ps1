# Setup script for Windows deployment

Write-Host "🚀 Hiring Assistant - Setup & Deployment Script (Windows)"
Write-Host "=========================================================="

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✓ Python version: $pythonVersion"

# Create virtual environment if not exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..."
    python -m venv venv
}

Write-Host "✓ Virtual environment ready"

# Install dependencies
Write-Host "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "🔑 Creating .env file..."
    Copy-Item .env.example .env
    
    # Generate SECRET_KEY
    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
    (Get-Content .env) -replace 'your-secret-key-here-change-this', $secretKey | Set-Content .env
    
    Write-Host "✓ Generated SECRET_KEY"
} else {
    Write-Host "✓ .env file already exists"
}

# Create upload directory
New-Item -ItemType Directory -Force -Path "uploads/resumes" | Out-Null
Write-Host "✓ Created upload directories"

Write-Host ""
Write-Host "✅ Setup Complete!"
Write-Host ""
Write-Host "To run locally:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python wsgi.py"
Write-Host ""
Write-Host "To run in production:"
Write-Host "  `$env:FLASK_ENV='production'"
Write-Host "  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"
Write-Host ""
