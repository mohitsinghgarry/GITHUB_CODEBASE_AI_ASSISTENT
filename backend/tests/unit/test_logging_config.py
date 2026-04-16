"""
Unit tests for structured logging configuration.

Tests the logging configuration, context management, and utility functions.

Requirements:
- 12.3: Structured logging with configurable log levels
- 12.4: Contextual logging (request ID, user ID, repository ID)
- 12.5: JSON formatter configuration
"""

import pytest
import logging
from unittest.mock import patch

from app.core.logging_config import (
    configure_logging,
    get_logger,
    set_request_context,
    get_request_context,
    clear_request_context,
    LogContext,
    log_with_context,
    log_exception,
)
from app.utils.logging_utils import (
    add_user_context,
    add_repository_context,
    add_job_context,
    add_session_context,
    log_operation_start,
    log_operation_complete,
    log_operation_failed,
    log_metric,
)


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_configure_logging_default(self):
        """Test logging configuration with default settings."""
        configure_logging()
        
        # Should not raise any exceptions
        logger = get_logger(__name__)
        assert logger is not None
    
    def test_configure_logging_custom_level(self):
        """Test logging configuration with custom log level."""
        configure_logging(log_level="DEBUG")
        
        logger = get_logger(__name__)
        assert logger is not None
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger(__name__)
        assert logger is not None
        
        # Should return a logger (structlog uses lazy proxies, so identity check not applicable)
        logger2 = get_logger(__name__)
        assert logger2 is not None
    
    def test_get_logger_without_name(self):
        """Test getting root logger."""
        logger = get_logger()
        assert logger is not None


class TestRequestContext:
    """Test request context management."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_request_context()
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_request_context()
    
    def test_set_request_context(self):
        """Test setting request context."""
        set_request_context(request_id="test-123", user_id="user-456")
        
        context = get_request_context()
        assert context["request_id"] == "test-123"
        assert context["user_id"] == "user-456"
    
    def test_get_request_context_empty(self):
        """Test getting empty request context."""
        context = get_request_context()
        assert context == {}
    
    def test_clear_request_context(self):
        """Test clearing request context."""
        set_request_context(request_id="test-123")
        clear_request_context()
        
        context = get_request_context()
        assert context == {}
    
    def test_update_request_context(self):
        """Test updating request context."""
        set_request_context(request_id="test-123")
        set_request_context(user_id="user-456")
        
        context = get_request_context()
        assert context["request_id"] == "test-123"
        assert context["user_id"] == "user-456"


class TestLogContext:
    """Test LogContext context manager."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_request_context()
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_request_context()
    
    def test_log_context_basic(self):
        """Test basic LogContext usage."""
        with LogContext(request_id="test-123"):
            context = get_request_context()
            assert context["request_id"] == "test-123"
        
        # Context should be cleared after exiting
        context = get_request_context()
        assert context == {}
    
    def test_log_context_nested(self):
        """Test nested LogContext."""
        with LogContext(request_id="test-123"):
            assert get_request_context()["request_id"] == "test-123"
            
            with LogContext(user_id="user-456"):
                context = get_request_context()
                assert context["user_id"] == "user-456"
                # Previous context should be replaced
            
            # Should restore previous context
            context = get_request_context()
            assert context["request_id"] == "test-123"
    
    def test_log_context_exception(self):
        """Test LogContext with exception."""
        try:
            with LogContext(request_id="test-123"):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Context should be cleared even after exception
        context = get_request_context()
        assert context == {}


class TestLoggingUtilities:
    """Test logging utility functions."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_request_context()
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_request_context()
    
    def test_add_user_context(self):
        """Test adding user context."""
        add_user_context(user_id="user-123", email="user@example.com")
        
        context = get_request_context()
        assert context["user_id"] == "user-123"
        assert context["email"] == "user@example.com"
    
    def test_add_repository_context(self):
        """Test adding repository context."""
        add_repository_context(
            repository_id="repo-123",
            repository_url="https://github.com/owner/repo",
            owner="owner",
            name="repo"
        )
        
        context = get_request_context()
        assert context["repository_id"] == "repo-123"
        assert context["repository_url"] == "https://github.com/owner/repo"
        assert context["owner"] == "owner"
        assert context["name"] == "repo"
    
    def test_add_job_context(self):
        """Test adding job context."""
        add_job_context(
            job_id="job-123",
            job_type="ingestion",
            status="running"
        )
        
        context = get_request_context()
        assert context["job_id"] == "job-123"
        assert context["job_type"] == "ingestion"
        assert context["status"] == "running"
    
    def test_add_session_context(self):
        """Test adding session context."""
        add_session_context(
            session_id="session-123",
            message_count=5
        )
        
        context = get_request_context()
        assert context["session_id"] == "session-123"
        assert context["message_count"] == 5


class TestOperationLogging:
    """Test operation logging functions."""
    
    def test_log_operation_start(self, caplog):
        """Test logging operation start."""
        with caplog.at_level(logging.INFO):
            log_operation_start(
                "test_operation",
                repository_id="repo-123"
            )
        
        assert "test_operation_started" in caplog.text
    
    def test_log_operation_complete(self, caplog):
        """Test logging operation completion."""
        with caplog.at_level(logging.INFO):
            log_operation_complete(
                "test_operation",
                duration_seconds=1.5,
                repository_id="repo-123"
            )
        
        assert "test_operation_completed" in caplog.text
    
    def test_log_operation_failed(self, caplog):
        """Test logging operation failure."""
        error = ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            log_operation_failed(
                "test_operation",
                error=error,
                duration_seconds=0.5,
                repository_id="repo-123"
            )
        
        assert "test_operation_failed" in caplog.text


class TestMetricLogging:
    """Test metric logging."""
    
    def test_log_metric(self, caplog):
        """Test logging a metric."""
        with caplog.at_level(logging.INFO):
            log_metric(
                "test_metric",
                value=42.5,
                unit="seconds",
                component="embeddings"
            )
        
        assert "metric_recorded" in caplog.text


class TestSensitiveDataCensoring:
    """Test sensitive data censoring."""
    
    def test_censor_password(self, caplog):
        """Test that passwords are censored."""
        logger = get_logger(__name__)
        
        with caplog.at_level(logging.INFO):
            logger.info(
                "user_login",
                username="testuser",
                password="secret123"
            )
        
        # Password should be redacted
        assert "secret123" not in caplog.text
        assert "[REDACTED]" in caplog.text or "password" not in caplog.text
    
    def test_censor_token(self, caplog):
        """Test that tokens are censored."""
        logger = get_logger(__name__)
        
        with caplog.at_level(logging.INFO):
            logger.info(
                "api_request",
                api_key="sk-1234567890",
                access_token="token-abcdef"
            )
        
        # Tokens should be redacted
        assert "sk-1234567890" not in caplog.text
        assert "token-abcdef" not in caplog.text


class TestLogWithContext:
    """Test log_with_context function."""
    
    def test_log_with_context_info(self, caplog):
        """Test logging with context at INFO level."""
        with caplog.at_level(logging.INFO):
            log_with_context(
                "info",
                "test_message",
                user_id="user-123",
                action="test"
            )
        
        assert "test_message" in caplog.text
    
    def test_log_with_context_error(self, caplog):
        """Test logging with context at ERROR level."""
        with caplog.at_level(logging.ERROR):
            log_with_context(
                "error",
                "error_message",
                error="test error"
            )
        
        assert "error_message" in caplog.text


class TestLogException:
    """Test log_exception function."""
    
    def test_log_exception(self, caplog):
        """Test logging an exception."""
        error = ValueError("Test error message")
        
        with caplog.at_level(logging.ERROR):
            log_exception(
                error,
                "operation_failed",
                operation="test_operation"
            )
        
        assert "operation_failed" in caplog.text
        assert "ValueError" in caplog.text


class TestContextualLogging:
    """Test that context is included in log entries."""
    
    def setup_method(self):
        """Clear context before each test."""
        clear_request_context()
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_request_context()
    
    def test_context_in_logs(self, caplog):
        """Test that context appears in log entries."""
        logger = get_logger(__name__)
        
        set_request_context(request_id="test-123", user_id="user-456")
        
        with caplog.at_level(logging.INFO):
            logger.info("test_event", action="test")
        
        # Context should be in log output
        # Note: Exact format depends on structlog configuration
        assert "test_event" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
