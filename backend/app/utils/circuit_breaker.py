"""
Circuit Breaker Pattern Implementation

This module implements the circuit breaker pattern for external service calls
to prevent cascade failures and provide graceful degradation.

The circuit breaker has three states:
- CLOSED: Normal operation, requests pass through
- OPEN: Failure threshold exceeded, requests fail immediately
- HALF_OPEN: Testing if service has recovered

Requirements:
- 15.6: Implement circuit breakers for external dependencies to prevent cascade failures
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker behavior.
    
    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes in half-open to close circuit
        timeout: Seconds to wait before transitioning from open to half-open
        expected_exception: Exception type(s) that count as failures
        excluded_exceptions: Exception type(s) that don't count as failures
    """
    
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    expected_exception: Union[type, tuple] = Exception
    excluded_exceptions: tuple = ()
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout < 0:
            raise ValueError("timeout must be >= 0")


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change_time: float = field(default_factory=time.time)
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0
    total_rejections: int = 0


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open and rejects a call."""
    
    def __init__(self, service_name: str, retry_after: float):
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker for '{service_name}' is OPEN. "
            f"Retry after {retry_after:.1f} seconds."
        )


class CircuitBreaker:
    """
    Circuit breaker for protecting external service calls.
    
    The circuit breaker monitors failures and automatically opens when
    the failure threshold is exceeded. After a timeout period, it transitions
    to half-open state to test if the service has recovered.
    
    Example:
        ```python
        # Create circuit breaker
        breaker = CircuitBreaker(
            name="ollama-service",
            config=CircuitBreakerConfig(
                failure_threshold=5,
                timeout=60.0
            )
        )
        
        # Use with async function
        async def call_ollama():
            return await breaker.call_async(ollama_client.generate, prompt="test")
        
        # Use with sync function
        def call_api():
            return breaker.call(requests.get, "https://api.example.com")
        ```
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker (e.g., "ollama-service")
            config: Configuration for circuit breaker behavior
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
        logger.info(
            f"Circuit breaker '{name}' initialized",
            extra={
                "circuit_breaker": name,
                "failure_threshold": self.config.failure_threshold,
                "timeout": self.config.timeout,
            }
        )
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self.stats.state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.stats.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)."""
        return self.stats.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.stats.state == CircuitState.HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """
        Check if circuit should transition from open to half-open.
        
        Returns:
            True if timeout has elapsed since last failure
        """
        if self.stats.state != CircuitState.OPEN:
            return False
        
        if self.stats.last_failure_time is None:
            return False
        
        elapsed = time.time() - self.stats.last_failure_time
        return elapsed >= self.config.timeout
    
    def _is_excluded_exception(self, exception: Exception) -> bool:
        """
        Check if exception should be excluded from failure counting.
        
        Args:
            exception: The exception to check
            
        Returns:
            True if exception is in excluded list
        """
        if not self.config.excluded_exceptions:
            return False
        return isinstance(exception, self.config.excluded_exceptions)
    
    def _is_expected_exception(self, exception: Exception) -> bool:
        """
        Check if exception should count as a failure.
        
        Args:
            exception: The exception to check
            
        Returns:
            True if exception should count as failure
        """
        if self._is_excluded_exception(exception):
            return False
        return isinstance(exception, self.config.expected_exception)
    
    async def _transition_to_open(self) -> None:
        """Transition circuit to open state."""
        async with self._lock:
            if self.stats.state == CircuitState.OPEN:
                return
            
            self.stats.state = CircuitState.OPEN
            self.stats.last_state_change_time = time.time()
            self.stats.success_count = 0
            
            logger.warning(
                f"Circuit breaker '{self.name}' opened",
                extra={
                    "circuit_breaker": self.name,
                    "failure_count": self.stats.failure_count,
                    "total_failures": self.stats.total_failures,
                }
            )
    
    async def _transition_to_half_open(self) -> None:
        """Transition circuit to half-open state."""
        async with self._lock:
            if self.stats.state == CircuitState.HALF_OPEN:
                return
            
            self.stats.state = CircuitState.HALF_OPEN
            self.stats.last_state_change_time = time.time()
            self.stats.failure_count = 0
            self.stats.success_count = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' half-opened (testing recovery)",
                extra={"circuit_breaker": self.name}
            )
    
    async def _transition_to_closed(self) -> None:
        """Transition circuit to closed state."""
        async with self._lock:
            if self.stats.state == CircuitState.CLOSED:
                return
            
            self.stats.state = CircuitState.CLOSED
            self.stats.last_state_change_time = time.time()
            self.stats.failure_count = 0
            self.stats.success_count = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' closed (service recovered)",
                extra={"circuit_breaker": self.name}
            )
    
    async def _record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            self.stats.success_count += 1
            self.stats.total_successes += 1
            
            # In half-open state, check if we should close
            if self.stats.state == CircuitState.HALF_OPEN:
                if self.stats.success_count >= self.config.success_threshold:
                    # Transition to closed (already holding lock)
                    self.stats.state = CircuitState.CLOSED
                    self.stats.last_state_change_time = time.time()
                    self.stats.failure_count = 0
                    self.stats.success_count = 0
                    
                    logger.info(
                        f"Circuit breaker '{self.name}' closed (service recovered)",
                        extra={"circuit_breaker": self.name}
                    )
    
    async def _record_failure(self, exception: Exception) -> None:
        """Record a failed call."""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.total_failures += 1
            self.stats.last_failure_time = time.time()
            
            # In half-open state, immediately open on failure
            if self.stats.state == CircuitState.HALF_OPEN:
                # Transition to open (already holding lock)
                self.stats.state = CircuitState.OPEN
                self.stats.last_state_change_time = time.time()
                self.stats.success_count = 0
                
                logger.warning(
                    f"Circuit breaker '{self.name}' opened",
                    extra={
                        "circuit_breaker": self.name,
                        "failure_count": self.stats.failure_count,
                        "total_failures": self.stats.total_failures,
                    }
                )
            
            # In closed state, check if we should open
            elif self.stats.state == CircuitState.CLOSED:
                if self.stats.failure_count >= self.config.failure_threshold:
                    # Transition to open (already holding lock)
                    self.stats.state = CircuitState.OPEN
                    self.stats.last_state_change_time = time.time()
                    self.stats.success_count = 0
                    
                    logger.warning(
                        f"Circuit breaker '{self.name}' opened",
                        extra={
                            "circuit_breaker": self.name,
                            "failure_count": self.stats.failure_count,
                            "total_failures": self.stats.total_failures,
                        }
                    )
    
    async def call_async(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Execute an async function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception raised by func
        """
        # Check if we should attempt reset
        if self._should_attempt_reset():
            await self._transition_to_half_open()
        
        # Reject if circuit is open
        if self.stats.state == CircuitState.OPEN:
            self.stats.total_rejections += 1
            
            retry_after = self.config.timeout
            if self.stats.last_failure_time:
                elapsed = time.time() - self.stats.last_failure_time
                retry_after = max(0, self.config.timeout - elapsed)
            
            raise CircuitBreakerError(self.name, retry_after)
        
        # Attempt the call
        self.stats.total_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        
        except Exception as e:
            # Only count expected exceptions as failures
            if self._is_expected_exception(e):
                await self._record_failure(e)
                logger.warning(
                    f"Circuit breaker '{self.name}' recorded failure",
                    extra={
                        "circuit_breaker": self.name,
                        "exception": type(e).__name__,
                        "failure_count": self.stats.failure_count,
                        "state": self.stats.state.value,
                    }
                )
            raise
    
    def call(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """
        Execute a sync function with circuit breaker protection.
        
        Args:
            func: Sync function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception raised by func
        """
        # Check if we should attempt reset
        if self._should_attempt_reset():
            # For sync calls, we can't await, so we update state directly
            self.stats.state = CircuitState.HALF_OPEN
            self.stats.last_state_change_time = time.time()
            self.stats.failure_count = 0
            self.stats.success_count = 0
        
        # Reject if circuit is open
        if self.stats.state == CircuitState.OPEN:
            self.stats.total_rejections += 1
            
            retry_after = self.config.timeout
            if self.stats.last_failure_time:
                elapsed = time.time() - self.stats.last_failure_time
                retry_after = max(0, self.config.timeout - elapsed)
            
            raise CircuitBreakerError(self.name, retry_after)
        
        # Attempt the call
        self.stats.total_calls += 1
        
        try:
            result = func(*args, **kwargs)
            
            # Record success
            self.stats.success_count += 1
            self.stats.total_successes += 1
            
            if self.stats.state == CircuitState.HALF_OPEN:
                if self.stats.success_count >= self.config.success_threshold:
                    self.stats.state = CircuitState.CLOSED
                    self.stats.last_state_change_time = time.time()
                    self.stats.failure_count = 0
                    self.stats.success_count = 0
            
            return result
        
        except Exception as e:
            # Only count expected exceptions as failures
            if self._is_expected_exception(e):
                self.stats.failure_count += 1
                self.stats.total_failures += 1
                self.stats.last_failure_time = time.time()
                
                if self.stats.state == CircuitState.HALF_OPEN:
                    self.stats.state = CircuitState.OPEN
                    self.stats.last_state_change_time = time.time()
                
                elif self.stats.state == CircuitState.CLOSED:
                    if self.stats.failure_count >= self.config.failure_threshold:
                        self.stats.state = CircuitState.OPEN
                        self.stats.last_state_change_time = time.time()
                        self.stats.success_count = 0
            
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with current statistics
        """
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "total_rejections": self.stats.total_rejections,
            "last_failure_time": self.stats.last_failure_time,
            "last_state_change_time": self.stats.last_state_change_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
            }
        }
    
    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self.stats = CircuitBreakerStats()
        logger.info(
            f"Circuit breaker '{self.name}' reset",
            extra={"circuit_breaker": self.name}
        )


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.
    
    This class provides a centralized way to create and access circuit breakers
    for different services.
    
    Example:
        ```python
        registry = CircuitBreakerRegistry()
        
        # Get or create circuit breaker
        ollama_breaker = registry.get_or_create(
            "ollama",
            CircuitBreakerConfig(failure_threshold=5)
        )
        
        # Get all stats
        all_stats = registry.get_all_stats()
        ```
    """
    
    def __init__(self):
        """Initialize circuit breaker registry."""
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one.
        
        Args:
            name: Circuit breaker name
            config: Configuration (only used if creating new breaker)
            
        Returns:
            CircuitBreaker instance
        """
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """
        Get circuit breaker by name.
        
        Args:
            name: Circuit breaker name
            
        Returns:
            CircuitBreaker instance or None if not found
        """
        return self._breakers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all circuit breakers.
        
        Returns:
            Dictionary mapping breaker names to their stats
        """
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()


# Global registry instance
_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """
    Get the global circuit breaker registry.
    
    Returns:
        CircuitBreakerRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = CircuitBreakerRegistry()
    return _registry
