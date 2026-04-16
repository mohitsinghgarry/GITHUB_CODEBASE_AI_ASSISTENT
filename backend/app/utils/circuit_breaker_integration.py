"""
Circuit Breaker Integration Examples

This module demonstrates how to integrate circuit breakers with external services
like Ollama, Redis, and PostgreSQL.

Requirements:
- 15.6: Implement circuit breakers for external dependencies to prevent cascade failures
"""

import logging
from typing import Any, Optional

import httpx
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    get_circuit_breaker_registry,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Circuit Breaker Factory
# ============================================================================


def create_circuit_breaker(
    service_name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Create a circuit breaker with default configuration from settings.
    
    Args:
        service_name: Name of the service (e.g., "ollama", "redis")
        config: Optional custom configuration
        
    Returns:
        CircuitBreaker instance
    """
    settings = get_settings()
    
    if config is None:
        cb_config = settings.get_circuit_breaker_config()
        config = CircuitBreakerConfig(
            failure_threshold=cb_config["failure_threshold"],
            success_threshold=cb_config["success_threshold"],
            timeout=cb_config["timeout"],
        )
    
    return CircuitBreaker(service_name, config)


async def get_or_create_circuit_breaker(
    service_name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker from the global registry.
    
    Args:
        service_name: Name of the service
        config: Optional custom configuration
        
    Returns:
        CircuitBreaker instance
    """
    settings = get_settings()
    
    if config is None:
        cb_config = settings.get_circuit_breaker_config()
        config = CircuitBreakerConfig(
            failure_threshold=cb_config["failure_threshold"],
            success_threshold=cb_config["success_threshold"],
            timeout=cb_config["timeout"],
        )
    
    registry = get_circuit_breaker_registry()
    return await registry.get_or_create(service_name, config)


# ============================================================================
# Ollama Circuit Breaker Integration
# ============================================================================


class OllamaCircuitBreaker:
    """
    Circuit breaker wrapper for Ollama LLM service.
    
    Example:
        ```python
        ollama_cb = OllamaCircuitBreaker()
        
        try:
            response = await ollama_cb.generate(
                prompt="Explain this code",
                model="codellama:7b"
            )
        except CircuitBreakerError:
            # Circuit is open, service unavailable
            return fallback_response()
        ```
    """
    
    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None):
        """
        Initialize Ollama circuit breaker.
        
        Args:
            circuit_breaker: Optional custom circuit breaker instance
        """
        if circuit_breaker is None:
            # Create with Ollama-specific configuration
            config = CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout=120.0,  # Longer timeout for LLM recovery
                expected_exception=(
                    httpx.HTTPError,
                    httpx.TimeoutException,
                    ConnectionError,
                ),
            )
            circuit_breaker = create_circuit_breaker("ollama", config)
        
        self.circuit_breaker = circuit_breaker
    
    async def generate(
        self,
        client: httpx.AsyncClient,
        prompt: str,
        model: str,
        **kwargs: Any
    ) -> Any:
        """
        Generate response from Ollama with circuit breaker protection.
        
        Args:
            client: HTTPX async client
            prompt: Prompt text
            model: Model name
            **kwargs: Additional generation parameters
            
        Returns:
            Response from Ollama
            
        Raises:
            CircuitBreakerError: If circuit is open
            httpx.HTTPError: If request fails
        """
        
        async def _generate():
            response = await client.post(
                "/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()
        
        return await self.circuit_breaker.call_async(_generate)
    
    async def list_models(self, client: httpx.AsyncClient) -> Any:
        """
        List available models with circuit breaker protection.
        
        Args:
            client: HTTPX async client
            
        Returns:
            List of models
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        
        async def _list_models():
            response = await client.get("/api/tags")
            response.raise_for_status()
            return response.json()
        
        return await self.circuit_breaker.call_async(_list_models)
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()


# ============================================================================
# Redis Circuit Breaker Integration
# ============================================================================


class RedisCircuitBreaker:
    """
    Circuit breaker wrapper for Redis operations.
    
    Example:
        ```python
        redis_cb = RedisCircuitBreaker()
        
        try:
            value = await redis_cb.get(redis_client, "key")
        except CircuitBreakerError:
            # Circuit is open, Redis unavailable
            # Fall back to in-memory cache or skip caching
            pass
        ```
    """
    
    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None):
        """
        Initialize Redis circuit breaker.
        
        Args:
            circuit_breaker: Optional custom circuit breaker instance
        """
        if circuit_breaker is None:
            # Create with Redis-specific configuration
            config = CircuitBreakerConfig(
                failure_threshold=3,
                success_threshold=2,
                timeout=30.0,
                expected_exception=(
                    ConnectionError,
                    TimeoutError,
                ),
            )
            circuit_breaker = create_circuit_breaker("redis", config)
        
        self.circuit_breaker = circuit_breaker
    
    async def get(self, client: Redis, key: str) -> Optional[str]:
        """
        Get value from Redis with circuit breaker protection.
        
        Args:
            client: Redis client
            key: Key to retrieve
            
        Returns:
            Value or None
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        
        async def _get():
            return await client.get(key)
        
        return await self.circuit_breaker.call_async(_get)
    
    async def set(
        self,
        client: Redis,
        key: str,
        value: str,
        ex: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis with circuit breaker protection.
        
        Args:
            client: Redis client
            key: Key to set
            value: Value to store
            ex: Expiration in seconds
            
        Returns:
            True if successful
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        
        async def _set():
            return await client.set(key, value, ex=ex)
        
        return await self.circuit_breaker.call_async(_set)
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()


# ============================================================================
# Database Circuit Breaker Integration
# ============================================================================


class DatabaseCircuitBreaker:
    """
    Circuit breaker wrapper for database operations.
    
    Note: Database circuit breakers should be used carefully as they can
    cause data consistency issues. Consider using connection pooling and
    retry logic instead for most database operations.
    
    Example:
        ```python
        db_cb = DatabaseCircuitBreaker()
        
        try:
            result = await db_cb.execute_query(
                session,
                select(Repository).where(Repository.id == repo_id)
            )
        except CircuitBreakerError:
            # Circuit is open, database unavailable
            return error_response()
        ```
    """
    
    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None):
        """
        Initialize database circuit breaker.
        
        Args:
            circuit_breaker: Optional custom circuit breaker instance
        """
        if circuit_breaker is None:
            # Create with database-specific configuration
            config = CircuitBreakerConfig(
                failure_threshold=10,  # Higher threshold for DB
                success_threshold=3,
                timeout=60.0,
                expected_exception=(
                    ConnectionError,
                    TimeoutError,
                ),
            )
            circuit_breaker = create_circuit_breaker("database", config)
        
        self.circuit_breaker = circuit_breaker
    
    async def execute_query(
        self,
        session: AsyncSession,
        query: Any
    ) -> Any:
        """
        Execute database query with circuit breaker protection.
        
        Args:
            session: SQLAlchemy async session
            query: Query to execute
            
        Returns:
            Query result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        
        async def _execute():
            result = await session.execute(query)
            return result
        
        return await self.circuit_breaker.call_async(_execute)
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()


# ============================================================================
# Health Check Integration
# ============================================================================


def get_all_circuit_breaker_health() -> dict:
    """
    Get health status of all circuit breakers.
    
    Returns:
        Dictionary with health status for each circuit breaker
        
    Example:
        ```python
        health = get_all_circuit_breaker_health()
        # {
        #     "ollama": {"state": "closed", "healthy": true, ...},
        #     "redis": {"state": "open", "healthy": false, ...}
        # }
        ```
    """
    registry = get_circuit_breaker_registry()
    all_stats = registry.get_all_stats()
    
    health = {}
    for name, stats in all_stats.items():
        health[name] = {
            "state": stats["state"],
            "healthy": stats["state"] != "open",
            "failure_count": stats["failure_count"],
            "total_failures": stats["total_failures"],
            "total_rejections": stats["total_rejections"],
            "last_failure_time": stats["last_failure_time"],
        }
    
    return health


def is_service_healthy(service_name: str) -> bool:
    """
    Check if a specific service is healthy (circuit not open).
    
    Args:
        service_name: Name of the service to check
        
    Returns:
        True if service is healthy (circuit closed or half-open)
    """
    registry = get_circuit_breaker_registry()
    breaker = registry.get(service_name)
    
    if breaker is None:
        # No circuit breaker means service hasn't been used yet
        return True
    
    return not breaker.is_open


# ============================================================================
# Graceful Degradation Helpers
# ============================================================================


async def with_fallback(
    circuit_breaker: CircuitBreaker,
    primary_func: Any,
    fallback_func: Any,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Execute function with circuit breaker and fallback on failure.
    
    Args:
        circuit_breaker: Circuit breaker to use
        primary_func: Primary function to call
        fallback_func: Fallback function if primary fails or circuit is open
        *args: Arguments for functions
        **kwargs: Keyword arguments for functions
        
    Returns:
        Result from primary or fallback function
        
    Example:
        ```python
        result = await with_fallback(
            ollama_breaker,
            ollama_client.generate,
            lambda: "Service temporarily unavailable",
            prompt="test"
        )
        ```
    """
    try:
        return await circuit_breaker.call_async(primary_func, *args, **kwargs)
    except CircuitBreakerError:
        logger.warning(
            f"Circuit breaker open for {circuit_breaker.name}, using fallback"
        )
        if callable(fallback_func):
            return await fallback_func(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_func) else fallback_func(*args, **kwargs)
        return fallback_func
    except Exception as e:
        logger.error(
            f"Primary function failed for {circuit_breaker.name}, using fallback",
            exc_info=True
        )
        if callable(fallback_func):
            return await fallback_func(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_func) else fallback_func(*args, **kwargs)
        return fallback_func
