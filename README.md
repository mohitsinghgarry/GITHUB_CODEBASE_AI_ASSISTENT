# GitHub Codebase RAG Assistant

A production-grade Retrieval-Augmented Generation (RAG) system that enables developers to interact with GitHub repositories through natural language. The system combines semantic search, keyword search, and local LLM inference to provide contextual answers, code reviews, and improvement suggestions.

## Features

- 🔍 **Hybrid Search**: Combines BM25 keyword search and vector semantic search
- 💬 **RAG Chat Interface**: Natural language conversations with your codebase
- 🔄 **Multi-Repository Support**: Index and query multiple repositories
- 🤖 **Local LLM**: Privacy-first inference using Ollama
- 📊 **Code Review**: AI-powered code analysis and improvement suggestions
- 🚀 **Background Processing**: Async ingestion pipeline with progress tracking
- 📈 **Monitoring**: Prometheus metrics and Grafana dashboards

## Architecture

- **Backend**: FastAPI with async/await patterns
- **Frontend**: Next.js 14 with App Router, TypeScript, TailwindCSS
- **Database**: PostgreSQL for metadata
- **Cache**: Redis for sessions and caching
- **Vector Store**: FAISS for embeddings
- **LLM**: Ollama for local inference
- **Queue**: Celery for background jobs
- **Monitoring**: Prometheus + Grafana

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git

## Quick Start

### Option 1: Docker (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone <repository-url>
cd github-rag-assistant

# Run the quick start script
./docker-quickstart.sh

# Pull Ollama models
make docker-pull-models
```

Access the application:
- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Docs**: http://localhost/api/v1/docs

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

### Option 2: Local Development

For local development with hot-reloading:

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd github-rag-assistant
```

#### 2. Set Up Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env.development

# Frontend
cp frontend/.env.example frontend/.env.development
```

#### 3. Start Development Services

```bash
# Start PostgreSQL, Redis, and Ollama
make docker-dev-up
```

#### 4. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### 6. Pull Ollama Model

```bash
# Pull the default model
make docker-pull-models
```

## Project Structure

```
github-rag-assistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core business logic
│   │   ├── models/         # Data models
│   │   ├── jobs/           # Celery tasks
│   │   └── utils/          # Utilities
│   ├── tests/              # Test suite
│   └── alembic/            # Database migrations
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/            # App Router pages
│       ├── components/     # React components
│       ├── hooks/          # Custom hooks
│       ├── store/          # State management
│       └── lib/            # Utilities
├── nginx/                  # NGINX configuration
├── monitoring/             # Prometheus & Grafana
└── docker-compose.yml      # Full stack orchestration
```

## Development

### Backend Development

```bash
cd backend

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

### Frontend Development

```bash
cd frontend

# Run type checking
npm run type-check

# Format code
npm run format

# Linting
npm run lint
```

## Production Deployment

### Docker Compose (Recommended)

Full production deployment with all services:

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY to a secure value

# Start all services
make docker-up

# Pull Ollama models
make docker-pull-models

# View logs
make docker-logs

# Check service status
make docker-ps
```

See [DOCKER.md](DOCKER.md) for:
- Detailed deployment instructions
- SSL/TLS configuration
- Scaling and resource management
- Backup and restore procedures
- Troubleshooting guide

### Manual Deployment

For manual deployment without Docker:

1. Set up PostgreSQL, Redis, and Ollama on separate servers
2. Configure environment variables in `.env.production`
3. Deploy backend with Gunicorn/Uvicorn
4. Deploy frontend with Next.js standalone build
5. Configure NGINX as reverse proxy
6. Set up Prometheus and Grafana for monitoring

### Environment Configuration

Update the following files for production:
- `.env` (root level for Docker Compose)
- `backend/.env.production`
- `frontend/.env.production`

Key changes:
- Set secure `SECRET_KEY` (min 32 characters)
- Update database credentials
- Configure CORS origins
- Set production API URLs
- Enable HTTPS/SSL
- Configure rate limits
- Set up backup schedules

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.
