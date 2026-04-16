"""
Graceful degradation utilities for handling service unavailability.

This module provides wrappers and utilities to handle graceful degradation when
external services (Redis, Ollama) are unavailable. It implements fallback logic
to maintain partial functionality when dependencies fail.

Requirements:
- 15.5: Implement graceful degradation for Redis and Ollama unavailability
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from app.services.llm_service import OllamaConnectionError, OllamaError

logger = logging.getLogger(__name__)

# Type variable for generic function wrapping
F = TypeVar('F', bound=Callable[..., Any])


# ============================================================================
# Service Availability Tracking
# ============================================================================


class ServiceAvailability:
    """
    Track availability status of external services.
    
    This class maintains the current availability status of Redis and Ollama,
    allowing the application to adapt its behavior based on service health.
    """
    
    def __init__(self):
        """Initialize service availability tracker."""
        self._redis_available = True
        self._ollama_available = True
        self._redis_failure_count = 0
        self._ollama_failure_count = 0
        
        # Threshold for marking service as unavailable
        self.failure_threshold = 3
    
    @property
    def redis_available(self) -> bool:
        """Check if Redis is currently available."""
        return self._redis_available
    
    @property
    def ollama_available(self) -> bool:
        """Check if Ollama is currently available."""
        return self._ollama_available
    
    def mark_redis_failure(self) -> None:
        """Mark a Redis failure and update availability status."""
        self._redis_failure_count += 1
        
        if self._redis_failure_count >= self.failure_threshold:
            if self._redis_available:
                logger.warning(
                    f"Redis marked as unavailable after {self._redis_failure_count} failures. "
                    "Caching and session persistence will be disabled."
                )
                self._redis_available = False
    
    def mark_redis_success(self) -> None:
        """Mark a Redis success and reset failure count."""
        if not self._redis_available:
            logger.info("Redis is now available. Re-enabling caching and session persistence.")
        
        self._redis_available = True
        self._redis_failure_count = 0
    
    def mark_ollama_failure(self) -> None:
        """Mark an Ollama failure and update availability status."""
        self._ollama_failure_count += 1
        
        if self._ollama_failure_count >= self.failure_threshold:
            if self._ollama_available:
                logger.warning(
                    f"Ollama marked as unavailable after {self._ollama_failure_count} failures. "
                    "Chat operations will be disabled, but search will continue to work."
                )
                self._ollama_available = False
    
    def mark_ollama_success(self) -> None:
        """Mark an Ollama success and reset failure count."""
        if not self._ollama_available:
            logger.info("Ollama is now available. Re-enabling chat operations.")
        
        self._ollama_available = True
        self._ollama_failure_count = 0
    
    def reset(self) -> None:
        """Reset all availability tracking."""
        self._redis_available = True
        self._ollama_available = True
        self._redis_failure_count = 0
        self._ollama_failure_count = 0
        logger.info("Service availability tracking reset")


# Global service availability tracker
_service_availability = ServiceAvailability()


def get_service_availability() -> ServiceAvailability:
    """
    Get the global service availability tracker.
    
    Returns:
        ServiceAvailability: The global tracker instance
    """
    return _service_availability


# ============================================================================
# Redis Graceful Degradation
# ============================================================================


def with_redis_fallback(
    fallback_value: Any = None,
    log_error: bool = True,
):
    """
    Decorator to handle Redis failures gracefully.
    
    When Redis is unavailable, the decorated function will return the fallback
    value instead of raising an exception. This allows the application to
    continue operating without caching/session persistence.
    
    Args:
        fallback_value: Value to return when Redis fails (default: None)
        log_error: Whether to log the error (default: True)
        
    Returns:
        Decorator function
        
    Requirement 15.5: Add fallback logic for Redis unavailability (disable caching)
    
    Example:
        @with_redis_fallback(fallback_value=None)
        async def get_cached_data(key: str):
            return await redis_client.get(key)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # Mark success if we got here
                _service_availability.mark_redis_success()
                return result
            except (RedisConnectionError, RedisError) as e:
                # Mark failure
                _service_availability.mark_redis_failure()
                
                if log_error:
                    logger.warning(
                        f"Redis operation failed in {func.__name__}: {e}. "
                        f"Returning fallback value. "
                        f"(Redis available: {_service_availability.redis_available})"
                    )
                
                return fallback_value
            except Exception as e:
                # Don't mark as Redis failure for other exceptions
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    exc_info=True
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                _service_availability.mark_redis_success()
                return result
            except (RedisConnectionError, RedisError) as e:
                _service_availability.mark_redis_failure()
                
                if log_error:
                    logger.warning(
                        f"Redis operation failed in {func.__name__}: {e}. "
                        f"Returning fallback value. "
                        f"(Redis available: {_service_availability.redis_available})"
                    )
                
                return fallback_value
            except Exception as e:
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    exc_info=True
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    
    return decorator


class RedisFallbackWrapper:
    """
    Wrapper for Redis client that provides graceful degradation.
    
    This wrapper intercepts Redis operations and returns fallback values
    when Redis is unavailable, allowing the application to continue
    operating without caching.
    
    Requirement 15.5: Add fallback logic for Redis unavailability (disable caching)
    """
    
    def __init__(self, redis_client):
        """
        Initialize the Redis fallback wrapper.
        
        Args:
            redis_client: The actual Redis client to wrap
        """
        self._redis_client = redis_client
        self._service_availability = get_service_availability()
    
    @with_redis_fallback(fallback_value=None)
    async def get_session(self, session_id: str):
        """Get session with fallback."""
        return await self._redis_client.get_session(session_id)
    
    @with_redis_fallback(fallback_value=False)
    async def save_session(self, session_id: str, session_data: dict, ttl: Optional[int] = None):
        """Save session with fallback."""
        return await self._redis_client.save_session(session_id, session_data, ttl)
    
    @with_redis_fallback(fallback_value=False)
    async def delete_session(self, session_id: str):
        """Delete session with fallback."""
        return await self._redis_client.delete_session(session_id)
    
    @with_redis_fallback(fallback_value=[])
    async def list_sessions(self, pattern: str = "session:*"):
        """List sessions with fallback."""
        return await self._redis_client.list_sessions(pattern)
    
    @with_redis_fallback(fallback_value=None)
    async def cache_get(self, key: str, prefix: str = "cache"):
        """Get cache with fallback."""
        return await self._redis_client.cache_get(key, prefix)
    
    @with_redis_fallback(fallback_value=False)
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None, prefix: str = "cache"):
        """Set cache with fallback."""
        return await self._redis_client.cache_set(key, value, ttl, prefix)
    
    @with_redis_fallback(fallback_value=False)
    async def cache_delete(self, key: str, prefix: str = "cache"):
        """Delete cache with fallback."""
        return await self._redis_client.cache_delete(key, prefix)
    
    @with_redis_fallback(fallback_value=False)
    async def cache_exists(self, key: str, prefix: str = "cache"):
        """Check cache existence with fallback."""
        return await self._redis_client.cache_exists(key, prefix)
    
    @with_redis_fallback(fallback_value=0)
    async def cache_clear(self, pattern: str = "cache:*"):
        """Clear cache with fallback."""
        return await self._redis_client.cache_clear(pattern)
    
    @with_redis_fallback(fallback_value=None)
    async def get_job_status(self, job_id: str):
        """Get job status with fallback."""
        return await self._redis_client.get_job_status(job_id)
    
    @with_redis_fallback(fallback_value=False)
    async def save_job_status(self, job_id: str, status_data: dict, ttl: Optional[int] = None):
        """Save job status with fallback."""
        return await self._redis_client.save_job_status(job_id, status_data, ttl)
    
    @with_redis_fallback(fallback_value=False)
    async def update_job_progress(self, job_id: str, progress: int, stage: Optional[str] = None):
        """Update job progress with fallback."""
        return await self._redis_client.update_job_progress(job_id, progress, stage)
    
    @with_redis_fallback(fallback_value=False)
    async def ping(self):
        """Ping Redis with fallback."""
        return await self._redis_client.ping()
    
    async def connect(self):
        """Connect to Redis (pass through)."""
        try:
            await self._redis_client.connect()
            self._service_availability.mark_redis_success()
        except (RedisConnectionError, RedisError) as e:
            self._service_availability.mark_redis_failure()
            logger.warning(
                f"Failed to connect to Redis: {e}. "
                "Application will continue without caching and session persistence."
            )
    
    async def disconnect(self):
        """Disconnect from Redis (pass through)."""
        try:
            await self._redis_client.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting from Redis: {e}")


# ============================================================================
# Ollama Graceful Degradation
# ============================================================================


def with_ollama_fallback(
    error_message: str = "LLM service is currently unavailable",
    log_error: bool = True,
):
    """
    Decorator to handle Ollama failures gracefully.
    
    When Ollama is unavailable, the decorated function will raise an
    OllamaConnectionError with a user-friendly message. This allows
    the API to return appropriate error responses while keeping
    search operations functional.
    
    Args:
        error_message: User-friendly error message
        log_error: Whether to log the error (default: True)
        
    Returns:
        Decorator function
        
    Requirement 15.5: Add fallback logic for Ollama unavailability (disable chat, keep search)
    
    Example:
        @with_ollama_fallback()
        async def generate_text(prompt: str):
            return await llm_service.generate(prompt)
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # Mark success if we got here
                _service_availability.mark_ollama_success()
                return result
            except (OllamaConnectionError, OllamaError) as e:
                # Mark failure
                _service_availability.mark_ollama_failure()
                
                if log_error:
                    logger.warning(
                        f"Ollama operation failed in {func.__name__}: {e}. "
                        f"(Ollama available: {_service_availability.ollama_available})"
                    )
                
                # Re-raise with user-friendly message
                raise OllamaConnectionError(error_message) from e
            except Exception as e:
                # Don't mark as Ollama failure for other exceptions
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    exc_info=True
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                _service_availability.mark_ollama_success()
                return result
            except (OllamaConnectionError, OllamaError) as e:
                _service_availability.mark_ollama_failure()
                
                if log_error:
                    logger.warning(
                        f"Ollama operation failed in {func.__name__}: {e}. "
                        f"(Ollama available: {_service_availability.ollama_available})"
                    )
                
                raise OllamaConnectionError(error_message) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    exc_info=True
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    
    return decorator


# ============================================================================
# Health Check Utilities
# ============================================================================


async def check_redis_health(redis_client) -> bool:
    """
    Check Redis health and update availability status.
    
    Args:
        redis_client: Redis client to check
        
    Returns:
        bool: True if Redis is healthy, False otherwise
    """
    try:
        result = await redis_client.ping()
        if result:
            _service_availability.mark_redis_success()
            return True
        else:
            _service_availability.mark_redis_failure()
            return False
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        _service_availability.mark_redis_failure()
        return False


async def check_ollama_health(llm_service) -> bool:
    """
    Check Ollama health and update availability status.
    
    Args:
        llm_service: LLM service to check
        
    Returns:
        bool: True if Ollama is healthy, False otherwise
    """
    try:
        result = await llm_service.health_check()
        if result:
            _service_availability.mark_ollama_success()
            return True
        else:
            _service_availability.mark_ollama_failure()
            return False
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        _service_availability.mark_ollama_failure()
        return False


def get_service_status() -> dict:
    """
    Get current status of all services.
    
    Returns:
        dict: Service status information
    """
    availability = get_service_availability()
    
    return {
        "redis": {
            "available": availability.redis_available,
            "failure_count": availability._redis_failure_count,
            "status": "healthy" if availability.redis_available else "degraded",
            "message": (
                "Redis is operational" if availability.redis_available
                else "Redis is unavailable - caching and session persistence disabled"
            ),
        },
        "ollama": {
            "available": availability.ollama_available,
            "failure_count": availability._ollama_failure_count,
            "status": "healthy" if availability.ollama_available else "degraded",
            "message": (
                "Ollama is operational" if availability.ollama_available
                else "Ollama is unavailable - chat operations disabled, search still functional"
            ),
        },
        "overall_status": (
            "healthy" if availability.redis_available and availability.ollama_available
            else "degraded" if availability.redis_available or availability.ollama_available
            else "critical"
        ),
    }
