"""
Unit tests for ingestion tasks.

This module tests the Celery task definitions for the ingestion pipeline.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from app.jobs.tasks.ingestion_tasks import (
    clone_repository,
    read_source_files,
    chunk_code_files,
    generate_embeddings,
    store_embeddings,
    create_ingestion_pipeline,
)


class TestIngestionTasks:
    """Test suite for ingestion tasks."""
    
    def test_clone_repository_task_registered(self):
        """Test that clone_repository task is registered with Celery."""
        assert clone_repository.name == "app.jobs.tasks.ingestion_tasks.clone_repository"
        # Check that the task is bound (has self parameter)
        assert hasattr(clone_repository, 'request')
    
    def test_read_source_files_task_registered(self):
        """Test that read_source_files task is registered with Celery."""
        assert read_source_files.name == "app.jobs.tasks.ingestion_tasks.read_source_files"
        # Check that the task is bound (has self parameter)
        assert hasattr(read_source_files, 'request')
    
    def test_chunk_code_files_task_registered(self):
        """Test that chunk_code_files task is registered with Celery."""
        assert chunk_code_files.name == "app.jobs.tasks.ingestion_tasks.chunk_code_files"
        # Check that the task is bound (has self parameter)
        assert hasattr(chunk_code_files, 'request')
    
    def test_generate_embeddings_task_registered(self):
        """Test that generate_embeddings task is registered with Celery."""
        assert generate_embeddings.name == "app.jobs.tasks.ingestion_tasks.generate_embeddings"
        # Check that the task is bound (has self parameter)
        assert hasattr(generate_embeddings, 'request')
    
    def test_store_embeddings_task_registered(self):
        """Test that store_embeddings task is registered with Celery."""
        assert store_embeddings.name == "app.jobs.tasks.ingestion_tasks.store_embeddings"
        # Check that the task is bound (has self parameter)
        assert hasattr(store_embeddings, 'request')
    
    def test_create_ingestion_pipeline(self):
        """Test that create_ingestion_pipeline creates a valid chain."""
        repository_id = str(uuid4())
        repository_url = "https://github.com/owner/repo"
        job_id = str(uuid4())
        
        pipeline = create_ingestion_pipeline(
            repository_id=repository_id,
            repository_url=repository_url,
            job_id=job_id,
        )
        
        # Verify it's a chain
        assert pipeline is not None
        assert hasattr(pipeline, "apply_async")
    
    def test_task_retry_configuration(self):
        """Test that tasks have proper retry configuration."""
        # All tasks should have retry configuration
        tasks = [
            clone_repository,
            read_source_files,
            chunk_code_files,
            generate_embeddings,
            store_embeddings,
        ]
        
        for task in tasks:
            assert task.autoretry_for == (Exception,)
            assert task.retry_kwargs == {"max_retries": 3}
            assert task.retry_backoff is True
            assert task.retry_backoff_max == 600
            assert task.retry_jitter is True


class TestIngestionTaskLogic:
    """Test suite for ingestion task logic."""
    
    @patch("app.jobs.tasks.ingestion_tasks.RepositoryService")
    @patch("app.jobs.tasks.ingestion_tasks.asyncio.run")
    def test_clone_repository_success(self, mock_asyncio_run, mock_repo_service_class):
        """Test successful repository cloning."""
        # Setup mocks
        mock_repo_service = Mock()
        mock_repo_service_class.return_value = mock_repo_service
        
        # Mock the clone_repository async call
        mock_metadata = {
            "url": "https://github.com/owner/repo",
            "owner": "owner",
            "name": "repo",
            "path": "/path/to/repo",
            "branch": "main",
            "commit_hash": "abc123",
        }
        mock_asyncio_run.return_value = mock_metadata
        
        # Execute task
        repository_id = str(uuid4())
        job_id = str(uuid4())
        
        result = clone_repository(
            repository_id=repository_id,
            repository_url="https://github.com/owner/repo",
            job_id=job_id,
        )
        
        # Verify result
        assert result["repository_id"] == repository_id
        assert result["job_id"] == job_id
        assert result["owner"] == "owner"
        assert result["name"] == "repo"
    
    @patch("app.jobs.tasks.ingestion_tasks.FileReader")
    @patch("app.jobs.tasks.ingestion_tasks.asyncio.run")
    def test_read_source_files_success(self, mock_asyncio_run, mock_file_reader_class):
        """Test successful source file reading."""
        # Setup mocks
        mock_file_reader = Mock()
        mock_file_reader_class.return_value = mock_file_reader
        
        # Mock file infos
        mock_file_info = Mock()
        mock_file_info.absolute_path = "/path/to/file.py"
        mock_file_info.relative_path = "file.py"
        mock_file_info.language = "python"
        mock_file_info.size_bytes = 1024
        
        mock_file_reader.read_files.return_value = [mock_file_info]
        
        # Execute task
        metadata = {
            "repository_id": str(uuid4()),
            "job_id": str(uuid4()),
            "path": "/path/to/repo",
        }
        
        result = read_source_files(metadata)
        
        # Verify result
        assert result["repository_id"] == metadata["repository_id"]
        assert result["job_id"] == metadata["job_id"]
        assert len(result["files"]) == 1
        assert result["files"][0]["relative_path"] == "file.py"
        assert result["files"][0]["language"] == "python"
    
    @patch("app.jobs.tasks.ingestion_tasks.ChunkingService")
    @patch("app.jobs.tasks.ingestion_tasks.asyncio.run")
    @patch("builtins.open", create=True)
    def test_chunk_code_files_success(self, mock_open, mock_asyncio_run, mock_chunking_service_class):
        """Test successful code file chunking."""
        # Setup mocks
        mock_chunking_service = Mock()
        mock_chunking_service_class.return_value = mock_chunking_service
        
        # Mock file content
        mock_open.return_value.__enter__.return_value.read.return_value = "def hello(): pass"
        
        # Mock chunks
        mock_chunk = Mock()
        mock_chunk.to_dict.return_value = {
            "content": "def hello(): pass",
            "file_path": "file.py",
            "start_line": 1,
            "end_line": 1,
            "language": "python",
            "chunk_index": 0,
        }
        mock_chunking_service.chunk_file.return_value = [mock_chunk]
        
        # Execute task
        data = {
            "repository_id": str(uuid4()),
            "job_id": str(uuid4()),
            "files": [
                {
                    "absolute_path": "/path/to/file.py",
                    "relative_path": "file.py",
                    "language": "python",
                    "size_bytes": 1024,
                }
            ],
        }
        
        result = chunk_code_files(data)
        
        # Verify result
        assert result["repository_id"] == data["repository_id"]
        assert result["job_id"] == data["job_id"]
        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["file_path"] == "file.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
