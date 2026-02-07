#!/bin/bash
# Setup script for deployment

echo "🚀 Hiring Assistant - Setup & Deployment Script"
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Virtual environment ready"

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/your-secret-key-here-change-this/$SECRET_KEY/" .env
    
    echo "✓ Generated SECRET_KEY"
else
    echo "✓ .env file already exists"
fi

# Create upload directory
mkdir -p uploads/resumes
echo "✓ Created upload directories"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "To run locally:"
echo "  source venv/bin/activate  # On Linux/Mac"
echo "  venv\\Scripts\\activate    # On Windows"
echo "  python wsgi.py"
echo ""
echo "To run in production:"
echo "  export FLASK_ENV=production  # On Linux/Mac"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"
echo ""
