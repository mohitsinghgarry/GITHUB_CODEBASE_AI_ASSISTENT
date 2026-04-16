# Retry Utility Usage Examples

This document provides examples of how to use the retry utility with exponential backoff in the GitHub Codebase RAG Assistant.

## Overview

The retry utility provides decorators and functions for retrying operations with exponential backoff. It supports both synchronous and asynchronous functions and is configurable for different use cases.

## Basic Usage

### Synchronous Functions

```python
from app.utils.retry import retry_sync

@retry_sync(max_attempts=3, initial_delay=1.0)
def fetch_data_from_api():
    """This function will retry up to 3 times with exponential backoff."""
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

### Asynchronous Functions

```python
from app.utils.retry import retry_async
import httpx

@retry_async(max_attempts=3, initial_delay=1.0)
async def fetch_data_async():
    """This async function will retry up to 3 times with exponential backoff."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
```

## Advanced Configuration

### Using RetryConfig

```python
from app.utils.retry import RetryConfig, retry_async
import httpx

# Create a custom retry configuration
ollama_retry_config = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=(httpx.TimeoutException, httpx.ConnectError),
)

@retry_async(config=ollama_retry_config)
async def call_ollama(prompt: str):
    """Call Ollama with custom retry configuration."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={"model": "codellama:7b", "prompt": prompt},
            timeout=120.0
        )
        response.raise_for_status()
        return response.json()
```

### Specific Exception Types

```python
from app.utils.retry import retry_sync
import requests

@retry_sync(
    max_attempts=3,
    initial_delay=1.0,
    retryable_exceptions=(requests.Timeout, requests.ConnectionError)
)
def fetch_with_specific_retries():
    """Only retry on timeout and connection errors."""
    response = requests.get("https://api.example.com/data", timeout=10)
    response.raise_for_status()
    return response.json()
```

## Functional Approach

### Retry Async Operation

```python
from app.utils.retry import retry_async_operation
import httpx

async def fetch_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()

# Use retry_async_operation to retry without decorating
user = await retry_async_operation(
    fetch_user,
    user_id=123,
    max_attempts=3,
    initial_delay=1.0
)
```

### Retry Sync Operation

```python
from app.utils.retry import retry_sync_operation
import requests

def fetch_user(user_id: int):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

# Use retry_sync_operation to retry without decorating
user = retry_sync_operation(
    fetch_user,
    user_id=123,
    max_attempts=3,
    initial_delay=1.0
)
```

## Real-World Examples

### Ollama LLM Service

```python
from app.utils.retry import retry_async, RetryConfig
from app.core.config import get_settings
import httpx
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Create retry config from settings
ollama_retry_config = RetryConfig(
    max_attempts=settings.retry_max_attempts,
    initial_delay=settings.retry_initial_delay,
    max_delay=settings.retry_max_delay,
    exponential_base=settings.retry_exponential_base,
    jitter=settings.retry_jitter,
    retryable_exceptions=(httpx.TimeoutException, httpx.ConnectError),
)

class OllamaService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.timeout = settings.ollama_timeout
    
    @retry_async(config=ollama_retry_config)
    async def generate(self, prompt: str, model: str = None) -> str:
        """Generate response from Ollama with automatic retries."""
        model = model or settings.ollama_model
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["response"]
```

### Redis Connection

```python
from app.utils.retry import retry_async
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, url: str):
        self.url = url
        self.client = None
    
    @retry_async(
        max_attempts=3,
        initial_delay=0.5,
        retryable_exceptions=(redis.ConnectionError, redis.TimeoutError)
    )
    async def connect(self):
        """Connect to Redis with automatic retries."""
        self.client = await redis.from_url(self.url)
        await self.client.ping()
        logger.info("Successfully connected to Redis")
    
    @retry_async(
        max_attempts=3,
        initial_delay=0.5,
        retryable_exceptions=(redis.ConnectionError,)
    )
    async def get(self, key: str):
        """Get value from Redis with automatic retries."""
        return await self.client.get(key)
```

### Database Operations

```python
from app.utils.retry import retry_async
from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

@retry_async(
    max_attempts=3,
    initial_delay=1.0,
    retryable_exceptions=(OperationalError, TimeoutError)
)
async def save_repository(session: AsyncSession, repository_data: dict):
    """Save repository to database with automatic retries."""
    from app.models.orm.repository import Repository
    
    repository = Repository(**repository_data)
    session.add(repository)
    await session.commit()
    await session.refresh(repository)
    
    logger.info(f"Successfully saved repository: {repository.id}")
    return repository
```

### GitHub API Calls

```python
from app.utils.retry import retry_async
import httpx
import logging

logger = logging.getLogger(__name__)

@retry_async(
    max_attempts=5,
    initial_delay=2.0,
    max_delay=60.0,
    retryable_exceptions=(httpx.HTTPStatusError, httpx.TimeoutException)
)
async def fetch_github_repo_info(owner: str, repo: str, token: str = None):
    """Fetch GitHub repository information with automatic retries."""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
            timeout=30.0
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            logger.warning("GitHub API rate limit exceeded, will retry")
            response.raise_for_status()
        
        response.raise_for_status()
        return response.json()
```

## Retry Callback

You can provide a callback function that will be called before each retry:

```python
from app.utils.retry import retry_async
import logging

logger = logging.getLogger(__name__)

def on_retry_callback(exception, attempt, delay):
    """Log retry attempts with custom formatting."""
    logger.warning(
        f"Retry attempt {attempt} after {exception.__class__.__name__}: {exception}. "
        f"Waiting {delay:.2f}s before next attempt."
    )
    
    # You could also:
    # - Send metrics to monitoring system
    # - Update a progress indicator
    # - Notify administrators of repeated failures

@retry_async(
    max_attempts=5,
    initial_delay=1.0,
    on_retry=on_retry_callback
)
async def critical_operation():
    """Operation with detailed retry logging."""
    # ... operation code ...
    pass
```

## Configuration from Settings

Load retry configuration from application settings:

```python
from app.core.config import get_settings
from app.utils.retry import RetryConfig, retry_async

settings = get_settings()

# Create retry config from settings
default_retry_config = RetryConfig(
    max_attempts=settings.retry_max_attempts,
    initial_delay=settings.retry_initial_delay,
    max_delay=settings.retry_max_delay,
    exponential_base=settings.retry_exponential_base,
    jitter=settings.retry_jitter,
)

@retry_async(config=default_retry_config)
async def external_service_call():
    """Use application-wide retry configuration."""
    # ... operation code ...
    pass
```

## Exponential Backoff Calculation

The retry utility uses exponential backoff with the following formula:

```
delay = min(initial_delay * (exponential_base ** attempt), max_delay)
```

With jitter enabled (default), the delay is multiplied by a random factor between 0.5 and 1.5:

```
delay = delay * random(0.5, 1.5)
```

### Example Delays

With `initial_delay=1.0`, `exponential_base=2.0`, `max_delay=60.0`, and `jitter=False`:

- Attempt 0 (first retry): 1.0s
- Attempt 1 (second retry): 2.0s
- Attempt 2 (third retry): 4.0s
- Attempt 3 (fourth retry): 8.0s
- Attempt 4 (fifth retry): 16.0s
- Attempt 5 (sixth retry): 32.0s
- Attempt 6+ (subsequent retries): 60.0s (capped at max_delay)

## Best Practices

1. **Choose appropriate max_attempts**: Too few attempts may not handle transient failures, too many may delay error reporting.

2. **Set reasonable delays**: Start with 1-2 seconds for initial_delay and cap at 30-60 seconds for max_delay.

3. **Use specific exception types**: Only retry on exceptions that are likely to be transient (timeouts, connection errors).

4. **Enable jitter**: Jitter helps prevent thundering herd problems when multiple clients retry simultaneously.

5. **Log retry attempts**: Use the `on_retry` callback or rely on the built-in logging to track retry behavior.

6. **Consider circuit breakers**: For critical services, combine retries with circuit breaker patterns to prevent cascading failures.

7. **Test retry behavior**: Write tests that verify retry logic works correctly with mock failures.

## Environment Variables

Configure retry behavior via environment variables:

```bash
# .env file
RETRY_MAX_ATTEMPTS=3
RETRY_INITIAL_DELAY=1.0
RETRY_MAX_DELAY=60.0
RETRY_EXPONENTIAL_BASE=2.0
RETRY_JITTER=true
```

These settings are loaded automatically by the `Settings` class and can be accessed via `get_settings()`.
