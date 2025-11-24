#!/bin/bash
# Quick Start Script for HackTheTrack Local Development
# This starts both backend and frontend servers

echo "🚀 Starting HackTheTrack Development Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "Goodbye! 👋"
    exit 0
}

# Set up cleanup trap
trap cleanup INT TERM

# Start Backend
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend in background
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${RED}Backend failed to start. Check backend.log for errors${NC}"
    cat ../backend.log
    exit 1
fi

echo -e "${GREEN}✓ Backend started successfully on http://localhost:8000${NC}"
echo ""

# Start Frontend
cd ../frontend

echo -e "${BLUE}Starting Frontend Server...${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env
fi

# Start frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

echo ""
echo -e "${GREEN}✓ Frontend started successfully on http://localhost:5173${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 HackTheTrack is ready!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  Frontend:     ${BLUE}http://localhost:5173${NC}"
echo -e "  Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "  Backend logs: tail -f backend.log"
echo "  Frontend logs: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running
while true; do
    sleep 1
done
