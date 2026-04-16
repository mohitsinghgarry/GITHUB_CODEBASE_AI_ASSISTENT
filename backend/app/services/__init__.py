"""
Services package for business logic components.

This package contains service classes that implement core business logic
for the GitHub Codebase RAG Assistant.
"""

from app.services.repository_service import RepositoryService
from app.services.chunking_service import ChunkingService, CodeChunk, chunk_code_file
from app.services.ingestion_service import IngestionService, get_ingestion_service
from app.services.search_service import (
    BM25SearchService,
    VectorSearchService,
    UnifiedSearchService,
    SearchMode,
    SearchResult,
    MatchLocation,
)
from app.services.llm_service import (
    LLMService,
    ExplanationMode,
    OllamaError,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelNotFoundError,
    OllamaGenerationError,
    get_llm_service,
)
from app.services.chat_service import (
    ChatService,
    ChatSession,
    ChatMessage,
    Citation,
    get_chat_service,
)
from app.services.review_service import (
    ReviewService,
    get_review_service,
)

__all__ = [
    "RepositoryService",
    "ChunkingService",
    "CodeChunk",
    "chunk_code_file",
    "IngestionService",
    "get_ingestion_service",
    "BM25SearchService",
    "VectorSearchService",
    "UnifiedSearchService",
    "SearchMode",
    "SearchResult",
    "MatchLocation",
    "LLMService",
    "ExplanationMode",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "OllamaModelNotFoundError",
    "OllamaGenerationError",
    "get_llm_service",
    "ChatService",
    "ChatSession",
    "ChatMessage",
    "Citation",
    "get_chat_service",
    "ReviewService",
    "get_review_service",
]
