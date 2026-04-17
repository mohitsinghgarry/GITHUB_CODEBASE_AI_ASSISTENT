"""
Settings API endpoints.

Provides endpoints for retrieving and updating application settings.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.core.config import get_settings, Settings
from app.services.groq_llm_service import GROQ_MODELS

router = APIRouter(prefix="/settings", tags=["settings"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ModelInfo(BaseModel):
    """Information about an available model."""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Model description")


class AvailableModelsResponse(BaseModel):
    """Response containing available models."""
    llm_models: List[ModelInfo] = Field(..., description="Available LLM models")
    embedding_models: List[ModelInfo] = Field(..., description="Available embedding models")


class SettingsResponse(BaseModel):
    """Current application settings."""
    # LLM Settings
    llm_provider: str = Field(default="groq", description="LLM provider")
    llm_model: str = Field(..., description="Current LLM model")
    temperature: float = Field(..., description="LLM temperature")
    max_context_tokens: int = Field(..., description="Maximum context tokens")
    max_response_tokens: int = Field(..., description="Maximum response tokens")
    
    # Embedding Settings
    embedding_model: str = Field(..., description="Current embedding model")
    embedding_dimension: int = Field(..., description="Embedding dimension")
    
    # Chunking Settings
    chunk_size: int = Field(..., description="Chunk size")
    chunk_overlap: int = Field(..., description="Chunk overlap")
    
    # Search Settings
    default_top_k: int = Field(..., description="Default top-K results")
    hybrid_search_alpha: float = Field(..., description="Hybrid search alpha")


class UpdateSettingsRequest(BaseModel):
    """Request to update settings."""
    llm_model: str | None = Field(None, description="LLM model to use")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="LLM temperature")
    max_context_tokens: int | None = Field(None, ge=512, le=32768, description="Max context tokens")
    max_response_tokens: int | None = Field(None, ge=128, le=8192, description="Max response tokens")
    
    embedding_model: str | None = Field(None, description="Embedding model")
    
    chunk_size: int | None = Field(None, ge=128, le=2048, description="Chunk size")
    chunk_overlap: int | None = Field(None, ge=0, le=512, description="Chunk overlap")
    
    default_top_k: int | None = Field(None, ge=1, le=100, description="Default top-K")
    hybrid_search_alpha: float | None = Field(None, ge=0.0, le=1.0, description="Hybrid search alpha")


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/models", response_model=AvailableModelsResponse)
async def get_available_models() -> AvailableModelsResponse:
    """
    Get list of available LLM and embedding models.
    
    Returns:
        AvailableModelsResponse: Lists of available models
    """
    # LLM models from Groq
    llm_models = [
        ModelInfo(
            id=model_id,
            name=model_id.split("/")[-1] if "/" in model_id else model_id,
            description=description
        )
        for model_id, description in GROQ_MODELS.items()
    ]
    
    # Embedding models
    embedding_models = [
        ModelInfo(
            id="sentence-transformers/all-MiniLM-L6-v2",
            name="all-MiniLM-L6-v2",
            description="Fast and efficient, 384 dimensions (Default)"
        ),
        ModelInfo(
            id="sentence-transformers/all-mpnet-base-v2",
            name="all-mpnet-base-v2",
            description="High quality, 768 dimensions"
        ),
        ModelInfo(
            id="BAAI/bge-small-en-v1.5",
            name="bge-small-en-v1.5",
            description="Optimized for retrieval, 384 dimensions"
        ),
        ModelInfo(
            id="BAAI/bge-base-en-v1.5",
            name="bge-base-en-v1.5",
            description="Better quality, 768 dimensions"
        ),
        ModelInfo(
            id="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            name="paraphrase-multilingual-MiniLM-L12-v2",
            description="Multilingual support, 384 dimensions"
        ),
    ]
    
    return AvailableModelsResponse(
        llm_models=llm_models,
        embedding_models=embedding_models
    )


@router.get("", response_model=SettingsResponse)
async def get_current_settings(
    settings: Settings = Depends(get_settings)
) -> SettingsResponse:
    """
    Get current application settings.
    
    Returns:
        SettingsResponse: Current settings
    """
    # Get Groq model from environment (fallback to default)
    import os
    llm_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    return SettingsResponse(
        llm_provider="groq",
        llm_model=llm_model,
        temperature=settings.rag_temperature,
        max_context_tokens=settings.max_context_tokens,
        max_response_tokens=settings.max_response_tokens,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dimension,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        default_top_k=settings.default_top_k,
        hybrid_search_alpha=settings.hybrid_search_alpha,
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    request: UpdateSettingsRequest,
    settings: Settings = Depends(get_settings)
) -> SettingsResponse:
    """
    Update application settings.
    
    Note: This updates runtime settings only. For persistent changes,
    update the .env file.
    
    Args:
        request: Settings to update
        
    Returns:
        SettingsResponse: Updated settings
    """
    import os
    
    # Update settings that can be changed at runtime
    if request.llm_model is not None:
        # Validate model exists
        if request.llm_model not in GROQ_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid LLM model: {request.llm_model}"
            )
        os.environ["GROQ_MODEL"] = request.llm_model
    
    if request.temperature is not None:
        settings.rag_temperature = request.temperature
    
    if request.max_context_tokens is not None:
        settings.max_context_tokens = request.max_context_tokens
    
    if request.max_response_tokens is not None:
        settings.max_response_tokens = request.max_response_tokens
    
    if request.embedding_model is not None:
        settings.embedding_model = request.embedding_model
    
    if request.chunk_size is not None:
        settings.chunk_size = request.chunk_size
    
    if request.chunk_overlap is not None:
        settings.chunk_overlap = request.chunk_overlap
    
    if request.default_top_k is not None:
        settings.default_top_k = request.default_top_k
    
    if request.hybrid_search_alpha is not None:
        settings.hybrid_search_alpha = request.hybrid_search_alpha
    
    # Return updated settings
    return await get_current_settings(settings)
