# Design Document: GitHub Codebase RAG Assistant

## Overview

The GitHub Codebase RAG Assistant is a production-grade Retrieval-Augmented Generation (RAG) system that enables developers to interact with GitHub repositories through natural language. The system combines semantic search, keyword search, and local LLM inference to provide contextual answers, code reviews, and improvement suggestions.

### Architecture Philosophy

The system follows a microservices-inspired architecture with clear separation of concerns:

1. **Backend Layer**: FastAPI async server handling API requests, orchestration, and business logic
2. **Data Layer**: PostgreSQL for metadata, Redis for caching/sessions, FAISS for vector storage
3. **Processing Layer**: Celery workers for background ingestion jobs
4. **AI Layer**: Ollama for LLM inference, sentence-transformers for embeddings
5. **Frontend Layer**: Next.js 14 with App Router for user interface
6. **Infrastructure Layer**: Docker Compose orchestration, NGINX reverse proxy, Prometheus/Grafana monitoring

### Key Design Decisions

1. **Local-First AI**: Using Ollama for LLM inference ensures privacy, eliminates API costs, and provides full control over model selection
2. **Hybrid Search**: Combining BM25 (keyword) and vector (semantic) search provides both precision and recall
3. **Per-Repository Indices**: Separate FAISS indices per repository enable efficient updates and deletion
4. **Multi-Stage Pipeline**: Breaking ingestion into clone → read → chunk → embed → store stages enables fault recovery and progress tracking
5. **Async Architecture**: FastAPI async patterns with Celery background workers ensure responsiveness under load
6. **Redis-Based Memory**: Using Redis for conversation sessions enables horizontal scaling and fast access

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js App<br/>Zustand + TailwindCSS]
    end
    
    subgraph "API Gateway"
        NGINX[NGINX Reverse Proxy]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server<br/>Async Endpoints]
        Celery[Celery Workers<br/>Background Jobs]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Metadata)]
        Redis[(Redis<br/>Cache + Sessions)]
        FAISS[(FAISS Indices<br/>Per Repository)]
    end
    
    subgraph "AI Layer"
        Ollama[Ollama<br/>LLM Inference]
        Embedder[sentence-transformers<br/>Embeddings]
    end
    
    subgraph "Monitoring"
        Prom[Prometheus]
        Graf[Grafana]
    end
    
    UI -->|HTTPS| NGINX
    NGINX -->|/api/*| API
    API -->|Metadata| PG
    API -->|Sessions/Cache| Redis
    API -->|Vector Search| FAISS
    API -->|Enqueue Jobs| Celery
    Celery -->|Update Status| PG
    Celery -->|Store Vectors| FAISS
    Celery -->|Generate Embeddings| Embedder
    API -->|LLM Queries| Ollama
    API -->|Metrics| Prom
    Prom -->|Visualize| Graf
```

### Component Interaction Flow

#### Repository Ingestion Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Celery
    participant GitHub
    participant Embedder
    participant FAISS
    participant PG
    
    User->>API: POST /repositories {url}
    API->>PG: Create repository record
    API->>Celery: Enqueue ingestion job
    API-->>User: 202 Accepted {job_id}
    
    Celery->>GitHub: Clone repository
    Celery->>PG: Update status: cloning
    Celery->>Celery: Read source files
    Celery->>PG: Update status: reading
    Celery->>Celery: Chunk code files
    Celery->>PG: Update status: chunking
    Celery->>Embedder: Generate embeddings
    Celery->>PG: Update status: embedding
    Celery->>FAISS: Store vectors + metadata
    Celery->>PG: Update status: completed
```

#### Chat Query Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Redis
    participant FAISS
    participant Ollama
    
    User->>API: POST /chat {message, session_id}
    API->>Redis: Get session history
    API->>FAISS: Hybrid search (BM25 + vector)
    FAISS-->>API: Top K code chunks
    API->>API: Construct RAG prompt
    API->>Ollama: Generate response
    Ollama-->>API: Stream response
    API->>Redis: Update session history
    API-->>User: Stream response + citations
```

## Components and Interfaces

### Project Structure Overview

```
github-rag-assistant/
├── backend/                             # FastAPI backend application
│   ├── app/                             # Main application code
│   │   ├── api/routes/                  # API endpoints
│   │   ├── core/                        # Core business logic
│   │   │   ├── ingestion/               # Repository ingestion pipeline
│   │   │   ├── embeddings/              # Embedding generation
│   │   │   ├── vectorstore/             # FAISS vector storage
│   │   │   ├── retrieval/               # Search and retrieval
│   │   │   ├── llm/                     # Ollama LLM integration
│   │   │   ├── rag/                     # RAG orchestration
│   │   │   ├── memory/                  # Conversation memory
│   │   │   └── postprocessing/          # Response formatting
│   │   ├── models/                      # Data models
│   │   │   ├── orm/                     # SQLAlchemy models
│   │   │   └── schemas/                 # Pydantic schemas
│   │   ├── jobs/                        # Celery background jobs
│   │   ├── middleware/                  # FastAPI middleware
│   │   └── utils/                       # Utility functions
│   ├── alembic/                         # Database migrations
│   ├── tests/                           # Test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/                            # Next.js frontend application
│   ├── src/
│   │   ├── app/                         # Next.js 14 App Router pages
│   │   ├── components/                  # React components
│   │   │   ├── ui/                      # shadcn/ui components
│   │   │   ├── layout/                  # Layout components
│   │   │   ├── repo/                    # Repository components
│   │   │   ├── chat/                    # Chat components
│   │   │   ├── code/                    # Code review components
│   │   │   ├── files/                   # File explorer components
│   │   │   ├── search/                  # Search components
│   │   │   └── common/                  # Shared components
│   │   ├── hooks/                       # Custom React hooks
│   │   ├── store/                       # Zustand state management
│   │   ├── lib/                         # Utilities and API client
│   │   └── types/                       # TypeScript types
│   ├── public/
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── nginx/                               # NGINX reverse proxy config
│   ├── nginx.conf
│   └── ssl/
├── monitoring/                          # Monitoring configuration
│   ├── prometheus.yml
│   └── grafana/
│       ├── datasources.yml
│       └── dashboards/
├── docker-compose.yml                   # Full stack orchestration
├── docker-compose.dev.yml               # Development environment
├── .github/workflows/                   # CI/CD pipelines
│   ├── ci.yml
│   └── deploy.yml
├── .env.example
└── README.md
```

### 1. FastAPI Backend (`backend/`)

#### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Settings via pydantic-settings
│   ├── database.py                      # SQLAlchemy async engine setup
│   ├── redis_client.py                  # Redis connection setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                      # Shared dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── repos.py                 # Repo load, status, stats, files
│   │       ├── chat.py                  # Chat endpoint
│   │       ├── search.py                # Search endpoint
│   │       ├── code.py                  # Review and improve endpoints
│   │       ├── sessions.py              # Session/message history
│   │       └── health.py                # Health check endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── cloner.py                # Git clone logic, safe subprocess
│   │   │   ├── file_reader.py           # File traversal, filtering, reading
│   │   │   ├── chunker.py               # AST-based + fallback chunking
│   │   │   └── pipeline.py              # Orchestrates full ingestion
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   ├── embedder.py              # sentence-transformers wrapper
│   │   │   └── batch_processor.py       # Batched embedding generation
│   │   ├── vectorstore/
│   │   │   ├── __init__.py
│   │   │   ├── faiss_store.py           # FAISS index management
│   │   │   └── index_manager.py         # Per-repo index lifecycle
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py             # Top-k similarity retrieval
│   │   │   ├── hybrid_search.py         # BM25 + vector hybrid ranking
│   │   │   └── reranker.py              # Result reranking
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── ollama_client.py         # Ollama HTTP client wrapper
│   │   │   ├── prompt_builder.py        # Prompt templates per task
│   │   │   └── response_parser.py       # Parse and clean LLM output
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py              # Full RAG orchestration
│   │   │   ├── query_rewriter.py        # Optional query rewriting
│   │   │   └── context_builder.py       # Build context window from chunks
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   └── conversation_store.py    # Redis-backed conversation memory
│   │   └── postprocessing/
│   │       ├── __init__.py
│   │       └── response_formatter.py    # Format final response
│   ├── models/
│   │   ├── __init__.py
│   │   ├── orm/
│   │   │   ├── __init__.py
│   │   │   ├── repository.py            # SQLAlchemy Repository model
│   │   │   ├── file_document.py         # SQLAlchemy FileDocument model
│   │   │   ├── chunk.py                 # SQLAlchemy Chunk model
│   │   │   ├── chat_message.py          # SQLAlchemy ChatMessage model
│   │   │   └── query_result.py          # SQLAlchemy QueryResult model
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── repository.py            # Pydantic schemas
│   │       ├── chat.py                  # Chat request/response schemas
│   │       ├── search.py                # Search schemas
│   │       ├── code.py                  # Code review/improve schemas
│   │       └── common.py                # Shared schemas, pagination
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── worker.py                    # Celery app definition
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── ingestion_task.py        # Background ingestion job
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── rate_limiter.py              # Redis-backed rate limiting
│   │   ├── request_logger.py            # Structured request logging
│   │   └── error_handler.py             # Global exception handlers
│   └── utils/
│       ├── __init__.py
│       ├── language_detector.py         # Detect programming language
│       ├── url_validator.py             # GitHub URL validation
│       ├── file_utils.py                # File type checks, path helpers
│       └── metrics.py                   # Prometheus metrics definitions
├── alembic/                             # DB migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_chunker.py
│   │   ├── test_embedder.py
│   │   ├── test_retriever.py
│   │   ├── test_prompt_builder.py
│   │   └── test_url_validator.py
│   ├── integration/
│   │   ├── test_ingestion_pipeline.py
│   │   ├── test_rag_pipeline.py
│   │   └── test_api_repos.py
│   └── api/
│       ├── test_chat_endpoint.py
│       ├── test_search_endpoint.py
│       └── test_code_endpoints.py
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .env.example
```

#### Core Modules

**`app/main.py`**: Application entry point
- FastAPI app initialization
- Middleware configuration (CORS, rate limiting, logging)
- Router registration from `api/routes/`
- Lifespan events (startup/shutdown)

**`app/config.py`**: Configuration management
- Pydantic Settings for environment variables
- Database, Redis, Ollama, embedding model configuration
- Validation and type checking

**`app/database.py`**: Database setup
- SQLAlchemy async engine configuration
- Session management and dependency injection

**`app/redis_client.py`**: Redis setup
- Redis connection pool management
- Helper methods for caching and session storage

**`app/api/routes/`**: API route handlers
- `repos.py`: Repository CRUD operations, load, status, stats, files
- `search.py`: Semantic, keyword, and hybrid search endpoints
- `chat.py`: RAG chat interface with streaming
- `code.py`: Code review and improvement endpoints
- `sessions.py`: Session and message history management
- `health.py`: Health checks and system status

**`app/core/ingestion/`**: Ingestion pipeline
- `cloner.py`: Git clone logic with safe subprocess handling
- `file_reader.py`: File traversal, filtering, and reading
- `chunker.py`: AST-based and fallback chunking strategies
- `pipeline.py`: Orchestrates the full 5-stage ingestion process

**`app/core/embeddings/`**: Embedding generation
- `embedder.py`: sentence-transformers wrapper
- `batch_processor.py`: Batched embedding generation for efficiency

**`app/core/vectorstore/`**: Vector storage
- `faiss_store.py`: FAISS index management and operations
- `index_manager.py`: Per-repository index lifecycle management

**`app/core/retrieval/`**: Search and retrieval
- `retriever.py`: Top-k similarity retrieval from FAISS
- `hybrid_search.py`: BM25 + vector hybrid ranking with RRF
- `reranker.py`: Result reranking logic

**`app/core/llm/`**: LLM integration
- `ollama_client.py`: Ollama HTTP client wrapper
- `prompt_builder.py`: Prompt templates for different tasks (chat, review, improve)
- `response_parser.py`: Parse and clean LLM output

**`app/core/rag/`**: RAG orchestration
- `pipeline.py`: Full RAG orchestration logic
- `query_rewriter.py`: Optional query rewriting for better retrieval
- `context_builder.py`: Build context window from retrieved chunks

**`app/core/memory/`**: Conversation memory
- `conversation_store.py`: Redis-backed conversation memory with TTL

**`app/core/postprocessing/`**: Response formatting
- `response_formatter.py`: Format final response with citations

**`app/jobs/`**: Background jobs
- `worker.py`: Celery app definition and configuration
- `tasks/ingestion_task.py`: Background ingestion job implementation

**`app/models/orm/`**: SQLAlchemy ORM models
- `repository.py`: Repository metadata
- `file_document.py`: File documents
- `chunk.py`: Code chunks
- `chat_message.py`: Chat messages
- `query_result.py`: Query results

**`app/models/schemas/`**: Pydantic schemas
- `repository.py`: Repository request/response schemas
- `chat.py`: Chat request/response schemas
- `search.py`: Search schemas
- `code.py`: Code review/improve schemas
- `common.py`: Shared schemas and pagination

**`app/middleware/`**: Middleware components
- `rate_limiter.py`: Redis-backed rate limiting
- `request_logger.py`: Structured request logging
- `error_handler.py`: Global exception handlers

**`app/utils/`**: Utility functions
- `language_detector.py`: Programming language detection
- `url_validator.py`: GitHub URL validation
- `file_utils.py`: File type checks and path helpers
- `metrics.py`: Prometheus metrics definitions

#### API Endpoints

```
POST   /api/v1/repositories              # Add repository
GET    /api/v1/repositories              # List repositories
GET    /api/v1/repositories/{id}         # Get repository details
DELETE /api/v1/repositories/{id}         # Delete repository
POST   /api/v1/repositories/{id}/reindex # Trigger re-indexing

GET    /api/v1/jobs/{job_id}             # Get job status
POST   /api/v1/jobs/{job_id}/retry       # Retry failed job

POST   /api/v1/search/semantic           # Semantic search
POST   /api/v1/search/keyword            # Keyword search
POST   /api/v1/search/hybrid             # Hybrid search

POST   /api/v1/chat                      # Send chat message (streaming)
GET    /api/v1/chat/sessions/{id}        # Get session history
DELETE /api/v1/chat/sessions/{id}        # Delete session

POST   /api/v1/review                    # Code review request
POST   /api/v1/improve                   # Code improvement request

GET    /api/v1/models                    # List available Ollama models
GET    /api/v1/health                    # Health check
GET    /api/v1/metrics                   # Prometheus metrics
```

### 2. Celery Workers (`backend/app/workers/`)

#### Ingestion Pipeline Tasks

**Task: `clone_repository`**
- Input: Repository URL, credentials
- Output: Local path, metadata (owner, name, branch, commit hash)
- Error handling: Invalid URL, authentication failure, network timeout

**Task: `read_source_files`**
- Input: Repository path
- Output: List of source file paths with language detection
- Filters: Exclude binary files, dependencies (`node_modules`, `venv`), build artifacts

**Task: `chunk_code_files`**
- Input: File paths, chunk size, overlap
- Output: Code chunks with metadata (file path, line numbers, language)
- Logic: Language-aware chunking respecting function/class boundaries

**Task: `generate_embeddings`**
- Input: Code chunks
- Output: Embedding vectors (384-dim for sentence-transformers)
- Batching: Process in batches of 32 for efficiency

**Task: `store_embeddings`**
- Input: Chunks + embeddings, repository ID
- Output: FAISS index persisted to disk
- Logic: Create/update repository-specific FAISS index

#### Task Orchestration

```python
# Celery chain for ingestion pipeline
chain(
    clone_repository.s(repo_url),
    read_source_files.s(),
    chunk_code_files.s(chunk_size=512, overlap=50),
    generate_embeddings.s(),
    store_embeddings.s(repo_id)
).apply_async()
```

### 3. Data Layer

#### PostgreSQL Schema

**Table: `repositories`**
```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    default_branch TEXT,
    last_commit_hash TEXT,
    status TEXT NOT NULL, -- pending, cloning, reading, chunking, embedding, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT,
    chunk_count INTEGER DEFAULT 0,
    index_path TEXT
);
```

**Table: `ingestion_jobs`**
```sql
CREATE TABLE ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    status TEXT NOT NULL, -- pending, running, completed, failed
    stage TEXT, -- clone, read, chunk, embed, store
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);
```

**Table: `code_chunks`**
```sql
CREATE TABLE code_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    language TEXT,
    content TEXT NOT NULL,
    embedding_id INTEGER, -- Reference to FAISS index position
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_chunks_repo ON code_chunks(repository_id);
CREATE INDEX idx_chunks_file ON code_chunks(file_path);
```

#### Redis Data Structures

**Chat Sessions**: `session:{session_id}`
```json
{
  "session_id": "uuid",
  "repository_ids": ["uuid1", "uuid2"],
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "citations": [...], "timestamp": "..."}
  ],
  "explanation_mode": "technical",
  "created_at": "...",
  "updated_at": "..."
}
```
TTL: 24 hours

**Search Cache**: `search:{query_hash}:{repo_id}`
```json
{
  "results": [...],
  "cached_at": "..."
}
```
TTL: 1 hour

**Job Status Cache**: `job:{job_id}`
```json
{
  "status": "running",
  "stage": "embedding",
  "progress": 65
}
```
TTL: 7 days

#### FAISS Index Structure

**Per-Repository Index**: `indices/{repo_id}.faiss`
- Index type: IndexFlatIP (inner product for cosine similarity)
- Dimension: 384 (sentence-transformers/all-MiniLM-L6-v2)
- Metadata file: `indices/{repo_id}.metadata.json`

**Metadata File Structure**:
```json
{
  "repository_id": "uuid",
  "chunk_count": 1523,
  "dimension": 384,
  "created_at": "...",
  "updated_at": "...",
  "chunks": [
    {
      "id": "uuid",
      "file_path": "src/main.py",
      "start_line": 10,
      "end_line": 25,
      "language": "python",
      "content": "..."
    }
  ]
}
```

### 4. AI Layer

#### Embedding Service

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Max sequence length: 256 tokens
- Inference: CPU or GPU (configurable)

**Interface**:
```python
class EmbeddingService:
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for batch of texts"""
        
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding optimized for query"""
```

#### LLM Service (Ollama)

**Default Model**: `codellama:7b` or `deepseek-coder:6.7b`

**Interface**:
```python
class LLMService:
    def generate(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """Generate response from Ollama"""
        
    def list_models(self) -> List[str]:
        """List available Ollama models"""
```

**System Prompts by Explanation Mode**:

- **Beginner**: "You are a helpful coding tutor. Explain concepts clearly with examples. Avoid jargon."
- **Technical**: "You are an expert software engineer. Provide detailed technical explanations with best practices."
- **Interview**: "You are a technical interviewer. Ask follow-up questions and explain trade-offs."

### 5. Search Service

#### Hybrid Search Implementation

**BM25 Component**:
- Library: `rank-bm25`
- Tokenization: Language-aware (use tree-sitter for code parsing)
- Parameters: k1=1.5, b=0.75

**Vector Component**:
- FAISS similarity search
- Metric: Cosine similarity (inner product on normalized vectors)
- Top-K: Configurable (default 20)

**Score Fusion**:
```python
def hybrid_search(query: str, repo_id: str, top_k: int = 10) -> List[Chunk]:
    # BM25 search
    bm25_results = bm25_search(query, repo_id, top_k=20)
    bm25_scores = normalize_scores(bm25_results)
    
    # Vector search
    query_embedding = embed_query(query)
    vector_results = faiss_search(query_embedding, repo_id, top_k=20)
    vector_scores = normalize_scores(vector_results)
    
    # Reciprocal Rank Fusion (RRF)
    combined_scores = {}
    for rank, chunk in enumerate(bm25_results):
        combined_scores[chunk.id] = 1 / (rank + 60)
    for rank, chunk in enumerate(vector_results):
        combined_scores[chunk.id] = combined_scores.get(chunk.id, 0) + 1 / (rank + 60)
    
    # Sort by combined score and return top K
    sorted_chunks = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return [get_chunk(chunk_id) for chunk_id, _ in sorted_chunks[:top_k]]
```

### 6. Frontend Application (`frontend/`)

#### Stitch Design Integration: RepoMind Assistant

**Design Project Details**:
- **Name**: RepoMind Assistant
- **Type**: Desktop application (Dark Mode)
- **Status**: Private
- **Created**: April 15, 2026
- **Last Updated**: April 15, 2026

**Integration Workflow**:
1. **Access Stitch Design**: Open the RepoMind Assistant project in Stitch
2. **Export Design Specs**: Use Stitch's export feature to get design tokens
3. **Extract Components**: Identify all screens and components in the design
4. **Map to React**: Create corresponding React components for each Stitch component
5. **Implement with TailwindCSS**: Use design tokens to configure Tailwind
6. **Add Animations**: Enhance with framer-motion based on design interactions

**Design Token Extraction**:
```typescript
// lib/design-tokens.ts
// TODO: Extract these values from RepoMind Assistant Stitch design

export const repoMindTokens = {
  colors: {
    // Extract from Stitch color palette
    background: {
      primary: '#0a0a0a',      // Main background (dark mode)
      secondary: '#1a1a1a',    // Card/panel background
      tertiary: '#2a2a2a',     // Elevated surfaces
    },
    text: {
      primary: '#ffffff',      // Primary text
      secondary: '#a0a0a0',    // Secondary text
      tertiary: '#707070',     // Muted text
    },
    accent: {
      primary: '#3b82f6',      // Primary accent color
      hover: '#2563eb',        // Hover state
      active: '#1d4ed8',       // Active state
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
  },
  spacing: {
    // Extract from Stitch spacing system
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
  },
  typography: {
    // Extract from Stitch typography
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['Fira Code', 'Consolas', 'monospace'],
    },
    fontSize: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '30px',
      '4xl': '36px',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  borderRadius: {
    // Extract from Stitch border radius
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    '2xl': '24px',
    full: '9999px',
  },
  shadows: {
    // Extract from Stitch shadow system
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  },
};
```

**Stitch Component Mapping**:

The following components should be extracted from the RepoMind Assistant Stitch design and mapped to React components:

| Stitch Screen/Component | React Component | File Path |
|------------------------|-----------------|-----------|
| Landing Page | `page.tsx` | `app/page.tsx` |
| Repository Load Screen | `RepoInputCard` | `components/repo/RepoInputCard.tsx` |
| Dashboard | `page.tsx` | `app/repos/[repoId]/page.tsx` |
| Sidebar Navigation | `Sidebar` | `components/layout/Sidebar.tsx` |
| Chat Interface | `ChatPanel` | `components/chat/ChatPanel.tsx` |
| Message Bubble (User) | `UserMessage` | `components/chat/UserMessage.tsx` |
| Message Bubble (Assistant) | `AssistantMessage` | `components/chat/AssistantMessage.tsx` |
| Code Snippet Card | `CodeSnippetCard` | `components/chat/CodeSnippetCard.tsx` |
| Search Bar | `SearchBar` | `components/search/SearchBar.tsx` |
| Search Result Card | `SearchResultCard` | `components/search/SearchResultCard.tsx` |
| File Tree | `FileTree` | `components/files/FileTree.tsx` |
| Code Viewer | `CodeViewer` | `components/code/CodeViewer.tsx` |
| Progress Indicator | `IndexingProgress` | `components/repo/IndexingProgress.tsx` |
| Status Badge | `StatusBadge` | `components/common/StatusBadge.tsx` |

**Implementation Steps**:

1. **Access Stitch Design**:
   ```bash
   # Open Stitch project
   # Navigate to RepoMind Assistant project
   # Review all screens and components
   ```

2. **Export Design Tokens**:
   - Use Stitch's export feature to download design specifications
   - Extract color palette, typography, spacing, and other tokens
   - Update `lib/design-tokens.ts` with actual values

3. **Screenshot Reference**:
   - Take screenshots of each screen for reference during implementation
   - Document component states (hover, active, disabled)
   - Note animation behaviors and transitions

4. **Component Implementation**:
   - Start with layout components (AppShell, Sidebar, Header)
   - Implement atomic components (buttons, inputs, badges)
   - Build composite components (cards, panels, forms)
   - Ensure pixel-perfect match with Stitch design

**Design System Tokens** (Placeholder - Update from Stitch):
```typescript
// lib/design-tokens.ts
export const designTokens = {
  colors: {
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
    },
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  },
  spacing: {
    xs: '0.25rem',    // 4px
    sm: '0.5rem',     // 8px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '3rem',    // 48px
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['Fira Code', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },
  borderRadius: {
    sm: '0.25rem',    // 4px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
    xl: '1rem',       // 16px
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  },
};
```

**Animation Presets**:
```typescript
// lib/animation-presets.ts
import { Variants } from 'framer-motion';

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

export const slideIn: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.2, ease: 'easeOut' } },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};
```

#### Component Specifications

**1. RepoInputCard Component**

*Stitch Design Mapping*: Card with input field, button, and validation feedback

```tsx
// components/repo/RepoInputCard.tsx
'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { fadeIn, slideUp } from '@/lib/animation-presets';

export function RepoInputCard() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="bg-white dark:bg-neutral-800 rounded-xl shadow-lg p-6 border border-neutral-200 dark:border-neutral-700"
    >
      <motion.h2
        variants={slideUp}
        className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2"
      >
        Load Repository
      </motion.h2>
      <motion.p
        variants={slideUp}
        className="text-sm text-neutral-600 dark:text-neutral-400 mb-6"
      >
        Enter a GitHub repository URL to start indexing
      </motion.p>
      
      <motion.div variants={slideUp} className="space-y-4">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          className="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 
                     bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-100
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     transition-all duration-200"
        />
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={isLoading}
          className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700 
                     text-white font-medium rounded-lg
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors duration-200"
        >
          {isLoading ? 'Loading...' : 'Load Repository'}
        </motion.button>
      </motion.div>
    </motion.div>
  );
}
```

**TailwindCSS Classes Used**:
- Layout: `p-6`, `space-y-4`, `w-full`
- Colors: `bg-white`, `dark:bg-neutral-800`, `text-neutral-900`
- Borders: `rounded-xl`, `border`, `border-neutral-200`
- Shadows: `shadow-lg`
- Focus states: `focus:ring-2`, `focus:ring-primary-500`
- Transitions: `transition-all`, `duration-200`

**2. IndexingProgress Component**

*Stitch Design Mapping*: Multi-step progress indicator with status badges

```tsx
// components/repo/IndexingProgress.tsx
'use client';

import { motion } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';
import { staggerContainer, slideIn } from '@/lib/animation-presets';

const steps = [
  { id: 'clone', label: 'Clone' },
  { id: 'read', label: 'Read' },
  { id: 'chunk', label: 'Chunk' },
  { id: 'embed', label: 'Embed' },
  { id: 'store', label: 'Store' },
];

export function IndexingProgress({ currentStep }: { currentStep: string }) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="bg-white dark:bg-neutral-800 rounded-lg p-6"
    >
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isComplete = steps.findIndex(s => s.id === currentStep) > index;
          const isCurrent = step.id === currentStep;
          
          return (
            <motion.div
              key={step.id}
              variants={slideIn}
              className="flex flex-col items-center"
            >
              <motion.div
                animate={{
                  scale: isCurrent ? [1, 1.1, 1] : 1,
                }}
                transition={{ repeat: isCurrent ? Infinity : 0, duration: 2 }}
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  ${isComplete ? 'bg-success text-white' : ''}
                  ${isCurrent ? 'bg-primary-600 text-white' : ''}
                  ${!isComplete && !isCurrent ? 'bg-neutral-200 dark:bg-neutral-700 text-neutral-500' : ''}
                `}
              >
                {isComplete ? (
                  <Check className="w-5 h-5" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </motion.div>
              
              <span className="mt-2 text-xs font-medium text-neutral-700 dark:text-neutral-300">
                {step.label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
```

**3. ChatPanel Component**

*Stitch Design Mapping*: Full-height panel with message list and input

```tsx
// components/chat/ChatPanel.tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ModeSelector } from './ModeSelector';

export function ChatPanel() {
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="flex flex-col h-full bg-neutral-50 dark:bg-neutral-900"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 dark:border-neutral-800">
        <h1 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
          Chat with Codebase
        </h1>
        <ModeSelector />
      </div>
      
      {/* Message List */}
      <div className="flex-1 overflow-y-auto">
        <MessageList />
      </div>
      
      {/* Input Area */}
      <div className="border-t border-neutral-200 dark:border-neutral-800 p-4">
        <ChatInput />
      </div>
    </motion.div>
  );
}
```

**4. UserMessage & AssistantMessage Components**

*Stitch Design Mapping*: Message bubbles with different alignments and colors

```tsx
// components/chat/UserMessage.tsx
'use client';

import { motion } from 'framer-motion';
import { slideIn } from '@/lib/animation-presets';

export function UserMessage({ content }: { content: string }) {
  return (
    <motion.div
      variants={slideIn}
      initial="hidden"
      animate="visible"
      className="flex justify-end mb-4 px-6"
    >
      <div className="max-w-[70%] bg-primary-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
        <p className="text-sm leading-relaxed">{content}</p>
      </div>
    </motion.div>
  );
}

// components/chat/AssistantMessage.tsx
'use client';

import { motion } from 'framer-motion';
import { slideIn } from '@/lib/animation-presets';
import { CodeSnippetCard } from './CodeSnippetCard';
import { SourceCitations } from './SourceCitations';

export function AssistantMessage({ 
  content, 
  codeSnippets, 
  sources 
}: { 
  content: string;
  codeSnippets?: Array<{ code: string; language: string }>;
  sources?: Array<{ file: string; lines: string }>;
}) {
  return (
    <motion.div
      variants={slideIn}
      initial="hidden"
      animate="visible"
      className="flex justify-start mb-4 px-6"
    >
      <div className="max-w-[70%] space-y-3">
        <div className="bg-white dark:bg-neutral-800 rounded-2xl rounded-tl-sm px-4 py-3 
                        border border-neutral-200 dark:border-neutral-700">
          <p className="text-sm leading-relaxed text-neutral-900 dark:text-neutral-100">
            {content}
          </p>
        </div>
        
        {codeSnippets && codeSnippets.map((snippet, i) => (
          <CodeSnippetCard key={i} {...snippet} />
        ))}
        
        {sources && <SourceCitations sources={sources} />}
      </div>
    </motion.div>
  );
}
```

**5. SearchResultCard Component**

*Stitch Design Mapping*: Card with file info, code preview, and relevance score

```tsx
// components/search/SearchResultCard.tsx
'use client';

import { motion } from 'framer-motion';
import { FileCode, ExternalLink } from 'lucide-react';
import { scaleIn } from '@/lib/animation-presets';

export function SearchResultCard({ 
  file, 
  lines, 
  code, 
  score, 
  language 
}: {
  file: string;
  lines: string;
  code: string;
  score: number;
  language: string;
}) {
  return (
    <motion.div
      variants={scaleIn}
      initial="hidden"
      animate="visible"
      whileHover={{ y: -2 }}
      className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700
                 hover:border-primary-500 dark:hover:border-primary-500
                 transition-all duration-200 cursor-pointer"
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-neutral-500" />
            <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
              {file}
            </span>
            <span className="text-xs text-neutral-500">
              Lines {lines}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-primary-600 dark:text-primary-400">
              {Math.round(score * 100)}% match
            </span>
            <ExternalLink className="w-4 h-4 text-neutral-400" />
          </div>
        </div>
        
        {/* Code Preview */}
        <div className="bg-neutral-50 dark:bg-neutral-900 rounded-md p-3 overflow-x-auto">
          <pre className="text-xs text-neutral-800 dark:text-neutral-200 font-mono">
            <code>{code}</code>
          </pre>
        </div>
        
        {/* Language Badge */}
        <div className="mt-3">
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium
                         bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
            {language}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
```

**6. StatusBadge Component**

*Stitch Design Mapping*: Pill-shaped badge with status colors

```tsx
// components/common/StatusBadge.tsx
'use client';

import { motion } from 'framer-motion';
import { scaleIn } from '@/lib/animation-presets';

const statusStyles = {
  pending: 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300',
  indexing: 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300',
  ready: 'bg-success/10 text-success',
  failed: 'bg-error/10 text-error',
};

export function StatusBadge({ status }: { status: keyof typeof statusStyles }) {
  return (
    <motion.span
      variants={scaleIn}
      initial="hidden"
      animate="visible"
      className={`
        inline-flex items-center px-3 py-1 rounded-full text-xs font-medium
        ${statusStyles[status]}
      `}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </motion.span>
  );
}
```

**7. LoadingSkeleton Component**

*Stitch Design Mapping*: Animated placeholder for loading states

```tsx
// components/common/LoadingSkeleton.tsx
'use client';

import { motion } from 'framer-motion';

export function LoadingSkeleton({ 
  className = '',
  variant = 'text' 
}: { 
  className?: string;
  variant?: 'text' | 'card' | 'circle';
}) {
  const baseClasses = 'bg-neutral-200 dark:bg-neutral-700 animate-pulse';
  
  const variantClasses = {
    text: 'h-4 rounded',
    card: 'h-32 rounded-lg',
    circle: 'rounded-full',
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    />
  );
}
```

#### Directory Structure

```
frontend/
├── src/
│   ├── app/                           # Next.js 14 App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing page
│   │   ├── globals.css
│   │   ├── load/
│   │   │   └── page.tsx               # Repository load page
│   │   └── repos/
│   │       └── [repoId]/
│   │           ├── layout.tsx         # Repo shell with sidebar
│   │           ├── page.tsx           # Dashboard
│   │           ├── chat/
│   │           │   └── page.tsx       # Chat page
│   │           ├── files/
│   │           │   ├── page.tsx       # File explorer
│   │           │   └── [fileId]/
│   │           │       └── page.tsx   # File detail/viewer
│   │           ├── search/
│   │           │   └── page.tsx       # Search page
│   │           ├── review/
│   │           │   └── page.tsx       # Code review page
│   │           ├── improve/
│   │           │   └── page.tsx       # Code improvement page
│   │           └── settings/
│   │               └── page.tsx       # Settings page
│   ├── components/
│   │   ├── ui/                        # shadcn/ui base components
│   │   ├── layout/
│   │   │   ├── AppShell.tsx           # Main app shell wrapper
│   │   │   ├── Sidebar.tsx            # Left navigation sidebar
│   │   │   ├── Header.tsx             # Top header bar
│   │   │   └── CommandPalette.tsx     # ⌘K command palette
│   │   ├── repo/
│   │   │   ├── RepoInputCard.tsx      # URL input card
│   │   │   ├── IndexingProgress.tsx   # Multi-step progress display
│   │   │   ├── RepoStats.tsx          # Stats cards
│   │   │   ├── RepoCard.tsx           # Recent repo card
│   │   │   ├── LanguageChart.tsx      # Language breakdown chart
│   │   │   └── QuickActions.tsx       # Dashboard quick actions
│   │   ├── chat/
│   │   │   ├── ChatPanel.tsx          # Main chat container
│   │   │   ├── MessageList.tsx        # Scrollable message list
│   │   │   ├── UserMessage.tsx        # User bubble
│   │   │   ├── AssistantMessage.tsx   # AI response bubble
│   │   │   ├── CodeSnippetCard.tsx    # Embedded code in answer
│   │   │   ├── SourceCitations.tsx    # File reference chips
│   │   │   ├── ChatInput.tsx          # Input area with controls
│   │   │   ├── SuggestedQuestions.tsx # Empty state suggestions
│   │   │   └── ModeSelector.tsx       # Beginner/Technical/Interview
│   │   ├── code/
│   │   │   ├── CodeViewer.tsx         # Syntax highlighted viewer
│   │   │   ├── DiffViewer.tsx         # Before/after diff display
│   │   │   ├── ReviewResultCard.tsx   # Single issue card
│   │   │   ├── ReviewSummaryBar.tsx   # Issue count summary
│   │   │   ├── CodeEditor.tsx         # Input code editor
│   │   │   └── ImprovementPanel.tsx   # Refactor results panel
│   │   ├── files/
│   │   │   ├── FileTree.tsx           # Tree structure component
│   │   │   ├── FileNode.tsx           # Individual tree node
│   │   │   ├── FileHeader.tsx         # File detail header
│   │   │   ├── FileSummaryCard.tsx    # AI summary panel
│   │   │   └── LanguageFilter.tsx     # File type filter
│   │   ├── search/
│   │   │   ├── SearchBar.tsx          # Main search input
│   │   │   ├── SearchModeToggle.tsx   # Semantic/Keyword/Hybrid
│   │   │   ├── SearchResultCard.tsx   # Individual result card
│   │   │   └── SearchFilters.tsx      # Language filters
│   │   └── common/
│   │       ├── LoadingSkeleton.tsx    # Skeleton components
│   │       ├── EmptyState.tsx         # Reusable empty state
│   │       ├── ErrorBanner.tsx        # Error display
│   │       ├── StatusBadge.tsx        # Status pill badges
│   │       ├── CopyButton.tsx         # Copy to clipboard
│   │       └── ToastProvider.tsx      # Toast notifications
│   ├── hooks/
│   │   ├── useRepo.ts                 # Repository data + mutations
│   │   ├── useChat.ts                 # Chat state + streaming
│   │   ├── useSearch.ts               # Search state
│   │   ├── useFileExplorer.ts         # File tree state
│   │   ├── useCodeReview.ts           # Review state
│   │   ├── useIndexingStatus.ts       # Polling indexing state
│   │   └── useCommandPalette.ts       # ⌘K state
│   ├── store/
│   │   ├── repoStore.ts               # Zustand: current repo state
│   │   ├── chatStore.ts               # Zustand: conversation state
│   │   ├── settingsStore.ts           # Zustand: user preferences
│   │   └── uiStore.ts                 # Zustand: UI state (panels)
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts              # Axios/fetch API client
│   │   │   ├── repos.ts               # Repo API functions
│   │   │   ├── chat.ts                # Chat API functions
│   │   │   ├── search.ts              # Search API functions
│   │   │   └── code.ts                # Code API functions
│   │   ├── utils/
│   │   │   ├── formatters.ts          # Date, size, etc formatters
│   │   │   ├── language-colors.ts     # Language → color mapping
│   │   │   └── syntax-highlight.ts    # Code highlighting helpers
│   │   └── constants.ts               # App-wide constants
│   └── types/
│       ├── repo.ts                    # TypeScript type definitions
│       ├── chat.ts
│       ├── search.ts
│       └── code.ts
├── public/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── Dockerfile
└── package.json
```

#### Key Features

**Repository Management**:
- `RepoInputCard`: URL input with validation
- `IndexingProgress`: Multi-step progress display (clone → read → chunk → embed → store)
- `RepoStats`: Dashboard with stats cards (files, chunks, languages)
- `LanguageChart`: Visual breakdown of programming languages
- Real-time progress updates via polling

**Chat Interface**:
- `ChatPanel`: Main container with message history
- `UserMessage` / `AssistantMessage`: Styled message bubbles
- `CodeSnippetCard`: Embedded code blocks with syntax highlighting
- `SourceCitations`: Clickable file reference chips
- `ModeSelector`: Toggle between Beginner/Technical/Interview modes
- `ChatInput`: Input area with send button and controls
- Streaming response display with real-time updates

**File Explorer**:
- `FileTree`: Hierarchical tree structure
- `FileNode`: Individual file/folder nodes with icons
- `FileSummaryCard`: AI-generated file summary
- `LanguageFilter`: Filter files by programming language

**Search Interface**:
- `SearchBar`: Main search input with autocomplete
- `SearchModeToggle`: Switch between Semantic/Keyword/Hybrid
- `SearchResultCard`: Result cards with file path, line numbers, relevance score
- `SearchFilters`: Filter by language, file type, directory
- Code preview with "View in context" link

**Code Review & Improvement**:
- `CodeEditor`: Input code editor for review/improvement
- `ReviewResultCard`: Individual issue cards with severity badges
- `ReviewSummaryBar`: Summary of issue counts by severity
- `DiffViewer`: Before/after comparison for improvements
- `ImprovementPanel`: Display refactored code with explanations

**Layout & Navigation**:
- `AppShell`: Main application wrapper
- `Sidebar`: Left navigation with repo selector and menu
- `Header`: Top bar with breadcrumbs and user menu
- `CommandPalette`: ⌘K quick actions and navigation

**Common Components**:
- `LoadingSkeleton`: Skeleton loaders for async content
- `EmptyState`: Reusable empty state illustrations
- `ErrorBanner`: Error display with retry actions
- `StatusBadge`: Status pills (pending, indexing, ready, failed)
- `ToastProvider`: Toast notifications for actions

**Theme Support**:
- Dark mode / Light mode toggle
- Persisted in localStorage via `settingsStore`
- TailwindCSS dark: variant throughout

#### TailwindCSS Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'Consolas', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};

export default config;
```

#### Additional Component Patterns

**8. CodeViewer with Syntax Highlighting**

```tsx
// components/code/CodeViewer.tsx
'use client';

import { motion } from 'framer-motion';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTheme } from 'next-themes';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { fadeIn } from '@/lib/animation-presets';

export function CodeViewer({ 
  code, 
  language, 
  fileName 
}: { 
  code: string;
  language: string;
  fileName?: string;
}) {
  const { theme } = useTheme();
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-700">
        <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          {fileName || 'Code'}
        </span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleCopy}
          className="p-1.5 rounded-md hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors"
        >
          {copied ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <Copy className="w-4 h-4 text-neutral-500" />
          )}
        </motion.button>
      </div>
      
      {/* Code */}
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={language}
          style={theme === 'dark' ? vscDarkPlus : vs}
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: 'transparent',
            fontSize: '0.875rem',
          }}
          showLineNumbers
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </motion.div>
  );
}
```

**9. EmptyState Component**

```tsx
// components/common/EmptyState.tsx
'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { fadeIn, slideUp } from '@/lib/animation-presets';

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center py-12 px-4"
    >
      <motion.div
        variants={slideUp}
        className="w-16 h-16 rounded-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mb-4"
      >
        <Icon className="w-8 h-8 text-neutral-400" />
      </motion.div>
      
      <motion.h3
        variants={slideUp}
        className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2"
      >
        {title}
      </motion.h3>
      
      <motion.p
        variants={slideUp}
        className="text-sm text-neutral-600 dark:text-neutral-400 text-center max-w-sm mb-6"
      >
        {description}
      </motion.p>
      
      {action && (
        <motion.button
          variants={slideUp}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={action.onClick}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {action.label}
        </motion.button>
      )}
    </motion.div>
  );
}
```

**10. CommandPalette Component**

```tsx
// components/layout/CommandPalette.tsx
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Search, FileCode, MessageSquare, Settings } from 'lucide-react';
import { useState, useEffect } from 'react';
import { scaleIn, staggerContainer, slideIn } from '@/lib/animation-presets';

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  const commands = [
    { icon: FileCode, label: 'Search code', action: () => {} },
    { icon: MessageSquare, label: 'New chat', action: () => {} },
    { icon: Settings, label: 'Settings', action: () => {} },
  ];
  
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />
          
          {/* Palette */}
          <motion.div
            variants={scaleIn}
            initial="hidden"
            animate="visible"
            exit="hidden"
            className="fixed top-1/4 left-1/2 -translate-x-1/2 w-full max-w-2xl z-50"
          >
            <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-2xl border border-neutral-200 dark:border-neutral-700 overflow-hidden">
              {/* Search Input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
                <Search className="w-5 h-5 text-neutral-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent text-neutral-900 dark:text-neutral-100 outline-none"
                  autoFocus
                />
                <kbd className="px-2 py-1 text-xs font-medium text-neutral-500 bg-neutral-100 dark:bg-neutral-700 rounded">
                  ESC
                </kbd>
              </div>
              
              {/* Commands */}
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="p-2 max-h-96 overflow-y-auto"
              >
                {commands.map((command, i) => (
                  <motion.button
                    key={i}
                    variants={slideIn}
                    whileHover={{ backgroundColor: 'rgba(0,0,0,0.05)' }}
                    onClick={() => {
                      command.action();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors"
                  >
                    <command.icon className="w-5 h-5 text-neutral-500" />
                    <span className="text-sm text-neutral-900 dark:text-neutral-100">
                      {command.label}
                    </span>
                  </motion.button>
                ))}
              </motion.div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

#### Responsive Design Patterns

**Breakpoint Usage**:
```tsx
// Mobile-first approach with Tailwind breakpoints
<div className="
  grid grid-cols-1           // Mobile: 1 column
  md:grid-cols-2             // Tablet: 2 columns
  lg:grid-cols-3             // Desktop: 3 columns
  gap-4                      // Consistent gap
  p-4 md:p-6 lg:p-8         // Responsive padding
">
  {/* Content */}
</div>
```

**Container Patterns**:
```tsx
// Max-width container with responsive padding
<div className="
  max-w-7xl mx-auto          // Centered with max width
  px-4 sm:px-6 lg:px-8       // Responsive horizontal padding
  py-8 sm:py-12 lg:py-16     // Responsive vertical padding
">
  {/* Content */}
</div>
```

### 7. Infrastructure

#### Docker Compose Services

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_assistant
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://rag_user:${DB_PASSWORD}@postgres:5432/rag_assistant
      REDIS_URL: redis://redis:6379
      OLLAMA_URL: http://ollama:11434
    volumes:
      - ./backend:/app
      - faiss_indices:/app/indices
      - repo_storage:/app/repositories
    depends_on:
      - postgres
      - redis
      - ollama
    ports:
      - "8000:8000"

  celery_worker:
    build: ./backend
    command: celery -A app.workers worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://rag_user:${DB_PASSWORD}@postgres:5432/rag_assistant
      REDIS_URL: redis://redis:6379
    volumes:
      - ./backend:/app
      - faiss_indices:/app/indices
      - repo_storage:/app/repositories
    depends_on:
      - postgres
      - redis
      - backend

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://nginx/api
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  faiss_indices:
  repo_storage:
  ollama_models:
  prometheus_data:
  grafana_data:
```

#### NGINX Configuration

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket support for streaming
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location / {
        proxy_pass http://frontend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Data Models

### Repository Model

```python
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum

class RepositoryStatus(str, Enum):
    PENDING = "pending"
    CLONING = "cloning"
    READING = "reading"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"

class Repository(BaseModel):
    id: str
    url: HttpUrl
    owner: str
    name: str
    default_branch: Optional[str]
    last_commit_hash: Optional[str]
    status: RepositoryStatus
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]
    chunk_count: int
    index_path: Optional[str]
```

### Code Chunk Model

```python
class CodeChunk(BaseModel):
    id: str
    repository_id: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    content: str
    embedding_id: Optional[int]
    created_at: datetime
```

### Chat Session Model

```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    citations: Optional[List[CodeChunk]]
    timestamp: datetime

class ExplanationMode(str, Enum):
    BEGINNER = "beginner"
    TECHNICAL = "technical"
    INTERVIEW = "interview"

class ChatSession(BaseModel):
    session_id: str
    repository_ids: List[str]
    messages: List[ChatMessage]
    explanation_mode: ExplanationMode
    created_at: datetime
    updated_at: datetime
```

### Search Models

```python
class SearchRequest(BaseModel):
    query: str
    repository_ids: Optional[List[str]]
    top_k: int = 10
    filters: Optional[Dict[str, Any]]

class SearchResult(BaseModel):
    chunk: CodeChunk
    score: float
    rank: int

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int
    query_time_ms: float
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following properties suitable for property-based testing. Many requirements involve infrastructure integration (Docker, PostgreSQL, Redis, FAISS, Ollama), UI rendering, or deterministic API behaviors that are better tested with integration or example-based tests. However, the core logic components—chunking, search fusion, filtering, metadata preservation, and configuration validation—contain universal properties that benefit from property-based testing.

**Redundancy Analysis:**
- Properties 1.7 and 2.3 both test file filtering logic → Combined into Property 1
- Properties 2.8 and 8.4 both test index isolation → Combined into Property 2
- Properties 2.9 and 2.10 both test incremental updates → Combined into Property 3
- Properties 4.5 and 8.3 both test repository filtering → Combined into Property 8
- Properties 5.5 covers hybrid search, which subsumes individual BM25/vector properties → Kept as comprehensive Property 11

### Property 1: File Filtering Preserves Source Code

*For any* file tree containing source code, binary files, dependencies, and build artifacts, the filtering operation SHALL exclude all binary files, dependency directories (node_modules, venv, target, etc.), and build artifacts while preserving all source code files.

**Validates: Requirements 1.7, 2.3**

### Property 2: Repository Index Isolation

*For any* set of repositories indexed in the system, each repository SHALL have a separate FAISS index file, and operations on one repository's index SHALL NOT affect any other repository's index.

**Validates: Requirements 2.8, 8.4**

### Property 3: Incremental Indexing Efficiency

*For any* repository with existing index and any set of file modifications, the re-indexing operation SHALL only process chunks from modified files, and the total number of chunks processed SHALL equal the number of chunks in modified files.

**Validates: Requirements 2.9, 2.10**

### Property 4: Chunking Preserves Content

*For any* source code file and any valid chunk size configuration, splitting the file into chunks and concatenating the chunk contents SHALL produce the original file content without loss or duplication.

**Validates: Requirements 2.4**

### Property 5: Chunking Metadata Preservation

*For any* source code file with file path, language, and line numbers, all chunks created from that file SHALL preserve the correct file path, language, and contiguous line number ranges that cover the entire file without gaps or overlaps.

**Validates: Requirements 2.5**

### Property 6: Language Detection Consistency

*For any* source code file with valid syntax for a supported language (Python, JavaScript, TypeScript, Java, Go, Rust, C++), the language detection SHALL return the correct language identifier.

**Validates: Requirements 2.11**

### Property 7: Index Persistence Round-Trip

*For any* FAISS index with repository metadata, persisting the index to disk and loading it back SHALL produce an index with identical metadata (repository ID, chunk count, dimension) and equivalent search results for any query.

**Validates: Requirements 2.13**

### Property 8: Repository Filtering Correctness

*For any* search query with repository filter specifying a subset of indexed repositories, all returned results SHALL only contain chunks from the specified repositories, and no chunks from excluded repositories SHALL appear in results.

**Validates: Requirements 4.5, 8.3**

### Property 9: Top-K Result Selection

*For any* search results with similarity scores and any valid K value (1 ≤ K ≤ 100), the top-K selection SHALL return exactly K results (or fewer if total results < K), and all returned results SHALL have scores greater than or equal to any non-returned results.

**Validates: Requirements 4.3, 4.4**

### Property 10: Result Structure Completeness

*For any* search result returned by the Query Engine, the result SHALL contain all required fields: chunk ID, file path, start line, end line, language, content, and similarity score, with no null or missing values.

**Validates: Requirements 4.6**

### Property 11: Hybrid Search Score Fusion

*For any* query with both BM25 and vector search results, the hybrid search fusion SHALL combine results using Reciprocal Rank Fusion (RRF), and the final ranking SHALL reflect contributions from both search methods such that a chunk appearing in both result sets ranks higher than chunks appearing in only one.

**Validates: Requirements 5.5**

### Property 12: Boolean Query Evaluation

*For any* set of code chunks and any boolean query using AND, OR, NOT operators, the result set SHALL correctly match the boolean logic: AND requires all terms present, OR requires at least one term present, and NOT excludes chunks containing the negated term.

**Validates: Requirements 5.4**

### Property 13: Multi-Criteria Filtering

*For any* search results and any combination of filters (file extension, directory path, programming language), the filtered results SHALL only include chunks that satisfy ALL filter criteria simultaneously.

**Validates: Requirements 5.6**

### Property 14: Match Location Accuracy

*For any* keyword search match in a code chunk, the highlighted match location (start position, end position) SHALL correspond to the actual occurrence of the search term in the chunk content.

**Validates: Requirements 5.3**

### Property 15: RAG Prompt Construction Completeness

*For any* user question and any set of retrieved code chunks, the constructed RAG prompt SHALL include the system instruction, all chunk contents with file paths, and the user question, with no chunks omitted.

**Validates: Requirements 6.3**

### Property 16: Citation Linking Correctness

*For any* LLM response and any set of source code chunks used as context, the citations attached to the response SHALL reference exactly the chunks that were included in the prompt, with correct chunk IDs and file paths.

**Validates: Requirements 6.5**

### Property 17: Session History Preservation

*For any* sequence of chat messages added to a session, retrieving the session history SHALL return all messages in chronological order with correct roles (user/assistant), content, and timestamps.

**Validates: Requirements 6.6**

### Property 18: Token Limit Truncation

*For any* chat session exceeding the configured token limit, the truncation operation SHALL preserve the most recent messages up to the token limit, and the truncated history SHALL remain under the limit.

**Validates: Requirements 6.7**

### Property 19: Review Feedback Structure

*For any* code review analysis output, the structured feedback SHALL contain all required fields for each issue: description, severity level, line number, and issue category, with no missing fields.

**Validates: Requirements 7.3**

### Property 20: Diff Parsing Completeness

*For any* valid git diff, the parsing operation SHALL extract all changed lines with correct line numbers, change types (addition/deletion/modification), and surrounding context lines.

**Validates: Requirements 7.5**

### Property 21: Diff Context Extraction

*For any* git diff with changed lines, the context extraction SHALL include all changed lines plus N surrounding lines (configurable), and the context SHALL form a contiguous code block.

**Validates: Requirements 7.6**

### Property 22: Repository Metadata Completeness

*For any* repository list response, each repository entry SHALL contain all required metadata fields: ID, name, owner, URL, status, last updated time, chunk count, with no null or missing values.

**Validates: Requirements 8.2**

### Property 23: Cascade Deletion Completeness

*For any* repository deletion operation, all associated data SHALL be removed: all code chunks, all embeddings from the FAISS index, all ingestion jobs, and the repository metadata record itself.

**Validates: Requirements 8.5**

### Property 24: Repository Namespace Uniqueness

*For any* two repositories with identical names but different owners, the system SHALL assign unique identifiers and maintain separate indices, and queries SHALL correctly distinguish between the two repositories.

**Validates: Requirements 8.6**

### Property 25: System Prompt Inclusion

*For any* prompt sent to Ollama, the prompt SHALL include the configured system instruction for code-focused responses, and the system instruction SHALL appear before the user content.

**Validates: Requirements 9.4**

### Property 26: Exponential Backoff Retry Pattern

*For any* sequence of retry attempts after timeouts, the delay between attempts SHALL follow exponential backoff: delay(n) = base_delay × 2^n, where n is the attempt number.

**Validates: Requirements 9.5**

### Property 27: Configuration Validation

*For any* configuration with required fields (embedding model, chunk size, Ollama endpoint), the validation SHALL reject configurations with missing required fields, out-of-range values, or invalid types, and SHALL accept all valid configurations.

**Validates: Requirements 13.1, 13.2, 13.3, 13.6, 13.8**



## Error Handling

### Error Categories

The system implements comprehensive error handling across four categories:

#### 1. External Service Errors

**GitHub API Errors**:
- **Invalid URL**: Return 400 Bad Request with message "Invalid GitHub repository URL format"
- **Repository Not Found**: Return 404 Not Found with message "Repository not accessible or does not exist"
- **Authentication Failed**: Return 401 Unauthorized with message "GitHub authentication failed. Check credentials."
- **Rate Limit Exceeded**: Return 429 Too Many Requests with retry-after header
- **Network Timeout**: Retry with exponential backoff (3 attempts), then return 503 Service Unavailable

**Ollama Errors**:
- **Connection Refused**: Return 503 Service Unavailable with message "LLM service unavailable. Please try again later."
- **Model Not Found**: Return 400 Bad Request with message "Requested model not available. Use /api/v1/models to list available models."
- **Inference Timeout**: Retry once with increased timeout, then return 504 Gateway Timeout
- **Out of Memory**: Return 507 Insufficient Storage with message "LLM service out of memory. Try a smaller model or reduce context size."

**Database Errors**:
- **Connection Failed**: Implement connection pool with retry logic (5 attempts, exponential backoff)
- **Query Timeout**: Log slow query, return 504 Gateway Timeout
- **Constraint Violation**: Return 409 Conflict with specific constraint message
- **Deadlock**: Automatic retry (3 attempts), then return 500 Internal Server Error

**Redis Errors**:
- **Connection Failed**: Degrade gracefully (disable caching, continue with direct DB queries)
- **Memory Full**: Evict oldest entries using LRU policy, log warning
- **Timeout**: Skip cache, serve from database, log warning

#### 2. Data Validation Errors

**Repository Input Validation**:
```python
class RepositoryValidationError(Exception):
    """Raised when repository input is invalid"""
    
def validate_repository_url(url: str) -> None:
    if not url.startswith(("https://github.com/", "git@github.com:")):
        raise RepositoryValidationError("URL must be a GitHub repository")
    
    if not re.match(r"^https://github\.com/[\w-]+/[\w.-]+$", url):
        raise RepositoryValidationError("Invalid GitHub URL format")
```

**Search Input Validation**:
```python
def validate_search_request(request: SearchRequest) -> None:
    if not request.query or len(request.query.strip()) == 0:
        raise ValidationError("Query cannot be empty")
    
    if request.top_k < 1 or request.top_k > 100:
        raise ValidationError("top_k must be between 1 and 100")
    
    if request.repository_ids:
        for repo_id in request.repository_ids:
            if not is_valid_uuid(repo_id):
                raise ValidationError(f"Invalid repository ID: {repo_id}")
```

**Configuration Validation**:
```python
class Settings(BaseSettings):
    # Embedding configuration
    embedding_model: str = Field(..., regex=r"^[\w/-]+$")
    embedding_dimension: int = Field(..., ge=128, le=1536)
    
    # Chunking configuration
    chunk_size: int = Field(512, ge=100, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)
    
    # Ollama configuration
    ollama_url: HttpUrl
    ollama_model: str = Field(..., min_length=1)
    ollama_timeout: int = Field(60, ge=10, le=300)
    
    @validator("chunk_overlap")
    def validate_overlap(cls, v, values):
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v
```

#### 3. Business Logic Errors

**Ingestion Pipeline Errors**:
- **Stage Failure**: Mark stage as failed, store error details, halt pipeline
- **Partial Success**: Store successfully processed chunks, mark failed files
- **Disk Space Exhausted**: Stop ingestion, return 507 Insufficient Storage
- **Invalid File Encoding**: Skip file, log warning, continue with remaining files

**Search Errors**:
- **Empty Index**: Return empty results with message "No repositories indexed yet"
- **Index Corruption**: Attempt rebuild, if fails return 500 Internal Server Error
- **Query Too Complex**: Return 400 Bad Request with message "Query too complex. Simplify boolean operators."

**Session Errors**:
- **Session Expired**: Return 404 Not Found with message "Session expired or not found"
- **Session Limit Exceeded**: Return 429 Too Many Requests with message "Maximum concurrent sessions reached"

#### 4. System Resource Errors

**Memory Management**:
- **Embedding Generation OOM**: Process in smaller batches, if still fails return 507
- **FAISS Index Load OOM**: Use memory-mapped files, if fails return 507
- **Request Payload Too Large**: Return 413 Payload Too Large (limit: 10MB)

**Disk Space Management**:
- **Low Disk Space Warning**: Log warning at 80% capacity
- **Critical Disk Space**: Reject new ingestion jobs at 90% capacity
- **Disk Full**: Return 507 Insufficient Storage, trigger cleanup of old indices

**Concurrency Limits**:
- **Max Workers Reached**: Queue job, return 202 Accepted with estimated wait time
- **Rate Limit Exceeded**: Return 429 Too Many Requests with retry-after header
- **Circuit Breaker Open**: Return 503 Service Unavailable with message "Service temporarily unavailable due to high error rate"

### Error Response Format

All API errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "Repository not accessible or does not exist",
    "details": {
      "url": "https://github.com/user/repo",
      "timestamp": "2024-01-15T10:30:00Z",
      "request_id": "req_abc123"
    },
    "retry_after": 60  // Optional, for rate limits
  }
}
```

### Retry Strategies

**Exponential Backoff**:
```python
def exponential_backoff_retry(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Any:
    for attempt in range(max_attempts):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            time.sleep(delay)
```

**Circuit Breaker**:
```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable) -> Any:
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = func()
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### Graceful Degradation

The system implements graceful degradation for non-critical failures:

1. **Redis Unavailable**: Disable caching, serve from PostgreSQL
2. **Ollama Unavailable**: Disable chat, keep search functional
3. **Monitoring Unavailable**: Continue operation, log locally
4. **Single Repository Index Corrupt**: Isolate failure, keep other repositories functional

### Logging Strategy

**Log Levels**:
- **DEBUG**: Detailed execution flow, variable values
- **INFO**: Request/response, job status changes, successful operations
- **WARNING**: Degraded functionality, retry attempts, slow queries
- **ERROR**: Failed operations, exceptions with stack traces
- **CRITICAL**: System-wide failures, data corruption, security breaches

**Structured Logging Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "ERROR",
  "service": "backend",
  "component": "ingestion_service",
  "message": "Failed to clone repository",
  "context": {
    "repository_url": "https://github.com/user/repo",
    "job_id": "job_abc123",
    "error_type": "AuthenticationError",
    "stack_trace": "..."
  },
  "request_id": "req_xyz789"
}
```

## Testing Strategy

### Testing Approach Overview

The GitHub Codebase RAG Assistant requires a comprehensive testing strategy that combines multiple testing methodologies:

1. **Property-Based Tests**: For core logic with universal properties (chunking, search fusion, filtering)
2. **Unit Tests**: For specific examples, edge cases, and business logic
3. **Integration Tests**: For external service interactions (GitHub, Ollama, PostgreSQL, Redis, FAISS)
4. **End-to-End Tests**: For complete user workflows
5. **Performance Tests**: For scalability and resource usage
6. **Security Tests**: For authentication, authorization, and input validation

### 1. Property-Based Testing

**Framework**: `hypothesis` (Python)

**Configuration**:
- Minimum 100 iterations per property test
- Deadline: 60 seconds per test
- Seed: Fixed for reproducibility in CI/CD

**Test Organization**:
```
tests/
├── properties/
│   ├── test_chunking_properties.py
│   ├── test_search_properties.py
│   ├── test_filtering_properties.py
│   ├── test_session_properties.py
│   └── test_config_properties.py
```

**Example Property Test**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: github-codebase-rag-assistant, Property 4: Chunking Preserves Content
@given(
    content=st.text(min_size=100, max_size=10000),
    chunk_size=st.integers(min_value=100, max_value=2000),
    overlap=st.integers(min_value=0, max_value=500)
)
def test_chunking_preserves_content(content, chunk_size, overlap):
    """
    For any source code content and valid chunk configuration,
    chunking and concatenating should preserve the original content.
    
    Feature: github-codebase-rag-assistant
    Property 4: Chunking Preserves Content
    """
    assume(overlap < chunk_size)  # Ensure valid configuration
    
    chunks = chunk_text(content, chunk_size, overlap)
    reconstructed = "".join(chunk.content for chunk in chunks)
    
    assert reconstructed == content, "Chunking must preserve all content"
```

**Property Test Coverage**:
- **Chunking Logic** (Properties 4, 5): Content preservation, metadata accuracy
- **Search Fusion** (Property 11): RRF algorithm correctness
- **Filtering** (Properties 1, 8, 13): Multi-criteria filtering accuracy
- **Session Management** (Properties 17, 18): History preservation, truncation
- **Configuration** (Property 27): Validation rules

### 2. Unit Testing

**Framework**: `pytest`

**Coverage Target**: 80% code coverage for business logic

**Test Organization**:
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_repository_service.py
│   │   ├── test_ingestion_service.py
│   │   ├── test_search_service.py
│   │   └── test_chat_service.py
│   ├── models/
│   │   ├── test_repository_model.py
│   │   └── test_chunk_model.py
│   └── utils/
│       ├── test_embeddings.py
│       └── test_vector_store.py
```

**Example Unit Tests**:
```python
def test_repository_url_validation_invalid_format():
    """Test that invalid URL formats are rejected"""
    with pytest.raises(RepositoryValidationError, match="Invalid GitHub URL format"):
        validate_repository_url("https://gitlab.com/user/repo")

def test_search_empty_query():
    """Test that empty queries return appropriate error"""
    with pytest.raises(ValidationError, match="Query cannot be empty"):
        validate_search_request(SearchRequest(query="", top_k=10))

def test_job_status_transition_completed():
    """Test job status transitions to completed on success"""
    job = IngestionJob(status=JobStatus.RUNNING)
    job.mark_completed()
    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None
```

### 3. Integration Testing

**Framework**: `pytest` with `pytest-docker` and `testcontainers`

**Test Environment**: Docker containers for PostgreSQL, Redis, Ollama

**Test Organization**:
```
tests/
├── integration/
│   ├── test_github_integration.py
│   ├── test_ollama_integration.py
│   ├── test_database_integration.py
│   ├── test_redis_integration.py
│   └── test_faiss_integration.py
```

**Example Integration Test**:
```python
@pytest.mark.integration
def test_repository_ingestion_pipeline(test_db, test_redis, test_ollama):
    """
    Test complete ingestion pipeline with real services.
    Validates: Requirements 2.1-2.7, 3.1-3.3
    """
    # Setup
    repo_url = "https://github.com/octocat/Hello-World"
    
    # Execute
    response = client.post("/api/v1/repositories", json={"url": repo_url})
    assert response.status_code == 202
    job_id = response.json()["job_id"]
    
    # Wait for completion (with timeout)
    job = wait_for_job_completion(job_id, timeout=300)
    
    # Verify
    assert job.status == "completed"
    assert job.error_message is None
    
    # Verify index created
    repo = get_repository_by_url(repo_url)
    assert repo.status == "completed"
    assert repo.chunk_count > 0
    assert os.path.exists(repo.index_path)
    
    # Verify search works
    results = client.post("/api/v1/search/semantic", json={
        "query": "hello world function",
        "repository_ids": [repo.id],
        "top_k": 5
    })
    assert results.status_code == 200
    assert len(results.json()["results"]) > 0
```

**Integration Test Coverage**:
- **GitHub API**: Clone public/private repos, handle auth failures
- **Ollama**: Model inference, streaming, error handling
- **PostgreSQL**: CRUD operations, transactions, migrations
- **Redis**: Session management, caching, expiration
- **FAISS**: Index creation, search, persistence

### 4. End-to-End Testing

**Framework**: `playwright` (for frontend) + API tests

**Test Scenarios**:
1. **Complete User Journey**: Add repository → Wait for indexing → Search code → Chat with codebase
2. **Multi-Repository Workflow**: Add multiple repos → Search across all → Filter by repo
3. **Code Review Workflow**: Index repo → Request review → Receive feedback
4. **Error Recovery**: Trigger failure → Verify error message → Retry successfully

**Example E2E Test**:
```python
@pytest.mark.e2e
async def test_complete_user_journey(page, api_client):
    """Test complete user workflow from repository addition to chat"""
    # Add repository
    await page.goto("http://localhost:3000/repositories")
    await page.fill('input[name="url"]', "https://github.com/octocat/Hello-World")
    await page.click('button:has-text("Add Repository")')
    
    # Wait for indexing to complete
    await page.wait_for_selector('text=Status: Completed', timeout=300000)
    
    # Navigate to chat
    await page.goto("http://localhost:3000/chat")
    
    # Send message
    await page.fill('textarea[name="message"]', "What does the main function do?")
    await page.click('button:has-text("Send")')
    
    # Verify response
    await page.wait_for_selector('.assistant-message')
    response = await page.text_content('.assistant-message')
    assert len(response) > 0
    
    # Verify citations
    citations = await page.query_selector_all('.citation')
    assert len(citations) > 0
```

### 5. Performance Testing

**Framework**: `locust` for load testing

**Performance Targets**:
- **API Response Time**: p95 < 500ms for search, p95 < 2s for chat
- **Throughput**: 100 concurrent users, 1000 requests/minute
- **Ingestion Speed**: 1000 files/minute on standard hardware
- **Memory Usage**: < 2GB for backend, < 500MB for worker
- **Index Size**: < 1MB per 1000 chunks

**Load Test Scenarios**:
```python
from locust import HttpUser, task, between

class RAGAssistantUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def search_code(self):
        self.client.post("/api/v1/search/hybrid", json={
            "query": "authentication function",
            "top_k": 10
        })
    
    @task(1)
    def chat_message(self):
        self.client.post("/api/v1/chat", json={
            "message": "Explain the authentication flow",
            "session_id": self.session_id
        })
    
    def on_start(self):
        # Create session
        response = self.client.post("/api/v1/chat/sessions")
        self.session_id = response.json()["session_id"]
```

### 6. Security Testing

**Static Analysis**: `bandit` for Python security issues

**Dependency Scanning**: `safety` for known vulnerabilities

**Security Test Cases**:
- **SQL Injection**: Test with malicious input in search queries
- **XSS**: Test with script tags in repository names
- **Authentication Bypass**: Test protected endpoints without tokens
- **Rate Limiting**: Test exceeding rate limits
- **Input Validation**: Test with oversized payloads, invalid types

**Example Security Test**:
```python
@pytest.mark.security
def test_sql_injection_prevention():
    """Test that SQL injection attempts are prevented"""
    malicious_query = "'; DROP TABLE repositories; --"
    
    response = client.post("/api/v1/search/keyword", json={
        "query": malicious_query,
        "top_k": 10
    })
    
    # Should not cause error, should treat as literal string
    assert response.status_code == 200
    
    # Verify tables still exist
    repos = client.get("/api/v1/repositories")
    assert repos.status_code == 200
```

### 7. Test Data Management

**Fixtures**:
```python
@pytest.fixture
def sample_repository():
    """Create a sample repository for testing"""
    return Repository(
        id=str(uuid.uuid4()),
        url="https://github.com/test/repo",
        owner="test",
        name="repo",
        status=RepositoryStatus.COMPLETED,
        chunk_count=100
    )

@pytest.fixture
def sample_chunks():
    """Create sample code chunks for testing"""
    return [
        CodeChunk(
            id=str(uuid.uuid4()),
            repository_id="repo_123",
            file_path="src/main.py",
            start_line=1,
            end_line=10,
            language="python",
            content="def main():\n    print('Hello')"
        )
        for _ in range(10)
    ]
```

**Test Database**:
- Use separate test database with automatic cleanup
- Use transactions with rollback for test isolation
- Seed with minimal required data

### 8. CI/CD Integration

**GitHub Actions Workflow**:
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      redis:
        image: redis:7-alpine
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run property tests
        run: pytest tests/properties/ -v --hypothesis-seed=42
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=app --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration/ -v -m integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 9. Test Maintenance

**Test Review Process**:
- Review test coverage in every PR
- Update tests when requirements change
- Remove obsolete tests
- Refactor duplicated test code

**Test Documentation**:
- Each test includes docstring explaining what it validates
- Property tests reference design document properties
- Integration tests reference requirement numbers
- Complex test setups include inline comments

### Testing Summary

| Test Type | Framework | Coverage | Execution Time | Frequency |
|-----------|-----------|----------|----------------|-----------|
| Property-Based | hypothesis | 27 properties | ~5 min | Every commit |
| Unit | pytest | 80% code coverage | ~2 min | Every commit |
| Integration | pytest + testcontainers | Key integrations | ~10 min | Every commit |
| E2E | playwright | Critical paths | ~15 min | Pre-merge |
| Performance | locust | Load scenarios | ~30 min | Nightly |
| Security | bandit + safety | Security issues | ~5 min | Every commit |

**Total Test Execution Time**: ~30 minutes for full suite

## Deployment and Operations

### Deployment Architecture

**Production Environment**:
- **Container Orchestration**: Docker Compose (single-node) or Kubernetes (multi-node)
- **Load Balancer**: NGINX with SSL termination
- **Database**: PostgreSQL 15 with replication
- **Cache**: Redis Cluster for high availability
- **Storage**: Persistent volumes for FAISS indices and repositories
- **Monitoring**: Prometheus + Grafana + AlertManager

### Environment Configuration

**Development**:
```bash
# .env.development
DATABASE_URL=postgresql://rag_user:dev_password@localhost:5432/rag_dev
REDIS_URL=redis://localhost:6379
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
LOG_LEVEL=DEBUG
```

**Production**:
```bash
# .env.production
DATABASE_URL=postgresql://rag_user:${DB_PASSWORD}@postgres:5432/rag_prod
REDIS_URL=redis://redis-cluster:6379
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-coder:6.7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENABLE_TRACING=true
```

### Monitoring and Alerting

**Key Metrics**:
- Request rate, error rate, latency (RED metrics)
- Ingestion job queue length and processing time
- FAISS index size and query latency
- Ollama inference time and token usage
- Database connection pool utilization
- Redis memory usage and hit rate

**Alerts**:
- Error rate > 5% for 5 minutes
- API latency p95 > 2s for 5 minutes
- Disk usage > 90%
- Ollama unavailable for 2 minutes
- Database connection pool exhausted

### Backup and Recovery

**Backup Strategy**:
- **PostgreSQL**: Daily full backup + continuous WAL archiving
- **FAISS Indices**: Daily backup to object storage (S3/MinIO)
- **Configuration**: Version controlled in Git
- **Retention**: 30 days for daily backups, 1 year for monthly

**Recovery Procedures**:
1. **Database Restore**: Restore from latest backup + replay WAL
2. **Index Restore**: Download from object storage, verify integrity
3. **Disaster Recovery**: Full system restore from backups (RTO: 4 hours, RPO: 24 hours)

### Scaling Considerations

**Horizontal Scaling**:
- **Backend API**: Stateless, scale with load balancer
- **Celery Workers**: Scale based on queue length
- **Redis**: Use Redis Cluster for sharding
- **PostgreSQL**: Read replicas for query scaling

**Vertical Scaling**:
- **Ollama**: GPU acceleration for faster inference
- **FAISS**: Memory-mapped indices for large datasets
- **Embedding Generation**: Batch processing with GPU

### Security Hardening

**Network Security**:
- All services in private network
- Only NGINX exposed to public internet
- TLS 1.3 for all external connections
- mTLS for internal service communication

**Application Security**:
- JWT-based authentication with short expiration
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- CSRF protection for state-changing operations

**Data Security**:
- Encryption at rest for sensitive data
- Encryption in transit (TLS)
- Secrets management (HashiCorp Vault or AWS Secrets Manager)
- Regular security audits and penetration testing

## Conclusion

The GitHub Codebase RAG Assistant design provides a comprehensive, production-ready architecture for semantic code search and AI-powered code assistance. The system leverages modern technologies (FastAPI, Next.js, Ollama, FAISS) with a focus on:

1. **Scalability**: Async architecture, background processing, horizontal scaling
2. **Reliability**: Comprehensive error handling, retry logic, graceful degradation
3. **Testability**: Property-based testing for core logic, extensive integration tests
4. **Observability**: Structured logging, metrics, distributed tracing
5. **Security**: Authentication, input validation, encryption, security testing

The multi-stage ingestion pipeline, hybrid search, and Redis-based session management provide a robust foundation for building an intelligent code assistant that respects privacy through local LLM inference while maintaining high performance and accuracy.
