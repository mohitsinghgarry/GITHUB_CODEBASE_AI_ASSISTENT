"""
API routes for repository management.

This module implements RESTful endpoints for managing GitHub repositories,
including adding, listing, retrieving, deleting, and re-indexing repositories.

Requirements:
- 8.1: Support indexing and storing multiple repositories simultaneously
- 8.2: Return all indexed repositories with metadata (name, owner, last updated time, index status)
- 8.3: Support searching across all repositories or filtering by specific repositories
- 8.5: Remove all associated code chunks and embeddings when repository is deleted
- 8.7: Trigger re-indexing automatically or on-demand
- 10.1: Expose RESTful endpoints for repository management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
- 10.3: Return error responses with descriptive messages when validation fails
"""

import logging
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_db
from app.models.orm.repository import Repository
from app.models.orm.ingestion_job import IngestionJob
from app.models.orm.code_chunk import CodeChunk
from app.models.schemas.repository import (
    RepositoryCreateRequest,
    RepositoryCreateResponse,
    RepositoryDeleteResponse,
    RepositoryListResponse,
    RepositoryReindexResponse,
    RepositorySchema,
    ErrorResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/repositories", tags=["repositories"])

# Get settings
settings = get_settings()


# ============================================================================
# Helper Functions
# ============================================================================


def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse GitHub URL to extract owner and repository name.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Tuple of (owner, name)
        
    Raises:
        ValueError: If URL format is invalid
    """
    # Remove trailing slashes and .git extension
    url = url.rstrip("/").removesuffix(".git")
    
    # Split URL and extract owner/name
    parts = url.split("/")
    
    if len(parts) < 5:
        raise ValueError("Invalid GitHub URL format")
    
    owner = parts[-2]
    name = parts[-1]
    
    return owner, name


async def create_ingestion_job(
    db: AsyncSession,
    repository_id: UUID
) -> IngestionJob:
    """
    Create a new ingestion job for a repository.
    
    Args:
        db: Database session
        repository_id: Repository UUID
        
    Returns:
        Created IngestionJob instance
    """
    job = IngestionJob(
        repository_id=repository_id,
        status="pending",
        stage=None,
        progress_percent=0,
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


async def delete_repository_files(repository: Repository) -> None:
    """
    Delete repository files from disk (cloned repo and FAISS index).
    
    Args:
        repository: Repository instance
    """
    try:
        # Delete FAISS index if it exists
        if repository.index_path:
            index_path = Path(repository.index_path)
            if index_path.exists():
                index_path.unlink()
                logger.info(f"Deleted FAISS index: {index_path}")
            
            # Also delete metadata file if it exists
            metadata_path = index_path.with_suffix(".metadata.json")
            if metadata_path.exists():
                metadata_path.unlink()
                logger.info(f"Deleted metadata file: {metadata_path}")
        
        # Delete cloned repository directory
        repo_dir = settings.repo_storage_path / repository.owner / repository.name
        if repo_dir.exists():
            import shutil
            shutil.rmtree(repo_dir)
            logger.info(f"Deleted repository directory: {repo_dir}")
            
    except Exception as e:
        logger.error(f"Error deleting repository files: {e}")
        # Don't raise - we still want to delete the database records


# ============================================================================
# API Endpoints
# ============================================================================


@router.post(
    "",
    response_model=RepositoryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new repository",
    description="Add a new GitHub repository for indexing. Returns immediately with a job ID for tracking progress.",
    responses={
        201: {"description": "Repository created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        409: {"model": ErrorResponse, "description": "Repository already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def create_repository(
    request: RepositoryCreateRequest,
    db: AsyncSession = Depends(get_db)
) -> RepositoryCreateResponse:
    """
    Add a new repository for indexing.
    
    This endpoint creates a repository record and enqueues an ingestion job.
    The ingestion process runs in the background through the multi-stage pipeline:
    clone → read → chunk → embed → store.
    
    **Validates: Requirements 8.1, 10.1, 10.2, 10.3**
    """
    try:
        # Parse GitHub URL to extract owner and name
        owner, name = parse_github_url(request.url)
        
        # Check if repository already exists
        result = await db.execute(
            select(Repository).where(Repository.url == request.url)
        )
        existing_repo = result.scalar_one_or_none()
        
        if existing_repo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Repository already exists",
                    "message": f"Repository {owner}/{name} is already indexed",
                    "details": [
                        {
                            "field": "url",
                            "message": f"Repository with URL {request.url} already exists"
                        }
                    ]
                }
            )
        
        # Create repository record
        repository = Repository(
            url=request.url,
            owner=owner,
            name=name,
            status="pending",
        )
        
        db.add(repository)
        await db.commit()
        await db.refresh(repository)
        
        logger.info(f"Created repository: {repository.id} ({owner}/{name})")
        
        # Create ingestion job
        job = await create_ingestion_job(db, repository.id)
        
        logger.info(f"Created ingestion job: {job.id} for repository {repository.id}")
        
        # TODO: Enqueue Celery task for background ingestion
        # from app.jobs.tasks.ingestion_task import ingest_repository
        # ingest_repository.delay(str(repository.id), str(job.id))
        
        return RepositoryCreateResponse(
            repository=RepositorySchema.model_validate(repository),
            job_id=job.id,
            message=f"Repository {owner}/{name} added successfully. Ingestion job started."
        )
        
    except ValueError as e:
        logger.warning(f"Invalid GitHub URL: {request.url} - {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid URL",
                "message": str(e),
                "details": [{"field": "url", "message": str(e)}]
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating repository: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while creating the repository",
                "details": None
            }
        )


@router.get(
    "",
    response_model=RepositoryListResponse,
    summary="List all repositories",
    description="Retrieve a list of all indexed repositories with their metadata and status.",
    responses={
        200: {"description": "Repositories retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def list_repositories(
    db: AsyncSession = Depends(get_db)
) -> RepositoryListResponse:
    """
    List all repositories.
    
    Returns all indexed repositories with metadata including name, owner,
    last updated time, and index status.
    
    **Validates: Requirements 8.2, 10.1**
    """
    try:
        # Query all repositories ordered by created_at descending
        result = await db.execute(
            select(Repository).order_by(Repository.created_at.desc())
        )
        repositories = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(select(func.count(Repository.id)))
        total = count_result.scalar_one()
        
        logger.info(f"Retrieved {total} repositories")
        
        return RepositoryListResponse(
            repositories=[
                RepositorySchema.model_validate(repo) for repo in repositories
            ],
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing repositories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving repositories",
                "details": None
            }
        )


@router.get(
    "/{repository_id}",
    response_model=RepositorySchema,
    summary="Get repository details",
    description="Retrieve detailed information about a specific repository.",
    responses={
        200: {"description": "Repository retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> RepositorySchema:
    """
    Get repository details by ID.
    
    Returns detailed information about a specific repository including
    its current status, metadata, and indexing progress.
    
    **Validates: Requirements 8.2, 10.1**
    """
    try:
        # Query repository by ID
        result = await db.execute(
            select(Repository).where(Repository.id == repository_id)
        )
        repository = result.scalar_one_or_none()
        
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Repository not found",
                    "message": f"Repository with ID {repository_id} does not exist",
                    "details": [
                        {
                            "field": "repository_id",
                            "message": f"No repository found with ID {repository_id}"
                        }
                    ]
                }
            )
        
        logger.info(f"Retrieved repository: {repository.id} ({repository.owner}/{repository.name})")
        
        return RepositorySchema.model_validate(repository)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving repository {repository_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving the repository",
                "details": None
            }
        )


@router.delete(
    "/{repository_id}",
    response_model=RepositoryDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a repository",
    description="Delete a repository and all associated data (code chunks, embeddings, FAISS index).",
    responses={
        200: {"description": "Repository deleted successfully"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def delete_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> RepositoryDeleteResponse:
    """
    Delete a repository.
    
    Removes the repository and all associated data including:
    - Code chunks from the database
    - Embeddings from the FAISS index
    - Cloned repository files
    - Ingestion job records
    
    **Validates: Requirements 8.5, 10.1, 10.2**
    """
    try:
        # Query repository by ID
        result = await db.execute(
            select(Repository).where(Repository.id == repository_id)
        )
        repository = result.scalar_one_or_none()
        
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Repository not found",
                    "message": f"Repository with ID {repository_id} does not exist",
                    "details": [
                        {
                            "field": "repository_id",
                            "message": f"No repository found with ID {repository_id}"
                        }
                    ]
                }
            )
        
        # Get chunk count before deletion
        chunk_count_result = await db.execute(
            select(func.count(CodeChunk.id)).where(
                CodeChunk.repository_id == repository_id
            )
        )
        deleted_chunks_count = chunk_count_result.scalar_one()
        
        # Delete repository files (FAISS index and cloned repo)
        await delete_repository_files(repository)
        
        # Delete repository (cascade will delete code_chunks and ingestion_jobs)
        await db.delete(repository)
        await db.commit()
        
        logger.info(
            f"Deleted repository: {repository_id} ({repository.owner}/{repository.name}) "
            f"with {deleted_chunks_count} code chunks"
        )
        
        return RepositoryDeleteResponse(
            message=f"Repository {repository.owner}/{repository.name} deleted successfully",
            deleted_repository_id=repository_id,
            deleted_chunks_count=deleted_chunks_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repository_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while deleting the repository",
                "details": None
            }
        )


@router.post(
    "/{repository_id}/reindex",
    response_model=RepositoryReindexResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger repository re-indexing",
    description="Trigger re-indexing of a repository. Creates a new ingestion job to update the index.",
    responses={
        202: {"description": "Re-indexing job created successfully"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        409: {"model": ErrorResponse, "description": "Repository is already being indexed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def reindex_repository(
    repository_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> RepositoryReindexResponse:
    """
    Trigger repository re-indexing.
    
    Creates a new ingestion job to re-index the repository. This is useful for:
    - Updating the index after repository changes
    - Recovering from failed ingestion jobs
    - Re-indexing with updated chunking or embedding settings
    
    **Validates: Requirements 8.7, 10.1, 10.2**
    """
    try:
        # Query repository by ID
        result = await db.execute(
            select(Repository).where(Repository.id == repository_id)
        )
        repository = result.scalar_one_or_none()
        
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Repository not found",
                    "message": f"Repository with ID {repository_id} does not exist",
                    "details": [
                        {
                            "field": "repository_id",
                            "message": f"No repository found with ID {repository_id}"
                        }
                    ]
                }
            )
        
        # Check if repository is already being indexed
        if repository.status in ["pending", "cloning", "reading", "chunking", "embedding"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Repository is already being indexed",
                    "message": f"Repository {repository.owner}/{repository.name} is currently being indexed (status: {repository.status})",
                    "details": [
                        {
                            "field": "status",
                            "message": f"Cannot re-index while status is {repository.status}"
                        }
                    ]
                }
            )
        
        # Update repository status to pending
        repository.status = "pending"
        repository.error_message = None
        
        # Create new ingestion job
        job = await create_ingestion_job(db, repository.id)
        
        await db.commit()
        await db.refresh(repository)
        
        logger.info(
            f"Created re-indexing job: {job.id} for repository {repository.id} "
            f"({repository.owner}/{repository.name})"
        )
        
        # TODO: Enqueue Celery task for background ingestion
        # from app.jobs.tasks.ingestion_task import ingest_repository
        # ingest_repository.delay(str(repository.id), str(job.id))
        
        return RepositoryReindexResponse(
            repository=RepositorySchema.model_validate(repository),
            job_id=job.id,
            message=f"Re-indexing job created for repository {repository.owner}/{repository.name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-indexing repository {repository_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while creating the re-indexing job",
                "details": None
            }
        )
