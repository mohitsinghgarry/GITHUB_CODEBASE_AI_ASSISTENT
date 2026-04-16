#!/bin/bash

# GitHub Codebase RAG Assistant - Setup Script

set -e

echo "🚀 Setting up GitHub Codebase RAG Assistant..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites found${NC}"

# Setup backend
echo -e "\n${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env.development" ]; then
    echo "Creating .env.development from example..."
    cp .env.example .env.development
fi

cd ..

# Setup frontend
echo -e "\n${BLUE}Setting up frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Copy environment file if it doesn't exist
if [ ! -f ".env.development" ]; then
    echo "Creating .env.development from example..."
    cp .env.example .env.development
fi

cd ..

# Start development services
echo -e "\n${BLUE}Starting development services (PostgreSQL, Redis, Ollama)...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if docker ps | grep -q "github-rag-postgres-dev"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL may not be running${NC}"
fi

if docker ps | grep -q "github-rag-redis-dev"; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Redis may not be running${NC}"
fi

if docker ps | grep -q "github-rag-ollama-dev"; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠ Ollama may not be running${NC}"
fi

# Pull Ollama model
echo -e "\n${BLUE}Pulling Ollama model (this may take a while)...${NC}"
docker exec github-rag-ollama-dev ollama pull codellama:7b || echo -e "${YELLOW}⚠ Failed to pull Ollama model. You can do this manually later.${NC}"

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Note: Make sure to run database migrations before starting the backend.${NC}"
