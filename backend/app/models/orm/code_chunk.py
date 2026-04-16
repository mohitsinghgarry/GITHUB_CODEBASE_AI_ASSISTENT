"""
SQLAlchemy ORM model for code_chunks table.

This module defines the CodeChunk model for storing indexed code segments.

Requirements:
- 14.2: Persist code chunks to a database
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CodeChunk(Base):
    """
    CodeChunk model for storing indexed code segments.
    
    Attributes:
        id: Unique identifier (UUID)
        repository_id: Foreign key to repositories table
        file_path: Relative path to the file within the repository
        start_line: Starting line number of the chunk
        end_line: Ending line number of the chunk
        language: Programming language of the code
        content: The actual code content
        embedding_id: Reference to FAISS index position
        created_at: Timestamp when chunk was created
    """
    
    __tablename__ = "code_chunks"
    
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
    
    # File metadata
    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )
    
    # Line numbers
    start_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    end_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    # Language
    language: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # FAISS index reference
    embedding_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
    )
    
    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository",
        back_populates="code_chunks",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_chunks_repo", "repository_id"),
        Index("idx_chunks_file", "file_path"),
        Index("idx_chunks_repo_file", "repository_id", "file_path"),
    )
    
    def __repr__(self) -> str:
        return f"<CodeChunk(id={self.id}, file_path={self.file_path}, lines={self.start_line}-{self.end_line})>"
