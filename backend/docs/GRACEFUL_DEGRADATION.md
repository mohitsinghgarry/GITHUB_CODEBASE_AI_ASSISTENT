# Graceful Degradation

This document describes the graceful degradation implementation for handling Redis and Ollama service unavailability.

## Overview

The GitHub Codebase RAG Assistant implements graceful degradation to maintain partial functionality when external services (Redis, Ollama) are unavailable. This ensures the application remains operational even when dependencies fail.

**Requirement 15.5**: Implement graceful degradation for Redis and Ollama unavailability

## Architecture

### Service Availability Tracking

The `ServiceAvailability` class tracks the health status of external services:

- **Redis**: Tracks connection failures and marks service as unavailable after 3 consecutive failures
- **Ollama**: Tracks connection failures and marks service as unavailable after 3 consecutive failures

```python
from app.core.graceful_degradation import get_service_availability

availability = get_service_availability()
print(f"Redis available: {availability.redis_available}")
print(f"Ollama available: {availability.ollama_available}")
```

### Fallback Behavior

#### Redis Unavailability

When Redis is unavailable:

- **Caching disabled**: Cache operations return `None` or `False` without raising exceptions
- **Session persistence disabled**: Sessions are not persisted, but chat operations continue
- **Job status tracking disabled**: Job status updates fail silently
- **Search operations continue**: Search functionality remains fully operational

#### Ollama Unavailability

When Ollama is unavailable:

- **Chat operations disabled**: Chat endpoints return 503 Service Unavailable
- **Search operations continue**: Semantic, keyword, and hybrid search remain fully functional
- **Repository operations continue**: Repository loading and indexing continue to work

## Usage

### Redis Fallback Decorator

Use the `@with_redis_fallback` decorator to handle Redis failures gracefully:

```python
from app.core.graceful_degradation import with_redis_fallback

@with_redis_fallback(fallback_value=None)
async def get_cached_data(key: str):
    return await redis_client.get(key)

# Returns None if Redis is unavailable, instead of raising an exception
result = await get_cached_data("my_key")
```

### Redis Fallback Wrapper

Use the `RedisFallbackWrapper` to wrap a Redis client:

```python
from app.core.graceful_degradation import RedisFallbackWrapper

wrapped_redis = RedisFallbackWrapper(redis_client)

# All operations return fallback values on failure
session = await wrapped_redis.get_session("session_id")  # Returns None on failure
success = await wrapped_redis.save_session("session_id", data)  # Returns False on failure
```

### Ollama Fallback Decorator

Use the `@with_ollama_fallback` decorator to handle Ollama failures:

```python
from app.core.graceful_degradation import with_ollama_fallback

@with_ollama_fallback(error_message="LLM service is currently unavailable")
async def generate_response(prompt: str):
    return await llm_service.generate(prompt)

# Raises OllamaConnectionError with user-friendly message if Ollama is unavailable
try:
    response = await generate_response("Hello")
except OllamaConnectionError as e:
    print(f"Error: {e}")  # "LLM service is currently unavailable"
```

### Health Checks

Check service health and update availability status:

```python
from app.core.graceful_degradation import check_redis_health, check_ollama_health

# Check Redis health
redis_healthy = await check_redis_health(redis_client)

# Check Ollama health
ollama_healthy = await check_ollama_health(llm_service)
```

### Service Status

Get the current status of all services:

```python
from app.core.graceful_degradation import get_service_status

status = get_service_status()
print(status)
# {
#     "redis": {
#         "available": True,
#         "failure_count": 0,
#         "status": "healthy",
#         "message": "Redis is operational"
#     },
#     "ollama": {
#         "available": True,
#         "failure_count": 0,
#         "status": "healthy",
#         "message": "Ollama is operational"
#     },
#     "overall_status": "healthy"
# }
```

## API Behavior

### Health Endpoint

The `/api/v1/health` endpoint includes degradation status:

```json
{
  "status": "degraded",
  "timestamp": "2026-04-16T12:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "components": {
    "database": {
      "name": "database",
      "status": "healthy",
      "message": "PostgreSQL is operational"
    },
    "redis": {
      "name": "redis",
      "status": "unhealthy",
      "message": "Redis connection failed"
    },
    "ollama": {
      "name": "ollama",
      "status": "healthy",
      "message": "Ollama is operational"
    }
  },
  "degradation": {
    "redis": {
      "available": false,
      "status": "degraded",
      "message": "Redis is unavailable - caching and session persistence disabled"
    },
    "ollama": {
      "available": true,
      "status": "healthy",
      "message": "Ollama is operational"
    },
    "overall_status": "degraded"
  }
}
```

### Chat Endpoints

When Ollama is unavailable, chat endpoints return 503:

```json
{
  "error": "LLM service unavailable",
  "message": "Unable to connect to Ollama. Please ensure it is running.",
  "details": [
    {
      "field": "ollama",
      "message": "Unable to connect to Ollama. Please ensure it is running."
    }
  ]
}
```

### Search Endpoints

Search endpoints continue to work even when Redis or Ollama are unavailable:

- Semantic search: ✅ Works (uses FAISS directly)
- Keyword search: ✅ Works (uses BM25 directly)
- Hybrid search: ✅ Works (combines both)

## Startup Behavior

During application startup:

1. **Database initialization**: Fails fast if database is unavailable (critical dependency)
2. **Redis initialization**: Logs warning and continues if Redis is unavailable
3. **Health checks**: Checks all services and logs degradation status
4. **Graceful degradation**: Automatically enabled for unavailable services

Example startup logs:

```
INFO: redis_initializing
WARNING: redis_initialization_failed error="Connection refused"
WARNING: redis_unavailable_graceful_degradation_enabled message="Application will continue without caching and session persistence"
INFO: health_checks_running
WARNING: health_check_failed component="redis" message="Connection failed - graceful degradation enabled" degraded=true
WARNING: graceful_degradation_active service="redis" message="Caching and session persistence disabled"
INFO: application_started
```

## Testing

Run the graceful degradation tests:

```bash
cd backend
python -m pytest tests/unit/test_graceful_degradation.py -v
```

Test coverage includes:

- Service availability tracking
- Redis fallback decorator
- Ollama fallback decorator
- Redis fallback wrapper
- Health check functions
- Service status reporting

## Monitoring

Monitor graceful degradation status:

1. **Health endpoint**: Check `/api/v1/health` for degradation status
2. **Logs**: Search for `graceful_degradation_active` log entries
3. **Metrics**: Monitor `system_health_status` Prometheus metric

## Recovery

Services automatically recover when they become available again:

1. **Automatic detection**: Health checks run periodically
2. **Failure count reset**: Success resets the failure counter
3. **Service re-enabled**: Service is marked as available
4. **Logging**: Recovery is logged for monitoring

Example recovery logs:

```
INFO: Redis is now available. Re-enabling caching and session persistence.
INFO: Ollama is now available. Re-enabling chat operations.
```

## Best Practices

1. **Monitor degradation status**: Set up alerts for when services enter degraded mode
2. **Test failure scenarios**: Regularly test application behavior with services unavailable
3. **Document user impact**: Clearly communicate to users when features are unavailable
4. **Plan for recovery**: Have procedures for bringing services back online
5. **Use fallback values wisely**: Choose appropriate fallback values for your use case

## Limitations

1. **Session persistence**: Chat sessions are not persisted when Redis is unavailable
2. **Caching disabled**: No caching when Redis is unavailable (may impact performance)
3. **Chat unavailable**: Chat operations fail when Ollama is unavailable
4. **No automatic retry**: Services must be manually restarted or fixed

## Future Enhancements

Potential improvements to graceful degradation:

1. **In-memory session fallback**: Store sessions in memory when Redis is unavailable
2. **Automatic service retry**: Periodically attempt to reconnect to failed services
3. **Circuit breaker integration**: Integrate with circuit breaker pattern for better resilience
4. **Partial chat functionality**: Allow read-only chat history when Ollama is unavailable
5. **Degraded mode UI**: Show degradation status in the frontend UI
