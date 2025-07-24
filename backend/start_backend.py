#!/usr/bin/env python3
"""
Model Myself Backend Starter
This script automatically starts MongoDB and then runs the backend server
"""

import subprocess
import sys
import time
import os
import platform
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def is_mongodb_running():
    """Check if MongoDB is running"""
    success, stdout, stderr = run_command("brew services list | grep mongodb-community")
    if success:
        return "started" in stdout
    return False

def start_mongodb():
    """Start MongoDB service"""
    print("🔧 Starting MongoDB...")
    
    if is_mongodb_running():
        print("✅ MongoDB is already running")
        return True
    
    # Try to start MongoDB
    success, stdout, stderr = run_command("sudo brew services start mongodb-community")
    
    if success:
        print("✅ MongoDB started successfully")
        print("⏳ Waiting for MongoDB to initialize...")
        time.sleep(5)
        
        # Verify MongoDB is running
        if is_mongodb_running():
            print("✅ MongoDB is running and ready")
            return True
        else:
            print("⚠️  MongoDB started but not yet ready, waiting...")
            time.sleep(5)
            return is_mongodb_running()
    else:
        print(f"❌ Failed to start MongoDB: {stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn available")
    except ImportError as e:
        print(f"❌ Missing Python dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Make sure you're in the backend directory")
        return False
    
    print("✅ All dependencies check passed")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Model Myself Backend...")
    
    # Set environment variables for better MongoDB connection handling
    os.environ["MONGODB_STARTUP"] = "auto"
    
    try:
        # Import and run the main application
        import main
        
        print("✅ Backend imports successful")
        print("🌐 Starting server on http://localhost:8089")
        print("📋 MongoDB integration: Enabled")
        print("📁 File storage: MongoDB with local fallback")
        print("\n🔥 Server is starting...")
        print("=" * 50)
        
        # Run the server
        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(
                "main:app",
                host="0.0.0.0",
                port=8089,
                reload=True,
                log_level="info"
            )
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚀 Model Myself Backend Startup")
    print("=" * 40)
    
    # Check if we're on macOS (required for brew services)
    if platform.system() != "Darwin":
        print("⚠️  This script is designed for macOS with Homebrew")
        print("💡 You may need to start MongoDB manually on other systems")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start MongoDB
    if not start_mongodb():
        print("⚠️  MongoDB failed to start, continuing with local storage fallback")
        print("💡 The backend will still work but use local file storage")
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main() 