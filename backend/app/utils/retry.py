"""
Retry utility with exponential backoff.

This module provides a decorator and utility functions for retrying operations
with exponential backoff. It supports both synchronous and asynchronous functions.

Requirements:
- 9.5: Handle Ollama timeouts and retry with exponential backoff
- 15.1: Retry operations with exponential backoff when external services are unavailable
- 15.2: Log failure and return error response when retries are exhausted
"""

import asyncio
import functools
import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

logger = logging.getLogger(__name__)

# Type variable for generic function return types
T = TypeVar("T")


class RetryConfig:
    """
    Configuration for retry behavior.
    
    Attributes:
        max_attempts: Maximum number of retry attempts (including initial attempt)
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exception types that should trigger retries
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of attempts (must be >= 1)
            initial_delay: Initial delay in seconds (must be > 0)
            max_delay: Maximum delay in seconds (must be >= initial_delay)
            exponential_base: Base for exponential calculation (must be > 1)
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Tuple of exception types that trigger retries
            
        Raises:
            ValueError: If configuration values are invalid
        """
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")
        if initial_delay <= 0:
            raise ValueError(f"initial_delay must be > 0, got {initial_delay}")
        if max_delay < initial_delay:
            raise ValueError(
                f"max_delay ({max_delay}) must be >= initial_delay ({initial_delay})"
            )
        if exponential_base <= 1:
            raise ValueError(f"exponential_base must be > 1, got {exponential_base}")
        
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.
        
        Uses exponential backoff with optional jitter:
        delay = min(initial_delay * (exponential_base ** attempt), max_delay)
        
        If jitter is enabled, adds random variation: delay * (0.5 to 1.5)
        
        Args:
            attempt: Attempt number (0-indexed, 0 = first retry)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential delay
        delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled (±50% variation)
        if self.jitter:
            jitter_factor = 0.5 + random.random()  # Random value between 0.5 and 1.5
            delay *= jitter_factor
        
        return delay
    
    def should_retry(self, exception: Exception) -> bool:
        """
        Check if an exception should trigger a retry.
        
        Args:
            exception: The exception that was raised
            
        Returns:
            True if the exception is retryable, False otherwise
        """
        return isinstance(exception, self.retryable_exceptions)


def retry_sync(
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying synchronous functions with exponential backoff.
    
    Args:
        config: RetryConfig instance (if provided, other args are ignored)
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Tuple of exception types to retry
        on_retry: Optional callback called before each retry (exception, attempt, delay)
        
    Returns:
        Decorated function that retries on failure
        
    Example:
        @retry_sync(max_attempts=3, initial_delay=1.0)
        def fetch_data():
            # This will retry up to 3 times with exponential backoff
            return requests.get("https://api.example.com/data")
    """
    # Use provided config or create new one
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if not config.should_retry(e):
                        logger.warning(
                            f"Non-retryable exception in {func.__name__}: {type(e).__name__}: {e}"
                        )
                        raise
                    
                    # Check if we have more attempts
                    if attempt + 1 >= config.max_attempts:
                        logger.error(
                            f"Max retry attempts ({config.max_attempts}) exhausted for {func.__name__}: "
                            f"{type(e).__name__}: {e}"
                        )
                        raise
                    
                    # Calculate delay and log retry
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts - 1} for {func.__name__} "
                        f"after {type(e).__name__}: {e}. Waiting {delay:.2f}s..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1, delay)
                        except Exception as callback_error:
                            logger.error(f"Error in on_retry callback: {callback_error}")
                    
                    # Wait before retry
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")
        
        return wrapper
    return decorator


def retry_async(
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying asynchronous functions with exponential backoff.
    
    Args:
        config: RetryConfig instance (if provided, other args are ignored)
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Tuple of exception types to retry
        on_retry: Optional callback called before each retry (exception, attempt, delay)
        
    Returns:
        Decorated async function that retries on failure
        
    Example:
        @retry_async(max_attempts=3, initial_delay=1.0)
        async def fetch_data():
            # This will retry up to 3 times with exponential backoff
            async with httpx.AsyncClient() as client:
                return await client.get("https://api.example.com/data")
    """
    # Use provided config or create new one
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if not config.should_retry(e):
                        logger.warning(
                            f"Non-retryable exception in {func.__name__}: {type(e).__name__}: {e}"
                        )
                        raise
                    
                    # Check if we have more attempts
                    if attempt + 1 >= config.max_attempts:
                        logger.error(
                            f"Max retry attempts ({config.max_attempts}) exhausted for {func.__name__}: "
                            f"{type(e).__name__}: {e}"
                        )
                        raise
                    
                    # Calculate delay and log retry
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts - 1} for {func.__name__} "
                        f"after {type(e).__name__}: {e}. Waiting {delay:.2f}s..."
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1, delay)
                        except Exception as callback_error:
                            logger.error(f"Error in on_retry callback: {callback_error}")
                    
                    # Wait before retry (async)
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")
        
        return wrapper
    return decorator


async def retry_async_operation(
    operation: Callable[..., T],
    *args: Any,
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
    **kwargs: Any,
) -> T:
    """
    Retry an async operation with exponential backoff (functional approach).
    
    This is an alternative to the decorator for cases where you want to
    retry a specific operation without decorating the function.
    
    Args:
        operation: Async function to retry
        *args: Positional arguments for the operation
        config: RetryConfig instance (if provided, other retry args are ignored)
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Tuple of exception types to retry
        on_retry: Optional callback called before each retry
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation
        
    Raises:
        Exception: The last exception if all retries are exhausted
        
    Example:
        result = await retry_async_operation(
            fetch_data,
            url="https://api.example.com",
            max_attempts=3,
            initial_delay=1.0
        )
    """
    # Use provided config or create new one
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
    
    last_exception: Optional[Exception] = None
    
    for attempt in range(config.max_attempts):
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this exception
            if not config.should_retry(e):
                logger.warning(
                    f"Non-retryable exception in {operation.__name__}: {type(e).__name__}: {e}"
                )
                raise
            
            # Check if we have more attempts
            if attempt + 1 >= config.max_attempts:
                logger.error(
                    f"Max retry attempts ({config.max_attempts}) exhausted for {operation.__name__}: "
                    f"{type(e).__name__}: {e}"
                )
                raise
            
            # Calculate delay and log retry
            delay = config.calculate_delay(attempt)
            logger.warning(
                f"Retry attempt {attempt + 1}/{config.max_attempts - 1} for {operation.__name__} "
                f"after {type(e).__name__}: {e}. Waiting {delay:.2f}s..."
            )
            
            # Call on_retry callback if provided
            if on_retry:
                try:
                    on_retry(e, attempt + 1, delay)
                except Exception as callback_error:
                    logger.error(f"Error in on_retry callback: {callback_error}")
            
            # Wait before retry
            await asyncio.sleep(delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Unexpected retry loop exit in {operation.__name__}")


def retry_sync_operation(
    operation: Callable[..., T],
    *args: Any,
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
    **kwargs: Any,
) -> T:
    """
    Retry a sync operation with exponential backoff (functional approach).
    
    This is an alternative to the decorator for cases where you want to
    retry a specific operation without decorating the function.
    
    Args:
        operation: Function to retry
        *args: Positional arguments for the operation
        config: RetryConfig instance (if provided, other retry args are ignored)
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Tuple of exception types to retry
        on_retry: Optional callback called before each retry
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation
        
    Raises:
        Exception: The last exception if all retries are exhausted
        
    Example:
        result = retry_sync_operation(
            fetch_data,
            url="https://api.example.com",
            max_attempts=3,
            initial_delay=1.0
        )
    """
    # Use provided config or create new one
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
    
    last_exception: Optional[Exception] = None
    
    for attempt in range(config.max_attempts):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this exception
            if not config.should_retry(e):
                logger.warning(
                    f"Non-retryable exception in {operation.__name__}: {type(e).__name__}: {e}"
                )
                raise
            
            # Check if we have more attempts
            if attempt + 1 >= config.max_attempts:
                logger.error(
                    f"Max retry attempts ({config.max_attempts}) exhausted for {operation.__name__}: "
                    f"{type(e).__name__}: {e}"
                )
                raise
            
            # Calculate delay and log retry
            delay = config.calculate_delay(attempt)
            logger.warning(
                f"Retry attempt {attempt + 1}/{config.max_attempts - 1} for {operation.__name__} "
                f"after {type(e).__name__}: {e}. Waiting {delay:.2f}s..."
            )
            
            # Call on_retry callback if provided
            if on_retry:
                try:
                    on_retry(e, attempt + 1, delay)
                except Exception as callback_error:
                    logger.error(f"Error in on_retry callback: {callback_error}")
            
            # Wait before retry
            time.sleep(delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Unexpected retry loop exit in {operation.__name__}")
