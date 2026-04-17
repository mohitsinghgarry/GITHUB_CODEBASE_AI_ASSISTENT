#!/bin/bash

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start celery worker
echo "Starting Celery worker..."
celery -A app.jobs.worker worker --loglevel=info &
CELERY_PID=$!

cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "All services started!"
echo "Backend PID: $BACKEND_PID"
echo "Celery PID: $CELERY_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait
