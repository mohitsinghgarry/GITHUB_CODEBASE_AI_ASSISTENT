# Prometheus Metrics Usage Guide

This document explains how to use Prometheus metrics throughout the application.

## Overview

All Prometheus metrics are centrally defined in `app/utils/metrics.py`. This ensures consistency and prevents duplicate metric definitions.

## Available Metrics

### HTTP Request Metrics

```python
from app.utils.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
)

# These are automatically tracked by MetricsMiddleware
# No manual tracking needed in route handlers
```

### Ingestion Job Metrics

```python
from app.utils.metrics import (
    ingestion_jobs_total,
    ingestion_jobs_queue_length,
    ingestion_jobs_active,
    ingestion_job_duration_seconds,
    ingestion_job_processing_time_seconds,
    ingestion_files_processed_total,
    ingestion_chunks_created_total,
    ingestion_errors_total,
)

# Example: Track job start
ingestion_jobs_total.labels(status="running").inc()
ingestion_jobs_active.inc()

# Example: Track job completion
import time
start_time = time.time()
# ... do work ...
duration = time.time() - start_time
ingestion_job_duration_seconds.labels(stage="clone").observe(duration)
ingestion_jobs_total.labels(status="completed").inc()
ingestion_jobs_active.dec()

# Example: Track files processed
ingestion_files_processed_total.labels(
    repository_id=str(repo_id),
    language="python"
).inc()

# Example: Track chunks created
ingestion_chunks_created_total.labels(
    repository_id=str(repo_id)
).inc(chunk_count)

# Example: Track errors
ingestion_errors_total.labels(
    stage="embed",
    error_type="timeout"
).inc()
```

### Vector Store (FAISS) Metrics

```python
from app.utils.metrics import (
    vector_search_duration_seconds,
    vector_search_total,
    vector_index_size_bytes,
    vector_chunks_total,
    faiss_query_latency_seconds,
)

# Example: Track FAISS query
import time
start_time = time.time()
results = faiss_index.search(query_embedding, k=10)
duration = time.time() - start_time

faiss_query_latency_seconds.labels(
    repository_id=str(repo_id),
    top_k="10"
).observe(duration)

vector_search_total.labels(
    repository_id=str(repo_id),
    status="success"
).inc()

# Example: Update index size
import os
index_path = f"indices/{repo_id}.faiss"
if os.path.exists(index_path):
    size_bytes = os.path.getsize(index_path)
    vector_index_size_bytes.labels(
        repository_id=str(repo_id)
    ).set(size_bytes)

# Example: Update chunk count
vector_chunks_total.labels(
    repository_id=str(repo_id)
).set(total_chunks)
```

### LLM (Ollama) Metrics

```python
from app.utils.metrics import (
    llm_inference_duration_seconds,
    llm_tokens_generated_total,
    llm_tokens_per_second,
    llm_requests_total,
    ollama_inference_time_seconds,
)

# Example: Track LLM inference
import time
start_time = time.time()
response = await ollama_client.generate(prompt, model="codellama:7b")
duration = time.time() - start_time

ollama_inference_time_seconds.labels(
    model="codellama:7b",
    operation="generate"
).observe(duration)

llm_requests_total.labels(
    model="codellama:7b",
    status="success"
).inc()

# If token count is available
if response.get("tokens"):
    token_count = response["tokens"]
    llm_tokens_generated_total.labels(
        model="codellama:7b"
    ).inc(token_count)
    
    tokens_per_sec = token_count / duration if duration > 0 else 0
    llm_tokens_per_second.labels(
        model="codellama:7b"
    ).observe(tokens_per_sec)
```

### Database Metrics

```python
from app.utils.metrics import (
    database_query_duration_seconds,
    database_queries_total,
)

# Example: Track database query
import time
start_time = time.time()
result = await db.execute(query)
duration = time.time() - start_time

database_query_duration_seconds.labels(
    operation="select_repositories"
).observe(duration)

database_queries_total.labels(
    operation="select_repositories",
    status="success"
).inc()
```

### Redis Metrics

```python
from app.utils.metrics import (
    redis_operations_total,
    redis_operation_duration_seconds,
    redis_cache_hits_total,
    redis_cache_misses_total,
)

# Example: Track Redis operation
import time
start_time = time.time()
value = await redis_client.get(key)
duration = time.time() - start_time

redis_operation_duration_seconds.labels(
    operation="get"
).observe(duration)

redis_operations_total.labels(
    operation="get",
    status="success"
).inc()

# Track cache hit/miss
if value is not None:
    redis_cache_hits_total.labels(cache_type="session").inc()
else:
    redis_cache_misses_total.labels(cache_type="session").inc()
```

### Search Metrics

```python
from app.utils.metrics import (
    search_requests_total,
    search_duration_seconds,
    search_results_count,
)

# Example: Track search request
import time
start_time = time.time()
results = await search_service.hybrid_search(query, repo_id)
duration = time.time() - start_time

search_duration_seconds.labels(
    search_type="hybrid"
).observe(duration)

search_requests_total.labels(
    search_type="hybrid",
    status="success"
).inc()

search_results_count.labels(
    search_type="hybrid"
).observe(len(results))
```

### Error Tracking

```python
from app.utils.metrics import errors_total, track_error

# Example: Track error
try:
    # ... some operation ...
    pass
except TimeoutError as e:
    track_error(error_type="timeout", component="ollama")
    raise
except Exception as e:
    track_error(error_type=type(e).__name__, component="ingestion")
    raise
```

## Helper Functions

The `app/utils/metrics.py` module provides helper functions for common metric tracking patterns:

```python
from app.utils.metrics import (
    track_request_metrics,
    track_ingestion_job_metrics,
    track_vector_search_metrics,
    track_llm_metrics,
    track_error,
)

# Track HTTP request (automatically done by middleware)
track_request_metrics(
    method="POST",
    endpoint="/api/v1/repositories",
    status_code=201,
    duration=0.5
)

# Track ingestion job
track_ingestion_job_metrics(
    status="completed",
    stage="embed",
    duration=120.5
)

# Track vector search
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
    error_type="connection_error",
    component="database"
)
```

## Viewing Metrics

### Local Development

1. Start the application:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Access metrics endpoint:
   ```
   http://localhost:8000/api/v1/metrics
   ```

### Prometheus Integration

Add this scrape config to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'github-rag-assistant'
    scrape_interval: 15s
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/v1/metrics'
```

### Grafana Dashboards

Example queries for Grafana:

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

## Best Practices

1. **Use Labels Wisely**: Keep label cardinality low. Don't use user IDs or timestamps as labels.

2. **Normalize Paths**: Use path normalization to avoid high cardinality (e.g., `/repos/{id}` instead of `/repos/123`).

3. **Track Duration**: Always use histograms for duration metrics, not gauges.

4. **Increment Counters**: Use `.inc()` for counters, `.set()` for gauges, `.observe()` for histograms.

5. **Error Handling**: Always track errors with appropriate labels.

6. **Consistent Naming**: Follow Prometheus naming conventions:
   - Use `_total` suffix for counters
   - Use `_seconds` suffix for durations
   - Use `_bytes` suffix for sizes

7. **Document Metrics**: Add docstrings to custom metrics explaining what they track.

## Testing Metrics

```python
# In tests, you can check if metrics are being tracked
from prometheus_client import REGISTRY

def test_ingestion_metrics():
    # Get metric value before
    before = REGISTRY.get_sample_value(
        'ingestion_jobs_total',
        labels={'status': 'completed'}
    ) or 0
    
    # Perform operation
    await ingestion_service.start_ingestion(repo_url)
    
    # Get metric value after
    after = REGISTRY.get_sample_value(
        'ingestion_jobs_total',
        labels={'status': 'completed'}
    ) or 0
    
    # Assert metric was incremented
    assert after > before
```

## Troubleshooting

### Metrics Not Appearing

1. Check if metrics are enabled in config:
   ```python
   settings.enable_metrics  # Should be True
   ```

2. Verify middleware is registered:
   ```python
   # In app/main.py
   app.add_middleware(MetricsMiddleware)
   ```

3. Check Prometheus scrape config and target health.

### High Cardinality Warning

If you see warnings about high cardinality:
- Review label values
- Use path normalization
- Avoid dynamic labels (user IDs, timestamps, etc.)
- Consider aggregating metrics

### Missing Labels

If labels are missing:
- Ensure all label values are strings
- Check for None values (convert to "unknown")
- Verify label names match metric definition
