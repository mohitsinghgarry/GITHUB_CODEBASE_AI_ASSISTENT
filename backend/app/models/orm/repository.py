"""
SQLAlchemy ORM model for repositories table.

This module defines the Repository model for storing GitHub repository metadata.

Requirements:
- 14.2: Persist repository metadata to a database
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Repository(Base):
    """
    Repository model for storing GitHub repository metadata.
    
    Attributes:
        id: Unique identifier (UUID)
        url: GitHub repository URL (unique)
        owner: Repository owner/organization name
        name: Repository name
        default_branch: Default branch name (e.g., 'main', 'master')
        last_commit_hash: SHA of the last indexed commit
        status: Current status (pending, cloning, reading, chunking, embedding, completed, failed)
        created_at: Timestamp when repository was added
        updated_at: Timestamp when repository was last updated
        error_message: Error message if status is 'failed'
        chunk_count: Number of code chunks indexed
        index_path: Path to the FAISS index file
    """
    
    __tablename__ = "repositories"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default="gen_random_uuid()",
    )
    
    # Repository metadata
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )
    
    owner: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    default_branch: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    last_commit_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
        index=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
        onupdate=datetime.utcnow,
    )
    
    # Error handling
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Indexing metadata
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    index_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Relationships
    ingestion_jobs: Mapped[List["IngestionJob"]] = relationship(
        "IngestionJob",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    
    code_chunks: Mapped[List["CodeChunk"]] = relationship(
        "CodeChunk",
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_repo_owner_name", "owner", "name"),
        Index("idx_repo_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, owner={self.owner}, name={self.name}, status={self.status})>"
