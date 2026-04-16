"""
Celery worker configuration for background job processing.

This module defines the Celery application instance and configuration
for processing background ingestion jobs.

Requirements:
- 3.1: Create Ingestion_Job and return immediately with job identifier
- 3.2: Allow users to query job status while running
- 3.4: Support concurrent Ingestion_Jobs for different repositories
"""

import logging
from celery import Celery
from kombu import Exchange, Queue

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create Celery application
celery_app = Celery(
    "github_rag_assistant",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker crashes
    
    # Result backend settings
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,  # Store additional task metadata
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    worker_disable_rate_limits=False,
    
    # Queue settings
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Define queues
    task_queues=(
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "ingestion",
            Exchange("ingestion"),
            routing_key="ingestion",
            queue_arguments={"x-max-priority": 10},
        ),
    ),
    
    # Task routes
    task_routes={
        "app.jobs.tasks.ingestion_tasks.*": {"queue": "ingestion"},
    },
    
    # Retry settings
    task_autoretry_for=(Exception,),
    task_retry_kwargs={"max_retries": 3},
    task_retry_backoff=True,
    task_retry_backoff_max=600,  # Max 10 minutes between retries
    task_retry_jitter=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.jobs.tasks"])

logger.info("Celery worker initialized")


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    logger.info(f"Request: {self.request!r}")
    return {"status": "ok", "task_id": self.request.id}
