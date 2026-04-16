"""
Global error handling middleware.

This module implements global exception handlers for consistent error responses
and proper error logging.

Requirements:
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
- 10.3: Return error responses with descriptive messages when validation fails
- 15.7: Catch unexpected exceptions, log details, and return 500 error with generic message
"""

import logging
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register global error handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        Handle HTTP exceptions (4xx, 5xx errors).
        
        Args:
            request: HTTP request
            exc: HTTP exception
            
        Returns:
            JSON error response
        """
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log error
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": exc.status_code,
            }
        )
        
        # Format error response
        error_response = {
            "error": _get_error_name(exc.status_code),
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "details": exc.detail if isinstance(exc.detail, dict) else None,
            "request_id": request_id,
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=getattr(exc, "headers", None),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle request validation errors (Pydantic validation).
        
        Args:
            request: HTTP request
            exc: Validation error
            
        Returns:
            JSON error response with validation details
        """
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Format validation errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        # Log validation error
        logger.warning(
            f"Validation error: {len(errors)} field(s) failed validation",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "errors": errors,
            }
        )
        
        # Format error response
        error_response = {
            "error": "Validation error",
            "message": "Request validation failed",
            "details": errors,
            "request_id": request_id,
        }
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response,
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        
        Args:
            request: HTTP request
            exc: Pydantic validation error
            
        Returns:
            JSON error response with validation details
        """
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Format validation errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        # Log validation error
        logger.warning(
            f"Pydantic validation error: {len(errors)} field(s) failed validation",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "errors": errors,
            }
        )
        
        # Format error response
        error_response = {
            "error": "Validation error",
            "message": "Data validation failed",
            "details": errors,
            "request_id": request_id,
        }
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response,
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle unexpected exceptions.
        
        Logs full stack trace and returns generic error message to client.
        
        Args:
            request: HTTP request
            exc: Exception
            
        Returns:
            JSON error response
        """
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log error with full stack trace
        logger.error(
            f"Unexpected exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(exc).__name__,
            },
            exc_info=True
        )
        
        # Format error response (generic message for security)
        error_response = {
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": None,
            "request_id": request_id,
        }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )


def _get_error_name(status_code: int) -> str:
    """
    Get human-readable error name from status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Error name string
    """
    error_names = {
        400: "Bad request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not found",
        405: "Method not allowed",
        409: "Conflict",
        422: "Validation error",
        429: "Too many requests",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }
    
    return error_names.get(status_code, f"HTTP {status_code}")
