"""
Ingestion orchestration service for managing repository indexing jobs.

This service orchestrates the Celery task chains for repository ingestion,
provides job status tracking, retry logic, and incremental indexing support.

Requirements:
- 2.9: Support incremental indexing for repository updates
- 2.10: Re-execute only necessary stages for changed Code_Chunks
- 3.1: Create Ingestion_Job and return immediately with job identifier
- 3.2: Allow users to query job status
- 3.3: Update job status to completed with success/failure indication
- 3.5: Store error details and allow retry
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from celery.result import AsyncResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_session_maker
from app.models.orm import Repository, IngestionJob, CodeChunk
from app.services.repository_service import RepositoryService

logger = logging.getLogger(__name__)


class IngestionServiceError(Exception):
    """Base exception for ingestion service errors."""
    pass


class JobNotFoundError(IngestionServiceError):
    """Raised when a job is not found."""
    pass


class RepositoryNotFoundError(IngestionServiceError):
    """Raised when a repository is not found."""
    pass


class IngestionService:
    """
    Service for orchestrating repository ingestion jobs.
    
    This service provides:
    - Job creation and Celery task chain triggering
    - Job status tracking from database and Celery
    - Retry logic for failed jobs
    - Incremental indexing for repository updates
    """
    
    def __init__(self):
        """Initialize the ingestion service."""
        self.settings = get_settings()
        self.repo_service = RepositoryService()
        logger.info("IngestionService initialized")
    
    async def start_ingestion(
        self,
        repository_id: UUID,
        repository_url: str,
        auth_token: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Start a new ingestion job for a repository.
        
        This method creates an IngestionJob record in the database and triggers
        the Celery task chain for the five-stage ingestion pipeline.
        
        Args:
            repository_id: UUID of the repository
            repository_url: GitHub repository URL
            auth_token: Optional GitHub personal access token
            ssh_key_path: Optional path to SSH private key
            
        Returns:
            Dictionary with job information:
            - job_id: UUID of the created job
            - repository_id: UUID of the repository
            - status: Initial job status (pending)
            - celery_task_id: Celery task chain ID
            
        Raises:
            IngestionServiceError: If job creation fails
            
        Requirements:
            - 3.1: Create Ingestion_Job and return immediately with job identifier
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Create ingestion job record
                job = IngestionJob(
                    repository_id=repository_id,
                    status="pending",
                    stage=None,
                    progress_percent=0,
                    retry_count=0,
                )
                
                session.add(job)
                await session.commit()
                await session.refresh(job)
                
                job_id = job.id
                
                logger.info(
                    f"Created ingestion job {job_id} for repository {repository_id}"
                )
                
                # Import here to avoid circular dependency
                from app.jobs.tasks.ingestion_tasks import create_ingestion_pipeline
                
                # Create Celery task chain
                pipeline = create_ingestion_pipeline(
                    repository_id=str(repository_id),
                    repository_url=repository_url,
                    job_id=str(job_id),
                    auth_token=auth_token,
                    ssh_key_path=ssh_key_path,
                )
                
                # Trigger the pipeline asynchronously
                logger.info(f"About to queue Celery pipeline for job {job_id}")
                try:
                    result = pipeline.apply_async(queue='ingestion')
                    celery_task_id = result.id
                    logger.info(
                        f"Started Celery pipeline {celery_task_id} for job {job_id}"
                    )
                except Exception as e:
                    logger.error(f"Failed to queue Celery pipeline: {e}", exc_info=True)
                    raise
                
                return {
                    "job_id": str(job_id),
                    "repository_id": str(repository_id),
                    "status": "pending",
                    "celery_task_id": celery_task_id,
                }
                
            except Exception as e:
                logger.error(f"Failed to start ingestion job: {e}")
                await session.rollback()
                raise IngestionServiceError(
                    f"Failed to start ingestion job: {str(e)}"
                )
    
    async def get_job_status(self, job_id: UUID) -> Dict:
        """
        Get the current status of an ingestion job.
        
        This method queries the database for job status and also checks
        Celery for task state if the job is still running.
        
        Args:
            job_id: UUID of the ingestion job
            
        Returns:
            Dictionary with job status:
            - job_id: UUID of the job
            - repository_id: UUID of the repository
            - status: Current status (pending, running, completed, failed)
            - stage: Current pipeline stage (clone, read, chunk, embed, store)
            - progress_percent: Progress percentage (0-100)
            - started_at: Timestamp when job started
            - completed_at: Timestamp when job completed
            - error_message: Error message if status is 'failed'
            - retry_count: Number of retry attempts
            
        Raises:
            JobNotFoundError: If job is not found
            
        Requirements:
            - 3.2: Allow users to query job status
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Query job from database
                result = await session.execute(
                    select(IngestionJob).where(IngestionJob.id == job_id)
                )
                job = result.scalar_one_or_none()
                
                if job is None:
                    raise JobNotFoundError(f"Job {job_id} not found")
                
                # Build status response
                status_data = {
                    "job_id": str(job.id),
                    "repository_id": str(job.repository_id),
                    "status": job.status,
                    "stage": job.stage,
                    "progress_percent": job.progress_percent,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "retry_count": job.retry_count,
                }
                
                logger.debug(f"Retrieved status for job {job_id}: {job.status}")
                
                return status_data
                
            except JobNotFoundError:
                raise
            except Exception as e:
                logger.error(f"Failed to get job status: {e}")
                raise IngestionServiceError(
                    f"Failed to get job status: {str(e)}"
                )
    
    async def retry_job(self, job_id: UUID) -> Dict[str, str]:
        """
        Retry a failed ingestion job.
        
        This method creates a new job for the same repository and triggers
        the ingestion pipeline again. The original job is kept for history.
        
        Args:
            job_id: UUID of the failed job to retry
            
        Returns:
            Dictionary with new job information:
            - job_id: UUID of the new job
            - repository_id: UUID of the repository
            - status: Initial job status (pending)
            - celery_task_id: Celery task chain ID
            
        Raises:
            JobNotFoundError: If job is not found
            IngestionServiceError: If retry fails
            
        Requirements:
            - 3.5: Store error details and allow retry
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Get the failed job
                result = await session.execute(
                    select(IngestionJob).where(IngestionJob.id == job_id)
                )
                old_job = result.scalar_one_or_none()
                
                if old_job is None:
                    raise JobNotFoundError(f"Job {job_id} not found")
                
                if old_job.status != "failed":
                    raise IngestionServiceError(
                        f"Job {job_id} is not in failed state (current: {old_job.status})"
                    )
                
                # Get repository information
                repo_result = await session.execute(
                    select(Repository).where(Repository.id == old_job.repository_id)
                )
                repository = repo_result.scalar_one_or_none()
                
                if repository is None:
                    raise RepositoryNotFoundError(
                        f"Repository {old_job.repository_id} not found"
                    )
                
                logger.info(
                    f"Retrying failed job {job_id} for repository {repository.id}"
                )
                
                # Start a new ingestion job
                new_job_info = await self.start_ingestion(
                    repository_id=repository.id,
                    repository_url=repository.url,
                    auth_token=None,  # TODO: Store auth credentials securely
                    ssh_key_path=None,
                )
                
                # Update retry count on the new job
                new_job_result = await session.execute(
                    select(IngestionJob).where(
                        IngestionJob.id == UUID(new_job_info["job_id"])
                    )
                )
                new_job = new_job_result.scalar_one()
                new_job.retry_count = old_job.retry_count + 1
                await session.commit()
                
                logger.info(
                    f"Created retry job {new_job_info['job_id']} "
                    f"(retry count: {new_job.retry_count})"
                )
                
                return new_job_info
                
            except (JobNotFoundError, RepositoryNotFoundError):
                raise
            except Exception as e:
                logger.error(f"Failed to retry job: {e}")
                await session.rollback()
                raise IngestionServiceError(f"Failed to retry job: {str(e)}")
    
    async def check_for_updates(self, repository_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Check if a repository has updates available.
        
        This method compares the current commit hash in the database with
        the latest commit hash from the remote repository.
        
        Args:
            repository_id: UUID of the repository
            
        Returns:
            Tuple of (has_updates, latest_commit_hash)
            
        Raises:
            RepositoryNotFoundError: If repository is not found
            IngestionServiceError: If check fails
            
        Requirements:
            - 2.9: Support incremental indexing for repository updates
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Get repository from database
                result = await session.execute(
                    select(Repository).where(Repository.id == repository_id)
                )
                repository = result.scalar_one_or_none()
                
                if repository is None:
                    raise RepositoryNotFoundError(
                        f"Repository {repository_id} not found"
                    )
                
                # Check if repository exists locally
                if not self.repo_service.repository_exists(
                    repository.owner, repository.name
                ):
                    logger.info(
                        f"Repository {repository_id} not cloned locally, "
                        "full indexing required"
                    )
                    return True, None
                
                # Check for updates
                has_updates, latest_commit = await self.repo_service.has_updates(
                    repository.owner, repository.name
                )
                
                logger.info(
                    f"Repository {repository_id} update check: "
                    f"has_updates={has_updates}, "
                    f"current={repository.last_commit_hash[:7] if repository.last_commit_hash else 'none'}, "
                    f"latest={latest_commit[:7] if latest_commit else 'none'}"
                )
                
                return has_updates, latest_commit
                
            except RepositoryNotFoundError:
                raise
            except Exception as e:
                logger.error(f"Failed to check for updates: {e}")
                raise IngestionServiceError(
                    f"Failed to check for updates: {str(e)}"
                )
    
    async def start_incremental_indexing(
        self,
        repository_id: UUID,
        auth_token: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Start incremental indexing for a repository with updates.
        
        This method detects changed files since the last indexing and
        re-indexes only those files. It creates a modified ingestion job
        that skips unchanged files.
        
        Args:
            repository_id: UUID of the repository
            auth_token: Optional GitHub personal access token
            ssh_key_path: Optional path to SSH private key
            
        Returns:
            Dictionary with job information:
            - job_id: UUID of the created job
            - repository_id: UUID of the repository
            - status: Initial job status (pending)
            - celery_task_id: Celery task chain ID
            - incremental: True to indicate incremental indexing
            - changed_files_count: Number of files to re-index
            
        Raises:
            RepositoryNotFoundError: If repository is not found
            IngestionServiceError: If incremental indexing fails
            
        Requirements:
            - 2.9: Support incremental indexing for repository updates
            - 2.10: Re-execute only necessary stages for changed Code_Chunks
            
        Note:
            This is a simplified implementation. A full implementation would:
            1. Pull latest changes from git
            2. Use git diff to identify changed files
            3. Delete old chunks for changed files
            4. Re-index only changed files
            5. Update the FAISS index incrementally
            
            For now, this triggers a full re-indexing. The incremental logic
            should be implemented in the Celery tasks.
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Get repository from database
                result = await session.execute(
                    select(Repository).where(Repository.id == repository_id)
                )
                repository = result.scalar_one_or_none()
                
                if repository is None:
                    raise RepositoryNotFoundError(
                        f"Repository {repository_id} not found"
                    )
                
                # Check for updates
                has_updates, latest_commit = await self.check_for_updates(
                    repository_id
                )
                
                if not has_updates:
                    logger.info(
                        f"Repository {repository_id} is already up to date, "
                        "no incremental indexing needed"
                    )
                    return {
                        "job_id": None,
                        "repository_id": str(repository_id),
                        "status": "up_to_date",
                        "message": "Repository is already up to date",
                    }
                
                logger.info(
                    f"Starting incremental indexing for repository {repository_id}"
                )
                
                # TODO: Implement incremental indexing logic
                # For now, trigger a full re-indexing
                # A full implementation would:
                # 1. Pull latest changes
                # 2. Identify changed files using git diff
                # 3. Delete old chunks for changed files
                # 4. Create a modified pipeline that only processes changed files
                # 5. Update FAISS index incrementally
                
                # Start full re-indexing for now
                job_info = await self.start_ingestion(
                    repository_id=repository_id,
                    repository_url=repository.url,
                    auth_token=auth_token,
                    ssh_key_path=ssh_key_path,
                )
                
                job_info["incremental"] = True
                job_info["message"] = (
                    "Full re-indexing triggered. "
                    "Incremental indexing will be implemented in future versions."
                )
                
                logger.info(
                    f"Started incremental indexing job {job_info['job_id']} "
                    f"for repository {repository_id}"
                )
                
                return job_info
                
            except RepositoryNotFoundError:
                raise
            except Exception as e:
                logger.error(f"Failed to start incremental indexing: {e}")
                raise IngestionServiceError(
                    f"Failed to start incremental indexing: {str(e)}"
                )
    
    async def get_changed_files(
        self,
        repository_id: UUID,
        old_commit: str,
        new_commit: str,
    ) -> List[str]:
        """
        Get list of changed files between two commits.
        
        This is a helper method for incremental indexing that uses git diff
        to identify files that have changed between commits.
        
        Args:
            repository_id: UUID of the repository
            old_commit: Old commit hash
            new_commit: New commit hash
            
        Returns:
            List of file paths that have changed
            
        Raises:
            RepositoryNotFoundError: If repository is not found
            IngestionServiceError: If git diff fails
            
        Requirements:
            - 2.10: Re-execute only necessary stages for changed Code_Chunks
            
        Note:
            This method is a placeholder for future incremental indexing support.
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Get repository from database
                result = await session.execute(
                    select(Repository).where(Repository.id == repository_id)
                )
                repository = result.scalar_one_or_none()
                
                if repository is None:
                    raise RepositoryNotFoundError(
                        f"Repository {repository_id} not found"
                    )
                
                # Get repository path
                repo_path = self.repo_service.get_repository_path(
                    repository.owner, repository.name
                )
                
                if not repo_path.exists():
                    raise IngestionServiceError(
                        f"Repository path {repo_path} does not exist"
                    )
                
                # Run git diff to get changed files
                import subprocess
                
                cmd = [
                    "git",
                    "-C",
                    str(repo_path),
                    "diff",
                    "--name-only",
                    old_commit,
                    new_commit,
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                changed_files = [
                    line.strip()
                    for line in result.stdout.split("\n")
                    if line.strip()
                ]
                
                logger.info(
                    f"Found {len(changed_files)} changed files between "
                    f"{old_commit[:7]} and {new_commit[:7]}"
                )
                
                return changed_files
                
            except RepositoryNotFoundError:
                raise
            except subprocess.CalledProcessError as e:
                logger.error(f"Git diff failed: {e.stderr}")
                raise IngestionServiceError(f"Git diff failed: {e.stderr}")
            except Exception as e:
                logger.error(f"Failed to get changed files: {e}")
                raise IngestionServiceError(
                    f"Failed to get changed files: {str(e)}"
                )
    
    async def delete_chunks_for_files(
        self,
        repository_id: UUID,
        file_paths: List[str],
    ) -> int:
        """
        Delete code chunks for specific files.
        
        This is a helper method for incremental indexing that removes
        old chunks for files that have changed.
        
        Args:
            repository_id: UUID of the repository
            file_paths: List of file paths to delete chunks for
            
        Returns:
            Number of chunks deleted
            
        Raises:
            IngestionServiceError: If deletion fails
            
        Requirements:
            - 2.10: Re-execute only necessary stages for changed Code_Chunks
            
        Note:
            This method is a placeholder for future incremental indexing support.
        """
        session_maker = get_session_maker()
        async with session_maker() as session:
            try:
                # Delete chunks for the specified files
                from sqlalchemy import delete
                
                stmt = delete(CodeChunk).where(
                    CodeChunk.repository_id == repository_id,
                    CodeChunk.file_path.in_(file_paths),
                )
                
                result = await session.execute(stmt)
                deleted_count = result.rowcount
                
                await session.commit()
                
                logger.info(
                    f"Deleted {deleted_count} chunks for {len(file_paths)} files "
                    f"in repository {repository_id}"
                )
                
                return deleted_count
                
            except Exception as e:
                logger.error(f"Failed to delete chunks: {e}")
                await session.rollback()
                raise IngestionServiceError(f"Failed to delete chunks: {str(e)}")


# ============================================================================
# Singleton Instance
# ============================================================================

_ingestion_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    """
    Get the global ingestion service instance.
    
    Returns:
        IngestionService: The global ingestion service instance
    """
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
