"""
Celery tasks for repository ingestion pipeline.

This module implements the five-stage ingestion pipeline:
1. clone_repository: Clone the GitHub repository
2. read_source_files: Read and filter source code files
3. chunk_code_files: Split files into chunks
4. generate_embeddings: Generate embeddings for chunks
5. store_embeddings: Store embeddings in FAISS index

Requirements:
- 2.1: Execute five sequential stages: clone, read, chunk, embed, and store
- 2.2: Clone the repository and validate its structure
- 2.3: Read all source code files and filter out binary files, dependencies, and build artifacts
- 2.4: Split code files into Code_Chunks with configurable size limits
- 2.5: Preserve file path, line numbers, and language metadata
- 2.6: Generate embeddings for all Code_Chunks
- 2.7: Persist embeddings to a repository-specific FAISS_Index
- 2.12: Log errors, mark stage as failed, and halt pipeline on failure
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

import numpy as np
from celery import Task, chain
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.embeddings.embedder import get_embedding_service
from app.core.vectorstore.vector_store import get_vector_store_manager
from app.database import get_session_maker
from app.jobs.worker import celery_app
from app.models.orm import Repository, IngestionJob, CodeChunk
from app.services.repository_service import RepositoryService
from app.core.ingestion.file_reader import FileReader
from app.services.chunking_service import ChunkingService

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions for Database Operations
# ============================================================================

async def update_job_status(
    job_id: UUID,
    status: str,
    stage: Optional[str] = None,
    progress_percent: Optional[int] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Update ingestion job status in the database.
    
    Args:
        job_id: UUID of the ingestion job
        status: New status (pending, running, completed, failed)
        stage: Current pipeline stage (clone, read, chunk, embed, store)
        progress_percent: Progress percentage (0-100)
        error_message: Error message if status is 'failed'
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # Get the job
            result = await session.execute(
                select(IngestionJob).where(IngestionJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if job is None:
                logger.error(f"Ingestion job {job_id} not found")
                return
            
            # Update fields
            job.status = status
            if stage is not None:
                job.stage = stage
            if progress_percent is not None:
                job.progress_percent = progress_percent
            if error_message is not None:
                job.error_message = error_message
            
            # Update timestamps
            if status == "running" and job.started_at is None:
                job.started_at = datetime.utcnow()
            elif status in ("completed", "failed"):
                job.completed_at = datetime.utcnow()
            
            await session.commit()
            logger.info(
                f"Updated job {job_id}: status={status}, stage={stage}, "
                f"progress={progress_percent}%"
            )
            
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            await session.rollback()


async def update_repository_status(
    repository_id: UUID,
    status: str,
    error_message: Optional[str] = None,
    chunk_count: Optional[int] = None,
    index_path: Optional[str] = None,
) -> None:
    """
    Update repository status in the database.
    
    Args:
        repository_id: UUID of the repository
        status: New status
        error_message: Error message if status is 'failed'
        chunk_count: Number of chunks indexed
        index_path: Path to the FAISS index
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # Get the repository
            result = await session.execute(
                select(Repository).where(Repository.id == repository_id)
            )
            repo = result.scalar_one_or_none()
            
            if repo is None:
                logger.error(f"Repository {repository_id} not found")
                return
            
            # Update fields
            repo.status = status
            if error_message is not None:
                repo.error_message = error_message
            if chunk_count is not None:
                repo.chunk_count = chunk_count
            if index_path is not None:
                repo.index_path = index_path
            
            repo.updated_at = datetime.utcnow()
            
            await session.commit()
            logger.info(f"Updated repository {repository_id}: status={status}")
            
        except Exception as e:
            logger.error(f"Failed to update repository status: {e}")
            await session.rollback()


async def save_code_chunks(
    repository_id: UUID,
    chunks: List[Dict],
) -> None:
    """
    Save code chunks to the database.
    
    Args:
        repository_id: UUID of the repository
        chunks: List of chunk dictionaries with metadata
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # Create CodeChunk objects
            code_chunks = []
            for i, chunk_data in enumerate(chunks):
                code_chunk = CodeChunk(
                    repository_id=repository_id,
                    file_path=chunk_data["file_path"],
                    start_line=chunk_data["start_line"],
                    end_line=chunk_data["end_line"],
                    language=chunk_data["language"],
                    content=chunk_data["content"],
                    embedding_id=i,  # Index in FAISS
                )
                code_chunks.append(code_chunk)
            
            # Bulk insert
            session.add_all(code_chunks)
            await session.commit()
            
            logger.info(f"Saved {len(code_chunks)} code chunks for repository {repository_id}")
            
        except Exception as e:
            logger.error(f"Failed to save code chunks: {e}")
            await session.rollback()
            raise


# ============================================================================
# Custom Task Base Class with Error Handling
# ============================================================================

class IngestionTask(Task):
    """
    Base class for ingestion tasks with error handling.
    
    This class provides common error handling and retry logic for all
    ingestion tasks.
    """
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failure.
        
        Args:
            exc: The exception raised
            task_id: Unique ID of the failed task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
            einfo: Exception info
        """
        logger.error(
            f"Task {self.name} failed: {exc}\n"
            f"Task ID: {task_id}\n"
            f"Args: {args}\n"
            f"Kwargs: {kwargs}\n"
            f"Exception info: {einfo}"
        )
        
        # Update job status if job_id is provided
        if "job_id" in kwargs:
            job_id = kwargs["job_id"]
            asyncio.run(
                update_job_status(
                    job_id=UUID(job_id),
                    status="failed",
                    error_message=str(exc),
                )
            )
        
        # Update repository status if repository_id is provided
        if "repository_id" in kwargs:
            repository_id = kwargs["repository_id"]
            asyncio.run(
                update_repository_status(
                    repository_id=UUID(repository_id),
                    status="failed",
                    error_message=str(exc),
                )
            )


# ============================================================================
# Stage 1: Clone Repository
# ============================================================================

@celery_app.task(
    bind=True,
    base=IngestionTask,
    name="app.jobs.tasks.ingestion_tasks.clone_repository",
)
def clone_repository(
    self,
    repository_id: str,
    repository_url: str,
    job_id: str,
    auth_token: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
) -> Dict:
    """
    Stage 1: Clone a GitHub repository.
    
    Args:
        repository_id: UUID of the repository (string)
        repository_url: GitHub repository URL
        job_id: UUID of the ingestion job (string)
        auth_token: Optional GitHub personal access token
        ssh_key_path: Optional path to SSH private key
    
    Returns:
        Dict with repository metadata:
        - repository_id: UUID string
        - url: Repository URL
        - owner: Repository owner
        - name: Repository name
        - path: Local storage path
        - branch: Default branch
        - commit_hash: Latest commit SHA
    
    Raises:
        Exception: If cloning fails
    
    Requirements:
        - 2.2: Clone the repository and validate its structure
    """
    logger.info(f"Starting clone_repository task for {repository_url}")
    
    # Update job status
    asyncio.run(
        update_job_status(
            job_id=UUID(job_id),
            status="running",
            stage="clone",
            progress_percent=0,
        )
    )
    
    # Update repository status
    asyncio.run(
        update_repository_status(
            repository_id=UUID(repository_id),
            status="cloning",
        )
    )
    
    try:
        # Initialize repository service
        repo_service = RepositoryService()
        
        # Clone repository
        metadata = asyncio.run(
            repo_service.clone_repository(
                url=repository_url,
                auth_token=auth_token,
                ssh_key_path=ssh_key_path,
            )
        )
        
        # Update job progress
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="running",
                stage="clone",
                progress_percent=20,
            )
        )
        
        logger.info(f"Successfully cloned repository {repository_url}")
        
        # Return metadata for next stage
        return {
            "repository_id": repository_id,
            "job_id": job_id,
            "url": metadata["url"],
            "owner": metadata["owner"],
            "name": metadata["name"],
            "path": metadata["path"],
            "branch": metadata["branch"],
            "commit_hash": metadata["commit_hash"],
        }
        
    except Exception as e:
        logger.error(f"Failed to clone repository {repository_url}: {e}")
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="failed",
                stage="clone",
                error_message=str(e),
            )
        )
        
        # Update repository status
        asyncio.run(
            update_repository_status(
                repository_id=UUID(repository_id),
                status="failed",
                error_message=str(e),
            )
        )
        
        raise


# ============================================================================
# Stage 2: Read Source Files
# ============================================================================

@celery_app.task(
    bind=True,
    base=IngestionTask,
    name="app.jobs.tasks.ingestion_tasks.read_source_files",
)
def read_source_files(
    self,
    metadata: Dict,
) -> Dict:
    """
    Stage 2: Read and filter source code files.
    
    Args:
        metadata: Dictionary from clone_repository stage
    
    Returns:
        Dict with file information:
        - repository_id: UUID string
        - job_id: UUID string
        - path: Repository path
        - files: List of file info dictionaries
    
    Raises:
        Exception: If reading files fails
    
    Requirements:
        - 2.3: Read all source code files and filter out binary files,
               dependencies, and build artifacts
    """
    repository_id = metadata["repository_id"]
    job_id = metadata["job_id"]
    repo_path = metadata["path"]
    
    logger.info(f"Starting read_source_files task for repository {repository_id}")
    
    # Update job status
    asyncio.run(
        update_job_status(
            job_id=UUID(job_id),
            status="running",
            stage="read",
            progress_percent=20,
        )
    )
    
    # Update repository status
    asyncio.run(
        update_repository_status(
            repository_id=UUID(repository_id),
            status="reading",
        )
    )
    
    try:
        # Initialize file reader
        file_reader = FileReader(
            repository_path=repo_path,
            include_hidden=False,
            max_file_size_mb=10.0,
        )
        
        # Read source files
        file_infos = file_reader.read_files()
        
        logger.info(f"Found {len(file_infos)} source files in repository {repository_id}")
        
        # Convert FileInfo objects to dictionaries
        files = [
            {
                "absolute_path": fi.absolute_path,
                "relative_path": fi.relative_path,
                "language": fi.language,
                "size_bytes": fi.size_bytes,
            }
            for fi in file_infos
        ]
        
        # Update job progress
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="running",
                stage="read",
                progress_percent=40,
            )
        )
        
        logger.info(f"Successfully read {len(files)} source files")
        
        # Return data for next stage
        return {
            "repository_id": repository_id,
            "job_id": job_id,
            "path": repo_path,
            "files": files,
        }
        
    except Exception as e:
        logger.error(f"Failed to read source files: {e}")
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="failed",
                stage="read",
                error_message=str(e),
            )
        )
        
        # Update repository status
        asyncio.run(
            update_repository_status(
                repository_id=UUID(repository_id),
                status="failed",
                error_message=str(e),
            )
        )
        
        raise


# ============================================================================
# Stage 3: Chunk Code Files
# ============================================================================

@celery_app.task(
    bind=True,
    base=IngestionTask,
    name="app.jobs.tasks.ingestion_tasks.chunk_code_files",
)
def chunk_code_files(
    self,
    data: Dict,
) -> Dict:
    """
    Stage 3: Split code files into chunks.
    
    Args:
        data: Dictionary from read_source_files stage
    
    Returns:
        Dict with chunk information:
        - repository_id: UUID string
        - job_id: UUID string
        - chunks: List of chunk dictionaries
    
    Raises:
        Exception: If chunking fails
    
    Requirements:
        - 2.4: Split code files into Code_Chunks with configurable size limits
        - 2.5: Preserve file path, line numbers, and language metadata
    """
    repository_id = data["repository_id"]
    job_id = data["job_id"]
    files = data["files"]
    
    logger.info(f"Starting chunk_code_files task for repository {repository_id}")
    
    # Update job status
    asyncio.run(
        update_job_status(
            job_id=UUID(job_id),
            status="running",
            stage="chunk",
            progress_percent=40,
        )
    )
    
    # Update repository status
    asyncio.run(
        update_repository_status(
            repository_id=UUID(repository_id),
            status="chunking",
        )
    )
    
    try:
        # Initialize chunking service
        settings = get_settings()
        chunking_service = ChunkingService(settings=settings)
        
        # Chunk all files
        all_chunks = []
        total_files = len(files)
        
        for i, file_info in enumerate(files):
            try:
                # Read file content
                with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Chunk the file
                chunks = chunking_service.chunk_file(
                    file_path=file_info["relative_path"],
                    content=content,
                )
                
                # Convert CodeChunk objects to dictionaries
                for chunk in chunks:
                    all_chunks.append(chunk.to_dict())
                
                # Update progress periodically
                if (i + 1) % 10 == 0 or (i + 1) == total_files:
                    progress = 40 + int((i + 1) / total_files * 20)
                    asyncio.run(
                        update_job_status(
                            job_id=UUID(job_id),
                            status="running",
                            stage="chunk",
                            progress_percent=progress,
                        )
                    )
                
            except Exception as e:
                logger.warning(f"Failed to chunk file {file_info['relative_path']}: {e}")
                continue
        
        logger.info(f"Successfully chunked {len(all_chunks)} chunks from {total_files} files")
        
        # Return data for next stage
        return {
            "repository_id": repository_id,
            "job_id": job_id,
            "chunks": all_chunks,
        }
        
    except Exception as e:
        logger.error(f"Failed to chunk code files: {e}")
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="failed",
                stage="chunk",
                error_message=str(e),
            )
        )
        
        # Update repository status
        asyncio.run(
            update_repository_status(
                repository_id=UUID(repository_id),
                status="failed",
                error_message=str(e),
            )
        )
        
        raise


# ============================================================================
# Stage 4: Generate Embeddings
# ============================================================================

@celery_app.task(
    bind=True,
    base=IngestionTask,
    name="app.jobs.tasks.ingestion_tasks.generate_embeddings",
)
def generate_embeddings(
    self,
    data: Dict,
) -> Dict:
    """
    Stage 4: Generate embeddings for code chunks.
    
    Args:
        data: Dictionary from chunk_code_files stage
    
    Returns:
        Dict with embeddings:
        - repository_id: UUID string
        - job_id: UUID string
        - chunks: List of chunk dictionaries
        - embeddings: Numpy array of embeddings
    
    Raises:
        Exception: If embedding generation fails
    
    Requirements:
        - 2.6: Generate embeddings for all Code_Chunks
    """
    repository_id = data["repository_id"]
    job_id = data["job_id"]
    chunks = data["chunks"]
    
    logger.info(f"Starting generate_embeddings task for repository {repository_id}")
    
    # Update job status
    asyncio.run(
        update_job_status(
            job_id=UUID(job_id),
            status="running",
            stage="embed",
            progress_percent=60,
        )
    )
    
    # Update repository status
    asyncio.run(
        update_repository_status(
            repository_id=UUID(repository_id),
            status="embedding",
        )
    )
    
    try:
        # Initialize embedding service
        embedding_service = get_embedding_service()
        
        # Extract chunk contents
        chunk_contents = [chunk["content"] for chunk in chunks]
        
        logger.info(f"Generating embeddings for {len(chunk_contents)} chunks")
        
        # Generate embeddings in batches
        embeddings = embedding_service.embed_batch(
            texts=chunk_contents,
            show_progress=False,
        )
        
        # Normalize embeddings for cosine similarity
        # (FAISS IndexFlatIP expects normalized vectors)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        
        # Update job progress
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="running",
                stage="embed",
                progress_percent=80,
            )
        )
        
        # Return data for next stage
        # Note: We convert numpy array to list for JSON serialization
        return {
            "repository_id": repository_id,
            "job_id": job_id,
            "chunks": chunks,
            "embeddings": embeddings.tolist(),
        }
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="failed",
                stage="embed",
                error_message=str(e),
            )
        )
        
        # Update repository status
        asyncio.run(
            update_repository_status(
                repository_id=UUID(repository_id),
                status="failed",
                error_message=str(e),
            )
        )
        
        raise


# ============================================================================
# Stage 5: Store Embeddings
# ============================================================================

@celery_app.task(
    bind=True,
    base=IngestionTask,
    name="app.jobs.tasks.ingestion_tasks.store_embeddings",
)
def store_embeddings(
    self,
    data: Dict,
) -> Dict:
    """
    Stage 5: Store embeddings in FAISS index.
    
    Args:
        data: Dictionary from generate_embeddings stage
    
    Returns:
        Dict with completion status:
        - repository_id: UUID string
        - job_id: UUID string
        - chunk_count: Number of chunks stored
        - index_path: Path to FAISS index
    
    Raises:
        Exception: If storing embeddings fails
    
    Requirements:
        - 2.7: Persist embeddings to a repository-specific FAISS_Index
        - 2.13: Persist the FAISS_Index to disk with repository metadata
    """
    repository_id = data["repository_id"]
    job_id = data["job_id"]
    chunks = data["chunks"]
    embeddings_list = data["embeddings"]
    
    logger.info(f"Starting store_embeddings task for repository {repository_id}")
    
    # Update job status
    asyncio.run(
        update_job_status(
            job_id=UUID(job_id),
            status="running",
            stage="store",
            progress_percent=80,
        )
    )
    
    # Update repository status
    asyncio.run(
        update_repository_status(
            repository_id=UUID(repository_id),
            status="storing",
        )
    )
    
    try:
        # Convert embeddings back to numpy array
        embeddings = np.array(embeddings_list, dtype=np.float32)
        
        # Initialize vector store manager
        vector_store_manager = get_vector_store_manager()
        
        # Get or create vector store for this repository
        repo_uuid = UUID(repository_id)
        vector_store = vector_store_manager.get_store(
            repository_id=repo_uuid,
            create_if_missing=True,
        )
        
        logger.info(f"Adding {len(embeddings)} embeddings to vector store")
        
        # Add embeddings to vector store
        vector_store.add_embeddings(
            embeddings=embeddings,
            chunks_metadata=chunks,
        )
        
        # Save vector store to disk
        vector_store.save()
        
        logger.info(f"Successfully stored embeddings for repository {repository_id}")
        
        # Save code chunks to database
        asyncio.run(
            save_code_chunks(
                repository_id=repo_uuid,
                chunks=chunks,
            )
        )
        
        # Update repository status
        index_path = str(vector_store.index_path)
        asyncio.run(
            update_repository_status(
                repository_id=repo_uuid,
                status="completed",
                chunk_count=len(chunks),
                index_path=index_path,
            )
        )
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="completed",
                stage="store",
                progress_percent=100,
            )
        )
        
        logger.info(f"Ingestion pipeline completed for repository {repository_id}")
        
        # Return completion status
        return {
            "repository_id": repository_id,
            "job_id": job_id,
            "chunk_count": len(chunks),
            "index_path": index_path,
            "status": "completed",
        }
        
    except Exception as e:
        logger.error(f"Failed to store embeddings: {e}")
        
        # Update job status
        asyncio.run(
            update_job_status(
                job_id=UUID(job_id),
                status="failed",
                stage="store",
                error_message=str(e),
            )
        )
        
        # Update repository status
        asyncio.run(
            update_repository_status(
                repository_id=UUID(repository_id),
                status="failed",
                error_message=str(e),
            )
        )
        
        raise


# ============================================================================
# Pipeline Orchestration
# ============================================================================

def create_ingestion_pipeline(
    repository_id: str,
    repository_url: str,
    job_id: str,
    auth_token: Optional[str] = None,
    ssh_key_path: Optional[str] = None,
) -> chain:
    """
    Create a Celery chain for the complete ingestion pipeline.
    
    This function creates a chain of tasks that execute sequentially:
    1. clone_repository
    2. read_source_files
    3. chunk_code_files
    4. generate_embeddings
    5. store_embeddings
    
    Args:
        repository_id: UUID of the repository (string)
        repository_url: GitHub repository URL
        job_id: UUID of the ingestion job (string)
        auth_token: Optional GitHub personal access token
        ssh_key_path: Optional path to SSH private key
    
    Returns:
        Celery chain object
    
    Example:
        >>> pipeline = create_ingestion_pipeline(
        ...     repository_id="123e4567-e89b-12d3-a456-426614174000",
        ...     repository_url="https://github.com/owner/repo",
        ...     job_id="123e4567-e89b-12d3-a456-426614174001",
        ... )
        >>> result = pipeline.apply_async()
    """
    return chain(
        clone_repository.s(
            repository_id=repository_id,
            repository_url=repository_url,
            job_id=job_id,
            auth_token=auth_token,
            ssh_key_path=ssh_key_path,
        ),
        read_source_files.s(),
        chunk_code_files.s(),
        generate_embeddings.s(),
        store_embeddings.s(),
    )
