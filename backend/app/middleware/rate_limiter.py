"""
Rate limiting middleware using Redis.

This module implements rate limiting to prevent abuse and ensure fair resource usage.
Uses Redis for distributed rate limiting across multiple backend instances.

Requirements:
- 10.6: Implement rate limiting to prevent abuse
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.redis_client import get_redis_client

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm with Redis.
    
    Implements per-client rate limiting based on IP address or API key.
    Uses Redis sorted sets for efficient sliding window tracking.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.rate_limit = settings.rate_limit_per_minute
        self.burst = settings.rate_limit_burst
        self.window_seconds = 60  # 1 minute window
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/api/v1/health", "/metrics", "/api/v1/metrics"]:
            return await call_next(request)
        
        # Get client identifier (IP address or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        try:
            is_allowed, remaining, reset_time = await self._check_rate_limit(client_id)
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for client {client_id} "
                    f"on {request.method} {request.url.path}"
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Please try again in {reset_time} seconds.",
                        "details": {
                            "limit": self.rate_limit,
                            "remaining": 0,
                            "reset": reset_time,
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.rate_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time),
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limiting: {e}", exc_info=True)
            # On error, allow the request through (fail open)
            return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.
        
        Uses API key if present, otherwise falls back to IP address.
        
        Args:
            request: HTTP request
            
        Returns:
            Client identifier string
        """
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use first IP in X-Forwarded-For chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(
        self, client_id: str
    ) -> tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit using sliding window.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time_seconds)
        """
        # Get Redis client
        if self.redis_client is None:
            self.redis_client = await get_redis_client()
        
        # Redis key for this client
        key = f"rate_limit:{client_id}"
        
        # Current timestamp
        now = time.time()
        window_start = now - self.window_seconds
        
        try:
            # Remove old entries outside the window
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            request_count = await self.redis_client.zcard(key)
            
            # Check if limit exceeded
            if request_count >= self.rate_limit:
                # Get oldest request timestamp to calculate reset time
                oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    reset_time = int(oldest_timestamp + self.window_seconds - now)
                else:
                    reset_time = self.window_seconds
                
                return False, 0, max(reset_time, 1)
            
            # Add current request to window
            await self.redis_client.zadd(key, {str(now): now})
            
            # Set expiry on key (cleanup)
            await self.redis_client.expire(key, self.window_seconds + 10)
            
            # Calculate remaining requests and reset time
            remaining = self.rate_limit - request_count - 1
            reset_time = self.window_seconds
            
            return True, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # On Redis error, allow the request (fail open)
            return True, self.rate_limit, self.window_seconds
