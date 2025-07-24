#!/bin/bash

# Model Myself - Automated Startup Script
# This script starts MongoDB, Backend (port 8089), and Frontend (port 3001)

echo "🚀 Starting Model Myself Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    echo -e "${YELLOW}Killing processes on port $port...${NC}"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check and start MongoDB
echo -e "${BLUE}1. Checking MongoDB status...${NC}"
if brew services list | grep mongodb-community | grep started >/dev/null; then
    echo -e "${GREEN}✅ MongoDB is already running${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB not running, starting it...${NC}"
    if sudo brew services start mongodb-community; then
        echo -e "${GREEN}✅ MongoDB started successfully${NC}"
        sleep 3  # Wait for MongoDB to fully start
    else
        echo -e "${RED}❌ Failed to start MongoDB${NC}"
        exit 1
    fi
fi

# Check for existing processes and kill them if needed
echo -e "${BLUE}2. Cleaning up existing processes...${NC}"

if check_port 8089; then
    echo -e "${YELLOW}Backend port 8089 is in use${NC}"
    kill_port 8089
fi

if check_port 3001; then
    echo -e "${YELLOW}Frontend port 3001 is in use${NC}"
    kill_port 3001
fi

# Start Backend
echo -e "${BLUE}3. Starting Backend (port 8089)...${NC}"
cd Model_Myself/backend

# Check for Python command
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python.${NC}"
    exit 1
fi

echo -e "${GREEN}Using $PYTHON_CMD${NC}"

# Activate virtual environment and start backend
source venv/bin/activate && $PYTHON_CMD main.py > ../../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if check_port 8089; then
    echo -e "${GREEN}✅ Backend is running on http://localhost:8089${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Start Frontend
echo -e "${BLUE}4. Starting Frontend (port 3001)...${NC}"
cd ..

# Start frontend in background
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 8

# Check if frontend is running
if check_port 3001; then
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3001${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    exit 1
fi

# Final status
echo -e "${GREEN}"
echo "🎉 Model Myself Application Started Successfully!"
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend:  http://localhost:8089"
echo "💾 MongoDB:  Running"
echo ""
echo "📋 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  backend.log"
echo "   Frontend: frontend.log"
echo ""
echo "To stop all services, run: ./stop.sh"
echo -e "${NC}"

# Save PIDs for easy stopping
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Keep script running and monitor services
echo -e "${BLUE}Monitoring services... Press Ctrl+C to stop all services.${NC}"

cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
    rm -f .backend.pid .frontend.pid
    exit 0
}

trap cleanup INT TERM

# Monitor services
while true; do
    sleep 10
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died${NC}"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died${NC}"
        break
    fi
done 