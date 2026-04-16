"""
Structured logging configuration using structlog.

This module provides JSON-formatted structured logging with contextual information
including request IDs, user IDs, and repository IDs for better observability.

Requirements:
- 12.3: Implement structured logging with configurable log levels
- 12.4: Add contextual logging (request ID, user ID, repository ID)
- 12.5: Configure Python logging with JSON formatter
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor

from app.core.config import get_settings


# ============================================================================
# Context Variables for Request-Scoped Logging
# ============================================================================

# Thread-local storage for request context
_request_context: Dict[str, Any] = {}


def set_request_context(**kwargs: Any) -> None:
    """
    Set request-scoped context variables for logging.
    
    Args:
        **kwargs: Context variables to set (request_id, user_id, repository_id, etc.)
    
    Example:
        set_request_context(request_id="abc-123", user_id="user-456")
    """
    _request_context.update(kwargs)


def get_request_context() -> Dict[str, Any]:
    """
    Get current request context variables.
    
    Returns:
        Dictionary of context variables
    """
    return _request_context.copy()


def clear_request_context() -> None:
    """Clear all request context variables."""
    _request_context.clear()


def add_request_context(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Processor to add request context to all log entries.
    
    This processor automatically adds request_id, user_id, repository_id,
    and other context variables to every log entry.
    
    **Validates: Requirement 12.4**
    """
    # Add all context variables to the event
    event_dict.update(_request_context)
    return event_dict


# ============================================================================
# Custom Processors
# ============================================================================

def add_app_context(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Add application-level context to log entries.
    
    Adds:
    - app_name: Application name
    - environment: Current environment (development, staging, production)
    - version: Application version
    """
    settings = get_settings()
    event_dict["app_name"] = settings.app_name
    event_dict["environment"] = settings.environment
    event_dict["version"] = settings.app_version
    return event_dict


def add_severity_level(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Add severity level for better log filtering.
    
    Maps Python log levels to severity strings:
    - DEBUG -> DEBUG
    - INFO -> INFO
    - WARNING -> WARNING
    - ERROR -> ERROR
    - CRITICAL -> CRITICAL
    """
    level = event_dict.get("level")
    if level:
        event_dict["severity"] = level.upper()
    return event_dict


def censor_sensitive_data(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """
    Censor sensitive data from log entries.
    
    Replaces sensitive fields with [REDACTED] to prevent leaking:
    - Passwords
    - API keys
    - Tokens
    - Secret keys
    """
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "access_token",
        "refresh_token",
        "secret_key",
        "private_key",
    }
    
    for key in list(event_dict.keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            event_dict[key] = "[REDACTED]"
    
    return event_dict


# ============================================================================
# Logging Configuration
# ============================================================================

def configure_logging(log_level: Optional[str] = None) -> None:
    """
    Configure structured logging for the application.
    
    Sets up structlog with JSON formatting and contextual processors.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses value from settings.
    
    **Validates: Requirements 12.3, 12.4, 12.5**
    """
    settings = get_settings()
    
    # Use provided log level or fall back to settings
    level = log_level or settings.log_level
    log_level_int = getattr(logging, level.upper())
    
    # ========================================================================
    # Configure Standard Library Logging
    # ========================================================================
    
    # Remove all existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set root logger level
    root_logger.setLevel(log_level_int)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_int)
    
    # Don't add formatter here - structlog will handle it
    root_logger.addHandler(console_handler)
    
    # ========================================================================
    # Configure Third-Party Library Logging
    # ========================================================================
    
    # Reduce noise from verbose libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # ========================================================================
    # Configure Structlog
    # ========================================================================
    
    # Define processor chain
    processors: list[Processor] = [
        # Add log level
        structlog.stdlib.add_log_level,
        
        # Add logger name
        structlog.stdlib.add_logger_name,
        
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        
        # Add application context
        add_app_context,
        
        # Add request context (request_id, user_id, repository_id)
        add_request_context,
        
        # Add severity level
        add_severity_level,
        
        # Censor sensitive data
        censor_sensitive_data,
        
        # Add stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        
        # Format exceptions
        structlog.processors.format_exc_info,
        
        # Decode unicode
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add development-friendly formatting in non-production
    if settings.is_development():
        # Use colored console output in development
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    else:
        # Use JSON formatting in production
        processors.append(
            structlog.processors.JSONRenderer()
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ============================================================================
# Logger Factory
# ============================================================================

def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the module).
              If None, returns the root logger.
    
    Returns:
        Structured logger instance with context support
    
    Example:
        logger = get_logger(__name__)
        logger.info("user_logged_in", user_id="123", email="user@example.com")
    """
    return structlog.get_logger(name)


# ============================================================================
# Convenience Functions
# ============================================================================

def log_with_context(
    level: str,
    message: str,
    logger_name: Optional[str] = None,
    **context: Any,
) -> None:
    """
    Log a message with additional context.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        logger_name: Logger name (defaults to root logger)
        **context: Additional context variables
    
    Example:
        log_with_context(
            "info",
            "repository_indexed",
            repository_id="repo-123",
            chunk_count=1523,
            duration_seconds=45.2
        )
    """
    logger = get_logger(logger_name)
    log_method = getattr(logger, level.lower())
    log_method(message, **context)


def log_exception(
    exception: Exception,
    message: str = "exception_occurred",
    logger_name: Optional[str] = None,
    **context: Any,
) -> None:
    """
    Log an exception with context.
    
    Args:
        exception: The exception to log
        message: Log message
        logger_name: Logger name (defaults to root logger)
        **context: Additional context variables
    
    Example:
        try:
            # Some operation
            pass
        except ValueError as e:
            log_exception(
                e,
                "invalid_repository_url",
                repository_url=url,
                user_id="user-123"
            )
    """
    logger = get_logger(logger_name)
    logger.exception(
        message,
        exc_info=exception,
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        **context,
    )


# ============================================================================
# Context Managers
# ============================================================================

class LogContext:
    """
    Context manager for scoped logging context.
    
    Automatically adds and removes context variables for a block of code.
    
    Example:
        with LogContext(request_id="abc-123", user_id="user-456"):
            logger.info("processing_request")  # Includes request_id and user_id
            # ... do work ...
            logger.info("request_completed")   # Still includes context
        # Context is cleared after exiting the block
    """
    
    def __init__(self, **context: Any):
        """
        Initialize log context.
        
        Args:
            **context: Context variables to add
        """
        self.context = context
        self.previous_context: Dict[str, Any] = {}
    
    def __enter__(self) -> "LogContext":
        """Enter context - save previous context and set new context."""
        self.previous_context = get_request_context()
        set_request_context(**self.context)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context - restore previous context."""
        clear_request_context()
        if self.previous_context:
            set_request_context(**self.previous_context)


# ============================================================================
# Initialization
# ============================================================================

# Configure logging on module import
configure_logging()
