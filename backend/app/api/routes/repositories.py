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
        
        # Start ingestion pipeline by triggering Celery tasks directly
        try:
            # Import here to avoid circular dependency
            from app.jobs.tasks.ingestion_tasks import create_ingestion_pipeline
            
            # Create Celery task chain
            pipeline = create_ingestion_pipeline(
                repository_id=str(repository.id),
                repository_url=request.url,
                job_id=str(job.id),
                auth_token=None,  # TODO: Add auth token support
                ssh_key_path=None,
            )
            
            # Trigger the pipeline asynchronously
            logger.info(f"About to queue Celery pipeline for job {job.id}")
            result = pipeline.apply_async(queue='ingestion')
            celery_task_id = result.id
            logger.info(f"Started Celery pipeline {celery_task_id} for job {job.id}")
        except Exception as e:
            logger.error(f"Failed to start ingestion pipeline: {e}", exc_info=True)
            # Don't fail the request, job is already created
        
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
        
        # Calculate total_files and total_chunks for each repository
        repo_schemas = []
        for repo in repositories:
            # Query to get distinct file count and total chunks
            stats_result = await db.execute(
                select(
                    func.count(func.distinct(CodeChunk.file_path)).label('total_files'),
                    func.count(CodeChunk.id).label('total_chunks')
                ).where(CodeChunk.repository_id == repo.id)
            )
            stats = stats_result.one()
            
            # Convert to schema and add calculated fields
            repo_dict = {
                "id": repo.id,
                "url": repo.url,
                "owner": repo.owner,
                "name": repo.name,
                "default_branch": repo.default_branch,
                "last_commit_hash": repo.last_commit_hash,
                "status": repo.status,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "error_message": repo.error_message,
                "chunk_count": repo.chunk_count,
                "index_path": repo.index_path,
                "total_files": stats.total_files,
                "total_chunks": stats.total_chunks,
                "indexed_at": repo.updated_at if repo.status == "completed" else None,
            }
            repo_schemas.append(RepositorySchema(**repo_dict))
        
        logger.info(f"Retrieved {total} repositories")
        
        return RepositoryListResponse(
            repositories=repo_schemas,
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
    "/stats/languages",
    summary="Get language statistics",
    description="Retrieve language breakdown statistics across all repositories.",
    responses={
        200: {"description": "Language statistics retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_language_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get language statistics across all repositories.
    
    Returns the distribution of programming languages based on code chunks.
    """
    try:
        # Query language statistics
        result = await db.execute(
            select(
                CodeChunk.language,
                func.count(CodeChunk.id).label('chunk_count')
            ).group_by(CodeChunk.language).order_by(func.count(CodeChunk.id).desc())
        )
        
        language_stats = result.all()
        
        # Calculate total chunks
        total_chunks = sum(stat.chunk_count for stat in language_stats)
        
        # Format response with percentages
        languages = []
        for stat in language_stats:
            percentage = (stat.chunk_count / total_chunks * 100) if total_chunks > 0 else 0
            languages.append({
                "name": stat.language.title() if stat.language else "Unknown",
                "chunk_count": stat.chunk_count,
                "percentage": round(percentage, 1)
            })
        
        logger.info(f"Retrieved language statistics: {len(languages)} languages")
        
        return {
            "languages": languages,
            "total_chunks": total_chunks
        }
        
    except Exception as e:
        logger.error(f"Error retrieving language statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving language statistics",
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
        
        # Calculate total_files and total_chunks
        stats_result = await db.execute(
            select(
                func.count(func.distinct(CodeChunk.file_path)).label('total_files'),
                func.count(CodeChunk.id).label('total_chunks')
            ).where(CodeChunk.repository_id == repository_id)
        )
        stats = stats_result.one()
        
        # Convert to schema and add calculated fields
        repo_dict = {
            "id": repository.id,
            "url": repository.url,
            "owner": repository.owner,
            "name": repository.name,
            "default_branch": repository.default_branch,
            "last_commit_hash": repository.last_commit_hash,
            "status": repository.status,
            "created_at": repository.created_at,
            "updated_at": repository.updated_at,
            "error_message": repository.error_message,
            "chunk_count": repository.chunk_count,
            "index_path": repository.index_path,
            "total_files": stats.total_files,
            "total_chunks": stats.total_chunks,
            "indexed_at": repository.updated_at if repository.status == "completed" else None,
        }
        
        logger.info(f"Retrieved repository: {repository.id} ({repository.owner}/{repository.name})")
        
        return RepositorySchema(**repo_dict)
        
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


@router.get(
    "/{repository_id}/files",
    summary="List all files in a repository",
    description="Retrieve all unique file paths and their languages from a repository.",
)
async def list_repository_files(
    repository_id: UUID,
    language: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all files in a repository with language info.
    Optionally filter by language.
    """
    try:
        query = select(
            CodeChunk.file_path,
            CodeChunk.language,
            func.min(CodeChunk.start_line).label('start_line'),
            func.max(CodeChunk.end_line).label('end_line'),
            func.count(CodeChunk.id).label('chunk_count'),
        ).where(CodeChunk.repository_id == repository_id)

        if language:
            query = query.where(CodeChunk.language == language.lower())

        query = query.group_by(CodeChunk.file_path, CodeChunk.language).order_by(CodeChunk.file_path)

        result = await db.execute(query)
        files = result.all()

        return {
            "files": [
                {
                    "file_path": f.file_path,
                    "language": f.language,
                    "start_line": f.start_line,
                    "end_line": f.end_line,
                    "chunk_count": f.chunk_count,
                }
                for f in files
            ],
            "total": len(files),
        }

    except Exception as e:
        logger.error(f"Error listing files for repository {repository_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)}
        )


@router.get(
    "/{repository_id}/files/content",
    summary="Get file content from a repository",
    description="Retrieve all code chunks for a specific file path, assembled in order.",
)
async def get_file_content(
    repository_id: UUID,
    file_path: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the full content of a file by assembling its chunks in order.
    """
    try:
        result = await db.execute(
            select(CodeChunk)
            .where(
                CodeChunk.repository_id == repository_id,
                CodeChunk.file_path == file_path,
            )
            .order_by(CodeChunk.start_line)
        )
        chunks = result.scalars().all()

        if not chunks:
            raise HTTPException(status_code=404, detail={"error": "File not found"})

        # Assemble content from chunks
        full_content = "\n".join(chunk.content for chunk in chunks)
        language = chunks[0].language if chunks else None

        return {
            "file_path": file_path,
            "language": language,
            "content": full_content,
            "start_line": chunks[0].start_line,
            "end_line": chunks[-1].end_line,
            "chunk_count": len(chunks),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file content: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)}
        )
