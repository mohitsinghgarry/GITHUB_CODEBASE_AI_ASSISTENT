"""
Request logging middleware with structured logging.

This module implements request/response logging with contextual information
for debugging and monitoring.

Requirements:
- 10.8: Handle concurrent requests efficiently using async/await patterns
- 12.3: Log all requests with timestamps, endpoints, status codes, and response times
- 12.4: Log stack traces and contextual information when errors occur
- 12.5: Implement structured logging with configurable log levels
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import get_logger, set_request_context, clear_request_context

# Get structured logger
logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs request details including:
    - Request ID (for tracing)
    - Method and path
    - Client IP
    - Response status code
    - Response time
    - Error details (if applicable)
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
            
        **Validates: Requirements 12.3, 12.4, 12.5**
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state for access in route handlers
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Set request context for all logs in this request
        set_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            query_params=str(request.query_params),
            user_agent=request.headers.get("user-agent", "unknown"),
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            if response.status_code < 400:
                logger.info(
                    "request_completed",
                    status_code=response.status_code,
                    response_time_ms=round(response_time * 1000, 2),
                )
            else:
                logger.warning(
                    "request_completed_with_error",
                    status_code=response.status_code,
                    response_time_ms=round(response_time * 1000, 2),
                )
            
            # Clear request context
            clear_request_context()
            
            return response
            
        except Exception as e:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log error
            logger.error(
                "request_failed",
                response_time_ms=round(response_time * 1000, 2),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            
            # Clear request context
            clear_request_context()
            
            # Re-raise exception to be handled by error handler
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        
        Handles X-Forwarded-For header for proxied requests.
        
        Args:
            request: HTTP request
            
        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use first IP in chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
