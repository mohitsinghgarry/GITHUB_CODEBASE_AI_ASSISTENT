"""
Pydantic schemas for search requests and responses.

This module defines the request and response models for search operations.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MatchLocationSchema(BaseModel):
    """Schema for match location within a code chunk."""
    
    start: int = Field(..., description="Start position of the match")
    end: int = Field(..., description="End position of the match")
    matched_text: str = Field(..., description="The actual matched text")
    line_number: int = Field(..., description="Line number within the chunk")
    
    class Config:
        from_attributes = True


class CodeChunkSchema(BaseModel):
    """Schema for code chunk in search results."""
    
    id: UUID = Field(..., description="Unique identifier")
    repository_id: UUID = Field(..., description="Repository ID")
    file_path: str = Field(..., description="File path within repository")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    language: Optional[str] = Field(None, description="Programming language")
    content: str = Field(..., description="Code content")
    
    class Config:
        from_attributes = True


class SearchResultSchema(BaseModel):
    """Schema for a single search result."""
    
    chunk: CodeChunkSchema = Field(..., description="The matched code chunk")
    score: float = Field(..., description="Relevance score")
    matches: List[MatchLocationSchema] = Field(..., description="Match locations")
    highlighted_content: str = Field(..., description="Content with matches highlighted")
    
    class Config:
        from_attributes = True


class KeywordSearchRequest(BaseModel):
    """Request schema for keyword search."""
    
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    mode: str = Field(
        "case_insensitive",
        description="Search mode: exact, case_insensitive, or regex"
    )
    use_boolean: bool = Field(
        False,
        description="Parse query as boolean expression (AND, OR, NOT)"
    )
    repository_ids: Optional[List[UUID]] = Field(
        None,
        description="Filter by repository IDs"
    )
    file_extensions: Optional[List[str]] = Field(
        None,
        description="Filter by file extensions (e.g., ['.py', '.js'])"
    )
    directory_paths: Optional[List[str]] = Field(
        None,
        description="Filter by directory paths (e.g., ['src/', 'lib/'])"
    )
    languages: Optional[List[str]] = Field(
        None,
        description="Filter by programming languages"
    )
    
    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate search mode."""
        valid_modes = ["exact", "case_insensitive", "regex"]
        if v not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}")
        return v


class KeywordSearchResponse(BaseModel):
    """Response schema for keyword search."""
    
    results: List[SearchResultSchema] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")
    
    class Config:
        from_attributes = True


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic search."""
    
    query: str = Field(..., min_length=1, description="Natural language query")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    repository_ids: Optional[List[UUID]] = Field(
        None,
        description="Filter by repository IDs"
    )
    file_extensions: Optional[List[str]] = Field(
        None,
        description="Filter by file extensions"
    )
    directory_paths: Optional[List[str]] = Field(
        None,
        description="Filter by directory paths"
    )
    languages: Optional[List[str]] = Field(
        None,
        description="Filter by programming languages"
    )


class SemanticSearchResponse(BaseModel):
    """Response schema for semantic search."""
    
    results: List[SearchResultSchema] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")
    
    class Config:
        from_attributes = True


class HybridSearchRequest(BaseModel):
    """Request schema for hybrid search (BM25 + vector)."""
    
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    bm25_weight: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Weight for BM25 score (1 - bm25_weight = vector weight)"
    )
    repository_ids: Optional[List[UUID]] = Field(
        None,
        description="Filter by repository IDs"
    )
    file_extensions: Optional[List[str]] = Field(
        None,
        description="Filter by file extensions"
    )
    directory_paths: Optional[List[str]] = Field(
        None,
        description="Filter by directory paths"
    )
    languages: Optional[List[str]] = Field(
        None,
        description="Filter by programming languages"
    )


class HybridSearchResponse(BaseModel):
    """Response schema for hybrid search."""
    
    results: List[SearchResultSchema] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")
    bm25_weight: float = Field(..., description="BM25 weight used")
    
    class Config:
        from_attributes = True
