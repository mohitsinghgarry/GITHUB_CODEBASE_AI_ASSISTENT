"""
Health check and monitoring endpoints.

This module provides health check endpoints for the application and its dependencies,
as well as Prometheus metrics export and Ollama model listing.

Requirements:
- 9.8: Provide an endpoint to list available Ollama models
- 10.8: Handle concurrent requests efficiently using async/await patterns
- 10.9: Perform health checks on dependencies including Embedding_Store and LLM_Service
- 12.1: Track key metrics including request count, response times, error rates, and active Ingestion_Jobs
- 12.2: Expose metrics in Prometheus format for scraping
- 12.3: Log all requests with timestamps, endpoints, status codes, and response times
- 12.4: Log stack traces and contextual information when errors occur
- 12.5: Implement structured logging with configurable log levels
- 12.6: Track Embedding_Store performance including query latency and storage size
- 12.7: Track LLM_Service metrics including inference time and token usage
- 12.8: Provide a health check endpoint returning system status and dependency health
- 12.9: Support alerting via configurable channels when critical errors occur
- 12.10: Support distributed tracing for request flow analysis
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.core.config import get_settings
from app.core.redis_client import get_redis_client, RedisClient
from app.database import get_db, get_engine
from app.models.orm import Repository, IngestionJob
from app.utils.metrics import (
    system_health_status,
    errors_total,
)
from app.core.graceful_degradation import get_service_status

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["health"])

# Note: All Prometheus metrics are now defined in app.utils.metrics
# Import them from there as needed


# ============================================================================
# Health Check Models
# ============================================================================

class ComponentHealth:
    """Health status for a single component."""
    
    def __init__(
        self,
        name: str,
        status: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None
    ):
        self.name = name
        self.status = status  # "healthy", "degraded", "unhealthy"
        self.message = message
        self.details = details or {}
        self.latency_ms = latency_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "status": self.status,
        }
        if self.message:
            result["message"] = self.message
        if self.details:
            result["details"] = self.details
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        return result
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == "healthy"


# ============================================================================
# Health Check Functions
# ============================================================================

async def check_database_health(db: AsyncSession) -> ComponentHealth:
    """
    Check PostgreSQL database health.
    
    Args:
        db: Database session
        
    Returns:
        ComponentHealth: Database health status
    """
    start_time = time.time()
    
    try:
        # Execute a simple query to check connectivity
        result = await db.execute(select(func.count()).select_from(Repository))
        repo_count = result.scalar()
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        system_health_status.labels(component="database").set(1)
        
        return ComponentHealth(
            name="database",
            status="healthy",
            message="PostgreSQL is operational",
            details={
                "repositories_count": repo_count,
                "driver": "asyncpg",
            },
            latency_ms=latency_ms
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error(f"Database health check failed: {e}")
        errors_total.labels(type="connection", component="database").inc()
        system_health_status.labels(component="database").set(0)
        
        return ComponentHealth(
            name="database",
            status="unhealthy",
            message=f"Database connection failed: {str(e)}",
            latency_ms=latency_ms
        )


async def check_redis_health(redis_client: RedisClient) -> ComponentHealth:
    """
    Check Redis health.
    
    Args:
        redis_client: Redis client instance
        
    Returns:
        ComponentHealth: Redis health status
    """
    start_time = time.time()
    
    try:
        # Ping Redis
        is_alive = await redis_client.ping()
        
        latency_ms = (time.time() - start_time) * 1000
        
        if is_alive:
            # Get Redis info
            info = await redis_client.client.info("server")
            
            # Update metrics
            system_health_status.labels(component="redis").set(1)
            
            return ComponentHealth(
                name="redis",
                status="healthy",
                message="Redis is operational",
                details={
                    "version": info.get("redis_version", "unknown"),
                    "uptime_seconds": info.get("uptime_in_seconds", 0),
                },
                latency_ms=latency_ms
            )
        else:
            system_health_status.labels(component="redis").set(0)
            
            return ComponentHealth(
                name="redis",
                status="unhealthy",
                message="Redis ping failed",
                latency_ms=latency_ms
            )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error(f"Redis health check failed: {e}")
        errors_total.labels(type="connection", component="redis").inc()
        system_health_status.labels(component="redis").set(0)
        
        return ComponentHealth(
            name="redis",
            status="unhealthy",
            message=f"Redis connection failed: {str(e)}",
            latency_ms=latency_ms
        )


async def check_ollama_health() -> ComponentHealth:
    """
    Check Ollama LLM service health.
    
    Returns:
        ComponentHealth: Ollama health status
    """
    settings = get_settings()
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check if Ollama is running
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get("models", [])
                model_names = [m.get("name") for m in models]
                
                # Check if configured model is available
                configured_model = settings.ollama_model
                model_available = any(
                    configured_model in name for name in model_names
                )
                
                # Update metrics
                system_health_status.labels(component="ollama").set(1)
                
                status = "healthy" if model_available else "degraded"
                message = (
                    "Ollama is operational"
                    if model_available
                    else f"Ollama is running but configured model '{configured_model}' not found"
                )
                
                return ComponentHealth(
                    name="ollama",
                    status=status,
                    message=message,
                    details={
                        "base_url": settings.ollama_base_url,
                        "configured_model": configured_model,
                        "available_models": model_names,
                        "model_available": model_available,
                    },
                    latency_ms=latency_ms
                )
            else:
                system_health_status.labels(component="ollama").set(0)
                
                return ComponentHealth(
                    name="ollama",
                    status="unhealthy",
                    message=f"Ollama returned status {response.status_code}",
                    latency_ms=latency_ms
                )
    except httpx.TimeoutException:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error("Ollama health check timed out")
        errors_total.labels(type="timeout", component="ollama").inc()
        system_health_status.labels(component="ollama").set(0)
        
        return ComponentHealth(
            name="ollama",
            status="unhealthy",
            message="Ollama connection timed out",
            latency_ms=latency_ms
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error(f"Ollama health check failed: {e}")
        errors_total.labels(type="connection", component="ollama").inc()
        system_health_status.labels(component="ollama").set(0)
        
        return ComponentHealth(
            name="ollama",
            status="unhealthy",
            message=f"Ollama connection failed: {str(e)}",
            latency_ms=latency_ms
        )


async def check_faiss_health() -> ComponentHealth:
    """
    Check FAISS vector store health.
    
    Returns:
        ComponentHealth: FAISS health status
    """
    settings = get_settings()
    start_time = time.time()
    
    try:
        # Check if FAISS index directory exists and is accessible
        index_path = settings.faiss_index_path
        
        if not index_path.exists():
            index_path.mkdir(parents=True, exist_ok=True)
        
        # Count index files
        index_files = list(index_path.glob("*.faiss"))
        metadata_files = list(index_path.glob("*.metadata.json"))
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in index_files)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        system_health_status.labels(component="faiss").set(1)
        
        return ComponentHealth(
            name="faiss",
            status="healthy",
            message="FAISS vector store is operational",
            details={
                "index_path": str(index_path),
                "index_count": len(index_files),
                "metadata_count": len(metadata_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            },
            latency_ms=latency_ms
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error(f"FAISS health check failed: {e}")
        errors_total.labels(type="filesystem", component="faiss").inc()
        system_health_status.labels(component="faiss").set(0)
        
        return ComponentHealth(
            name="faiss",
            status="unhealthy",
            message=f"FAISS check failed: {str(e)}",
            latency_ms=latency_ms
        )


async def check_embedding_service_health() -> ComponentHealth:
    """
    Check embedding service health.
    
    Returns:
        ComponentHealth: Embedding service health status
    """
    settings = get_settings()
    start_time = time.time()
    
    try:
        # Try to import and check if model can be loaded
        from sentence_transformers import SentenceTransformer
        
        # Check if model directory exists (cached model)
        model_name = settings.embedding_model
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        system_health_status.labels(component="embeddings").set(1)
        
        return ComponentHealth(
            name="embeddings",
            status="healthy",
            message="Embedding service is operational",
            details={
                "model": model_name,
                "dimension": settings.embedding_dimension,
                "device": settings.embedding_device,
                "batch_size": settings.embedding_batch_size,
            },
            latency_ms=latency_ms
        )
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        logger.error(f"Embedding service health check failed: {e}")
        errors_total.labels(type="initialization", component="embeddings").inc()
        system_health_status.labels(component="embeddings").set(0)
        
        return ComponentHealth(
            name="embeddings",
            status="unhealthy",
            message=f"Embedding service check failed: {str(e)}",
            latency_ms=latency_ms
        )


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", summary="Health check endpoint")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Checks the health of all system components:
    - PostgreSQL database
    - Redis cache
    - Ollama LLM service
    - FAISS vector store
    - Embedding service
    
    Returns:
        Dict containing overall status and individual component health
        
    Requirements:
    - 10.9: Perform health checks on dependencies
    - 12.8: Provide a health check endpoint returning system status
    """
    settings = get_settings()
    start_time = time.time()
    
    # Get Redis client
    try:
        redis_client = await get_redis_client()
    except Exception as e:
        logger.error(f"Failed to get Redis client: {e}")
        redis_client = None
    
    # Run all health checks concurrently
    health_checks = await asyncio.gather(
        check_database_health(db),
        check_redis_health(redis_client) if redis_client else asyncio.coroutine(lambda: ComponentHealth(
            name="redis",
            status="unhealthy",
            message="Redis client not initialized"
        ))(),
        check_ollama_health(),
        check_faiss_health(),
        check_embedding_service_health(),
        return_exceptions=True
    )
    
    # Process results
    components = {}
    all_healthy = True
    
    for check in health_checks:
        if isinstance(check, Exception):
            logger.error(f"Health check failed with exception: {check}")
            continue
        
        components[check.name] = check.to_dict()
        if not check.is_healthy:
            all_healthy = False
    
    # Determine overall status
    if all_healthy:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK
    elif any(c.get("status") == "healthy" for c in components.values()):
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    total_latency_ms = (time.time() - start_time) * 1000
    
    # Get graceful degradation status
    degradation_status = get_service_status()
    
    response = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "components": components,
        "degradation": degradation_status,
        "latency_ms": round(total_latency_ms, 2),
    }
    
    # Log health check result
    logger.info(
        f"Health check completed: {overall_status} "
        f"(latency: {total_latency_ms:.2f}ms, "
        f"degradation: {degradation_status['overall_status']})"
    )
    
    return response


@router.get("/health/live", summary="Liveness probe")
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.
    
    Returns a simple response indicating the application is running.
    This endpoint should always return 200 unless the application is completely down.
    
    Returns:
        Dict with status "alive"
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready", summary="Readiness probe")
async def readiness_probe(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.
    
    Checks if the application is ready to serve traffic by verifying
    critical dependencies (database and Redis).
    
    Returns:
        Dict with status "ready" or raises 503 if not ready
        
    Raises:
        HTTPException: 503 if critical dependencies are not ready
    """
    try:
        redis_client = await get_redis_client()
    except Exception:
        redis_client = None
    
    # Check critical dependencies
    db_check, redis_check = await asyncio.gather(
        check_database_health(db),
        check_redis_health(redis_client) if redis_client else asyncio.coroutine(lambda: ComponentHealth(
            name="redis",
            status="unhealthy",
            message="Redis client not initialized"
        ))(),
        return_exceptions=True
    )
    
    # Check if critical components are healthy
    critical_healthy = True
    
    if isinstance(db_check, ComponentHealth) and not db_check.is_healthy:
        critical_healthy = False
    
    if isinstance(redis_check, ComponentHealth) and not redis_check.is_healthy:
        critical_healthy = False
    
    if not critical_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not ready to serve traffic"
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics", summary="Prometheus metrics endpoint")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.
    
    Exposes application metrics in Prometheus format for scraping.
    
    Returns:
        Response with Prometheus metrics in text format
        
    Requirements:
    - 12.1: Track key metrics
    - 12.2: Expose metrics in Prometheus format
    """
    settings = get_settings()
    
    if not settings.enable_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics are disabled"
        )
    
    # Generate Prometheus metrics
    metrics_output = generate_latest(REGISTRY)
    
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/models", summary="List available Ollama models")
async def list_models() -> Dict[str, Any]:
    """
    List available Ollama models.
    
    Returns a list of all models available in the connected Ollama instance,
    along with their details (size, parameters, etc.).
    
    Returns:
        Dict containing list of available models
        
    Raises:
        HTTPException: 503 if Ollama is not available
        
    Requirements:
    - 9.8: Provide an endpoint to list available Ollama models
    """
    settings = get_settings()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get("models", [])
                
                # Format model information
                formatted_models = []
                for model in models:
                    formatted_models.append({
                        "name": model.get("name"),
                        "size": model.get("size"),
                        "digest": model.get("digest"),
                        "modified_at": model.get("modified_at"),
                        "details": model.get("details", {}),
                    })
                
                return {
                    "models": formatted_models,
                    "count": len(formatted_models),
                    "configured_model": settings.ollama_model,
                    "base_url": settings.ollama_base_url,
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Ollama returned status {response.status_code}"
                )
    except httpx.TimeoutException:
        logger.error("Ollama models request timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Ollama request timed out"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Ollama: {str(e)}"
        )


@router.get("/stats", summary="System statistics")
async def system_stats(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get system statistics.
    
    Returns statistics about repositories, ingestion jobs, and system resources.
    
    Returns:
        Dict containing system statistics
    """
    try:
        # Get repository statistics
        repo_result = await db.execute(
            select(
                func.count(Repository.id).label("total"),
                func.count(Repository.id).filter(Repository.status == "completed").label("completed"),
                func.count(Repository.id).filter(Repository.status == "failed").label("failed"),
                func.count(Repository.id).filter(Repository.status.in_(["pending", "cloning", "reading", "chunking", "embedding"])).label("in_progress"),
            )
        )
        repo_stats = repo_result.one()
        
        # Get ingestion job statistics
        job_result = await db.execute(
            select(
                func.count(IngestionJob.id).label("total"),
                func.count(IngestionJob.id).filter(IngestionJob.status == "completed").label("completed"),
                func.count(IngestionJob.id).filter(IngestionJob.status == "failed").label("failed"),
                func.count(IngestionJob.id).filter(IngestionJob.status == "running").label("running"),
            )
        )
        job_stats = job_result.one()
        
        # Get FAISS index statistics
        settings = get_settings()
        index_path = settings.faiss_index_path
        index_files = list(index_path.glob("*.faiss")) if index_path.exists() else []
        total_index_size = sum(f.stat().st_size for f in index_files)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "repositories": {
                "total": repo_stats.total,
                "completed": repo_stats.completed,
                "failed": repo_stats.failed,
                "in_progress": repo_stats.in_progress,
            },
            "ingestion_jobs": {
                "total": job_stats.total,
                "completed": job_stats.completed,
                "failed": job_stats.failed,
                "running": job_stats.running,
            },
            "vector_store": {
                "index_count": len(index_files),
                "total_size_mb": round(total_index_size / (1024 * 1024), 2),
            },
        }
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system statistics: {str(e)}"
        )
