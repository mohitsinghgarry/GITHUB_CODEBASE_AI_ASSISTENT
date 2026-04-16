"""
Unit tests for the ingestion service.

This module tests the IngestionService class functionality including
job creation, status tracking, retry logic, and incremental indexing.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ingestion_service import (
    IngestionService,
    IngestionServiceError,
    JobNotFoundError,
    RepositoryNotFoundError,
)


@pytest.fixture
def ingestion_service():
    """Create an IngestionService instance for testing."""
    return IngestionService()


@pytest.fixture
def mock_repository():
    """Create a mock repository object."""
    repo = MagicMock()
    repo.id = uuid4()
    repo.url = "https://github.com/owner/repo"
    repo.owner = "owner"
    repo.name = "repo"
    repo.last_commit_hash = "abc123"
    return repo


@pytest.fixture
def mock_job():
    """Create a mock ingestion job object."""
    job = MagicMock()
    job.id = uuid4()
    job.repository_id = uuid4()
    job.status = "pending"
    job.stage = None
    job.progress_percent = 0
    job.started_at = None
    job.completed_at = None
    job.error_message = None
    job.retry_count = 0
    return job


class TestIngestionService:
    """Test suite for IngestionService."""
    
    @pytest.mark.asyncio
    async def test_start_ingestion_creates_job(
        self, ingestion_service, mock_repository
    ):
        """Test that start_ingestion creates a job and triggers Celery pipeline."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker, \
             patch("app.services.ingestion_service.create_ingestion_pipeline") as mock_pipeline, \
             patch("app.services.ingestion_service.IngestionJob") as mock_job_class:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the IngestionJob instance
            mock_job = MagicMock()
            mock_job.id = uuid4()
            mock_job_class.return_value = mock_job
            
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            
            mock_result = MagicMock()
            mock_result.id = "celery-task-id-123"
            mock_pipeline.return_value.apply_async.return_value = mock_result
            
            # Execute
            result = await ingestion_service.start_ingestion(
                repository_id=mock_repository.id,
                repository_url=mock_repository.url,
            )
            
            # Verify
            assert "job_id" in result
            assert "repository_id" in result
            assert result["status"] == "pending"
            assert result["celery_task_id"] == "celery-task-id-123"
            mock_session.add.assert_called_once_with(mock_job)
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_job_status_returns_job_info(
        self, ingestion_service, mock_job
    ):
        """Test that get_job_status returns job information."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the result object - scalar_one_or_none() is synchronous
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_job)
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            # Execute
            result = await ingestion_service.get_job_status(mock_job.id)
            
            # Verify
            assert result["job_id"] == str(mock_job.id)
            assert result["status"] == "pending"
            assert result["progress_percent"] == 0
    
    @pytest.mark.asyncio
    async def test_get_job_status_raises_not_found(self, ingestion_service):
        """Test that get_job_status raises JobNotFoundError for missing job."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the result object - scalar_one_or_none() is synchronous
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            # Execute and verify
            with pytest.raises(JobNotFoundError):
                await ingestion_service.get_job_status(uuid4())
    
    @pytest.mark.asyncio
    async def test_retry_job_creates_new_job(
        self, ingestion_service, mock_job, mock_repository
    ):
        """Test that retry_job creates a new job for failed job."""
        mock_job.status = "failed"
        
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker, \
             patch.object(ingestion_service, "start_ingestion") as mock_start:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock job query - scalar_one_or_none() is synchronous
            mock_job_result = MagicMock()
            mock_job_result.scalar_one_or_none = MagicMock(return_value=mock_job)
            
            # Mock repository query - scalar_one_or_none() is synchronous
            mock_repo_result = MagicMock()
            mock_repo_result.scalar_one_or_none = MagicMock(return_value=mock_repository)
            
            # Mock new job query for retry count update - scalar_one() is synchronous
            new_job_id = uuid4()
            mock_new_job = MagicMock()
            mock_new_job.id = new_job_id
            mock_new_job.retry_count = 0
            mock_new_job_result = MagicMock()
            mock_new_job_result.scalar_one = MagicMock(return_value=mock_new_job)
            
            mock_session.execute = AsyncMock(
                side_effect=[mock_job_result, mock_repo_result, mock_new_job_result]
            )
            mock_session.commit = AsyncMock()
            
            mock_start.return_value = {
                "job_id": str(new_job_id),
                "repository_id": str(mock_repository.id),
                "status": "pending",
                "celery_task_id": "new-task-id",
            }
            
            # Execute
            result = await ingestion_service.retry_job(mock_job.id)
            
            # Verify
            assert result["job_id"] == str(new_job_id)
            mock_start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_job_raises_error_for_non_failed_job(
        self, ingestion_service, mock_job
    ):
        """Test that retry_job raises error for non-failed job."""
        mock_job.status = "running"
        
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the result object - scalar_one_or_none() is synchronous
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_job)
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            # Execute and verify
            with pytest.raises(IngestionServiceError, match="not in failed state"):
                await ingestion_service.retry_job(mock_job.id)
    
    @pytest.mark.asyncio
    async def test_check_for_updates_detects_changes(
        self, ingestion_service, mock_repository
    ):
        """Test that check_for_updates detects repository changes."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker, \
             patch.object(ingestion_service.repo_service, "repository_exists") as mock_exists, \
             patch.object(ingestion_service.repo_service, "has_updates") as mock_has_updates:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the result object - scalar_one_or_none() is synchronous
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_repository)
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_exists.return_value = True
            mock_has_updates.return_value = (True, "def456")
            
            # Execute
            has_updates, latest_commit = await ingestion_service.check_for_updates(
                mock_repository.id
            )
            
            # Verify
            assert has_updates is True
            assert latest_commit == "def456"
    
    @pytest.mark.asyncio
    async def test_start_incremental_indexing_triggers_job(
        self, ingestion_service, mock_repository
    ):
        """Test that start_incremental_indexing triggers a job when updates exist."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker, \
             patch.object(ingestion_service, "check_for_updates") as mock_check, \
             patch.object(ingestion_service, "start_ingestion") as mock_start:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the result object - scalar_one_or_none() is synchronous
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=mock_repository)
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_check.return_value = (True, "def456")
            mock_start.return_value = {
                "job_id": str(uuid4()),
                "repository_id": str(mock_repository.id),
                "status": "pending",
                "celery_task_id": "task-id",
            }
            
            # Execute
            result = await ingestion_service.start_incremental_indexing(
                mock_repository.id
            )
            
            # Verify
            assert result["incremental"] is True
            assert "message" in result
            mock_start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_incremental_indexing_skips_when_up_to_date(
        self, ingestion_service, mock_repository
    ):
        """Test that start_incremental_indexing skips when no updates."""
        with patch("app.services.ingestion_service.get_session_maker") as mock_session_maker, \
             patch.object(ingestion_service, "check_for_updates") as mock_check:
            
            # Setup mocks
            mock_session = AsyncMock()
            mock_session_maker.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_repository
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            mock_check.return_value = (False, "abc123")
            
            # Execute
            result = await ingestion_service.start_incremental_indexing(
                mock_repository.id
            )
            
            # Verify
            assert result["status"] == "up_to_date"
            assert result["job_id"] is None
