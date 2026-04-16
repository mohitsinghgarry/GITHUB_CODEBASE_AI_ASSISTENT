"""
Pydantic schemas for chat requests and responses.

This module defines the request and response models for chat operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.services.llm_service import ExplanationMode


class CitationSchema(BaseModel):
    """Schema for a citation to a source code chunk."""
    
    chunk_id: UUID = Field(..., description="Unique chunk identifier")
    repository_id: UUID = Field(..., description="Repository identifier")
    file_path: str = Field(..., description="Path to the source file")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    language: Optional[str] = Field(None, description="Programming language")
    content: str = Field(..., description="Code content")
    score: float = Field(..., description="Relevance score")
    
    class Config:
        from_attributes = True


class ChatMessageSchema(BaseModel):
    """Schema for a chat message."""
    
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    citations: Optional[List[CitationSchema]] = Field(
        None,
        description="Source citations (for assistant messages)"
    )
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate message role."""
        if v not in ["user", "assistant"]:
            raise ValueError("role must be 'user' or 'assistant'")
        return v
    
    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    """Schema for a chat session."""
    
    session_id: str = Field(..., description="Unique session identifier")
    repository_ids: List[UUID] = Field(..., description="Repository IDs to search in")
    messages: List[ChatMessageSchema] = Field(..., description="Chat messages")
    explanation_mode: ExplanationMode = Field(..., description="Explanation mode")
    created_at: datetime = Field(..., description="Session creation time")
    updated_at: datetime = Field(..., description="Last update time")
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    message: str = Field(..., min_length=1, description="User message/question")
    session_id: Optional[str] = Field(
        None,
        description="Session ID (creates new session if not provided)"
    )
    repository_ids: List[UUID] = Field(
        ...,
        min_length=1,
        description="Repository IDs to search in"
    )
    explanation_mode: ExplanationMode = Field(
        default=ExplanationMode.TECHNICAL,
        description="Explanation mode for response"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of code chunks to retrieve"
    )
    include_history: bool = Field(
        default=True,
        description="Include conversation history in prompt"
    )
    stream: bool = Field(
        default=False,
        description="Stream the response"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint (non-streaming)."""
    
    response: str = Field(..., description="Generated response")
    citations: List[CitationSchema] = Field(..., description="Source citations")
    session_id: str = Field(..., description="Session identifier")
    
    class Config:
        from_attributes = True


class ChatStreamChunk(BaseModel):
    """Schema for a streaming chat response chunk."""
    
    chunk: str = Field(..., description="Response chunk")
    citations: Optional[List[CitationSchema]] = Field(
        None,
        description="Source citations (only in first chunk)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier (only in first chunk)"
    )
    done: bool = Field(default=False, description="Whether streaming is complete")
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response schema for listing sessions."""
    
    sessions: List[str] = Field(..., description="List of session IDs")
    total: int = Field(..., description="Total number of sessions")
    
    class Config:
        from_attributes = True


class SessionDeleteResponse(BaseModel):
    """Response schema for deleting a session."""
    
    message: str = Field(..., description="Success message")
    deleted_session_id: str = Field(..., description="Deleted session ID")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[dict]] = Field(None, description="Additional error details")
    
    class Config:
        from_attributes = True
