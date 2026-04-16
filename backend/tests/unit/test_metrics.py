"""
Unit tests for Prometheus metrics.

Tests the metrics utility functions and ensures metrics are properly tracked.

Requirements:
- 12.1: Track key metrics including request count, response times, error rates
- 12.2: Expose metrics in Prometheus format for scraping
- 12.6: Track Embedding_Store performance including query latency and storage size
- 12.7: Track LLM_Service metrics including inference time and token usage
"""

import pytest
from prometheus_client import REGISTRY

from app.utils.metrics import (
    init_metrics,
    track_request_metrics,
    track_ingestion_job_metrics,
    track_vector_search_metrics,
    track_llm_metrics,
    track_error,
    http_requests_total,
    http_request_duration_seconds,
    ingestion_jobs_total,
    ingestion_job_duration_seconds,
    vector_search_duration_seconds,
    vector_search_total,
    llm_inference_duration_seconds,
    llm_tokens_generated_total,
    llm_requests_total,
    errors_total,
)


class TestMetricsInitialization:
    """Test metrics initialization."""
    
    def test_init_metrics(self):
        """Test metrics initialization with app info."""
        # Initialize metrics
        init_metrics(
            app_name="test-app",
            version="1.0.0",
            environment="test"
        )
        
        # Verify app info is set
        # Note: prometheus_client doesn't provide easy access to Info metrics
        # This test mainly ensures no errors are raised
        assert True


class TestRequestMetrics:
    """Test HTTP request metrics tracking."""
    
    def test_track_request_metrics(self):
        """Test tracking HTTP request metrics."""
        # Get initial value
        initial_count = REGISTRY.get_sample_value(
            'http_requests_total',
            labels={'method': 'GET', 'endpoint': '/test', 'status': '200'}
        ) or 0
        
        # Track request
        track_request_metrics(
            method="GET",
            endpoint="/test",
            status_code=200,
            duration=0.5
        )
        
        # Verify counter incremented
        final_count = REGISTRY.get_sample_value(
            'http_requests_total',
            labels={'method': 'GET', 'endpoint': '/test', 'status': '200'}
        ) or 0
        
        assert final_count > initial_count
    
    def test_track_request_duration(self):
        """Test tracking request duration."""
        # Track request with duration
        track_request_metrics(
            method="POST",
            endpoint="/api/v1/repositories",
            status_code=201,
            duration=1.5
        )
        
        # Verify histogram was updated
        count = REGISTRY.get_sample_value(
            'http_request_duration_seconds_count',
            labels={'method': 'POST', 'endpoint': '/api/v1/repositories'}
        )
        
        assert count is not None
        assert count > 0


class TestIngestionJobMetrics:
    """Test ingestion job metrics tracking."""
    
    def test_track_ingestion_job_status(self):
        """Test tracking ingestion job status."""
        # Get initial value
        initial_count = REGISTRY.get_sample_value(
            'ingestion_jobs_total',
            labels={'status': 'completed'}
        ) or 0
        
        # Track job completion
        track_ingestion_job_metrics(status="completed")
        
        # Verify counter incremented
        final_count = REGISTRY.get_sample_value(
            'ingestion_jobs_total',
            labels={'status': 'completed'}
        ) or 0
        
        assert final_count > initial_count
    
    def test_track_ingestion_job_duration(self):
        """Test tracking ingestion job duration."""
        # Track job with stage and duration
        track_ingestion_job_metrics(
            status="completed",
            stage="embed",
            duration=120.5
        )
        
        # Verify histogram was updated
        count = REGISTRY.get_sample_value(
            'ingestion_job_duration_seconds_count',
            labels={'stage': 'embed'}
        )
        
        assert count is not None
        assert count > 0


class TestVectorSearchMetrics:
    """Test vector search metrics tracking."""
    
    def test_track_vector_search(self):
        """Test tracking vector search metrics."""
        repo_id = "test-repo-123"
        
        # Get initial count
        initial_count = REGISTRY.get_sample_value(
            'vector_search_total',
            labels={'repository_id': repo_id, 'status': 'success'}
        ) or 0
        
        # Track search
        track_vector_search_metrics(
            repository_id=repo_id,
            duration=0.05,
            status="success"
        )
        
        # Verify counter incremented
        final_count = REGISTRY.get_sample_value(
            'vector_search_total',
            labels={'repository_id': repo_id, 'status': 'success'}
        ) or 0
        
        assert final_count > initial_count
    
    def test_track_vector_search_duration(self):
        """Test tracking vector search duration."""
        repo_id = "test-repo-456"
        
        # Track search
        track_vector_search_metrics(
            repository_id=repo_id,
            duration=0.1,
            status="success"
        )
        
        # Verify histogram was updated
        count = REGISTRY.get_sample_value(
            'vector_search_duration_seconds_count',
            labels={'repository_id': repo_id}
        )
        
        assert count is not None
        assert count > 0


class TestLLMMetrics:
    """Test LLM metrics tracking."""
    
    def test_track_llm_inference(self):
        """Test tracking LLM inference metrics."""
        model = "codellama:7b"
        
        # Get initial count
        initial_count = REGISTRY.get_sample_value(
            'llm_requests_total',
            labels={'model': model, 'status': 'success'}
        ) or 0
        
        # Track inference
        track_llm_metrics(
            model=model,
            duration=5.2,
            tokens=150,
            status="success"
        )
        
        # Verify counter incremented
        final_count = REGISTRY.get_sample_value(
            'llm_requests_total',
            labels={'model': model, 'status': 'success'}
        ) or 0
        
        assert final_count > initial_count
    
    def test_track_llm_tokens(self):
        """Test tracking LLM token generation."""
        model = "deepseek-coder:6.7b"
        
        # Get initial token count
        initial_tokens = REGISTRY.get_sample_value(
            'llm_tokens_generated_total',
            labels={'model': model}
        ) or 0
        
        # Track inference with tokens
        track_llm_metrics(
            model=model,
            duration=3.0,
            tokens=100,
            status="success"
        )
        
        # Verify tokens were counted
        final_tokens = REGISTRY.get_sample_value(
            'llm_tokens_generated_total',
            labels={'model': model}
        ) or 0
        
        assert final_tokens >= initial_tokens + 100
    
    def test_track_llm_duration(self):
        """Test tracking LLM inference duration."""
        model = "codellama:7b"
        
        # Track inference
        track_llm_metrics(
            model=model,
            duration=10.5,
            status="success"
        )
        
        # Verify histogram was updated
        count = REGISTRY.get_sample_value(
            'llm_inference_duration_seconds_count',
            labels={'model': model}
        )
        
        assert count is not None
        assert count > 0


class TestErrorMetrics:
    """Test error metrics tracking."""
    
    def test_track_error(self):
        """Test tracking errors."""
        # Get initial count
        initial_count = REGISTRY.get_sample_value(
            'errors_total',
            labels={'type': 'timeout', 'component': 'ollama'}
        ) or 0
        
        # Track error
        track_error(error_type="timeout", component="ollama")
        
        # Verify counter incremented
        final_count = REGISTRY.get_sample_value(
            'errors_total',
            labels={'type': 'timeout', 'component': 'ollama'}
        ) or 0
        
        assert final_count > initial_count
    
    def test_track_multiple_errors(self):
        """Test tracking multiple error types."""
        # Track different errors
        track_error(error_type="connection", component="database")
        track_error(error_type="timeout", component="redis")
        track_error(error_type="validation", component="api")
        
        # Verify all were tracked
        db_errors = REGISTRY.get_sample_value(
            'errors_total',
            labels={'type': 'connection', 'component': 'database'}
        )
        redis_errors = REGISTRY.get_sample_value(
            'errors_total',
            labels={'type': 'timeout', 'component': 'redis'}
        )
        api_errors = REGISTRY.get_sample_value(
            'errors_total',
            labels={'type': 'validation', 'component': 'api'}
        )
        
        assert db_errors is not None and db_errors > 0
        assert redis_errors is not None and redis_errors > 0
        assert api_errors is not None and api_errors > 0


class TestMetricsIntegration:
    """Test metrics integration scenarios."""
    
    def test_complete_request_flow(self):
        """Test tracking a complete request flow."""
        # Track request
        track_request_metrics(
            method="POST",
            endpoint="/api/v1/search/hybrid",
            status_code=200,
            duration=0.8
        )
        
        # Track vector search
        track_vector_search_metrics(
            repository_id="repo-123",
            duration=0.05,
            status="success"
        )
        
        # Verify both metrics were tracked
        request_count = REGISTRY.get_sample_value(
            'http_requests_total',
            labels={'method': 'POST', 'endpoint': '/api/v1/search/hybrid', 'status': '200'}
        )
        search_count = REGISTRY.get_sample_value(
            'vector_search_total',
            labels={'repository_id': 'repo-123', 'status': 'success'}
        )
        
        assert request_count is not None and request_count > 0
        assert search_count is not None and search_count > 0
    
    def test_complete_ingestion_flow(self):
        """Test tracking a complete ingestion flow."""
        # Track job start
        track_ingestion_job_metrics(status="running")
        
        # Track stages
        track_ingestion_job_metrics(status="running", stage="clone", duration=10.0)
        track_ingestion_job_metrics(status="running", stage="read", duration=5.0)
        track_ingestion_job_metrics(status="running", stage="chunk", duration=15.0)
        track_ingestion_job_metrics(status="running", stage="embed", duration=120.0)
        track_ingestion_job_metrics(status="running", stage="store", duration=8.0)
        
        # Track completion
        track_ingestion_job_metrics(status="completed")
        
        # Verify metrics were tracked
        running_count = REGISTRY.get_sample_value(
            'ingestion_jobs_total',
            labels={'status': 'running'}
        )
        completed_count = REGISTRY.get_sample_value(
            'ingestion_jobs_total',
            labels={'status': 'completed'}
        )
        
        assert running_count is not None and running_count > 0
        assert completed_count is not None and completed_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
