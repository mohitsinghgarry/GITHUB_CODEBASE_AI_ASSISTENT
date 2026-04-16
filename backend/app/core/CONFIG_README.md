# Configuration Management

## Overview

The `config.py` module provides centralized configuration management for the GitHub Codebase RAG Assistant using Pydantic Settings. All configuration is loaded from environment variables with comprehensive validation and type checking.

## Requirements Satisfied

- **13.1**: Load configuration from environment variables and configuration files
- **13.2**: Support configuration for embedding model selection, chunk size, and overlap
- **13.3**: Support configuration for Ollama endpoint, model name, and timeout settings
- **13.4**: Support configuration for vector database connection parameters
- **13.5**: Support configuration for authentication secrets and API keys
- **13.8**: Validate configuration values against expected types and ranges

## Usage

### Basic Usage

```python
from app.core.config import get_settings

# Get the global settings instance
settings = get_settings()

# Access configuration values
print(settings.database_url)
print(settings.ollama_model)
print(settings.chunk_size)
```

### Helper Methods

The Settings class provides convenient helper methods to get grouped configuration:

```python
settings = get_settings()

# Get database configuration
db_config = settings.get_database_config()
# Returns: {"url": "...", "pool_size": 20, "max_overflow": 10}

# Get Redis configuration
redis_config = settings.get_redis_config()
# Returns: {"url": "...", "max_connections": 50}

# Get Ollama configuration
ollama_config = settings.get_ollama_config()
# Returns: {"base_url": "...", "model": "...", "timeout": 120, "max_retries": 3}

# Get embedding configuration
embedding_config = settings.get_embedding_config()
# Returns: {"model": "...", "dimension": 384, "batch_size": 32, "device": "cpu"}

# Get chunking configuration
chunking_config = settings.get_chunking_config()
# Returns: {"chunk_size": 512, "chunk_overlap": 50, "max_chunk_size": 1024}

# Get search configuration
search_config = settings.get_search_config()
# Returns: {"default_top_k": 10, "max_top_k": 100, "hybrid_search_alpha": 0.5}

# Get RAG configuration
rag_config = settings.get_rag_config()
# Returns: {"max_context_tokens": 4096, "max_response_tokens": 2048, "temperature": 0.7}

# Check environment
if settings.is_production():
    print("Running in production mode")
elif settings.is_development():
    print("Running in development mode")
```

## Configuration Categories

### Application Settings
- `app_name`: Application name
- `app_version`: Application version
- `environment`: Environment (development, staging, production)
- `debug`: Enable debug mode
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### API Settings
- `api_v1_prefix`: API v1 route prefix (default: `/api/v1`)
- `backend_cors_origins`: Allowed CORS origins (list)

### Database Settings
- `database_url`: PostgreSQL database URL (required, must use asyncpg driver)
- `database_pool_size`: Connection pool size (1-100, default: 20)
- `database_max_overflow`: Maximum overflow connections (0-50, default: 10)

### Redis Settings
- `redis_url`: Redis connection URL (required)
- `redis_max_connections`: Maximum connection pool size (1-200, default: 50)

### Celery Settings
- `celery_broker_url`: Celery broker URL (required)
- `celery_result_backend`: Celery result backend URL (required)

### Ollama Settings
- `ollama_base_url`: Ollama API base URL (default: `http://localhost:11434`)
- `ollama_model`: Default Ollama model name (default: `codellama:7b`)
- `ollama_timeout`: Request timeout in seconds (10-600, default: 120)
- `ollama_max_retries`: Maximum retry attempts (0-10, default: 3)

### Embedding Settings
- `embedding_model`: Sentence transformers model name (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `embedding_dimension`: Embedding vector dimension (128-1536, default: 384)
- `embedding_batch_size`: Batch size for embedding generation (1-256, default: 32)
- `embedding_device`: Device for embedding model (cpu, cuda, mps, default: cpu)

### Chunking Settings
- `chunk_size`: Default chunk size in characters (128-2048, default: 512)
- `chunk_overlap`: Overlap between chunks (0-512, default: 50)
- `max_chunk_size`: Maximum allowed chunk size (256-4096, default: 1024)

### Search Settings
- `default_top_k`: Default number of results (1-100, default: 10)
- `max_top_k`: Maximum allowed top-K value (1-1000, default: 100)
- `hybrid_search_alpha`: Weight for hybrid search (0.0-1.0, default: 0.5)

### RAG Settings
- `max_context_tokens`: Maximum context window size (512-32768, default: 4096)
- `max_response_tokens`: Maximum response length (128-8192, default: 2048)
- `rag_temperature`: Temperature for LLM generation (0.0-2.0, default: 0.7)

### Session Settings
- `session_ttl_hours`: Session time-to-live in hours (1-168, default: 24)
- `cache_ttl_hours`: Cache time-to-live in hours (0-24, default: 1)

### Storage Settings
- `repo_storage_path`: Path for storing cloned repositories (default: `./data/repositories`)
- `faiss_index_path`: Path for storing FAISS indices (default: `./data/indices`)

### Rate Limiting Settings
- `rate_limit_per_minute`: Maximum requests per minute (1-1000, default: 60)
- `rate_limit_burst`: Burst allowance (1-100, default: 10)

### Security Settings
- `secret_key`: Secret key for JWT token signing (required, min 32 characters)
- `algorithm`: JWT signing algorithm (default: `HS256`)
- `access_token_expire_minutes`: Token expiration time (5-1440, default: 30)

### Monitoring Settings
- `enable_metrics`: Enable Prometheus metrics (default: True)
- `metrics_port`: Port for Prometheus metrics (1024-65535, default: 9090)

## Validation Rules

The configuration module includes comprehensive validation:

### Field Validators
- **log_level**: Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL
- **environment**: Must be one of development, staging, production
- **embedding_device**: Must be one of cpu, cuda, mps
- **backend_cors_origins**: Parsed from JSON array or comma-separated string
- **database_url**: Must use asyncpg driver (`postgresql+asyncpg://...`)
- **redis_url**: Must start with `redis://`
- **ollama_base_url**: Must start with `http://` or `https://`
- **storage_paths**: Automatically converted to absolute paths and created if missing

### Model Validators
- **chunk_overlap**: Must be less than chunk_size
- **chunk_size**: Must not exceed max_chunk_size
- **default_top_k**: Must not exceed max_top_k
- **max_response_tokens**: Must not exceed max_context_tokens

## Environment Variables

All configuration can be set via environment variables. See `.env.example` for a complete list.

### Required Variables
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
SECRET_KEY=your-secret-key-at-least-32-characters-long
```

### Optional Variables
All other variables have sensible defaults and can be overridden as needed.

## Error Handling

If configuration is invalid or missing required fields, a `ValidationError` will be raised with descriptive messages:

```python
from pydantic import ValidationError

try:
    settings = get_settings()
except ValidationError as e:
    print(e.errors())
    # [
    #   {
    #     'loc': ('database_url',),
    #     'msg': 'Field required',
    #     'type': 'missing'
    #   }
    # ]
```

## Testing

To test the configuration module:

```bash
# Set required environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/1"
export CELERY_RESULT_BACKEND="redis://localhost:6379/2"
export SECRET_KEY="test-secret-key-at-least-32-characters-long"

# Run the test script
python test_config.py
```

## Reloading Configuration

For testing or when environment variables change:

```python
from app.core.config import reload_settings

# Force reload settings from environment
settings = reload_settings()
```

## Best Practices

1. **Never commit secrets**: Use `.env` files for local development and environment variables in production
2. **Use strong secret keys**: Generate with `openssl rand -hex 32`
3. **Validate early**: Load settings at application startup to catch configuration errors immediately
4. **Use helper methods**: Prefer `get_database_config()` over accessing individual fields
5. **Check environment**: Use `is_production()` and `is_development()` for environment-specific logic
