"""
SQLAlchemy ORM model for ingestion_jobs table.

This module defines the IngestionJob model for tracking background ingestion tasks.

Requirements:
- 14.2: Persist ingestion job status to a database
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IngestionJob(Base):
    """
    IngestionJob model for tracking background ingestion tasks.
    
    Attributes:
        id: Unique identifier (UUID)
        repository_id: Foreign key to repositories table
        status: Current status (pending, running, completed, failed)
        stage: Current pipeline stage (clone, read, chunk, embed, store)
        progress_percent: Progress percentage (0-100)
        started_at: Timestamp when job started
        completed_at: Timestamp when job completed
        error_message: Error message if status is 'failed'
        retry_count: Number of retry attempts
    """
    
    __tablename__ = "ingestion_jobs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default="gen_random_uuid()",
    )
    
    # Foreign key to repository
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Job status
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
        index=True,
    )
    
    # Pipeline stage
    stage: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Progress tracking
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    
    # Error handling
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Retry tracking
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="ingestion_jobs",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_job_repo_status", "repository_id", "status"),
        Index("idx_job_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<IngestionJob(id={self.id}, repository_id={self.repository_id}, status={self.status}, stage={self.stage})>"
