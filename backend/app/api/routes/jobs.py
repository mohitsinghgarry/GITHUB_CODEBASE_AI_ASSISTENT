"""
API routes for job management.

This module implements RESTful endpoints for managing ingestion jobs,
including querying job status and retrying failed jobs.

Requirements:
- 3.1: Create an Ingestion_Job and return immediately with a job identifier
- 3.2: Allow users to query the job status
- 3.3: Update the job status to completed with success or failure indication
- 3.5: Store error details and allow retry when an Ingestion_Job fails
- 3.6: Provide progress updates including percentage complete and estimated time remaining
- 10.1: Expose RESTful endpoints for job management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.orm.ingestion_job import IngestionJob
from app.models.orm.repository import Repository
from app.models.schemas.job import (
    IngestionJobSchema,
    JobStatusResponse,
    JobRetryResponse,
    JobErrorResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/jobs", tags=["jobs"])


# ============================================================================
# Helper Functions
# ============================================================================


def calculate_estimated_time_remaining(job: IngestionJob) -> Optional[int]:
    """
    Calculate estimated time remaining for a job based on progress.
    
    Args:
        job: IngestionJob instance
        
    Returns:
        Estimated time remaining in seconds, or None if not calculable
    """
    # Only calculate for running jobs with progress > 0
    if job.status != "running" or job.progress_percent <= 0 or not job.started_at:
        return None
    
    # Calculate elapsed time
    elapsed_seconds = (datetime.utcnow() - job.started_at).total_seconds()
    
    # Avoid division by zero
    if job.progress_percent == 0:
        return None
    
    # Calculate estimated total time and remaining time
    estimated_total_seconds = (elapsed_seconds / job.progress_percent) * 100
    estimated_remaining_seconds = estimated_total_seconds - elapsed_seconds
    
    # Return as integer, minimum 0
    return max(0, int(estimated_remaining_seconds))


async def create_retry_job(
    db: AsyncSession,
    old_job: IngestionJob
) -> IngestionJob:
    """
    Create a new ingestion job as a retry of a failed job.
    
    Args:
        db: Database session
        old_job: The failed job to retry
        
    Returns:
        Created IngestionJob instance
    """
    new_job = IngestionJob(
        repository_id=old_job.repository_id,
        status="pending",
        stage=None,
        progress_percent=0,
        retry_count=old_job.retry_count + 1,
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    return new_job


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Retrieve the current status and progress of an ingestion job.",
    responses={
        200: {"description": "Job status retrieved successfully"},
        404: {"model": JobErrorResponse, "description": "Job not found"},
        500: {"model": JobErrorResponse, "description": "Internal server error"},
    }
)
async def get_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> JobStatusResponse:
    """
    Get job status and progress.
    
    Returns the current status of an ingestion job including:
    - Current status (pending, running, completed, failed)
    - Pipeline stage (clone, read, chunk, embed, store)
    - Progress percentage (0-100)
    - Estimated time remaining
    - Error message if failed
    
    **Validates: Requirements 3.2, 3.3, 3.6, 10.1, 10.2**
    """
    try:
        # Query job by ID
        result = await db.execute(
            select(IngestionJob).where(IngestionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Job not found",
                    "message": f"Ingestion job with ID {job_id} does not exist",
                    "details": [
                        {
                            "field": "job_id",
                            "message": f"No job found with ID {job_id}"
                        }
                    ]
                }
            )
        
        # Calculate estimated time remaining
        estimated_time_remaining = calculate_estimated_time_remaining(job)
        
        logger.info(
            f"Retrieved job status: {job.id} (status={job.status}, "
            f"stage={job.stage}, progress={job.progress_percent}%)"
        )
        
        return JobStatusResponse(
            job=IngestionJobSchema.model_validate(job),
            estimated_time_remaining=estimated_time_remaining
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving job status",
                "details": None
            }
        )


@router.post(
    "/{job_id}/retry",
    response_model=JobRetryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Retry a failed job",
    description="Create a new ingestion job to retry a failed job.",
    responses={
        201: {"description": "Retry job created successfully"},
        404: {"model": JobErrorResponse, "description": "Job not found"},
        409: {"model": JobErrorResponse, "description": "Job is not in failed state"},
        500: {"model": JobErrorResponse, "description": "Internal server error"},
    }
)
async def retry_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> JobRetryResponse:
    """
    Retry a failed ingestion job.
    
    Creates a new ingestion job to retry a failed job. The new job will:
    - Start from the beginning of the pipeline
    - Increment the retry count
    - Use the same repository as the original job
    
    Only jobs with status 'failed' can be retried.
    
    **Validates: Requirements 3.5, 10.1, 10.2**
    """
    try:
        # Query job by ID
        result = await db.execute(
            select(IngestionJob).where(IngestionJob.id == job_id)
        )
        old_job = result.scalar_one_or_none()
        
        if not old_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Job not found",
                    "message": f"Ingestion job with ID {job_id} does not exist",
                    "details": [
                        {
                            "field": "job_id",
                            "message": f"No job found with ID {job_id}"
                        }
                    ]
                }
            )
        
        # Check if job is in failed state
        if old_job.status != "failed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Job is not in failed state",
                    "message": f"Job {job_id} cannot be retried (current status: {old_job.status})",
                    "details": [
                        {
                            "field": "status",
                            "message": f"Only failed jobs can be retried. Current status: {old_job.status}"
                        }
                    ]
                }
            )
        
        # Get repository to update status
        repo_result = await db.execute(
            select(Repository).where(Repository.id == old_job.repository_id)
        )
        repository = repo_result.scalar_one_or_none()
        
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Repository not found",
                    "message": f"Repository {old_job.repository_id} not found for job {job_id}",
                    "details": None
                }
            )
        
        # Create new retry job
        new_job = await create_retry_job(db, old_job)
        
        # Update repository status to pending
        repository.status = "pending"
        repository.error_message = None
        await db.commit()
        await db.refresh(repository)
        
        logger.info(
            f"Created retry job {new_job.id} for failed job {job_id} "
            f"(repository={repository.id}, retry_count={new_job.retry_count})"
        )
        
        # TODO: Enqueue Celery task for background ingestion
        # from app.jobs.tasks.ingestion_task import ingest_repository
        # ingest_repository.delay(str(repository.id), str(new_job.id))
        
        return JobRetryResponse(
            message=f"Retry job created successfully for repository {repository.owner}/{repository.name}",
            old_job_id=old_job.id,
            new_job_id=new_job.id,
            repository_id=repository.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrying the job",
                "details": None
            }
        )
