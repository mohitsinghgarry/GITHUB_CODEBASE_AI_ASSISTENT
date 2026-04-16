"""
Vector store module for FAISS index management.

This module provides per-repository FAISS index management with metadata
support for code chunk information.
"""

from app.core.vectorstore.vector_store import (
    VectorStore,
    VectorStoreManager,
    VectorStoreMetadata,
    get_vector_store_manager,
    reload_vector_store_manager,
)

__all__ = [
    "VectorStore",
    "VectorStoreManager",
    "VectorStoreMetadata",
    "get_vector_store_manager",
    "reload_vector_store_manager",
]
