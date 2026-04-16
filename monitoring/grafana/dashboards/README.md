# Grafana Dashboards

This directory contains Grafana dashboard configurations for the GitHub Codebase RAG Assistant.

## Dashboard Files

Place your dashboard JSON files in this directory. They will be automatically loaded by Grafana on startup.

## Creating Dashboards

1. Access Grafana at http://localhost:3001
2. Login with admin/admin (or your configured password)
3. Create dashboards using the UI
4. Export dashboards as JSON
5. Place JSON files in this directory

## Recommended Dashboards

### System Overview Dashboard

Metrics to include:
- Total repositories indexed
- Active ingestion jobs
- API request rate
- Error rate
- Response time (p50, p95, p99)

### API Performance Dashboard

Metrics to include:
- Request count by endpoint
- Request duration by endpoint
- Error rate by endpoint
- Rate limit hits
- Active sessions

### Ingestion Pipeline Dashboard

Metrics to include:
- Jobs in queue
- Jobs processing
- Jobs completed/failed
- Average processing time per stage
- Chunks processed per minute

### LLM Performance Dashboard

Metrics to include:
- Ollama inference time
- FAISS query latency
- Embedding generation time
- Context window utilization
- Token usage

### Resource Usage Dashboard

Metrics to include:
- CPU usage per service
- Memory usage per service
- Disk I/O
- Network I/O
- PostgreSQL connections
- Redis memory usage

## Example Queries

### Request Rate
```promql
rate(http_requests_total[5m])
```

### Error Rate
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

### Response Time (p95)
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Active Ingestion Jobs
```promql
ingestion_jobs_active
```

### FAISS Query Latency
```promql
histogram_quantile(0.95, rate(faiss_query_duration_seconds_bucket[5m]))
```
