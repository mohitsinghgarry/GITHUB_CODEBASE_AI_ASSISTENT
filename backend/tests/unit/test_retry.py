"""
Unit tests for retry utility with exponential backoff.

Tests cover:
- RetryConfig validation
- Exponential backoff calculation
- Jitter behavior
- Sync and async retry decorators
- Sync and async retry operations
- Exception handling
- Retry exhaustion
- Non-retryable exceptions
"""

import asyncio
import time
from typing import List
from unittest.mock import Mock, call

import pytest

from app.utils.retry import (
    RetryConfig,
    retry_async,
    retry_async_operation,
    retry_sync,
    retry_sync_operation,
)


class TestRetryConfig:
    """Test RetryConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.retryable_exceptions == (Exception,)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False,
            retryable_exceptions=(ValueError, TypeError),
        )
        
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 3.0
        assert config.jitter is False
        assert config.retryable_exceptions == (ValueError, TypeError)
    
    def test_invalid_max_attempts(self):
        """Test validation of max_attempts."""
        with pytest.raises(ValueError, match="max_attempts must be >= 1"):
            RetryConfig(max_attempts=0)
    
    def test_invalid_initial_delay(self):
        """Test validation of initial_delay."""
        with pytest.raises(ValueError, match="initial_delay must be > 0"):
            RetryConfig(initial_delay=0)
    
    def test_invalid_max_delay(self):
        """Test validation of max_delay."""
        with pytest.raises(ValueError, match="max_delay.*must be >= initial_delay"):
            RetryConfig(initial_delay=10.0, max_delay=5.0)
    
    def test_invalid_exponential_base(self):
        """Test validation of exponential_base."""
        with pytest.raises(ValueError, match="exponential_base must be > 1"):
            RetryConfig(exponential_base=1.0)
    
    def test_calculate_delay_without_jitter(self):
        """Test delay calculation without jitter."""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=False,
        )
        
        # Attempt 0: 1.0 * (2.0 ** 0) = 1.0
        assert config.calculate_delay(0) == 1.0
        
        # Attempt 1: 1.0 * (2.0 ** 1) = 2.0
        assert config.calculate_delay(1) == 2.0
        
        # Attempt 2: 1.0 * (2.0 ** 2) = 4.0
        assert config.calculate_delay(2) == 4.0
        
        # Attempt 3: 1.0 * (2.0 ** 3) = 8.0
        assert config.calculate_delay(3) == 8.0
        
        # Attempt 10: Should be capped at max_delay
        assert config.calculate_delay(10) == 60.0
    
    def test_calculate_delay_with_jitter(self):
        """Test delay calculation with jitter."""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0,
            jitter=True,
        )
        
        # With jitter, delay should be between 0.5x and 1.5x the base delay
        for attempt in range(5):
            base_delay = min(1.0 * (2.0 ** attempt), 60.0)
            delay = config.calculate_delay(attempt)
            
            # Jitter adds ±50% variation
            assert base_delay * 0.5 <= delay <= base_delay * 1.5
    
    def test_should_retry_with_retryable_exception(self):
        """Test should_retry with retryable exception."""
        config = RetryConfig(retryable_exceptions=(ValueError, TypeError))
        
        assert config.should_retry(ValueError("test"))
        assert config.should_retry(TypeError("test"))
    
    def test_should_retry_with_non_retryable_exception(self):
        """Test should_retry with non-retryable exception."""
        config = RetryConfig(retryable_exceptions=(ValueError,))
        
        assert not config.should_retry(TypeError("test"))
        assert not config.should_retry(RuntimeError("test"))


class TestRetrySyncDecorator:
    """Test retry_sync decorator."""
    
    def test_success_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0
        
        @retry_sync(max_attempts=3, initial_delay=0.1)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_func()
        
        assert result == "success"
        assert call_count == 1
    
    def test_success_after_retries(self):
        """Test function succeeds after retries."""
        call_count = 0
        
        @retry_sync(max_attempts=3, initial_delay=0.1, jitter=False)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = flaky_func()
        
        assert result == "success"
        assert call_count == 3
    
    def test_exhausted_retries(self):
        """Test all retries are exhausted."""
        call_count = 0
        
        @retry_sync(max_attempts=3, initial_delay=0.1)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent error")
        
        with pytest.raises(ValueError, match="permanent error"):
            always_fails()
        
        assert call_count == 3
    
    def test_non_retryable_exception(self):
        """Test non-retryable exception is not retried."""
        call_count = 0
        
        @retry_sync(
            max_attempts=3,
            initial_delay=0.1,
            retryable_exceptions=(ValueError,)
        )
        def raises_non_retryable():
            nonlocal call_count
            call_count += 1
            raise TypeError("non-retryable")
        
        with pytest.raises(TypeError, match="non-retryable"):
            raises_non_retryable()
        
        # Should only be called once (no retries)
        assert call_count == 1
    
    def test_exponential_backoff_timing(self):
        """Test exponential backoff timing."""
        call_times: List[float] = []
        
        @retry_sync(max_attempts=3, initial_delay=0.1, jitter=False)
        def timed_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("retry")
            return "success"
        
        timed_func()
        
        # Check delays between calls
        # First retry: ~0.1s delay
        # Second retry: ~0.2s delay
        assert len(call_times) == 3
        assert call_times[1] - call_times[0] >= 0.1
        assert call_times[2] - call_times[1] >= 0.2
    
    def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        callback_calls = []
        
        def on_retry_callback(exception, attempt, delay):
            callback_calls.append((exception, attempt, delay))
        
        @retry_sync(
            max_attempts=3,
            initial_delay=0.1,
            jitter=False,
            on_retry=on_retry_callback
        )
        def flaky_func():
            if len(callback_calls) < 2:
                raise ValueError("retry")
            return "success"
        
        flaky_func()
        
        # Should have 2 callback calls (for 2 retries)
        assert len(callback_calls) == 2
        assert callback_calls[0][1] == 1  # First retry
        assert callback_calls[1][1] == 2  # Second retry


class TestRetryAsyncDecorator:
    """Test retry_async decorator."""
    
    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test async function succeeds on first attempt."""
        call_count = 0
        
        @retry_async(max_attempts=3, initial_delay=0.1)
        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await successful_func()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        """Test async function succeeds after retries."""
        call_count = 0
        
        @retry_async(max_attempts=3, initial_delay=0.1, jitter=False)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = await flaky_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Test all retries are exhausted."""
        call_count = 0
        
        @retry_async(max_attempts=3, initial_delay=0.1)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent error")
        
        with pytest.raises(ValueError, match="permanent error"):
            await always_fails()
        
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_non_retryable_exception(self):
        """Test non-retryable exception is not retried."""
        call_count = 0
        
        @retry_async(
            max_attempts=3,
            initial_delay=0.1,
            retryable_exceptions=(ValueError,)
        )
        async def raises_non_retryable():
            nonlocal call_count
            call_count += 1
            raise TypeError("non-retryable")
        
        with pytest.raises(TypeError, match="non-retryable"):
            await raises_non_retryable()
        
        # Should only be called once (no retries)
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test exponential backoff timing."""
        call_times: List[float] = []
        
        @retry_async(max_attempts=3, initial_delay=0.1, jitter=False)
        async def timed_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("retry")
            return "success"
        
        await timed_func()
        
        # Check delays between calls
        assert len(call_times) == 3
        assert call_times[1] - call_times[0] >= 0.1
        assert call_times[2] - call_times[1] >= 0.2


class TestRetrySyncOperation:
    """Test retry_sync_operation function."""
    
    def test_success_on_first_attempt(self):
        """Test operation succeeds on first attempt."""
        def successful_op():
            return "success"
        
        result = retry_sync_operation(
            successful_op,
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == "success"
    
    def test_success_after_retries(self):
        """Test operation succeeds after retries."""
        call_count = 0
        
        def flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = retry_sync_operation(
            flaky_op,
            max_attempts=3,
            initial_delay=0.1,
            jitter=False
        )
        
        assert result == "success"
        assert call_count == 3
    
    def test_with_arguments(self):
        """Test operation with arguments."""
        def add(a, b):
            return a + b
        
        result = retry_sync_operation(
            add,
            5,
            3,
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == 8
    
    def test_with_kwargs(self):
        """Test operation with keyword arguments."""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        result = retry_sync_operation(
            greet,
            name="World",
            greeting="Hi",
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == "Hi, World!"


class TestRetryAsyncOperation:
    """Test retry_async_operation function."""
    
    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        """Test async operation succeeds on first attempt."""
        async def successful_op():
            return "success"
        
        result = await retry_async_operation(
            successful_op,
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        """Test async operation succeeds after retries."""
        call_count = 0
        
        async def flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary error")
            return "success"
        
        result = await retry_async_operation(
            flaky_op,
            max_attempts=3,
            initial_delay=0.1,
            jitter=False
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_with_arguments(self):
        """Test async operation with arguments."""
        async def add(a, b):
            await asyncio.sleep(0.01)
            return a + b
        
        result = await retry_async_operation(
            add,
            5,
            3,
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == 8
    
    @pytest.mark.asyncio
    async def test_with_kwargs(self):
        """Test async operation with keyword arguments."""
        async def greet(name, greeting="Hello"):
            await asyncio.sleep(0.01)
            return f"{greeting}, {name}!"
        
        result = await retry_async_operation(
            greet,
            name="World",
            greeting="Hi",
            max_attempts=3,
            initial_delay=0.1
        )
        
        assert result == "Hi, World!"


class TestRetryConfigIntegration:
    """Test using RetryConfig with retry functions."""
    
    def test_sync_decorator_with_config(self):
        """Test sync decorator with RetryConfig."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.1,
            jitter=False,
            retryable_exceptions=(ValueError,)
        )
        
        call_count = 0
        
        @retry_sync(config=config)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("retry")
            return "success"
        
        result = flaky_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_decorator_with_config(self):
        """Test async decorator with RetryConfig."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.1,
            jitter=False,
            retryable_exceptions=(ValueError,)
        )
        
        call_count = 0
        
        @retry_async(config=config)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("retry")
            return "success"
        
        result = await flaky_func()
        
        assert result == "success"
        assert call_count == 3
