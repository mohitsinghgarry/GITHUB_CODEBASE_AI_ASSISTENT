"""
Metrics middleware for automatic Prometheus metrics collection.

This middleware automatically tracks HTTP request metrics including:
- Request count by method, endpoint, and status
- Request duration
- Requests in progress
- Request and response sizes

Requirements:
- 12.1: Track key metrics including request count, response times, error rates
- 12.2: Expose metrics in Prometheus format for scraping
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    http_request_size_bytes,
    http_response_size_bytes,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic Prometheus metrics collection.
    
    Tracks:
    - Total requests by method, endpoint, and status
    - Request duration by method and endpoint
    - Requests in progress by method and endpoint
    - Request and response sizes
    
    **Validates: Requirements 12.1, 12.2**
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with metrics tracking.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Extract method and path
        method = request.method
        path = self._normalize_path(request.url.path)
        
        # Skip metrics endpoint to avoid recursion
        if path == "/api/v1/metrics":
            return await call_next(request)
        
        # Track request size
        request_size = int(request.headers.get("content-length", 0))
        if request_size > 0:
            http_request_size_bytes.labels(
                method=method,
                endpoint=path
            ).observe(request_size)
        
        # Increment in-progress counter
        http_requests_in_progress.labels(
            method=method,
            endpoint=path
        ).inc()
        
        # Start timer
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Track response size
            response_size = int(response.headers.get("content-length", 0))
            if response_size > 0:
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=path
                ).observe(response_size)
            
            # Track metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=str(response.status_code)
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Track error metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status="500"
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Re-raise exception
            raise
            
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method,
                endpoint=path
            ).dec()
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metrics to avoid high cardinality.
        
        Replaces dynamic path parameters (UUIDs, IDs) with placeholders.
        
        Args:
            path: Request path
            
        Returns:
            Normalized path
        """
        # Split path into segments
        segments = path.split("/")
        
        # Replace UUIDs and numeric IDs with placeholders
        normalized_segments = []
        for segment in segments:
            if not segment:
                continue
            
            # Check if segment is a UUID
            if self._is_uuid(segment):
                normalized_segments.append("{id}")
            # Check if segment is numeric
            elif segment.isdigit():
                normalized_segments.append("{id}")
            else:
                normalized_segments.append(segment)
        
        return "/" + "/".join(normalized_segments)
    
    def _is_uuid(self, value: str) -> bool:
        """
        Check if value is a UUID.
        
        Args:
            value: String to check
            
        Returns:
            True if value is a UUID, False otherwise
        """
        try:
            import uuid
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False
