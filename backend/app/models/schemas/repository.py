"""
Pydantic schemas for repository requests and responses.

This module defines the request and response models for repository management operations.

Requirements:
- 8.1: Support indexing and storing multiple repositories simultaneously
- 8.2: Return all indexed repositories with metadata
- 8.3: Support searching across all repositories or filtering by specific repositories
- 8.5: Remove all associated code chunks and embeddings when repository is deleted
- 8.7: Trigger re-indexing automatically or on-demand
- 10.1: Expose RESTful endpoints for repository management
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
- 10.3: Return error responses with descriptive messages
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ============================================================================
# Repository Status Enum
# ============================================================================


class RepositoryStatus:
    """Repository indexing status constants."""
    
    PENDING = "pending"
    CLONING = "cloning"
    READING = "reading"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Repository Request Schemas
# ============================================================================


class RepositoryCreateRequest(BaseModel):
    """Request schema for creating a new repository."""
    
    url: str = Field(
        ...,
        min_length=1,
        description="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )
    
    @field_validator("url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that the URL is a valid GitHub repository URL."""
        v = v.strip()
        
        # Basic validation - must contain github.com
        if "github.com" not in v.lower():
            raise ValueError("URL must be a GitHub repository URL")
        
        # Ensure it starts with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        
        # Remove trailing slashes
        v = v.rstrip("/")
        
        # Basic format check: should have owner/repo pattern
        parts = v.split("/")
        if len(parts) < 5:  # https://github.com/owner/repo
            raise ValueError("Invalid GitHub repository URL format")
        
        return v


class RepositoryUpdateRequest(BaseModel):
    """Request schema for updating repository metadata."""
    
    # Currently, repositories are primarily managed through re-indexing
    # This schema is reserved for future metadata updates
    pass


# ============================================================================
# Repository Response Schemas
# ============================================================================


class RepositoryMetadataSchema(BaseModel):
    """Schema for repository metadata."""
    
    owner: str = Field(..., description="Repository owner/organization name")
    name: str = Field(..., description="Repository name")
    default_branch: Optional[str] = Field(None, description="Default branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last indexed commit hash")
    chunk_count: int = Field(0, description="Number of code chunks indexed")
    
    class Config:
        from_attributes = True


class RepositorySchema(BaseModel):
    """Schema for repository details."""
    
    id: UUID = Field(..., description="Unique repository identifier")
    url: str = Field(..., description="GitHub repository URL")
    owner: str = Field(..., description="Repository owner/organization name")
    name: str = Field(..., description="Repository name")
    default_branch: Optional[str] = Field(None, description="Default branch name")
    last_commit_hash: Optional[str] = Field(None, description="Last indexed commit hash")
    status: str = Field(..., description="Current indexing status")
    created_at: datetime = Field(..., description="Timestamp when repository was added")
    updated_at: datetime = Field(..., description="Timestamp when repository was last updated")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")
    chunk_count: int = Field(0, description="Number of code chunks indexed")
    index_path: Optional[str] = Field(None, description="Path to FAISS index file")
    total_files: Optional[int] = Field(None, description="Total number of unique files indexed")
    total_chunks: Optional[int] = Field(None, description="Total number of code chunks (same as chunk_count)")
    indexed_at: Optional[datetime] = Field(None, description="Timestamp when repository was last indexed")
    
    class Config:
        from_attributes = True


class RepositoryListResponse(BaseModel):
    """Response schema for listing repositories."""
    
    repositories: List[RepositorySchema] = Field(..., description="List of repositories")
    total: int = Field(..., description="Total number of repositories")
    
    class Config:
        from_attributes = True


class RepositoryCreateResponse(BaseModel):
    """Response schema for repository creation."""
    
    repository: RepositorySchema = Field(..., description="Created repository details")
    job_id: UUID = Field(..., description="Ingestion job identifier")
    message: str = Field(..., description="Success message")
    
    class Config:
        from_attributes = True


class RepositoryDeleteResponse(BaseModel):
    """Response schema for repository deletion."""
    
    message: str = Field(..., description="Success message")
    deleted_repository_id: UUID = Field(..., description="ID of deleted repository")
    deleted_chunks_count: int = Field(0, description="Number of code chunks deleted")
    
    class Config:
        from_attributes = True


class RepositoryReindexResponse(BaseModel):
    """Response schema for repository re-indexing."""
    
    repository: RepositorySchema = Field(..., description="Repository details")
    job_id: UUID = Field(..., description="New ingestion job identifier")
    message: str = Field(..., description="Success message")
    
    class Config:
        from_attributes = True


# ============================================================================
# Error Response Schemas
# ============================================================================


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    
    class Config:
        from_attributes = True
