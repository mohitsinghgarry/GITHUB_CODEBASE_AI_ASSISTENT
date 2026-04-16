"""
Unit tests for database models and connection management.

This module tests the SQLAlchemy ORM models and database setup.

**Validates: Requirements 14.2**
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.orm import Repository, IngestionJob, CodeChunk


class TestRepositoryModel:
    """Tests for the Repository ORM model."""
    
    def test_repository_creation(self):
        """Test creating a Repository instance."""
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            default_branch="main",
            status="pending",
            chunk_count=0,
        )
        
        assert repo.url == "https://github.com/test/repo"
        assert repo.owner == "test"
        assert repo.name == "repo"
        assert repo.default_branch == "main"
        assert repo.status == "pending"
        assert repo.chunk_count == 0
    
    def test_repository_repr(self):
        """Test Repository string representation."""
        repo = Repository(
            id=uuid.uuid4(),
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="completed",
        )
        
        repr_str = repr(repo)
        assert "Repository" in repr_str
        assert "test" in repr_str
        assert "repo" in repr_str
        assert "completed" in repr_str
    
    @pytest.mark.asyncio
    async def test_repository_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Missing required fields should fail
        repo = Repository()
        db_session.add(repo)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_repository_unique_url(self, db_session):
        """Test that repository URL must be unique."""
        # Create first repository
        repo1 = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repo1)
        await db_session.commit()
        
        # Try to create second repository with same URL
        repo2 = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repo2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_repository_default_values(self, db_session):
        """Test that default values are set correctly."""
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Check default values
        assert repo.status == "pending"
        assert repo.chunk_count == 0
        assert repo.created_at is not None
        assert repo.updated_at is not None
        assert repo.id is not None
    
    @pytest.mark.asyncio
    async def test_repository_optional_fields(self, db_session):
        """Test that optional fields can be None."""
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            default_branch=None,
            last_commit_hash=None,
            error_message=None,
            index_path=None,
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        assert repo.default_branch is None
        assert repo.last_commit_hash is None
        assert repo.error_message is None
        assert repo.index_path is None


class TestIngestionJobModel:
    """Tests for the IngestionJob ORM model."""
    
    def test_ingestion_job_creation(self):
        """Test creating an IngestionJob instance."""
        repo_id = uuid.uuid4()
        job = IngestionJob(
            repository_id=repo_id,
            status="pending",
            stage="clone",
            progress_percent=0,
            retry_count=0,
        )
        
        assert job.repository_id == repo_id
        assert job.status == "pending"
        assert job.stage == "clone"
        assert job.progress_percent == 0
        assert job.retry_count == 0
    
    def test_ingestion_job_repr(self):
        """Test IngestionJob string representation."""
        repo_id = uuid.uuid4()
        job = IngestionJob(
            id=uuid.uuid4(),
            repository_id=repo_id,
            status="running",
            stage="embed",
        )
        
        repr_str = repr(job)
        assert "IngestionJob" in repr_str
        assert "running" in repr_str
        assert "embed" in repr_str
    
    @pytest.mark.asyncio
    async def test_ingestion_job_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Missing repository_id should fail
        job = IngestionJob(status="pending")
        db_session.add(job)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_ingestion_job_default_values(self, db_session):
        """Test that default values are set correctly."""
        # First create a repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create job
        job = IngestionJob(repository_id=repo.id)
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        # Check default values
        assert job.status == "pending"
        assert job.progress_percent == 0
        assert job.retry_count == 0
        assert job.id is not None
    
    @pytest.mark.asyncio
    async def test_ingestion_job_optional_fields(self, db_session):
        """Test that optional fields can be None."""
        # First create a repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create job with optional fields as None
        job = IngestionJob(
            repository_id=repo.id,
            stage=None,
            started_at=None,
            completed_at=None,
            error_message=None,
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.stage is None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.error_message is None


class TestCodeChunkModel:
    """Tests for the CodeChunk ORM model."""
    
    def test_code_chunk_creation(self):
        """Test creating a CodeChunk instance."""
        repo_id = uuid.uuid4()
        chunk = CodeChunk(
            repository_id=repo_id,
            file_path="src/main.py",
            start_line=10,
            end_line=25,
            language="python",
            content="def hello():\n    print('Hello, World!')",
        )
        
        assert chunk.repository_id == repo_id
        assert chunk.file_path == "src/main.py"
        assert chunk.start_line == 10
        assert chunk.end_line == 25
        assert chunk.language == "python"
        assert "hello" in chunk.content
    
    def test_code_chunk_repr(self):
        """Test CodeChunk string representation."""
        repo_id = uuid.uuid4()
        chunk = CodeChunk(
            id=uuid.uuid4(),
            repository_id=repo_id,
            file_path="src/utils.py",
            start_line=1,
            end_line=10,
            content="# Utility functions",
        )
        
        repr_str = repr(chunk)
        assert "CodeChunk" in repr_str
        assert "src/utils.py" in repr_str
        assert "1-10" in repr_str
    
    @pytest.mark.asyncio
    async def test_code_chunk_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Missing required fields should fail
        chunk = CodeChunk()
        db_session.add(chunk)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_code_chunk_default_values(self, db_session):
        """Test that default values are set correctly."""
        # First create a repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create chunk
        chunk = CodeChunk(
            repository_id=repo.id,
            file_path="test.py",
            start_line=1,
            end_line=10,
            content="test content",
        )
        db_session.add(chunk)
        await db_session.commit()
        await db_session.refresh(chunk)
        
        # Check default values
        assert chunk.created_at is not None
        assert chunk.id is not None
    
    @pytest.mark.asyncio
    async def test_code_chunk_optional_fields(self, db_session):
        """Test that optional fields can be None."""
        # First create a repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create chunk with optional fields as None
        chunk = CodeChunk(
            repository_id=repo.id,
            file_path="test.py",
            start_line=1,
            end_line=10,
            content="test content",
            language=None,
            embedding_id=None,
        )
        db_session.add(chunk)
        await db_session.commit()
        await db_session.refresh(chunk)
        
        assert chunk.language is None
        assert chunk.embedding_id is None


class TestModelRelationships:
    """Tests for model relationships and cascades."""
    
    @pytest.mark.asyncio
    async def test_repository_ingestion_jobs_relationship(self, db_session):
        """Test Repository to IngestionJob relationship."""
        # Create repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create ingestion jobs
        job1 = IngestionJob(repository_id=repo.id, status="pending")
        job2 = IngestionJob(repository_id=repo.id, status="running")
        db_session.add_all([job1, job2])
        await db_session.commit()
        
        # Refresh and check relationship - use explicit query instead of lazy loading
        from sqlalchemy import select
        result = await db_session.execute(
            select(IngestionJob).where(IngestionJob.repository_id == repo.id)
        )
        jobs = result.scalars().all()
        assert len(jobs) == 2
        assert all(job.repository_id == repo.id for job in jobs)
    
    @pytest.mark.asyncio
    async def test_repository_code_chunks_relationship(self, db_session):
        """Test Repository to CodeChunk relationship."""
        # Create repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create code chunks
        chunk1 = CodeChunk(
            repository_id=repo.id,
            file_path="file1.py",
            start_line=1,
            end_line=10,
            content="content1",
        )
        chunk2 = CodeChunk(
            repository_id=repo.id,
            file_path="file2.py",
            start_line=1,
            end_line=10,
            content="content2",
        )
        db_session.add_all([chunk1, chunk2])
        await db_session.commit()
        
        # Refresh and check relationship - use explicit query instead of lazy loading
        from sqlalchemy import select
        result = await db_session.execute(
            select(CodeChunk).where(CodeChunk.repository_id == repo.id)
        )
        chunks = result.scalars().all()
        assert len(chunks) == 2
        assert all(chunk.repository_id == repo.id for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_ingestion_job_repository_relationship(self, db_session):
        """Test IngestionJob to Repository relationship."""
        # Create repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create job
        job = IngestionJob(repository_id=repo.id, status="pending")
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        # Check relationship
        assert job.repository.id == repo.id
        assert job.repository.url == repo.url
    
    @pytest.mark.asyncio
    async def test_code_chunk_repository_relationship(self, db_session):
        """Test CodeChunk to Repository relationship."""
        # Create repository
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        # Create chunk
        chunk = CodeChunk(
            repository_id=repo.id,
            file_path="test.py",
            start_line=1,
            end_line=10,
            content="test",
        )
        db_session.add(chunk)
        await db_session.commit()
        await db_session.refresh(chunk)
        
        # Check relationship
        assert chunk.repository.id == repo.id
        assert chunk.repository.url == repo.url
    
    @pytest.mark.asyncio
    async def test_cascade_delete_ingestion_jobs(self, db_session):
        """Test that deleting a repository cascades to ingestion jobs."""
        # Create repository with jobs
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        job = IngestionJob(repository_id=repo.id, status="pending")
        db_session.add(job)
        await db_session.commit()
        job_id = job.id
        
        # Delete repository
        await db_session.delete(repo)
        await db_session.commit()
        
        # Check that job was also deleted
        result = await db_session.execute(
            select(IngestionJob).where(IngestionJob.id == job_id)
        )
        assert result.scalar_one_or_none() is None
    
    @pytest.mark.asyncio
    async def test_cascade_delete_code_chunks(self, db_session):
        """Test that deleting a repository cascades to code chunks."""
        # Create repository with chunks
        repo = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
        )
        db_session.add(repo)
        await db_session.commit()
        await db_session.refresh(repo)
        
        chunk = CodeChunk(
            repository_id=repo.id,
            file_path="test.py",
            start_line=1,
            end_line=10,
            content="test",
        )
        db_session.add(chunk)
        await db_session.commit()
        chunk_id = chunk.id
        
        # Delete repository
        await db_session.delete(repo)
        await db_session.commit()
        
        # Check that chunk was also deleted
        result = await db_session.execute(
            select(CodeChunk).where(CodeChunk.id == chunk_id)
        )
        assert result.scalar_one_or_none() is None
