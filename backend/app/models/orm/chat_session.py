"""
Chat session ORM models for persisting chat history.

This module defines SQLAlchemy ORM models for storing chat sessions
and messages permanently in the database.
"""

from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class ChatSession(Base):
    """
    Chat session model for storing conversation metadata.
    
    A chat session represents a conversation thread with associated
    repository context and model configuration.
    """
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Session metadata
    repository_ids = Column(JSON, nullable=False)  # List of repository IDs
    model = Column(String(100), nullable=False)
    title = Column(String(200), nullable=True)  # Optional session title
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    """
    Chat message model for storing individual messages in a session.
    
    Each message belongs to a session and contains the role (user/assistant),
    content, and optional citations.
    """
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Message data
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # Optional citations array
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
