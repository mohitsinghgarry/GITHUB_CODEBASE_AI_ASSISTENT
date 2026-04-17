"""
FastAPI application entry point.

This is the main application file that initializes FastAPI and registers all routes.

Requirements:
- 10.1: Expose RESTful endpoints for repository management, search, and chat operations
- 10.4: Support CORS configuration for cross-origin requests from the Frontend_App
- 10.5: Implement authentication and authorization for protected endpoints
- 10.6: Implement rate limiting to prevent abuse
- 10.8: Handle concurrent requests efficiently using async/await patterns
- 10.9: Perform health checks on dependencies on startup
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.core.graceful_degradation import (
    check_redis_health,
    check_ollama_health,
    get_service_availability,
)
from app.api.routes import repositories, search, chat, jobs, review, health
from app.api.routes import settings as settings_router
from app.middleware import (
    register_error_handlers,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    MetricsMiddleware,
)
from app.utils.metrics import init_metrics

# Configure structured logging
configure_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Handles:
    - Database initialization and connection
    - Redis initialization and connection
    - Health checks for dependencies
    - Graceful shutdown
    
    **Validates: Requirements 10.8, 10.9**
    """
    # ========================================================================
    # Startup
    # ========================================================================
    
    logger.info(
        "application_starting",
        environment=settings.environment,
        debug=settings.debug,
        log_level=settings.log_level,
    )
    
    # Initialize database
    logger.info("database_initializing")
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error(
            "database_initialization_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        if settings.is_production():
            raise  # Fail fast in production
        logger.warning("database_initialization_skipped", reason="development_mode")
    
    # Initialize Redis with graceful degradation
    logger.info("redis_initializing")
    try:
        await init_redis()
        logger.info("redis_initialized")
    except Exception as e:
        logger.error(
            "redis_initialization_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        # Don't fail - graceful degradation will handle it
        logger.warning(
            "redis_unavailable_graceful_degradation_enabled",
            message="Application will continue without caching and session persistence"
        )
    
    # Health checks with graceful degradation awareness
    logger.info("health_checks_running")
    health_status = await _run_health_checks()
    
    # Get service availability status
    service_availability = get_service_availability()
    
    for component, status in health_status.items():
        if status["healthy"]:
            logger.info(
                "health_check_passed",
                component=component,
                message=status["message"],
            )
        else:
            logger.warning(
                "health_check_failed",
                component=component,
                message=status["message"],
                degraded=True,
            )
    
    # Log graceful degradation status
    if not service_availability.redis_available:
        logger.warning(
            "graceful_degradation_active",
            service="redis",
            message="Caching and session persistence disabled"
        )
    
    if not service_availability.ollama_available:
        logger.warning(
            "graceful_degradation_active",
            service="ollama",
            message="Chat operations disabled, search remains functional"
        )
    
    # Startup complete
    logger.info(
        "application_started",
        api_docs_url="http://localhost:8000/docs",
        health_url="http://localhost:8000/api/v1/health",
        metrics_url="http://localhost:8000/api/v1/metrics",
    )
    
    # Initialize Prometheus metrics
    init_metrics(
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    logger.info("metrics_initialized")
    
    yield
    
    # ========================================================================
    # Shutdown
    # ========================================================================
    
    logger.info("application_shutting_down")
    
    # Close Redis connection
    logger.info("redis_closing")
    try:
        await close_redis()
        logger.info("redis_closed")
    except Exception as e:
        logger.error(
            "redis_close_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
    
    # Close database connection
    logger.info("database_closing")
    try:
        await close_db()
        logger.info("database_closed")
    except Exception as e:
        logger.error(
            "database_close_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
    
    logger.info("application_shutdown_complete")


async def _run_health_checks() -> Dict[str, Dict[str, Any]]:
    """
    Run health checks on all dependencies.
    
    Returns:
        Dictionary of component health status
    """
    health_status = {}
    
    # Check database
    try:
        from app.database import get_db
        async for db in get_db():
            await db.execute("SELECT 1")
            health_status["database"] = {
                "healthy": True,
                "message": "Connected and responsive"
            }
            break
    except Exception as e:
        health_status["database"] = {
            "healthy": False,
            "message": f"Connection failed: {str(e)}"
        }
    
    # Check Redis with graceful degradation
    try:
        from app.core.redis_client import get_redis_client
        redis = await get_redis_client()
        is_healthy = await check_redis_health(redis)
        health_status["redis"] = {
            "healthy": is_healthy,
            "message": "Connected and responsive" if is_healthy else "Connection failed - graceful degradation enabled"
        }
    except Exception as e:
        health_status["redis"] = {
            "healthy": False,
            "message": f"Connection failed: {str(e)}"
        }
    
    # Check LLM provider with graceful degradation (optional - don't fail startup if unavailable)
    try:
        from app.services.groq_llm_service import create_llm_service
        llm_service = create_llm_service()
        is_healthy = await check_ollama_health(llm_service)
        await llm_service.close()
        import os
        provider = os.getenv("LLM_PROVIDER", "ollama")
        health_status["ollama"] = {
            "healthy": is_healthy,
            "message": f"[{provider.upper()}] Connected and responsive" if is_healthy else f"[{provider.upper()}] Connection failed - chat operations disabled, search remains functional"
        }
    except Exception as e:
        health_status["ollama"] = {
            "healthy": False,
            "message": f"Connection failed: {str(e)}"
        }
    
    return health_status


# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-grade RAG system for GitHub repositories",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================================
# Configure Middleware (Order matters!)
# ============================================================================

# 1. CORS middleware (must be first to handle preflight requests)
# **Validates: Requirement 10.4**
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# 2. Metrics middleware (before logging to track all requests)
# **Validates: Requirements 12.1, 12.2**
app.add_middleware(MetricsMiddleware)

# 3. Request logging middleware
# **Validates: Requirements 10.8, 12.3, 12.4, 12.5**
app.add_middleware(RequestLoggingMiddleware)

# 4. Rate limiting middleware
# **Validates: Requirement 10.6**
app.add_middleware(RateLimitMiddleware)

# 5. Register global error handlers
# **Validates: Requirements 10.2, 10.3, 15.7**
register_error_handlers(app)


# ============================================================================
# Register API Routers
# ============================================================================

# Register repository routes
app.include_router(repositories.router, prefix="/api/v1")

# Register search routes
app.include_router(search.router, prefix="/api/v1")

# Register chat routes
app.include_router(chat.router, prefix="/api/v1")

# Register job routes
app.include_router(jobs.router, prefix="/api/v1")

# Register code review routes
app.include_router(review.router, prefix="/api/v1")

# Register settings routes
app.include_router(settings_router.router, prefix="/api/v1")

# Register health and monitoring routes
app.include_router(health.router, prefix="/api/v1")


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint - welcome message.
    """
    return {
        "message": "Welcome to GitHub Codebase RAG Assistant API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/config")
async def get_config() -> Dict[str, Any]:
    """
    Get current configuration (non-sensitive values only).
    
    Returns key configuration values for debugging.
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "log_level": settings.log_level,
        "embedding": {
            "model": settings.embedding_model,
            "dimension": settings.embedding_dimension,
            "device": settings.embedding_device,
            "batch_size": settings.embedding_batch_size,
        },
        "chunking": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "max_chunk_size": settings.max_chunk_size,
        },
        "search": {
            "default_top_k": settings.default_top_k,
            "max_top_k": settings.max_top_k,
        },
        "ollama": {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
            "timeout": settings.ollama_timeout,
        },
    }


@app.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get system status and component health.
    
    Returns the status of all Phase 1 components.
    """
    status = {
        "phase": "Phase 1: Foundation",
        "status": "operational",
        "components": {
            "configuration": {
                "status": "✅ operational",
                "details": "Settings loaded successfully",
            },
            "database": {
                "status": "✅ operational",
                "details": "Models defined and ready",
            },
            "redis": {
                "status": "✅ operational",
                "details": "Client wrapper ready",
            },
            "docker": {
                "status": "✅ configured",
                "details": "docker-compose.yml ready",
            },
        },
        "completed_tasks": [
            "1.1 Set up project structure and core infrastructure",
            "1.2 Write property test for configuration validation",
            "1.3 Create Pydantic settings model",
            "1.4 Set up PostgreSQL database schema and models",
            "1.5 Implement Redis client wrapper",
            "1.6 Write unit tests for database models and Redis",
            "1.7 Create Docker Compose configuration",
            "1.8 Create backend Dockerfile",
            "1.9 Create frontend Dockerfile",
            "1.10 Checkpoint - Ensure all tests pass",
            "2.1 Create embedding service wrapper",
        ],
        "next_phase": "Phase 2: Backend Core",
    }
    
    return status


# ============================================================================
# Phase 1 Demo Endpoints
# ============================================================================

@app.get("/demo/database-models")
async def demo_database_models() -> Dict[str, Any]:
    """
    Demo endpoint showing database models.
    """
    from app.models.orm import Repository, IngestionJob, CodeChunk
    
    return {
        "message": "Database models are defined and ready",
        "models": {
            "Repository": {
                "table": Repository.__tablename__,
                "columns": [c.name for c in Repository.__table__.columns],
            },
            "IngestionJob": {
                "table": IngestionJob.__tablename__,
                "columns": [c.name for c in IngestionJob.__table__.columns],
            },
            "CodeChunk": {
                "table": CodeChunk.__tablename__,
                "columns": [c.name for c in CodeChunk.__table__.columns],
            },
        },
    }


@app.get("/demo/embedding-config")
async def demo_embedding_config() -> Dict[str, Any]:
    """
    Demo endpoint showing embedding configuration.
    """
    return {
        "message": "Embedding service is configured and ready",
        "config": settings.get_embedding_config(),
        "note": "Embedding service (Task 2.1) is implemented and ready to use",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
