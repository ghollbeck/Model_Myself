#!/bin/bash

echo "🚀 Starting Model Myself Project..."
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Dependencies check passed"

# Backend setup
echo ""
echo "🔧 Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt
cd ..

# Frontend setup
echo ""
echo "🔧 Setting up frontend..."
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 To start the applications:"
echo "1. Backend:  cd backend && python main.py (in terminal 1)"
echo "2. Frontend: npm run (in terminal 2)"
echo ""
echo "🌐 URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend:  http://localhost:8000"
echo ""
echo "📝 Check Readme_running.md for detailed logs and changes" 