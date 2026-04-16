"""
Logging utility functions for adding contextual information.

This module provides helper functions for adding user_id, repository_id,
and other contextual information to logs throughout the application.

Requirements:
- 12.4: Add contextual logging (request ID, user ID, repository ID)
"""

from typing import Any, Optional
from uuid import UUID

from app.core.logging_config import set_request_context, get_logger

logger = get_logger(__name__)


def add_user_context(user_id: Optional[str] = None, **kwargs: Any) -> None:
    """
    Add user context to current request logs.
    
    Args:
        user_id: User identifier
        **kwargs: Additional user-related context (email, role, etc.)
    
    Example:
        add_user_context(user_id="user-123", email="user@example.com", role="admin")
    
    **Validates: Requirement 12.4**
    """
    context = {}
    if user_id:
        context["user_id"] = user_id
    context.update(kwargs)
    
    if context:
        set_request_context(**context)
        logger.debug("user_context_added", **context)


def add_repository_context(
    repository_id: Optional[str] = None,
    repository_url: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Add repository context to current request logs.
    
    Args:
        repository_id: Repository identifier
        repository_url: Repository URL
        **kwargs: Additional repository-related context (owner, name, branch, etc.)
    
    Example:
        add_repository_context(
            repository_id="repo-123",
            repository_url="https://github.com/owner/repo",
            owner="owner",
            name="repo"
        )
    
    **Validates: Requirement 12.4**
    """
    context = {}
    if repository_id:
        context["repository_id"] = repository_id
    if repository_url:
        context["repository_url"] = repository_url
    context.update(kwargs)
    
    if context:
        set_request_context(**context)
        logger.debug("repository_context_added", **context)


def add_job_context(
    job_id: Optional[str] = None,
    job_type: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Add job context to current request logs.
    
    Args:
        job_id: Job identifier
        job_type: Job type (ingestion, indexing, etc.)
        **kwargs: Additional job-related context (status, stage, etc.)
    
    Example:
        add_job_context(
            job_id="job-123",
            job_type="ingestion",
            status="running",
            stage="embedding"
        )
    
    **Validates: Requirement 12.4**
    """
    context = {}
    if job_id:
        context["job_id"] = job_id
    if job_type:
        context["job_type"] = job_type
    context.update(kwargs)
    
    if context:
        set_request_context(**context)
        logger.debug("job_context_added", **context)


def add_session_context(
    session_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Add chat session context to current request logs.
    
    Args:
        session_id: Session identifier
        **kwargs: Additional session-related context (message_count, etc.)
    
    Example:
        add_session_context(
            session_id="session-123",
            message_count=5,
            explanation_mode="technical"
        )
    
    **Validates: Requirement 12.4**
    """
    context = {}
    if session_id:
        context["session_id"] = session_id
    context.update(kwargs)
    
    if context:
        set_request_context(**context)
        logger.debug("session_context_added", **context)


def log_operation_start(
    operation: str,
    **context: Any,
) -> None:
    """
    Log the start of an operation with context.
    
    Args:
        operation: Operation name (e.g., "repository_indexing", "search_query")
        **context: Operation-specific context
    
    Example:
        log_operation_start(
            "repository_indexing",
            repository_id="repo-123",
            file_count=150
        )
    """
    logger.info(f"{operation}_started", **context)


def log_operation_complete(
    operation: str,
    duration_seconds: Optional[float] = None,
    **context: Any,
) -> None:
    """
    Log the completion of an operation with context.
    
    Args:
        operation: Operation name (e.g., "repository_indexing", "search_query")
        duration_seconds: Operation duration in seconds
        **context: Operation-specific context
    
    Example:
        log_operation_complete(
            "repository_indexing",
            duration_seconds=45.2,
            repository_id="repo-123",
            chunk_count=1523
        )
    """
    if duration_seconds is not None:
        context["duration_seconds"] = round(duration_seconds, 3)
    logger.info(f"{operation}_completed", **context)


def log_operation_failed(
    operation: str,
    error: Exception,
    duration_seconds: Optional[float] = None,
    **context: Any,
) -> None:
    """
    Log the failure of an operation with context.
    
    Args:
        operation: Operation name (e.g., "repository_indexing", "search_query")
        error: Exception that caused the failure
        duration_seconds: Operation duration in seconds before failure
        **context: Operation-specific context
    
    Example:
        try:
            # ... operation ...
        except Exception as e:
            log_operation_failed(
                "repository_indexing",
                error=e,
                duration_seconds=12.5,
                repository_id="repo-123"
            )
    """
    if duration_seconds is not None:
        context["duration_seconds"] = round(duration_seconds, 3)
    
    context["error"] = str(error)
    context["error_type"] = type(error).__name__
    
    logger.error(f"{operation}_failed", exc_info=error, **context)


def log_metric(
    metric_name: str,
    value: float,
    unit: Optional[str] = None,
    **context: Any,
) -> None:
    """
    Log a metric value with context.
    
    Args:
        metric_name: Metric name (e.g., "embedding_generation_time")
        value: Metric value
        unit: Unit of measurement (e.g., "seconds", "bytes", "count")
        **context: Additional context
    
    Example:
        log_metric(
            "embedding_generation_time",
            value=2.5,
            unit="seconds",
            batch_size=32,
            model="all-MiniLM-L6-v2"
        )
    """
    context["metric_name"] = metric_name
    context["metric_value"] = value
    if unit:
        context["metric_unit"] = unit
    
    logger.info("metric_recorded", **context)
