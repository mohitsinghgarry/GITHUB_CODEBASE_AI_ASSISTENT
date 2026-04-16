"""
Unit tests for graceful degradation functionality.

Tests the graceful degradation utilities for handling Redis and Ollama
unavailability without crashing the application.

Requirements:
- 15.5: Implement graceful degradation for Redis and Ollama unavailability
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from app.core.graceful_degradation import (
    ServiceAvailability,
    with_redis_fallback,
    with_ollama_fallback,
    RedisFallbackWrapper,
    get_service_availability,
    check_redis_health,
    check_ollama_health,
    get_service_status,
)
from app.services.llm_service import OllamaConnectionError


# ============================================================================
# ServiceAvailability Tests
# ============================================================================


def test_service_availability_initial_state():
    """Test that ServiceAvailability starts with all services available."""
    availability = ServiceAvailability()
    
    assert availability.redis_available is True
    assert availability.ollama_available is True
    assert availability._redis_failure_count == 0
    assert availability._ollama_failure_count == 0


def test_service_availability_redis_failure_tracking():
    """Test that Redis failures are tracked correctly."""
    availability = ServiceAvailability()
    
    # Mark failures below threshold
    availability.mark_redis_failure()
    assert availability.redis_available is True
    assert availability._redis_failure_count == 1
    
    availability.mark_redis_failure()
    assert availability.redis_available is True
    assert availability._redis_failure_count == 2
    
    # Mark failure at threshold
    availability.mark_redis_failure()
    assert availability.redis_available is False
    assert availability._redis_failure_count == 3


def test_service_availability_redis_success_resets():
    """Test that Redis success resets failure count."""
    availability = ServiceAvailability()
    
    # Mark failures
    availability.mark_redis_failure()
    availability.mark_redis_failure()
    availability.mark_redis_failure()
    assert availability.redis_available is False
    
    # Mark success
    availability.mark_redis_success()
    assert availability.redis_available is True
    assert availability._redis_failure_count == 0


def test_service_availability_ollama_failure_tracking():
    """Test that Ollama failures are tracked correctly."""
    availability = ServiceAvailability()
    
    # Mark failures below threshold
    availability.mark_ollama_failure()
    assert availability.ollama_available is True
    assert availability._ollama_failure_count == 1
    
    availability.mark_ollama_failure()
    assert availability.ollama_available is True
    assert availability._ollama_failure_count == 2
    
    # Mark failure at threshold
    availability.mark_ollama_failure()
    assert availability.ollama_available is False
    assert availability._ollama_failure_count == 3


def test_service_availability_ollama_success_resets():
    """Test that Ollama success resets failure count."""
    availability = ServiceAvailability()
    
    # Mark failures
    availability.mark_ollama_failure()
    availability.mark_ollama_failure()
    availability.mark_ollama_failure()
    assert availability.ollama_available is False
    
    # Mark success
    availability.mark_ollama_success()
    assert availability.ollama_available is True
    assert availability._ollama_failure_count == 0


def test_service_availability_reset():
    """Test that reset clears all tracking."""
    availability = ServiceAvailability()
    
    # Mark failures
    availability.mark_redis_failure()
    availability.mark_redis_failure()
    availability.mark_redis_failure()
    availability.mark_ollama_failure()
    availability.mark_ollama_failure()
    
    # Reset
    availability.reset()
    
    assert availability.redis_available is True
    assert availability.ollama_available is True
    assert availability._redis_failure_count == 0
    assert availability._ollama_failure_count == 0


# ============================================================================
# Redis Fallback Decorator Tests
# ============================================================================


@pytest.mark.asyncio
async def test_with_redis_fallback_success():
    """Test that decorator passes through successful operations."""
    @with_redis_fallback(fallback_value="fallback")
    async def test_func():
        return "success"
    
    result = await test_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_with_redis_fallback_connection_error():
    """Test that decorator returns fallback on Redis connection error."""
    @with_redis_fallback(fallback_value="fallback")
    async def test_func():
        raise RedisConnectionError("Connection failed")
    
    result = await test_func()
    assert result == "fallback"


@pytest.mark.asyncio
async def test_with_redis_fallback_redis_error():
    """Test that decorator returns fallback on Redis error."""
    @with_redis_fallback(fallback_value=None)
    async def test_func():
        raise RedisError("Redis error")
    
    result = await test_func()
    assert result is None


@pytest.mark.asyncio
async def test_with_redis_fallback_other_exception():
    """Test that decorator re-raises non-Redis exceptions."""
    @with_redis_fallback(fallback_value="fallback")
    async def test_func():
        raise ValueError("Not a Redis error")
    
    with pytest.raises(ValueError, match="Not a Redis error"):
        await test_func()


# ============================================================================
# Ollama Fallback Decorator Tests
# ============================================================================


@pytest.mark.asyncio
async def test_with_ollama_fallback_success():
    """Test that decorator passes through successful operations."""
    @with_ollama_fallback()
    async def test_func():
        return "success"
    
    result = await test_func()
    assert result == "success"


@pytest.mark.asyncio
async def test_with_ollama_fallback_connection_error():
    """Test that decorator re-raises with user-friendly message on Ollama error."""
    @with_ollama_fallback(error_message="Service unavailable")
    async def test_func():
        raise OllamaConnectionError("Connection failed")
    
    with pytest.raises(OllamaConnectionError, match="Service unavailable"):
        await test_func()


@pytest.mark.asyncio
async def test_with_ollama_fallback_other_exception():
    """Test that decorator re-raises non-Ollama exceptions."""
    @with_ollama_fallback()
    async def test_func():
        raise ValueError("Not an Ollama error")
    
    with pytest.raises(ValueError, match="Not an Ollama error"):
        await test_func()


# ============================================================================
# RedisFallbackWrapper Tests
# ============================================================================


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_get_session_success():
    """Test that wrapper passes through successful get_session."""
    mock_redis = AsyncMock()
    mock_redis.get_session.return_value = {"session_id": "test"}
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.get_session("test")
    
    assert result == {"session_id": "test"}
    mock_redis.get_session.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_get_session_failure():
    """Test that wrapper returns None on get_session failure."""
    mock_redis = AsyncMock()
    mock_redis.get_session.side_effect = RedisConnectionError("Connection failed")
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.get_session("test")
    
    assert result is None


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_save_session_success():
    """Test that wrapper passes through successful save_session."""
    mock_redis = AsyncMock()
    mock_redis.save_session.return_value = True
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.save_session("test", {"data": "value"})
    
    assert result is True
    mock_redis.save_session.assert_called_once()


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_save_session_failure():
    """Test that wrapper returns False on save_session failure."""
    mock_redis = AsyncMock()
    mock_redis.save_session.side_effect = RedisError("Save failed")
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.save_session("test", {"data": "value"})
    
    assert result is False


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_cache_get_success():
    """Test that wrapper passes through successful cache_get."""
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = {"cached": "data"}
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.cache_get("key")
    
    assert result == {"cached": "data"}


@pytest.mark.asyncio
async def test_redis_fallback_wrapper_cache_get_failure():
    """Test that wrapper returns None on cache_get failure."""
    mock_redis = AsyncMock()
    mock_redis.cache_get.side_effect = RedisConnectionError("Connection failed")
    
    wrapper = RedisFallbackWrapper(mock_redis)
    result = await wrapper.cache_get("key")
    
    assert result is None


# ============================================================================
# Health Check Tests
# ============================================================================


@pytest.mark.asyncio
async def test_check_redis_health_success():
    """Test Redis health check with successful ping."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    
    result = await check_redis_health(mock_redis)
    
    assert result is True
    mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_check_redis_health_failure():
    """Test Redis health check with failed ping."""
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = False
    
    result = await check_redis_health(mock_redis)
    
    assert result is False


@pytest.mark.asyncio
async def test_check_redis_health_exception():
    """Test Redis health check with exception."""
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = RedisConnectionError("Connection failed")
    
    result = await check_redis_health(mock_redis)
    
    assert result is False


@pytest.mark.asyncio
async def test_check_ollama_health_success():
    """Test Ollama health check with successful response."""
    mock_llm = AsyncMock()
    mock_llm.health_check.return_value = True
    
    result = await check_ollama_health(mock_llm)
    
    assert result is True
    mock_llm.health_check.assert_called_once()


@pytest.mark.asyncio
async def test_check_ollama_health_failure():
    """Test Ollama health check with failed response."""
    mock_llm = AsyncMock()
    mock_llm.health_check.return_value = False
    
    result = await check_ollama_health(mock_llm)
    
    assert result is False


@pytest.mark.asyncio
async def test_check_ollama_health_exception():
    """Test Ollama health check with exception."""
    mock_llm = AsyncMock()
    mock_llm.health_check.side_effect = OllamaConnectionError("Connection failed")
    
    result = await check_ollama_health(mock_llm)
    
    assert result is False


# ============================================================================
# Service Status Tests
# ============================================================================


def test_get_service_status_all_healthy():
    """Test service status when all services are healthy."""
    availability = get_service_availability()
    availability.reset()
    
    status = get_service_status()
    
    assert status["redis"]["available"] is True
    assert status["redis"]["status"] == "healthy"
    assert status["ollama"]["available"] is True
    assert status["ollama"]["status"] == "healthy"
    assert status["overall_status"] == "healthy"


def test_get_service_status_redis_degraded():
    """Test service status when Redis is degraded."""
    availability = get_service_availability()
    availability.reset()
    
    # Mark Redis as unavailable
    for _ in range(3):
        availability.mark_redis_failure()
    
    status = get_service_status()
    
    assert status["redis"]["available"] is False
    assert status["redis"]["status"] == "degraded"
    assert status["ollama"]["available"] is True
    assert status["overall_status"] == "degraded"


def test_get_service_status_ollama_degraded():
    """Test service status when Ollama is degraded."""
    availability = get_service_availability()
    availability.reset()
    
    # Mark Ollama as unavailable
    for _ in range(3):
        availability.mark_ollama_failure()
    
    status = get_service_status()
    
    assert status["redis"]["available"] is True
    assert status["ollama"]["available"] is False
    assert status["ollama"]["status"] == "degraded"
    assert status["overall_status"] == "degraded"


def test_get_service_status_all_degraded():
    """Test service status when all services are degraded."""
    availability = get_service_availability()
    availability.reset()
    
    # Mark both as unavailable
    for _ in range(3):
        availability.mark_redis_failure()
        availability.mark_ollama_failure()
    
    status = get_service_status()
    
    assert status["redis"]["available"] is False
    assert status["ollama"]["available"] is False
    assert status["overall_status"] == "critical"
