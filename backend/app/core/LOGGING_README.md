# Structured Logging Guide

This document explains how to use the structured logging system in the GitHub Codebase RAG Assistant.

## Overview

The application uses **structlog** for structured logging with JSON formatting in production and colored console output in development. All logs include contextual information like request IDs, user IDs, and repository IDs for better observability.

## Requirements Validation

- **Requirement 12.3**: Structured logging with configurable log levels ✅
- **Requirement 12.4**: Contextual logging (request ID, user ID, repository ID) ✅
- **Requirement 12.5**: JSON formatter for production logs ✅

## Basic Usage

### Getting a Logger

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)
```

### Logging Messages

Use structured logging with key-value pairs instead of string formatting:

```python
# ❌ Bad - String formatting
logger.info(f"User {user_id} indexed repository {repo_id}")

# ✅ Good - Structured logging
logger.info(
    "repository_indexed",
    user_id=user_id,
    repository_id=repo_id,
    chunk_count=1523,
    duration_seconds=45.2
)
```

### Log Levels

```python
logger.debug("debug_message", detail="verbose information")
logger.info("info_message", status="success")
logger.warning("warning_message", issue="potential problem")
logger.error("error_message", error="something went wrong")
logger.critical("critical_message", error="system failure")
```

## Contextual Logging

### Request Context

Request context is automatically added by the `RequestLoggingMiddleware`:

- `request_id`: Unique identifier for the request
- `method`: HTTP method (GET, POST, etc.)
- `path`: Request path
- `client_ip`: Client IP address

All logs within a request automatically include this context.

### Adding User Context

```python
from app.utils.logging_utils import add_user_context

# In your route handler
add_user_context(
    user_id="user-123",
    email="user@example.com",
    role="admin"
)

# All subsequent logs in this request will include user context
logger.info("user_action", action="create_repository")
```

### Adding Repository Context

```python
from app.utils.logging_utils import add_repository_context

add_repository_context(
    repository_id="repo-123",
    repository_url="https://github.com/owner/repo",
    owner="owner",
    name="repo"
)

logger.info("repository_operation", operation="indexing")
```

### Adding Job Context

```python
from app.utils.logging_utils import add_job_context

add_job_context(
    job_id="job-123",
    job_type="ingestion",
    status="running",
    stage="embedding"
)

logger.info("job_progress", progress_percent=65)
```

### Adding Session Context

```python
from app.utils.logging_utils import add_session_context

add_session_context(
    session_id="session-123",
    message_count=5,
    explanation_mode="technical"
)

logger.info("chat_message", role="user")
```

## Logging Operations

Use the utility functions for consistent operation logging:

```python
from app.utils.logging_utils import (
    log_operation_start,
    log_operation_complete,
    log_operation_failed
)
import time

# Start operation
start_time = time.time()
log_operation_start(
    "repository_indexing",
    repository_id="repo-123",
    file_count=150
)

try:
    # ... perform operation ...
    
    # Log completion
    duration = time.time() - start_time
    log_operation_complete(
        "repository_indexing",
        duration_seconds=duration,
        repository_id="repo-123",
        chunk_count=1523
    )
except Exception as e:
    # Log failure
    duration = time.time() - start_time
    log_operation_failed(
        "repository_indexing",
        error=e,
        duration_seconds=duration,
        repository_id="repo-123"
    )
    raise
```

## Logging Exceptions

```python
from app.core.logging_config import log_exception

try:
    # Some operation
    result = process_repository(repo_url)
except ValueError as e:
    log_exception(
        e,
        "invalid_repository_url",
        repository_url=repo_url,
        user_id="user-123"
    )
    raise
```

## Context Managers

Use `LogContext` for scoped logging context:

```python
from app.core.logging_config import LogContext

with LogContext(repository_id="repo-123", operation="indexing"):
    logger.info("starting_indexing")  # Includes repository_id and operation
    # ... do work ...
    logger.info("indexing_complete")  # Still includes context
# Context is cleared after exiting the block
```

## Logging Metrics

```python
from app.utils.logging_utils import log_metric

log_metric(
    "embedding_generation_time",
    value=2.5,
    unit="seconds",
    batch_size=32,
    model="all-MiniLM-L6-v2"
)
```

## Configuration

### Environment Variables

Set the log level via environment variable:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Programmatic Configuration

```python
from app.core.logging_config import configure_logging

# Configure with specific log level
configure_logging(log_level="DEBUG")
```

## Output Formats

### Development (Colored Console)

```
2024-04-16T10:30:45.123456Z [info     ] repository_indexed         app_name=GitHub Codebase RAG Assistant chunk_count=1523 duration_seconds=45.2 environment=development repository_id=repo-123 request_id=abc-123 user_id=user-456 version=1.0.0
```

### Production (JSON)

```json
{
  "event": "repository_indexed",
  "timestamp": "2024-04-16T10:30:45.123456Z",
  "level": "info",
  "severity": "INFO",
  "logger": "app.services.ingestion",
  "app_name": "GitHub Codebase RAG Assistant",
  "environment": "production",
  "version": "1.0.0",
  "request_id": "abc-123",
  "user_id": "user-456",
  "repository_id": "repo-123",
  "chunk_count": 1523,
  "duration_seconds": 45.2
}
```

## Best Practices

### 1. Use Descriptive Event Names

```python
# ❌ Bad
logger.info("done")

# ✅ Good
logger.info("repository_indexing_completed")
```

### 2. Include Relevant Context

```python
# ❌ Bad
logger.info("error")

# ✅ Good
logger.error(
    "repository_indexing_failed",
    repository_id="repo-123",
    error="Connection timeout",
    retry_count=3
)
```

### 3. Use Consistent Naming

- Use snake_case for event names: `repository_indexed`, `user_logged_in`
- Use snake_case for context keys: `user_id`, `repository_id`, `chunk_count`
- Use past tense for completed events: `repository_indexed`, `search_completed`
- Use present tense for ongoing events: `repository_indexing`, `search_running`

### 4. Don't Log Sensitive Data

The logging system automatically censors common sensitive fields (passwords, tokens, API keys), but be careful with custom fields:

```python
# ❌ Bad
logger.info("user_login", password=password)

# ✅ Good
logger.info("user_login", user_id=user_id)
```

### 5. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information (verbose)
- **INFO**: General informational messages (normal operations)
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (operation failed but recoverable)
- **CRITICAL**: Critical messages (system failure)

## Integration with Monitoring

The structured logs can be easily integrated with monitoring systems:

### Prometheus

Metrics can be extracted from logs using log-based metrics in Prometheus.

### Grafana Loki

JSON logs can be ingested directly into Loki for querying and visualization.

### ELK Stack

JSON logs can be shipped to Elasticsearch for indexing and analysis.

## Example: Complete Route Handler

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.logging_config import get_logger
from app.utils.logging_utils import (
    add_user_context,
    add_repository_context,
    log_operation_start,
    log_operation_complete,
    log_operation_failed
)
import time

router = APIRouter()
logger = get_logger(__name__)

@router.post("/repositories/{repo_id}/reindex")
async def reindex_repository(
    repo_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reindex a repository."""
    
    # Add user context
    add_user_context(user_id=current_user.id, email=current_user.email)
    
    # Add repository context
    add_repository_context(repository_id=repo_id)
    
    # Start operation
    start_time = time.time()
    log_operation_start("repository_reindexing", repository_id=repo_id)
    
    try:
        # Perform reindexing
        result = await reindex_service.reindex(repo_id)
        
        # Log completion
        duration = time.time() - start_time
        log_operation_complete(
            "repository_reindexing",
            duration_seconds=duration,
            repository_id=repo_id,
            chunk_count=result.chunk_count
        )
        
        return {"status": "success", "chunk_count": result.chunk_count}
        
    except Exception as e:
        # Log failure
        duration = time.time() - start_time
        log_operation_failed(
            "repository_reindexing",
            error=e,
            duration_seconds=duration,
            repository_id=repo_id
        )
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing

When testing, you can capture and assert on log output:

```python
import pytest
from app.core.logging_config import get_logger

def test_logging(caplog):
    logger = get_logger(__name__)
    
    logger.info("test_event", user_id="test-123")
    
    assert "test_event" in caplog.text
    assert "test-123" in caplog.text
```

## Troubleshooting

### Logs Not Appearing

1. Check log level configuration: `LOG_LEVEL` environment variable
2. Ensure logger is configured: `configure_logging()` is called
3. Check if logs are being filtered by third-party libraries

### Context Not Appearing

1. Ensure context is set before logging: `set_request_context()` or `add_*_context()`
2. Check if context is cleared prematurely: `clear_request_context()`
3. Verify middleware is registered: `RequestLoggingMiddleware` in `main.py`

### JSON Format Not Working

1. Check environment: JSON format is only used in non-development environments
2. Set `ENVIRONMENT=production` to enable JSON formatting
3. Verify structlog configuration in `logging_config.py`
