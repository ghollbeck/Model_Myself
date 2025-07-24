#!/bin/bash

# Backend Runner Script
# This script ensures the virtual environment is properly activated before running the backend

cd "$(dirname "$0")"

echo "🔧 Starting Backend with MongoDB integration..."

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if MongoDB is running and start if needed
if ! brew services list | grep mongodb-community | grep started >/dev/null; then
    echo "🔧 Starting MongoDB..."
    sudo brew services start mongodb-community
    sleep 3
fi

# Start the backend
echo "🚀 Starting backend server..."
python main.py 