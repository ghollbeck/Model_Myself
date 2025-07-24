#!/bin/bash

# Model Myself - Stop Script
# This script stops all running services

echo "🛑 Stopping Model Myself Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill processes on a port
kill_port() {
    local port=$1
    local service_name=$2
    echo -e "${YELLOW}Stopping $service_name (port $port)...${NC}"
    
    if lsof -i:$port >/dev/null 2>&1; then
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if lsof -i:$port >/dev/null 2>&1; then
            echo -e "${RED}❌ Failed to stop $service_name${NC}"
        else
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  $service_name was not running${NC}"
    fi
}

# Stop services using PID files if available
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo -e "${YELLOW}Stopping Backend (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo -e "${YELLOW}Stopping Frontend (PID: $FRONTEND_PID)...${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    rm -f .frontend.pid
fi

# Stop services by port as backup
kill_port 8089 "Backend"
kill_port 3001 "Frontend"

# Option to stop MongoDB (ask user)
echo -e "${BLUE}Do you want to stop MongoDB as well? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Stopping MongoDB...${NC}"
    if sudo brew services stop mongodb-community; then
        echo -e "${GREEN}✅ MongoDB stopped${NC}"
    else
        echo -e "${RED}❌ Failed to stop MongoDB${NC}"
    fi
else
    echo -e "${BLUE}ℹ️  MongoDB left running${NC}"
fi

# Clean up log files (optional)
echo -e "${BLUE}Do you want to clean up log files? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -f backend.log frontend.log
    echo -e "${GREEN}✅ Log files cleaned${NC}"
fi

echo -e "${GREEN}🎯 Model Myself Application stopped successfully!${NC}" 