#!/bin/bash
# Quick start script for GitHub Codebase RAG Assistant with Docker

set -e

echo "=========================================="
echo "GitHub Codebase RAG Assistant"
echo "Docker Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    
    # Generate a secure secret key
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        # Replace the SECRET_KEY in .env
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        else
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        fi
        echo "✓ Generated secure SECRET_KEY"
    else
        echo "⚠ Warning: openssl not found. Please manually set SECRET_KEY in .env"
    fi
fi

# Ask user for deployment mode
echo ""
echo "Select deployment mode:"
echo "1) Production (recommended for deployment)"
echo "2) Development (with hot-reloading)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        MODE="production"
        COMPOSE_CMD="docker-compose up -d"
        ;;
    2)
        MODE="development"
        COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
        ;;
    *)
        echo "Invalid choice. Defaulting to production mode."
        MODE="production"
        COMPOSE_CMD="docker-compose up -d"
        ;;
esac

echo ""
echo "Starting services in $MODE mode..."
echo ""

# Start services
eval $COMPOSE_CMD

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
./docker-healthcheck.sh all || true

echo ""
echo "=========================================="
echo "Services Started!"
echo "=========================================="
echo ""

if [ "$MODE" = "production" ]; then
    echo "Access points:"
    echo "  - Frontend: http://localhost"
    echo "  - Backend API: http://localhost/api/v1"
    echo "  - API Docs: http://localhost/api/v1/docs"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3001 (admin/admin)"
else
    echo "Access points (Development):"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000/api/v1"
    echo "  - API Docs: http://localhost:8000/api/v1/docs"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - Ollama: http://localhost:11434"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3001 (admin/admin)"
fi

echo ""
echo "Next steps:"
echo "  1. Pull Ollama models: make docker-pull-models"
echo "  2. View logs: make docker-logs"
echo "  3. Check status: make docker-ps"
echo ""
echo "To stop services: make docker-down"
echo ""
