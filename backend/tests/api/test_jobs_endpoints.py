"""
Tests for job management API endpoints.

This module tests the job management endpoints including:
- GET /jobs/{job_id} - Get job status
- POST /jobs/{job_id}/retry - Retry failed job

Requirements:
- 3.1: Create an Ingestion_Job and return immediately with a job identifier
- 3.2: Allow users to query the job status
- 3.3: Update the job status to completed with success or failure indication
- 3.5: Store error details and allow retry when an Ingestion_Job fails
- 3.6: Provide progress updates including percentage complete and estimated time remaining
- 10.1: Expose RESTful endpoints for job management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.orm.repository import Repository
from app.models.orm.ingestion_job import IngestionJob


# ============================================================================
# Test GET /jobs/{job_id}
# ============================================================================


@pytest.mark.asyncio
async def test_get_job_status_success(client: AsyncClient, db_session):
    """Test getting job status for an existing job."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/repo",
        owner="test",
        name="repo",
        status="pending",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a test job
    job = IngestionJob(
        repository_id=repository.id,
        status="running",
        stage="chunk",
        progress_percent=50,
        started_at=datetime.utcnow(),
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    # Get job status
    response = await client.get(f"/api/v1/jobs/{job.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "job" in data
    assert data["job"]["id"] == str(job.id)
    assert data["job"]["repository_id"] == str(repository.id)
    assert data["job"]["status"] == "running"
    assert data["job"]["stage"] == "chunk"
    assert data["job"]["progress_percent"] == 50
    assert "estimated_time_remaining" in data


@pytest.mark.asyncio
async def test_get_job_status_not_found(client: AsyncClient):
    """Test getting job status for a non-existent job."""
    fake_job_id = uuid.uuid4()
    response = await client.get(f"/api/v1/jobs/{fake_job_id}")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert data["detail"]["error"] == "Job not found"


@pytest.mark.asyncio
async def test_get_job_status_with_estimated_time(client: AsyncClient, db_session):
    """Test that estimated time remaining is calculated for running jobs."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/repo2",
        owner="test",
        name="repo2",
        status="pending",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a running job that started 10 minutes ago and is 25% complete
    job = IngestionJob(
        repository_id=repository.id,
        status="running",
        stage="embed",
        progress_percent=25,
        started_at=datetime.utcnow() - timedelta(minutes=10),
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    # Get job status
    response = await client.get(f"/api/v1/jobs/{job.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have estimated time remaining
    assert data["estimated_time_remaining"] is not None
    # With 25% done in 10 minutes, should estimate ~30 minutes remaining
    # Allow some tolerance for calculation
    assert 1500 < data["estimated_time_remaining"] < 2100  # 25-35 minutes in seconds


@pytest.mark.asyncio
async def test_get_job_status_completed(client: AsyncClient, db_session):
    """Test getting status for a completed job."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/repo3",
        owner="test",
        name="repo3",
        status="completed",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a completed job
    job = IngestionJob(
        repository_id=repository.id,
        status="completed",
        stage="store",
        progress_percent=100,
        started_at=datetime.utcnow() - timedelta(minutes=30),
        completed_at=datetime.utcnow(),
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    # Get job status
    response = await client.get(f"/api/v1/jobs/{job.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["job"]["status"] == "completed"
    assert data["job"]["progress_percent"] == 100
    # Completed jobs should not have estimated time remaining
    assert data["estimated_time_remaining"] is None


# ============================================================================
# Test POST /jobs/{job_id}/retry
# ============================================================================


@pytest.mark.asyncio
async def test_retry_failed_job_success(client: AsyncClient, db_session):
    """Test retrying a failed job."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/retry-repo",
        owner="test",
        name="retry-repo",
        status="failed",
        error_message="Clone failed",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a failed job
    failed_job = IngestionJob(
        repository_id=repository.id,
        status="failed",
        stage="clone",
        progress_percent=10,
        started_at=datetime.utcnow() - timedelta(minutes=5),
        completed_at=datetime.utcnow(),
        error_message="Git clone failed: connection timeout",
        retry_count=0,
    )
    db_session.add(failed_job)
    await db_session.commit()
    await db_session.refresh(failed_job)
    
    # Retry the job
    response = await client.post(f"/api/v1/jobs/{failed_job.id}/retry")
    
    assert response.status_code == 201
    data = response.json()
    
    assert "message" in data
    assert data["old_job_id"] == str(failed_job.id)
    assert "new_job_id" in data
    assert data["repository_id"] == str(repository.id)
    
    # Verify new job was created
    new_job_id = uuid.UUID(data["new_job_id"])
    result = await db_session.execute(
        select(IngestionJob).where(IngestionJob.id == new_job_id)
    )
    new_job = result.scalar_one()
    
    assert new_job.status == "pending"
    assert new_job.retry_count == 1
    assert new_job.repository_id == repository.id
    
    # Verify repository status was updated
    await db_session.refresh(repository)
    assert repository.status == "pending"
    assert repository.error_message is None


@pytest.mark.asyncio
async def test_retry_job_not_found(client: AsyncClient):
    """Test retrying a non-existent job."""
    fake_job_id = uuid.uuid4()
    response = await client.post(f"/api/v1/jobs/{fake_job_id}/retry")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert data["detail"]["error"] == "Job not found"


@pytest.mark.asyncio
async def test_retry_job_not_failed(client: AsyncClient, db_session):
    """Test that only failed jobs can be retried."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/running-repo",
        owner="test",
        name="running-repo",
        status="running",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a running job
    running_job = IngestionJob(
        repository_id=repository.id,
        status="running",
        stage="chunk",
        progress_percent=50,
        started_at=datetime.utcnow(),
    )
    db_session.add(running_job)
    await db_session.commit()
    await db_session.refresh(running_job)
    
    # Try to retry the running job
    response = await client.post(f"/api/v1/jobs/{running_job.id}/retry")
    
    assert response.status_code == 409
    data = response.json()
    
    assert "detail" in data
    assert data["detail"]["error"] == "Job is not in failed state"


@pytest.mark.asyncio
async def test_retry_job_increments_retry_count(client: AsyncClient, db_session):
    """Test that retry count is incremented when retrying a job."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/retry-count-repo",
        owner="test",
        name="retry-count-repo",
        status="failed",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a failed job with retry_count = 2
    failed_job = IngestionJob(
        repository_id=repository.id,
        status="failed",
        stage="embed",
        progress_percent=75,
        error_message="Embedding generation failed",
        retry_count=2,
    )
    db_session.add(failed_job)
    await db_session.commit()
    await db_session.refresh(failed_job)
    
    # Retry the job
    response = await client.post(f"/api/v1/jobs/{failed_job.id}/retry")
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify new job has incremented retry count
    new_job_id = uuid.UUID(data["new_job_id"])
    result = await db_session.execute(
        select(IngestionJob).where(IngestionJob.id == new_job_id)
    )
    new_job = result.scalar_one()
    
    assert new_job.retry_count == 3


@pytest.mark.asyncio
async def test_retry_job_completed(client: AsyncClient, db_session):
    """Test that completed jobs cannot be retried."""
    # Create a test repository
    repository = Repository(
        url="https://github.com/test/completed-repo",
        owner="test",
        name="completed-repo",
        status="completed",
    )
    db_session.add(repository)
    await db_session.commit()
    await db_session.refresh(repository)
    
    # Create a completed job
    completed_job = IngestionJob(
        repository_id=repository.id,
        status="completed",
        stage="store",
        progress_percent=100,
        started_at=datetime.utcnow() - timedelta(minutes=30),
        completed_at=datetime.utcnow(),
    )
    db_session.add(completed_job)
    await db_session.commit()
    await db_session.refresh(completed_job)
    
    # Try to retry the completed job
    response = await client.post(f"/api/v1/jobs/{completed_job.id}/retry")
    
    assert response.status_code == 409
    data = response.json()
    
    assert "detail" in data
    assert data["detail"]["error"] == "Job is not in failed state"
