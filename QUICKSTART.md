# Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git

## Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

This will automatically:
1. Create Python virtual environment
2. Install all backend dependencies
3. Install all frontend dependencies
4. Start development services (PostgreSQL, Redis, Ollama)
5. Pull the Ollama model

## Option 2: Manual Setup

### 1. Start Development Services

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 2. Setup Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env.development
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.development
```

### 4. Pull Ollama Model

```bash
docker exec github-rag-ollama-dev ollama pull codellama:7b
```

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Using Make Commands

```bash
# View all available commands
make help

# Complete setup
make setup

# Start development services only
make dev-services

# Start backend
make start-backend

# Start frontend
make start-frontend

# Run tests
make test

# Clean build artifacts
make clean
```

## Verify Installation

### Check Backend

```bash
curl http://localhost:8000/api/v1/health
```

### Check Ollama

```bash
docker exec github-rag-ollama-dev ollama list
```

### Check Database

```bash
docker exec github-rag-postgres-dev psql -U postgres -d github_rag_dev -c "\dt"
```

### Check Redis

```bash
docker exec github-rag-redis-dev redis-cli ping
```

## Troubleshooting

### Services not starting

```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Backend issues

```bash
# Check if virtual environment is activated
which python  # Should point to backend/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Ollama model not found

```bash
# Pull the model manually
docker exec github-rag-ollama-dev ollama pull codellama:7b

# List available models
docker exec github-rag-ollama-dev ollama list
```

## Next Steps

1. Review the [README.md](README.md) for detailed documentation
2. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for implementation status
3. Start implementing the next tasks from `.kiro/specs/github-codebase-rag-assistant/tasks.md`

## Development Workflow

1. Make changes to backend code in `backend/app/`
2. Backend auto-reloads on file changes (FastAPI --reload)
3. Make changes to frontend code in `frontend/src/`
4. Frontend auto-reloads on file changes (Next.js dev mode)
5. Run tests before committing:
   ```bash
   make test
   ```

## Stopping Services

```bash
# Stop development services
docker-compose -f docker-compose.dev.yml down

# Stop all services (if using full docker-compose)
docker-compose down
```

## Clean Restart

```bash
# Stop services
docker-compose -f docker-compose.dev.yml down -v

# Clean build artifacts
make clean

# Start fresh
./setup.sh
```
