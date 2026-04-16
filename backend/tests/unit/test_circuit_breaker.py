"""
Unit tests for circuit breaker pattern implementation.

Tests cover:
- State transitions (closed -> open -> half-open -> closed)
- Failure threshold behavior
- Success threshold behavior
- Timeout and recovery
- Exception handling
- Statistics tracking
"""

import asyncio
import time
from typing import Any

import pytest

from app.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerRegistry,
    CircuitState,
    get_circuit_breaker_registry,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def circuit_breaker_config():
    """Create a test circuit breaker configuration."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=0.1,  # Very short timeout for testing
    )


@pytest.fixture
def circuit_breaker(circuit_breaker_config):
    """Create a test circuit breaker."""
    return CircuitBreaker("test-service", circuit_breaker_config)


@pytest.fixture
def registry():
    """Create a fresh circuit breaker registry."""
    return CircuitBreakerRegistry()


# ============================================================================
# Test Circuit Breaker Configuration
# ============================================================================


def test_circuit_breaker_config_defaults():
    """Test default configuration values."""
    config = CircuitBreakerConfig()
    
    assert config.failure_threshold == 5
    assert config.success_threshold == 2
    assert config.timeout == 60.0
    assert config.expected_exception == Exception
    assert config.excluded_exceptions == ()


def test_circuit_breaker_config_validation():
    """Test configuration validation."""
    # Invalid failure threshold
    with pytest.raises(ValueError, match="failure_threshold must be >= 1"):
        CircuitBreakerConfig(failure_threshold=0)
    
    # Invalid success threshold
    with pytest.raises(ValueError, match="success_threshold must be >= 1"):
        CircuitBreakerConfig(success_threshold=0)
    
    # Invalid timeout
    with pytest.raises(ValueError, match="timeout must be >= 0"):
        CircuitBreakerConfig(timeout=-1)


# ============================================================================
# Test Circuit Breaker State Transitions
# ============================================================================


@pytest.mark.asyncio
async def test_initial_state(circuit_breaker):
    """Test circuit breaker starts in closed state."""
    assert circuit_breaker.state == CircuitState.CLOSED
    assert circuit_breaker.is_closed
    assert not circuit_breaker.is_open
    assert not circuit_breaker.is_half_open


@pytest.mark.asyncio
async def test_transition_to_open_on_failures(circuit_breaker):
    """Test circuit opens after failure threshold is reached."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Execute failures up to threshold
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    # Circuit should now be open
    assert circuit_breaker.is_open
    assert circuit_breaker.stats.failure_count == 3
    assert circuit_breaker.stats.total_failures == 3


@pytest.mark.asyncio
async def test_reject_calls_when_open(circuit_breaker):
    """Test circuit breaker rejects calls when open."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.is_open
    
    # Next call should be rejected immediately
    with pytest.raises(CircuitBreakerError) as exc_info:
        await circuit_breaker.call_async(failing_function)
    
    assert exc_info.value.service_name == "test-service"
    assert circuit_breaker.stats.total_rejections == 1


@pytest.mark.asyncio
async def test_transition_to_half_open_after_timeout(circuit_breaker):
    """Test circuit transitions to half-open after timeout."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.is_open
    
    # Wait for timeout
    await asyncio.sleep(0.15)
    
    # Next call should transition to half-open
    async def successful_function():
        return "success"
    
    result = await circuit_breaker.call_async(successful_function)
    assert result == "success"
    assert circuit_breaker.is_half_open or circuit_breaker.is_closed


@pytest.mark.asyncio
async def test_transition_to_closed_on_success_threshold(circuit_breaker):
    """Test circuit closes after success threshold in half-open state."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    async def successful_function():
        return "success"
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.is_open
    
    # Wait for timeout
    await asyncio.sleep(0.15)
    
    # Execute successful calls to close circuit
    for i in range(2):
        result = await circuit_breaker.call_async(successful_function)
        assert result == "success"
    
    # Circuit should now be closed
    assert circuit_breaker.is_closed
    assert circuit_breaker.stats.failure_count == 0


@pytest.mark.asyncio
async def test_reopen_on_failure_in_half_open(circuit_breaker):
    """Test circuit reopens immediately on failure in half-open state."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    async def successful_function():
        return "success"
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.is_open
    
    # Wait for timeout
    await asyncio.sleep(0.15)
    
    # First call succeeds (half-open)
    result = await circuit_breaker.call_async(successful_function)
    assert result == "success"
    assert circuit_breaker.is_half_open
    
    # Second call fails (should reopen)
    with pytest.raises(Exception):
        await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.is_open


# ============================================================================
# Test Exception Handling
# ============================================================================


@pytest.mark.asyncio
async def test_excluded_exceptions_dont_count(circuit_breaker):
    """Test excluded exceptions don't count as failures."""
    
    class IgnoredException(Exception):
        pass
    
    # Configure to exclude specific exception
    circuit_breaker.config.excluded_exceptions = (IgnoredException,)
    
    async def function_with_ignored_exception():
        raise IgnoredException("This should be ignored")
    
    # Execute multiple times
    for i in range(5):
        with pytest.raises(IgnoredException):
            await circuit_breaker.call_async(function_with_ignored_exception)
    
    # Circuit should still be closed
    assert circuit_breaker.is_closed
    assert circuit_breaker.stats.failure_count == 0


@pytest.mark.asyncio
async def test_expected_exceptions_count(circuit_breaker):
    """Test only expected exceptions count as failures."""
    
    class ExpectedException(Exception):
        pass
    
    class UnexpectedException(Exception):
        pass
    
    # Configure to only count specific exception
    circuit_breaker.config.expected_exception = ExpectedException
    
    async def function_with_unexpected_exception():
        raise UnexpectedException("This should not count")
    
    # Execute multiple times
    for i in range(5):
        with pytest.raises(UnexpectedException):
            await circuit_breaker.call_async(function_with_unexpected_exception)
    
    # Circuit should still be closed
    assert circuit_breaker.is_closed
    assert circuit_breaker.stats.failure_count == 0


# ============================================================================
# Test Synchronous Calls
# ============================================================================


def test_sync_call_success(circuit_breaker):
    """Test synchronous successful call."""
    
    def successful_function(x: int, y: int) -> int:
        return x + y
    
    result = circuit_breaker.call(successful_function, 2, 3)
    assert result == 5
    assert circuit_breaker.stats.total_successes == 1


def test_sync_call_failure(circuit_breaker):
    """Test synchronous failing call."""
    
    def failing_function():
        raise Exception("Service unavailable")
    
    # Execute failures up to threshold
    for i in range(3):
        with pytest.raises(Exception):
            circuit_breaker.call(failing_function)
    
    # Circuit should now be open
    assert circuit_breaker.is_open


def test_sync_call_rejected_when_open(circuit_breaker):
    """Test synchronous call rejected when circuit is open."""
    
    def failing_function():
        raise Exception("Service unavailable")
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            circuit_breaker.call(failing_function)
    
    # Next call should be rejected
    with pytest.raises(CircuitBreakerError):
        circuit_breaker.call(failing_function)


# ============================================================================
# Test Statistics
# ============================================================================


@pytest.mark.asyncio
async def test_statistics_tracking(circuit_breaker):
    """Test circuit breaker tracks statistics correctly."""
    
    async def successful_function():
        return "success"
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Execute some successful calls
    for i in range(3):
        await circuit_breaker.call_async(successful_function)
    
    # Execute some failing calls
    for i in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    stats = circuit_breaker.get_stats()
    
    assert stats["name"] == "test-service"
    assert stats["state"] == CircuitState.CLOSED.value
    assert stats["total_calls"] == 5
    assert stats["total_successes"] == 3
    assert stats["total_failures"] == 2
    assert stats["failure_count"] == 2


@pytest.mark.asyncio
async def test_reset_statistics(circuit_breaker):
    """Test resetting circuit breaker statistics."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Generate some failures
    for i in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    assert circuit_breaker.stats.total_failures == 2
    
    # Reset
    circuit_breaker.reset()
    
    # Check statistics are cleared
    assert circuit_breaker.is_closed
    assert circuit_breaker.stats.total_failures == 0
    assert circuit_breaker.stats.failure_count == 0


# ============================================================================
# Test Circuit Breaker Registry
# ============================================================================


@pytest.mark.asyncio
async def test_registry_get_or_create(registry):
    """Test registry creates and retrieves circuit breakers."""
    
    config = CircuitBreakerConfig(failure_threshold=5)
    
    # Create new breaker
    breaker1 = await registry.get_or_create("service1", config)
    assert breaker1.name == "service1"
    
    # Get existing breaker
    breaker2 = await registry.get_or_create("service1")
    assert breaker1 is breaker2


def test_registry_get(registry):
    """Test registry get method."""
    
    # Non-existent breaker
    breaker = registry.get("nonexistent")
    assert breaker is None


@pytest.mark.asyncio
async def test_registry_get_all_stats(registry):
    """Test registry returns all statistics."""
    
    # Create multiple breakers
    await registry.get_or_create("service1")
    await registry.get_or_create("service2")
    
    stats = registry.get_all_stats()
    
    assert len(stats) == 2
    assert "service1" in stats
    assert "service2" in stats


@pytest.mark.asyncio
async def test_registry_reset_all(registry):
    """Test registry resets all circuit breakers."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Create breaker and generate failures
    breaker = await registry.get_or_create("service1")
    
    for i in range(2):
        with pytest.raises(Exception):
            await breaker.call_async(failing_function)
    
    assert breaker.stats.total_failures == 2
    
    # Reset all
    registry.reset_all()
    
    assert breaker.stats.total_failures == 0


def test_global_registry():
    """Test global registry singleton."""
    
    registry1 = get_circuit_breaker_registry()
    registry2 = get_circuit_breaker_registry()
    
    assert registry1 is registry2


# ============================================================================
# Test Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_calls(circuit_breaker):
    """Test circuit breaker handles concurrent calls correctly."""
    
    call_count = 0
    
    async def slow_function():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return "success"
    
    # Execute concurrent calls
    tasks = [
        circuit_breaker.call_async(slow_function)
        for _ in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 10
    assert all(r == "success" for r in results)
    assert call_count == 10


@pytest.mark.asyncio
async def test_retry_after_calculation(circuit_breaker):
    """Test retry_after is calculated correctly."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    
    # Immediately try again
    try:
        await circuit_breaker.call_async(failing_function)
    except CircuitBreakerError as e:
        # Should be close to timeout value
        assert 0.05 <= e.retry_after <= 0.15
    
    # Wait a bit
    await asyncio.sleep(0.05)
    
    # Try again
    try:
        await circuit_breaker.call_async(failing_function)
    except CircuitBreakerError as e:
        # Should be reduced
        assert 0.0 <= e.retry_after <= 0.1


@pytest.mark.asyncio
async def test_multiple_state_transitions(circuit_breaker):
    """Test circuit breaker handles multiple state transitions."""
    
    async def failing_function():
        raise Exception("Service unavailable")
    
    async def successful_function():
        return "success"
    
    # Cycle 1: Close -> Open
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    assert circuit_breaker.is_open
    
    # Wait for timeout
    await asyncio.sleep(0.15)
    
    # Cycle 2: Open -> Half-Open -> Closed
    for i in range(2):
        await circuit_breaker.call_async(successful_function)
    assert circuit_breaker.is_closed
    
    # Cycle 3: Close -> Open again
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call_async(failing_function)
    assert circuit_breaker.is_open
