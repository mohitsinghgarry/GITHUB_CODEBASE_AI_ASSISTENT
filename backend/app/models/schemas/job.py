"""
Pydantic schemas for ingestion job requests and responses.

This module defines the request and response models for job management operations.

Requirements:
- 3.1: Create an Ingestion_Job and return immediately with a job identifier
- 3.2: Allow users to query the job status
- 3.3: Update the job status to completed with success or failure indication
- 3.5: Store error details and allow retry when an Ingestion_Job fails
- 3.6: Provide progress updates including percentage complete and estimated time remaining
- 10.1: Expose RESTful endpoints for job management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Job Status Enum
# ============================================================================


class JobStatus:
    """Ingestion job status constants."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStage:
    """Ingestion pipeline stage constants."""
    
    CLONE = "clone"
    READ = "read"
    CHUNK = "chunk"
    EMBED = "embed"
    STORE = "store"


# ============================================================================
# Job Response Schemas
# ============================================================================


class IngestionJobSchema(BaseModel):
    """Schema for ingestion job details."""
    
    id: UUID = Field(..., description="Unique job identifier")
    repository_id: UUID = Field(..., description="Repository being indexed")
    status: str = Field(..., description="Current job status (pending, running, completed, failed)")
    stage: Optional[str] = Field(None, description="Current pipeline stage (clone, read, chunk, embed, store)")
    progress_percent: int = Field(0, ge=0, le=100, description="Progress percentage (0-100)")
    started_at: Optional[datetime] = Field(None, description="Timestamp when job started")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when job completed")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Response schema for job status query."""
    
    job: IngestionJobSchema = Field(..., description="Job details")
    estimated_time_remaining: Optional[int] = Field(
        None,
        description="Estimated time remaining in seconds (null if not available)"
    )
    
    class Config:
        from_attributes = True


class JobRetryResponse(BaseModel):
    """Response schema for job retry."""
    
    message: str = Field(..., description="Success message")
    old_job_id: UUID = Field(..., description="ID of the failed job")
    new_job_id: UUID = Field(..., description="ID of the new retry job")
    repository_id: UUID = Field(..., description="Repository being indexed")
    
    class Config:
        from_attributes = True


# ============================================================================
# Error Response Schemas
# ============================================================================


class JobErrorDetail(BaseModel):
    """Schema for job error details."""
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    
    class Config:
        from_attributes = True


class JobErrorResponse(BaseModel):
    """Schema for job error responses."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[list[JobErrorDetail]] = Field(None, description="Detailed error information")
    
    class Config:
        from_attributes = True
