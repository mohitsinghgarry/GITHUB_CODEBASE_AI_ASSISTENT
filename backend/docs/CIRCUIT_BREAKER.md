# Circuit Breaker Pattern Implementation

## Overview

The circuit breaker pattern has been implemented to protect external service calls and prevent cascade failures. This implementation provides automatic failure detection, recovery testing, and graceful degradation.

## Features

- **Three States**: CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)
- **Configurable Thresholds**: Failure and success thresholds
- **Automatic Recovery**: Transitions to half-open after timeout
- **Statistics Tracking**: Comprehensive metrics for monitoring
- **Registry Pattern**: Centralized management of multiple circuit breakers
- **Async/Sync Support**: Works with both async and sync functions

## Configuration

Circuit breaker settings are configured in `.env`:

```bash
# Circuit Breaker Settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5      # Failures before opening
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2      # Successes to close from half-open
CIRCUIT_BREAKER_TIMEOUT=60.0             # Seconds before testing recovery
CIRCUIT_BREAKER_ENABLED=true             # Enable/disable globally
```

## Basic Usage

### Creating a Circuit Breaker

```python
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# Create with default config
breaker = CircuitBreaker("my-service")

# Create with custom config
config = CircuitBreakerConfig(
    failure_threshold=5,
    success_threshold=2,
    timeout=60.0
)
breaker = CircuitBreaker("my-service", config)
```

### Using with Async Functions

```python
async def call_external_service():
    async def api_call():
        response = await client.get("https://api.example.com/data")
        return response.json()
    
    try:
        result = await breaker.call_async(api_call)
        return result
    except CircuitBreakerError as e:
        # Circuit is open, service unavailable
        logger.warning(f"Circuit open: {e.service_name}, retry after {e.retry_after}s")
        return fallback_response()
```

### Using with Sync Functions

```python
def call_external_service():
    def api_call():
        response = requests.get("https://api.example.com/data")
        return response.json()
    
    try:
        result = breaker.call(api_call)
        return result
    except CircuitBreakerError as e:
        return fallback_response()
```

## Service-Specific Integrations

### Ollama LLM Service

```python
from app.utils.circuit_breaker_integration import OllamaCircuitBreaker

ollama_cb = OllamaCircuitBreaker()

try:
    response = await ollama_cb.generate(
        client=httpx_client,
        prompt="Explain this code",
        model="codellama:7b"
    )
except CircuitBreakerError:
    return "LLM service temporarily unavailable"
```

### Redis Cache

```python
from app.utils.circuit_breaker_integration import RedisCircuitBreaker

redis_cb = RedisCircuitBreaker()

try:
    value = await redis_cb.get(redis_client, "cache_key")
except CircuitBreakerError:
    # Fall back to direct database query
    value = await db.query(...)
```

### Database Operations

```python
from app.utils.circuit_breaker_integration import DatabaseCircuitBreaker

db_cb = DatabaseCircuitBreaker()

try:
    result = await db_cb.execute_query(session, query)
except CircuitBreakerError:
    return error_response("Database temporarily unavailable")
```

## Using the Registry

```python
from app.utils.circuit_breaker import get_circuit_breaker_registry

registry = get_circuit_breaker_registry()

# Get or create circuit breaker
breaker = await registry.get_or_create("my-service", config)

# Get all statistics
all_stats = registry.get_all_stats()

# Reset all circuit breakers
registry.reset_all()
```

## Graceful Degradation

```python
from app.utils.circuit_breaker_integration import with_fallback

result = await with_fallback(
    circuit_breaker=ollama_breaker,
    primary_func=ollama_client.generate,
    fallback_func=lambda: "Service temporarily unavailable",
    prompt="test"
)
```

## Health Checks

```python
from app.utils.circuit_breaker_integration import (
    get_all_circuit_breaker_health,
    is_service_healthy
)

# Check all services
health = get_all_circuit_breaker_health()
# {
#     "ollama": {"state": "closed", "healthy": true, ...},
#     "redis": {"state": "open", "healthy": false, ...}
# }

# Check specific service
if is_service_healthy("ollama"):
    # Service is available
    pass
```

## Monitoring

### Get Statistics

```python
stats = breaker.get_stats()
# {
#     "name": "my-service",
#     "state": "closed",
#     "failure_count": 0,
#     "success_count": 5,
#     "total_calls": 10,
#     "total_failures": 2,
#     "total_successes": 8,
#     "total_rejections": 0,
#     "last_failure_time": 1234567890.0,
#     "config": {...}
# }
```

### Integration with Prometheus

Circuit breaker metrics are automatically exposed via the `/metrics` endpoint:

- `circuit_breaker_state{service="name"}` - Current state (0=closed, 1=open, 2=half_open)
- `circuit_breaker_failures_total{service="name"}` - Total failures
- `circuit_breaker_successes_total{service="name"}` - Total successes
- `circuit_breaker_rejections_total{service="name"}` - Total rejections

## State Transitions

```
CLOSED (Normal Operation)
    |
    | Failure threshold reached
    v
OPEN (Rejecting Calls)
    |
    | Timeout elapsed
    v
HALF_OPEN (Testing Recovery)
    |
    +-- Success threshold reached --> CLOSED
    |
    +-- Any failure --> OPEN
```

## Exception Handling

### Expected Exceptions

Only configured exceptions count as failures:

```python
config = CircuitBreakerConfig(
    expected_exception=(httpx.HTTPError, TimeoutError)
)
```

### Excluded Exceptions

Some exceptions can be excluded from failure counting:

```python
config = CircuitBreakerConfig(
    excluded_exceptions=(ValidationError, NotFoundError)
)
```

## Best Practices

1. **Use Service-Specific Configurations**: Different services have different failure characteristics
   - LLM services: Higher timeout (120s), moderate threshold (5)
   - Cache services: Lower timeout (30s), lower threshold (3)
   - Databases: Higher threshold (10), moderate timeout (60s)

2. **Implement Fallbacks**: Always provide fallback behavior when circuit is open

3. **Monitor Circuit State**: Track circuit breaker metrics in production

4. **Test Recovery**: Ensure services can recover gracefully after failures

5. **Use Registry**: Centralize circuit breaker management with the registry

6. **Configure Appropriately**: Tune thresholds based on service SLAs and traffic patterns

## Testing

Run circuit breaker tests:

```bash
cd backend
python -m pytest tests/unit/test_circuit_breaker.py -v
```

## Requirements Satisfied

- **15.6**: Implement circuit breakers for external dependencies to prevent cascade failures

## Related Files

- `backend/app/utils/circuit_breaker.py` - Core implementation
- `backend/app/utils/circuit_breaker_integration.py` - Service integrations
- `backend/tests/unit/test_circuit_breaker.py` - Unit tests
- `backend/app/core/config.py` - Configuration settings
