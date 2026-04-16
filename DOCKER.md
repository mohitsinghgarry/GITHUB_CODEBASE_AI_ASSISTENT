# Docker Deployment Guide

This guide covers deploying the GitHub Codebase RAG Assistant using Docker Compose.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- At least 8GB RAM available for Docker
- 20GB free disk space (for models and data)

### Optional: GPU Support for Ollama

For GPU acceleration with Ollama:
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit ([Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))

If running on CPU-only systems, remove the GPU configuration from `docker-compose.yml`:

```yaml
# Remove this section from the ollama service:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd github-rag-assistant
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32

# Edit .env and set SECRET_KEY to the generated value
nano .env
```

**Important**: Change the `SECRET_KEY` in `.env` to a secure random string (minimum 32 characters).

### 3. Start All Services

```bash
# Production deployment
make docker-up

# Or using docker-compose directly
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama (port 11434)
- FastAPI Backend (port 8000)
- Celery Worker
- Next.js Frontend (port 3000)
- NGINX Reverse Proxy (ports 80, 443)
- Prometheus (port 9090)
- Grafana (port 3001)

### 4. Pull Ollama Models

```bash
# Pull the default model (codellama:7b)
make docker-pull-models

# Or manually
docker-compose exec ollama ollama pull codellama:7b
```

**Note**: Model download may take 5-15 minutes depending on your connection speed.

### 5. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Documentation**: http://localhost/api/v1/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Development Mode

For local development with hot-reloading:

```bash
# Start development environment
make docker-dev-up

# Or using docker-compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Development mode features:
- Hot-reloading for backend and frontend
- Debug logging enabled
- Source code mounted as volumes
- Direct access to all service ports

Access points in development mode:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Ollama**: http://localhost:11434

## Service Management

### View Logs

```bash
# All services
make docker-logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f ollama
```

### Check Service Status

```bash
make docker-ps

# Or
docker-compose ps
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Stop Services

```bash
# Stop all services (preserves data)
make docker-down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

## Data Persistence

All data is stored in named Docker volumes:

| Volume | Purpose | Location |
|--------|---------|----------|
| `github-rag-postgres-data` | PostgreSQL database | Repository metadata, jobs, chunks |
| `github-rag-redis-data` | Redis cache | Sessions, cache |
| `github-rag-ollama-models` | Ollama models | Downloaded LLM models |
| `github-rag-repo-storage` | Git repositories | Cloned repositories |
| `github-rag-faiss-indices` | FAISS indices | Vector embeddings |
| `github-rag-prometheus-data` | Prometheus metrics | Time-series metrics |
| `github-rag-grafana-data` | Grafana dashboards | Dashboard configs |

### Backup Data

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U postgres github_rag > backup.sql

# Backup volumes
docker run --rm -v github-rag-faiss-indices:/data -v $(pwd):/backup alpine tar czf /backup/faiss-backup.tar.gz /data
docker run --rm -v github-rag-repo-storage:/data -v $(pwd):/backup alpine tar czf /backup/repos-backup.tar.gz /data
```

### Restore Data

```bash
# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U postgres github_rag

# Restore volumes
docker run --rm -v github-rag-faiss-indices:/data -v $(pwd):/backup alpine tar xzf /backup/faiss-backup.tar.gz -C /
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Security (REQUIRED)
SECRET_KEY=your-secure-secret-key-min-32-chars

# Grafana
GRAFANA_PASSWORD=admin

# Ollama Model Selection
OLLAMA_MODEL=codellama:7b
# Alternatives: deepseek-coder:6.7b, llama2:13b, mistral:7b
```

### Service Configuration

#### Backend Configuration

Edit environment variables in `docker-compose.yml` under the `backend` service:

```yaml
environment:
  CHUNK_SIZE: 512              # Code chunk size
  CHUNK_OVERLAP: 50            # Chunk overlap
  DEFAULT_TOP_K: 10            # Default search results
  MAX_CONTEXT_TOKENS: 4096     # Max context window
  RATE_LIMIT_PER_MINUTE: 60    # API rate limit
```

#### Ollama Model Selection

To use a different model:

1. Update `OLLAMA_MODEL` in `docker-compose.yml`
2. Pull the model:
   ```bash
   docker-compose exec ollama ollama pull <model-name>
   ```

Available models:
- `codellama:7b` - Code-focused (default)
- `deepseek-coder:6.7b` - Code-focused, efficient
- `llama2:13b` - General purpose, larger
- `mistral:7b` - General purpose, efficient

### Resource Limits

Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090

Key metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `ingestion_jobs_total` - Total ingestion jobs
- `faiss_query_duration_seconds` - FAISS query latency
- `ollama_inference_duration_seconds` - LLM inference time

### Grafana Dashboards

Access Grafana at http://localhost:3001 (default: admin/admin)

Pre-configured dashboards:
- System Overview
- API Performance
- Ingestion Pipeline
- LLM Performance

## Troubleshooting

### Services Won't Start

```bash
# Check service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs ollama

# Check service health
docker-compose ps
```

### Ollama Model Not Found

```bash
# List available models
docker-compose exec ollama ollama list

# Pull the required model
docker-compose exec ollama ollama pull codellama:7b
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Out of Memory

```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or adjust service resource limits in docker-compose.yml
```

### Port Conflicts

If ports are already in use, modify port mappings in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change host port (left side)
```

### Reset Everything

```bash
# Stop all services and remove volumes
make docker-clean

# Or manually
docker-compose down -v
docker volume prune -f
```

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Change `GRAFANA_PASSWORD` from default
- [ ] Configure HTTPS with SSL certificates in NGINX
- [ ] Set `DEBUG=false` in backend environment
- [ ] Configure firewall rules (only expose ports 80, 443)
- [ ] Enable authentication for Prometheus and Grafana
- [ ] Set up regular backups
- [ ] Configure log rotation
- [ ] Review and adjust rate limits

### SSL/TLS Configuration

1. Place SSL certificates in `nginx/ssl/`:
   ```
   nginx/ssl/cert.pem
   nginx/ssl/key.pem
   ```

2. Update `nginx/nginx.conf` to enable HTTPS

3. Restart NGINX:
   ```bash
   docker-compose restart nginx
   ```

### Scaling

Scale Celery workers:

```bash
docker-compose up -d --scale celery-worker=3
```

### Health Checks

All services include health checks. Check status:

```bash
docker-compose ps
```

Healthy services show `(healthy)` status.

## Useful Commands

```bash
# View all logs
make docker-logs

# View specific service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres github_rag

# Rebuild images
make docker-build

# Pull latest images
docker-compose pull

# Remove unused images and volumes
docker system prune -a --volumes
```

## Support

For issues and questions:
- Check logs: `make docker-logs`
- Review health checks: `docker-compose ps`
- See main README.md for application documentation
