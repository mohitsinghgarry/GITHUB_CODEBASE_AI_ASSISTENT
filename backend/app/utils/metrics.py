"""
Prometheus metrics definitions and utilities.

This module provides centralized Prometheus metrics for monitoring the application.
All metrics are defined here and can be imported by other modules.

Requirements:
- 12.1: Track key metrics including request count, response times, error rates, and active Ingestion_Jobs
- 12.2: Expose metrics in Prometheus format for scraping
- 12.6: Track Embedding_Store performance including query latency and storage size
- 12.7: Track LLM_Service metrics including inference time and token usage
"""

from prometheus_client import Counter, Gauge, Histogram, Info

# ============================================================================
# Application Info
# ============================================================================

app_info = Info(
    "app",
    "Application information"
)

# ============================================================================
# HTTP Request Metrics (Requirement 12.1)
# ============================================================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000)
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000)
)

# ============================================================================
# Ingestion Job Metrics (Requirement 12.1)
# ============================================================================

ingestion_jobs_total = Counter(
    "ingestion_jobs_total",
    "Total ingestion jobs",
    ["status"]
)

ingestion_jobs_queue_length = Gauge(
    "ingestion_jobs_queue_length",
    "Number of jobs in the ingestion queue"
)

ingestion_jobs_active = Gauge(
    "ingestion_jobs_active",
    "Number of active ingestion jobs"
)

ingestion_job_duration_seconds = Histogram(
    "ingestion_job_duration_seconds",
    "Ingestion job duration in seconds",
    ["stage"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)

ingestion_job_processing_time_seconds = Histogram(
    "ingestion_job_processing_time_seconds",
    "Total processing time for ingestion jobs in seconds",
    ["repository_id"],
    buckets=(10, 30, 60, 120, 300, 600, 1800, 3600, 7200)
)

ingestion_files_processed_total = Counter(
    "ingestion_files_processed_total",
    "Total files processed during ingestion",
    ["repository_id", "language"]
)

ingestion_chunks_created_total = Counter(
    "ingestion_chunks_created_total",
    "Total chunks created during ingestion",
    ["repository_id"]
)

ingestion_errors_total = Counter(
    "ingestion_errors_total",
    "Total ingestion errors",
    ["stage", "error_type"]
)

# ============================================================================
# Database Metrics
# ============================================================================

database_connections_active = Gauge(
    "database_connections_active",
    "Number of active database connections"
)

database_connections_idle = Gauge(
    "database_connections_idle",
    "Number of idle database connections"
)

database_query_duration_seconds = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

database_queries_total = Counter(
    "database_queries_total",
    "Total database queries",
    ["operation", "status"]
)

# ============================================================================
# Redis Metrics
# ============================================================================

redis_operations_total = Counter(
    "redis_operations_total",
    "Total Redis operations",
    ["operation", "status"]
)

redis_operation_duration_seconds = Histogram(
    "redis_operation_duration_seconds",
    "Redis operation duration in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

redis_connections_active = Gauge(
    "redis_connections_active",
    "Number of active Redis connections"
)

redis_cache_hits_total = Counter(
    "redis_cache_hits_total",
    "Total Redis cache hits",
    ["cache_type"]
)

redis_cache_misses_total = Counter(
    "redis_cache_misses_total",
    "Total Redis cache misses",
    ["cache_type"]
)

# ============================================================================
# Vector Store Metrics (FAISS) (Requirement 12.6)
# ============================================================================

vector_search_duration_seconds = Histogram(
    "vector_search_duration_seconds",
    "Vector search duration in seconds",
    ["repository_id"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

vector_search_total = Counter(
    "vector_search_total",
    "Total vector searches",
    ["repository_id", "status"]
)

vector_index_size_bytes = Gauge(
    "vector_index_size_bytes",
    "Size of vector index in bytes",
    ["repository_id"]
)

vector_chunks_total = Gauge(
    "vector_chunks_total",
    "Total number of indexed chunks",
    ["repository_id"]
)

vector_index_load_duration_seconds = Histogram(
    "vector_index_load_duration_seconds",
    "Vector index load duration in seconds",
    ["repository_id"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

vector_index_save_duration_seconds = Histogram(
    "vector_index_save_duration_seconds",
    "Vector index save duration in seconds",
    ["repository_id"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

faiss_query_latency_seconds = Histogram(
    "faiss_query_latency_seconds",
    "FAISS query latency in seconds",
    ["repository_id", "top_k"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# ============================================================================
# Embedding Service Metrics
# ============================================================================

embedding_generation_duration_seconds = Histogram(
    "embedding_generation_duration_seconds",
    "Embedding generation duration in seconds",
    ["batch_size"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

embedding_generation_total = Counter(
    "embedding_generation_total",
    "Total embeddings generated",
    ["status"]
)

embedding_batch_size = Histogram(
    "embedding_batch_size",
    "Embedding batch size",
    buckets=(1, 5, 10, 20, 32, 50, 64, 100, 128)
)

# ============================================================================
# LLM Service Metrics (Ollama) (Requirement 12.7)
# ============================================================================

llm_inference_duration_seconds = Histogram(
    "llm_inference_duration_seconds",
    "LLM inference duration in seconds",
    ["model"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0)
)

llm_tokens_generated_total = Counter(
    "llm_tokens_generated_total",
    "Total tokens generated by LLM",
    ["model"]
)

llm_tokens_per_second = Histogram(
    "llm_tokens_per_second",
    "LLM tokens generated per second",
    ["model"],
    buckets=(1, 5, 10, 20, 30, 50, 75, 100, 150, 200)
)

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status"]
)

llm_prompt_tokens_total = Counter(
    "llm_prompt_tokens_total",
    "Total prompt tokens sent to LLM",
    ["model"]
)

llm_completion_tokens_total = Counter(
    "llm_completion_tokens_total",
    "Total completion tokens generated by LLM",
    ["model"]
)

ollama_inference_time_seconds = Histogram(
    "ollama_inference_time_seconds",
    "Ollama inference time in seconds",
    ["model", "operation"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0, 60.0)
)

# ============================================================================
# Search Metrics
# ============================================================================

search_requests_total = Counter(
    "search_requests_total",
    "Total search requests",
    ["search_type", "status"]
)

search_duration_seconds = Histogram(
    "search_duration_seconds",
    "Search duration in seconds",
    ["search_type"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

search_results_count = Histogram(
    "search_results_count",
    "Number of search results returned",
    ["search_type"],
    buckets=(0, 1, 5, 10, 20, 50, 100)
)

# ============================================================================
# Chat Session Metrics
# ============================================================================

chat_sessions_active = Gauge(
    "chat_sessions_active",
    "Number of active chat sessions"
)

chat_messages_total = Counter(
    "chat_messages_total",
    "Total chat messages",
    ["role"]
)

chat_session_duration_seconds = Histogram(
    "chat_session_duration_seconds",
    "Chat session duration in seconds",
    buckets=(60, 300, 600, 1800, 3600, 7200)
)

# ============================================================================
# System Health Metrics
# ============================================================================

system_health_status = Gauge(
    "system_health_status",
    "System health status (1=healthy, 0=unhealthy)",
    ["component"]
)

system_uptime_seconds = Gauge(
    "system_uptime_seconds",
    "System uptime in seconds"
)

# ============================================================================
# Error Metrics (Requirement 12.1)
# ============================================================================

errors_total = Counter(
    "errors_total",
    "Total errors",
    ["type", "component"]
)

error_rate = Gauge(
    "error_rate",
    "Error rate (errors per second)",
    ["component"]
)

# ============================================================================
# Repository Metrics
# ============================================================================

repositories_total = Gauge(
    "repositories_total",
    "Total number of repositories",
    ["status"]
)

repository_size_bytes = Gauge(
    "repository_size_bytes",
    "Repository size in bytes",
    ["repository_id"]
)

repository_files_total = Gauge(
    "repository_files_total",
    "Total files in repository",
    ["repository_id"]
)

# ============================================================================
# Utility Functions
# ============================================================================

def init_metrics(app_name: str, version: str, environment: str):
    """
    Initialize application metrics with metadata.
    
    Args:
        app_name: Application name
        version: Application version
        environment: Environment (development, staging, production)
    """
    app_info.info({
        "name": app_name,
        "version": version,
        "environment": environment,
    })


def track_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """
    Track HTTP request metrics.
    
    Args:
        method: HTTP method
        endpoint: Request endpoint
        status_code: Response status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def track_ingestion_job_metrics(status: str, stage: str = None, duration: float = None):
    """
    Track ingestion job metrics.
    
    Args:
        status: Job status (pending, running, completed, failed)
        stage: Job stage (clone, read, chunk, embed, store)
        duration: Job duration in seconds
    """
    ingestion_jobs_total.labels(status=status).inc()
    
    if stage and duration:
        ingestion_job_duration_seconds.labels(stage=stage).observe(duration)


def track_vector_search_metrics(repository_id: str, duration: float, status: str = "success"):
    """
    Track vector search metrics.
    
    Args:
        repository_id: Repository ID
        duration: Search duration in seconds
        status: Search status (success, error)
    """
    vector_search_duration_seconds.labels(repository_id=repository_id).observe(duration)
    vector_search_total.labels(repository_id=repository_id, status=status).inc()


def track_llm_metrics(model: str, duration: float, tokens: int = None, status: str = "success"):
    """
    Track LLM inference metrics.
    
    Args:
        model: Model name
        duration: Inference duration in seconds
        tokens: Number of tokens generated
        status: Request status (success, error)
    """
    llm_inference_duration_seconds.labels(model=model).observe(duration)
    llm_requests_total.labels(model=model, status=status).inc()
    
    if tokens:
        llm_tokens_generated_total.labels(model=model).inc(tokens)
        tokens_per_second = tokens / duration if duration > 0 else 0
        llm_tokens_per_second.labels(model=model).observe(tokens_per_second)


def track_error(error_type: str, component: str):
    """
    Track error occurrence.
    
    Args:
        error_type: Type of error
        component: Component where error occurred
    """
    errors_total.labels(type=error_type, component=component).inc()
