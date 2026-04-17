#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}Starting GitHub Codebase RAG Assistant - Development Mode${NC}"
echo ""
echo -e "${BLUE}Services will start in the background...${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}[1/3] Starting Backend API...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Start celery worker
echo -e "${GREEN}[2/3] Starting Celery Worker...${NC}"
cd backend
celery -A app.jobs.worker worker --loglevel=info > ../logs/celery.log 2>&1 &
CELERY_PID=$!
cd ..

# Start frontend
echo -e "${GREEN}[3/3] Starting Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✓ All services started!${NC}"
echo ""
echo "Service PIDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Celery:   $CELERY_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Logs are available in the logs/ directory"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background processes
wait
