"""
Middleware components for the FastAPI application.

This module exports all middleware classes and functions for use in the main application.
"""

from app.middleware.error_handler import register_error_handlers
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logger import RequestLoggingMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware

__all__ = [
    "register_error_handlers",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware",
    "MetricsMiddleware",
]
