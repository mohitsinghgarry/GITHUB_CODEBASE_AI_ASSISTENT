"""
Background job processing with Celery.

This module provides Celery worker configuration and task definitions
for background processing of repository ingestion jobs.
"""

from app.jobs.worker import celery_app, debug_task
from app.jobs.tasks import (
    clone_repository,
    read_source_files,
    chunk_code_files,
    generate_embeddings,
    store_embeddings,
    create_ingestion_pipeline,
)

__all__ = [
    "celery_app",
    "debug_task",
    "clone_repository",
    "read_source_files",
    "chunk_code_files",
    "generate_embeddings",
    "store_embeddings",
    "create_ingestion_pipeline",
]
