.PHONY: help setup install-backend install-frontend dev-services start-backend start-frontend dev test clean docker-up docker-down docker-dev-up docker-dev-down docker-build docker-logs docker-ps docker-pull-models

help:
	@echo "GitHub Codebase RAG Assistant - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup              - Complete setup (backend + frontend + services)"
	@echo "  make install-backend    - Install backend dependencies"
	@echo "  make install-frontend   - Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev-services       - Start development services (PostgreSQL, Redis, Ollama)"
	@echo "  make start-backend      - Start backend server"
	@echo "  make start-frontend     - Start frontend server"
	@echo "  make dev                - Start all services and servers"
	@echo ""
	@echo "Testing:"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests"
	@echo "  make test-frontend      - Run frontend tests"
	@echo ""
	@echo "Docker (Production):"
	@echo "  make docker-up          - Start all services with Docker Compose"
	@echo "  make docker-down        - Stop all Docker services"
	@echo "  make docker-build       - Build all Docker images"
	@echo "  make docker-logs        - View logs from all services"
	@echo "  make docker-ps          - Show running containers"
	@echo ""
	@echo "Docker (Development):"
	@echo "  make docker-dev-up      - Start development environment with Docker"
	@echo "  make docker-dev-down    - Stop development Docker services"
	@echo ""
	@echo "Ollama:"
	@echo "  make docker-pull-models - Pull Ollama models (codellama:7b)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              - Clean build artifacts and caches"
	@echo "  make docker-clean       - Remove all Docker volumes and images"

setup:
	@echo "Running setup script..."
	@./setup.sh

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install

dev-services:
	@echo "Starting development services..."
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "Services started. Waiting for initialization..."
	@sleep 5

start-backend:
	@echo "Starting backend server..."
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start-frontend:
	@echo "Starting frontend server..."
	@cd frontend && npm run dev

dev: dev-services
	@echo "Starting development environment..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"

test:
	@echo "Running all tests..."
	@make test-backend
	@make test-frontend

test-backend:
	@echo "Running backend tests..."
	@cd backend && source venv/bin/activate && pytest

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm run test

docker-up:
	@echo "Starting all services with Docker Compose (Production)..."
	@docker-compose up -d
	@echo ""
	@echo "Services started! Access points:"
	@echo "  - Frontend: http://localhost"
	@echo "  - Backend API: http://localhost/api/v1"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3001"
	@echo ""
	@echo "Run 'make docker-logs' to view logs"
	@echo "Run 'make docker-pull-models' to download Ollama models"

docker-down:
	@echo "Stopping all Docker services..."
	@docker-compose down

docker-dev-up:
	@echo "Starting development environment with Docker..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo ""
	@echo "Development services started! Access points:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Backend API: http://localhost:8000/api/v1"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Ollama: http://localhost:11434"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3001"
	@echo ""
	@echo "Run 'make docker-logs' to view logs"

docker-dev-down:
	@echo "Stopping development Docker services..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

docker-build:
	@echo "Building all Docker images..."
	@docker-compose build

docker-logs:
	@echo "Viewing logs from all services (Ctrl+C to exit)..."
	@docker-compose logs -f

docker-ps:
	@echo "Running containers:"
	@docker-compose ps

docker-pull-models:
	@echo "Pulling Ollama models..."
	@echo "This may take several minutes depending on your connection..."
	@docker-compose exec ollama ollama pull codellama:7b
	@echo ""
	@echo "Model pulled successfully!"
	@echo "You can also pull other models:"
	@echo "  docker-compose exec ollama ollama pull deepseek-coder:6.7b"
	@echo "  docker-compose exec ollama ollama pull llama2:13b"

docker-clean:
	@echo "WARNING: This will remove all Docker volumes and images!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@docker-compose down -v
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
	@docker volume rm github-rag-postgres-data github-rag-redis-data github-rag-ollama-models github-rag-repo-storage github-rag-faiss-indices github-rag-prometheus-data github-rag-grafana-data 2>/dev/null || true
	@echo "Docker cleanup complete!"

clean:
	@echo "Cleaning build artifacts and caches..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/htmlcov
	@rm -rf frontend/.next
	@echo "Cleanup complete!"
