#!/bin/bash
# Docker health check script for GitHub Codebase RAG Assistant services

set -e

SERVICE=${1:-all}

check_postgres() {
    echo "Checking PostgreSQL..."
    docker-compose exec -T postgres pg_isready -U postgres || return 1
    echo "✓ PostgreSQL is healthy"
}

check_redis() {
    echo "Checking Redis..."
    docker-compose exec -T redis redis-cli ping | grep -q PONG || return 1
    echo "✓ Redis is healthy"
}

check_ollama() {
    echo "Checking Ollama..."
    curl -sf http://localhost:11434/api/tags > /dev/null || return 1
    echo "✓ Ollama is healthy"
}

check_backend() {
    echo "Checking Backend..."
    curl -sf http://localhost:8000/api/v1/health > /dev/null || return 1
    echo "✓ Backend is healthy"
}

check_frontend() {
    echo "Checking Frontend..."
    curl -sf http://localhost:3000 > /dev/null || return 1
    echo "✓ Frontend is healthy"
}

check_nginx() {
    echo "Checking NGINX..."
    curl -sf http://localhost/health > /dev/null || return 1
    echo "✓ NGINX is healthy"
}

check_prometheus() {
    echo "Checking Prometheus..."
    curl -sf http://localhost:9090/-/healthy > /dev/null || return 1
    echo "✓ Prometheus is healthy"
}

check_grafana() {
    echo "Checking Grafana..."
    curl -sf http://localhost:3001/api/health > /dev/null || return 1
    echo "✓ Grafana is healthy"
}

case "$SERVICE" in
    postgres)
        check_postgres
        ;;
    redis)
        check_redis
        ;;
    ollama)
        check_ollama
        ;;
    backend)
        check_backend
        ;;
    frontend)
        check_frontend
        ;;
    nginx)
        check_nginx
        ;;
    prometheus)
        check_prometheus
        ;;
    grafana)
        check_grafana
        ;;
    all)
        echo "Running health checks for all services..."
        echo ""
        
        FAILED=0
        
        check_postgres || FAILED=$((FAILED + 1))
        check_redis || FAILED=$((FAILED + 1))
        check_ollama || FAILED=$((FAILED + 1))
        check_backend || FAILED=$((FAILED + 1))
        check_frontend || FAILED=$((FAILED + 1))
        check_nginx || FAILED=$((FAILED + 1))
        check_prometheus || FAILED=$((FAILED + 1))
        check_grafana || FAILED=$((FAILED + 1))
        
        echo ""
        if [ $FAILED -eq 0 ]; then
            echo "✓ All services are healthy!"
            exit 0
        else
            echo "✗ $FAILED service(s) failed health check"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {postgres|redis|ollama|backend|frontend|nginx|prometheus|grafana|all}"
        exit 1
        ;;
esac
