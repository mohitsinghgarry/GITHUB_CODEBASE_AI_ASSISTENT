"""
Embeddings module for generating vector embeddings from text.

This module provides the embedding service for converting text into
dense vector representations using sentence-transformers models.
"""

from app.core.embeddings.embedder import (
    EmbeddingService,
    get_embedding_service,
    reload_embedding_service,
)

__all__ = [
    "EmbeddingService",
    "get_embedding_service",
    "reload_embedding_service",
]
