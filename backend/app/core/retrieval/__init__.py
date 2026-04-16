"""
Retrieval module for semantic search and code retrieval.

This module provides semantic search functionality using FAISS vector similarity
search with support for query embedding generation and repository filtering.
"""

from app.core.retrieval.retriever import (
    SearchResult,
    SemanticSearchRetriever,
    get_semantic_search_retriever,
    reload_semantic_search_retriever,
)

__all__ = [
    "SearchResult",
    "SemanticSearchRetriever",
    "get_semantic_search_retriever",
    "reload_semantic_search_retriever",
]
