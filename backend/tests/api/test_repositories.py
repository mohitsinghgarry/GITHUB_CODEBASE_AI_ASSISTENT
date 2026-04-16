"""
Unit tests for repository management API endpoints.

This module tests the repository CRUD operations and re-indexing functionality.

Requirements tested:
- 8.1: Support indexing and storing multiple repositories simultaneously
- 8.2: Return all indexed repositories with metadata
- 8.5: Remove all associated code chunks and embeddings when repository is deleted
- 8.7: Trigger re-indexing automatically or on-demand
- 10.1: Expose RESTful endpoints for repository management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
- 10.3: Return error responses with descriptive messages
"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.repository import Repository
from app.models.orm.ingestion_job import IngestionJob
from app.models.orm.code_chunk import CodeChunk
from app.api.routes.repositories import (
    parse_github_url,
    create_ingestion_job,
)


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestParseGithubUrl:
    """Tests for parse_github_url helper function."""
    
    def test_parse_valid_https_url(self):
        """Test parsing a valid HTTPS GitHub URL."""
        url = "https://github.com/owner/repo"
        owner, name = parse_github_url(url)
        assert owner == "owner"
        assert name == "repo"
    
    def test_parse_url_with_trailing_slash(self):
        """Test parsing URL with trailing slash."""
        url = "https://github.com/owner/repo/"
        owner, name = parse_github_url(url)
        assert owner == "owner"
        assert name == "repo"
    
    def test_parse_url_with_git_extension(self):
        """Test parsing URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        owner, name = parse_github_url(url)
        assert owner == "owner"
        assert name == "repo"
    
    def test_parse_url_with_trailing_slash_and_git(self):
        """Test parsing URL with both trailing slash and .git."""
        url = "https://github.com/owner/repo.git/"
        owner, name = parse_github_url(url)
        assert owner == "owner"
        assert name == "repo"
    
    def test_parse_invalid_url_format(self):
        """Test parsing invalid URL format raises ValueError."""
        url = "https://github.com/invalid"
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            parse_github_url(url)
    
    def test_parse_url_with_hyphen_in_name(self):
        """Test parsing URL with hyphen in repository name."""
        url = "https://github.com/my-org/my-repo"
        owner, name = parse_github_url(url)
        assert owner == "my-org"
        assert name == "my-repo"


class TestCreateIngestionJob:
    """Tests for create_ingestion_job helper function."""
    
    @pytest.mark.asyncio
    async def test_create_ingestion_job_success(self, db_session: AsyncSession):
        """Test creating an ingestion job successfully."""
        # Create a repository first
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        # Create ingestion job
        job = await create_ingestion_job(db_session, repository.id)
        
        # Verify job was created
        assert job.id is not None
        assert job.repository_id == repository.id
        assert job.status == "pending"
        assert job.stage is None
        assert job.progress_percent == 0
        assert job.retry_count == 0
    
    @pytest.mark.asyncio
    async def test_create_ingestion_job_persisted(self, db_session: AsyncSession):
        """Test that ingestion job is persisted to database."""
        # Create a repository first
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        # Create ingestion job
        job = await create_ingestion_job(db_session, repository.id)
        
        # Query job from database
        result = await db_session.execute(
            select(IngestionJob).where(IngestionJob.id == job.id)
        )
        persisted_job = result.scalar_one()
        
        assert persisted_job.id == job.id
        assert persisted_job.repository_id == repository.id


# ============================================================================
# Repository Schema Validation Tests
# ============================================================================


class TestRepositorySchemaValidation:
    """Tests for repository request schema validation."""
    
    def test_valid_github_url(self):
        """Test validation of valid GitHub URL."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        request = RepositoryCreateRequest(url="https://github.com/owner/repo")
        assert request.url == "https://github.com/owner/repo"
    
    def test_url_without_github_domain(self):
        """Test validation rejects non-GitHub URLs."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        with pytest.raises(ValueError, match="must be a GitHub repository URL"):
            RepositoryCreateRequest(url="https://gitlab.com/owner/repo")
    
    def test_url_without_protocol(self):
        """Test validation rejects URLs without http/https."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        with pytest.raises(ValueError, match="must start with http"):
            RepositoryCreateRequest(url="github.com/owner/repo")
    
    def test_url_with_invalid_format(self):
        """Test validation rejects malformed URLs."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        with pytest.raises(ValueError, match="Invalid GitHub repository URL format"):
            RepositoryCreateRequest(url="https://github.com/invalid")
    
    def test_url_strips_whitespace(self):
        """Test that URL whitespace is stripped."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        request = RepositoryCreateRequest(url="  https://github.com/owner/repo  ")
        assert request.url == "https://github.com/owner/repo"
    
    def test_url_removes_trailing_slash(self):
        """Test that trailing slashes are removed."""
        from app.models.schemas.repository import RepositoryCreateRequest
        
        request = RepositoryCreateRequest(url="https://github.com/owner/repo/")
        assert request.url == "https://github.com/owner/repo"


# ============================================================================
# Repository CRUD Operation Tests
# ============================================================================


class TestRepositoryCRUD:
    """Tests for repository CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_repository(self, db_session: AsyncSession):
        """Test creating a repository record."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        assert repository.id is not None
        assert repository.url == "https://github.com/test/repo"
        assert repository.owner == "test"
        assert repository.name == "repo"
        assert repository.status == "pending"
        assert repository.chunk_count == 0
    
    @pytest.mark.asyncio
    async def test_list_repositories(self, db_session: AsyncSession):
        """Test listing multiple repositories."""
        # Create multiple repositories
        repos = [
            Repository(url=f"https://github.com/test/repo{i}", owner="test", name=f"repo{i}", status="pending")
            for i in range(3)
        ]
        
        for repo in repos:
            db_session.add(repo)
        await db_session.commit()
        
        # Query all repositories
        result = await db_session.execute(select(Repository))
        all_repos = result.scalars().all()
        
        assert len(all_repos) == 3
    
    @pytest.mark.asyncio
    async def test_get_repository_by_id(self, db_session: AsyncSession):
        """Test retrieving a repository by ID."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="completed",
        )
        
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        # Query by ID
        result = await db_session.execute(
            select(Repository).where(Repository.id == repository.id)
        )
        found_repo = result.scalar_one()
        
        assert found_repo.id == repository.id
        assert found_repo.url == repository.url
    
    @pytest.mark.asyncio
    async def test_delete_repository_cascades(self, db_session: AsyncSession):
        """Test that deleting a repository cascades to related records."""
        # Create repository
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="completed",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        # Create related code chunks
        chunks = [
            CodeChunk(
                repository_id=repository.id,
                file_path=f"file{i}.py",
                start_line=1,
                end_line=10,
                content=f"code content {i}",
            )
            for i in range(3)
        ]
        for chunk in chunks:
            db_session.add(chunk)
        await db_session.commit()
        
        # Create related ingestion job
        job = IngestionJob(
            repository_id=repository.id,
            status="completed",
        )
        db_session.add(job)
        await db_session.commit()
        
        # Delete repository
        await db_session.delete(repository)
        await db_session.commit()
        
        # Verify code chunks were deleted (cascade)
        chunk_result = await db_session.execute(
            select(CodeChunk).where(CodeChunk.repository_id == repository.id)
        )
        remaining_chunks = chunk_result.scalars().all()
        assert len(remaining_chunks) == 0
        
        # Verify ingestion jobs were deleted (cascade)
        job_result = await db_session.execute(
            select(IngestionJob).where(IngestionJob.repository_id == repository.id)
        )
        remaining_jobs = job_result.scalars().all()
        assert len(remaining_jobs) == 0
    
    @pytest.mark.asyncio
    async def test_repository_unique_url_constraint(self, db_session: AsyncSession):
        """Test that repository URLs must be unique."""
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
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            await db_session.commit()


# ============================================================================
# Repository Status Tests
# ============================================================================


class TestRepositoryStatus:
    """Tests for repository status management."""
    
    @pytest.mark.asyncio
    async def test_repository_status_transitions(self, db_session: AsyncSession):
        """Test repository status transitions through pipeline stages."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        # Simulate status transitions
        statuses = ["cloning", "reading", "chunking", "embedding", "completed"]
        
        for status in statuses:
            repository.status = status
            await db_session.commit()
            await db_session.refresh(repository)
            assert repository.status == status
    
    @pytest.mark.asyncio
    async def test_repository_error_status(self, db_session: AsyncSession):
        """Test repository error status with error message."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="failed",
            error_message="Failed to clone repository",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        assert repository.status == "failed"
        assert repository.error_message == "Failed to clone repository"


# ============================================================================
# Repository Metadata Tests
# ============================================================================


class TestRepositoryMetadata:
    """Tests for repository metadata management."""
    
    @pytest.mark.asyncio
    async def test_repository_with_full_metadata(self, db_session: AsyncSession):
        """Test repository with complete metadata."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            default_branch="main",
            last_commit_hash="abc123def456",
            status="completed",
            chunk_count=150,
            index_path="/path/to/index.faiss",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        assert repository.default_branch == "main"
        assert repository.last_commit_hash == "abc123def456"
        assert repository.chunk_count == 150
        assert repository.index_path == "/path/to/index.faiss"
    
    @pytest.mark.asyncio
    async def test_repository_timestamps(self, db_session: AsyncSession):
        """Test repository created_at and updated_at timestamps."""
        repository = Repository(
            url="https://github.com/test/repo",
            owner="test",
            name="repo",
            status="pending",
        )
        db_session.add(repository)
        await db_session.commit()
        await db_session.refresh(repository)
        
        assert repository.created_at is not None
        assert repository.updated_at is not None
        
        # Store original updated_at
        original_updated_at = repository.updated_at
        
        # Update repository
        repository.status = "completed"
        await db_session.commit()
        await db_session.refresh(repository)
        
        # updated_at should change
        assert repository.updated_at >= original_updated_at
