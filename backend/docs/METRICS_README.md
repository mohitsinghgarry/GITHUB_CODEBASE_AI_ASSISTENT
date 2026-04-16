# Prometheus Metrics Implementation

## Overview

This document describes the Prometheus metrics implementation for the GitHub Codebase RAG Assistant. The implementation satisfies requirements 12.1, 12.2, 12.6, and 12.7.

## Architecture

### Components

1. **Metrics Definitions** (`app/utils/metrics.py`)
   - Centralized metrics definitions
   - Helper functions for common tracking patterns
   - Prevents duplicate metric definitions

2. **Metrics Middleware** (`app/middleware/metrics_middleware.py`)
   - Automatic HTTP request tracking
   - Path normalization to prevent high cardinality
   - Request/response size tracking

3. **Health Endpoint** (`app/api/routes/health.py`)
   - Exposes `/api/v1/metrics` endpoint
   - Prometheus-compatible format
   - System health status tracking

## Metrics Categories

### 1. HTTP Request Metrics (Requirement 12.1)

**Automatically tracked by MetricsMiddleware:**

- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Current in-progress requests
- `http_request_size_bytes` - Request size histogram
- `http_response_size_bytes` - Response size histogram

### 2. Ingestion Job Metrics (Requirement 12.1)

**Track ingestion pipeline performance:**

- `ingestion_jobs_total` - Total jobs by status
- `ingestion_jobs_queue_length` - Jobs waiting in queue
- `ingestion_jobs_active` - Currently running jobs
- `ingestion_job_duration_seconds` - Duration by stage
- `ingestion_job_processing_time_seconds` - Total processing time
- `ingestion_files_processed_total` - Files processed by language
- `ingestion_chunks_created_total` - Chunks created per repository
- `ingestion_errors_total` - Errors by stage and type

### 3. Vector Store (FAISS) Metrics (Requirement 12.6)

**Track FAISS performance:**

- `vector_search_duration_seconds` - Search duration by repository
- `vector_search_total` - Total searches by status
- `vector_index_size_bytes` - Index size per repository
- `vector_chunks_total` - Chunks indexed per repository
- `vector_index_load_duration_seconds` - Index load time
- `vector_index_save_duration_seconds` - Index save time
- `faiss_query_latency_seconds` - Query latency by repository and top-K

### 4. LLM (Ollama) Metrics (Requirement 12.7)

**Track LLM inference:**

- `llm_inference_duration_seconds` - Inference duration by model
- `llm_tokens_generated_total` - Total tokens generated
- `llm_tokens_per_second` - Token generation rate
- `llm_requests_total` - Total requests by model and status
- `llm_prompt_tokens_total` - Prompt tokens sent
- `llm_completion_tokens_total` - Completion tokens generated
- `ollama_inference_time_seconds` - Ollama-specific inference time

### 5. Database Metrics

- `database_connections_active` - Active connections
- `database_connections_idle` - Idle connections
- `database_query_duration_seconds` - Query duration by operation
- `database_queries_total` - Total queries by operation and status

### 6. Redis Metrics

- `redis_operations_total` - Total operations by type and status
- `redis_operation_duration_seconds` - Operation duration
- `redis_connections_active` - Active connections
- `redis_cache_hits_total` - Cache hits by type
- `redis_cache_misses_total` - Cache misses by type

### 7. Search Metrics

- `search_requests_total` - Total searches by type and status
- `search_duration_seconds` - Search duration by type
- `search_results_count` - Number of results returned

### 8. Error Metrics (Requirement 12.1)

- `errors_total` - Total errors by type and component
- `error_rate` - Error rate per second

## Usage

### Automatic Tracking

HTTP requests are automatically tracked by the `MetricsMiddleware`. No manual instrumentation needed.

### Manual Tracking

For other metrics, use the helper functions:

```python
from app.utils.metrics import (
    track_ingestion_job_metrics,
    track_vector_search_metrics,
    track_llm_metrics,
    track_error,
)

# Track ingestion job
track_ingestion_job_metrics(
    status="completed",
    stage="embed",
    duration=120.5
)

# Track FAISS query
track_vector_search_metrics(
    repository_id=str(repo_id),
    duration=0.05,
    status="success"
)

# Track LLM inference
track_llm_metrics(
    model="codellama:7b",
    duration=5.2,
    tokens=150,
    status="success"
)

# Track error
track_error(
    error_type="timeout",
    component="ollama"
)
```

## Accessing Metrics

### Local Development

```bash
# Start the application
cd backend
uvicorn app.main:app --reload

# Access metrics endpoint
curl http://localhost:8000/api/v1/metrics
```

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'github-rag-assistant'
    scrape_interval: 15s
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/v1/metrics'
```

### Docker Compose

Metrics are automatically exposed when running with Docker Compose:

```bash
docker-compose up -d
```

Access metrics at: `http://localhost:8000/api/v1/metrics`

## Grafana Dashboards

### Example Queries

**Request Rate:**
```promql
rate(http_requests_total[5m])
```

**Request Duration (p95):**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Error Rate:**
```promql
rate(errors_total[5m])
```

**Active Ingestion Jobs:**
```promql
ingestion_jobs_active
```

**Ingestion Queue Length:**
```promql
ingestion_jobs_queue_length
```

**FAISS Query Latency (p99):**
```promql
histogram_quantile(0.99, rate(faiss_query_latency_seconds_bucket[5m]))
```

**Ollama Inference Time (avg):**
```promql
rate(ollama_inference_time_seconds_sum[5m]) / rate(ollama_inference_time_seconds_count[5m])
```

**Tokens per Second:**
```promql
rate(llm_tokens_generated_total[5m])
```

**Cache Hit Rate:**
```promql
rate(redis_cache_hits_total[5m]) / (rate(redis_cache_hits_total[5m]) + rate(redis_cache_misses_total[5m]))
```

## Testing

Run metrics tests:

```bash
cd backend
pytest tests/unit/test_metrics.py -v
```

## Requirements Validation

### ✅ Requirement 12.1: Track key metrics

- HTTP request count, latency, error rate ✓
- Ingestion job queue length and processing time ✓
- Active jobs tracking ✓

### ✅ Requirement 12.2: Expose metrics in Prometheus format

- `/api/v1/metrics` endpoint ✓
- Prometheus-compatible format ✓
- Scrape-ready configuration ✓

### ✅ Requirement 12.6: Track FAISS performance

- Query latency by repository ✓
- Storage size per repository ✓
- Index load/save duration ✓

### ✅ Requirement 12.7: Track LLM metrics

- Inference time by model ✓
- Token usage (prompt + completion) ✓
- Tokens per second ✓

## Best Practices

1. **Low Cardinality**: Keep label values limited to prevent metric explosion
2. **Path Normalization**: Dynamic IDs are replaced with `{id}` placeholder
3. **Consistent Naming**: Follow Prometheus conventions (`_total`, `_seconds`, `_bytes`)
4. **Helper Functions**: Use provided helpers for common patterns
5. **Error Tracking**: Always track errors with appropriate labels

## Troubleshooting

### Metrics not appearing

1. Check if metrics are enabled:
   ```python
   settings.enable_metrics  # Should be True
   ```

2. Verify middleware is registered in `app/main.py`

3. Check Prometheus scrape configuration

### High cardinality warning

- Review label values
- Ensure path normalization is working
- Avoid dynamic labels (user IDs, timestamps)

## Future Enhancements

- [ ] Add custom Grafana dashboard JSON
- [ ] Add alerting rules for Prometheus
- [ ] Add metrics for embedding generation
- [ ] Add metrics for chunking performance
- [ ] Add metrics for chat sessions
