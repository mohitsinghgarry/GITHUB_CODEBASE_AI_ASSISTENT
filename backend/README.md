# GitHub Codebase RAG Assistant - Backend

FastAPI backend for the GitHub Codebase RAG Assistant.

## Features

- Repository ingestion and indexing
- Semantic and keyword search
- RAG-based chat interface
- Code review and improvement suggestions
- Background job processing with Celery
- PostgreSQL for metadata storage
- Redis for caching and sessions
- FAISS for vector storage
- Ollama integration for local LLM inference

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env.development
# Edit .env.development with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

## Testing

Run tests with:
```bash
pytest
```

## Documentation

API documentation is available at `/docs` when the server is running.
