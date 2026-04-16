"""
Vector semantic search retriever using FAISS.

This module implements semantic search functionality using FAISS vector similarity
search. It provides methods for searching code chunks using query embeddings with
configurable top-K results and repository filtering.

Requirements:
- 4.1: Generate an embedding for the query
- 4.2: Perform vector similarity search against the Embedding_Store
- 4.3: Return the top K most relevant Code_Chunks with similarity scores
- 4.4: Support configurable result limits between 1 and 100 chunks
- 4.5: Support filtering results by repository
"""

import logging
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

import numpy as np

from app.core.embeddings.embedder import EmbeddingService, get_embedding_service
from app.core.vectorstore.vector_store import VectorStoreManager, get_vector_store_manager

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """
    Represents a semantic search result.
    
    Attributes:
        chunk_id: UUID of the code chunk
        repository_id: UUID of the repository
        file_path: Path to the source file
        start_line: Starting line number in the file
        end_line: Ending line number in the file
        language: Programming language of the chunk
        content: The code content
        score: Similarity score (higher is more similar)
    """
    chunk_id: str
    repository_id: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    content: str
    score: float


class SemanticSearchRetriever:
    """
    Semantic search retriever using FAISS vector similarity.
    
    This class provides semantic search functionality by:
    1. Generating embeddings for user queries
    2. Performing FAISS similarity search against repository indices
    3. Returning ranked results with metadata
    
    Attributes:
        embedding_service: Service for generating query embeddings
        vector_store_manager: Manager for FAISS vector stores
        min_top_k: Minimum allowed top-K value (1)
        max_top_k: Maximum allowed top-K value (100)
    """
    
    MIN_TOP_K = 1
    MAX_TOP_K = 100
    DEFAULT_TOP_K = 10
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store_manager: Optional[VectorStoreManager] = None,
    ):
        """
        Initialize the semantic search retriever.
        
        Args:
            embedding_service: Service for generating embeddings.
                             If None, uses the global embedding service.
            vector_store_manager: Manager for vector stores.
                                If None, uses the global vector store manager.
        """
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store_manager = vector_store_manager or get_vector_store_manager()
        
        logger.info(
            f"Initialized SemanticSearchRetriever with "
            f"embedding_service={self.embedding_service}, "
            f"vector_store_manager={self.vector_store_manager}"
        )
    
    def _validate_top_k(self, top_k: int) -> int:
        """
        Validate and clamp top_k value to allowed range.
        
        Args:
            top_k: Requested top-K value
        
        Returns:
            int: Validated top-K value clamped to [MIN_TOP_K, MAX_TOP_K]
        """
        if top_k < self.MIN_TOP_K:
            logger.warning(
                f"top_k={top_k} is below minimum {self.MIN_TOP_K}. "
                f"Using minimum value."
            )
            return self.MIN_TOP_K
        
        if top_k > self.MAX_TOP_K:
            logger.warning(
                f"top_k={top_k} exceeds maximum {self.MAX_TOP_K}. "
                f"Using maximum value."
            )
            return self.MAX_TOP_K
        
        return top_k
    
    def _generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.
        
        Args:
            query: The query text
        
        Returns:
            np.ndarray: Query embedding vector
        
        Raises:
            ValueError: If query is empty
            RuntimeError: If embedding generation fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # Generate normalized embedding for cosine similarity
            query_embedding = self.embedding_service.embed_query(
                query=query,
                normalize=True,
            )
            
            logger.debug(
                f"Generated query embedding with shape {query_embedding.shape}"
            )
            
            return query_embedding
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise RuntimeError(f"Failed to generate query embedding: {e}") from e
    
    def _search_single_repository(
        self,
        query_embedding: np.ndarray,
        repository_id: UUID,
        top_k: int,
    ) -> List[SearchResult]:
        """
        Search a single repository for similar code chunks.
        
        Args:
            query_embedding: The query embedding vector
            repository_id: UUID of the repository to search
            top_k: Number of results to return
        
        Returns:
            List[SearchResult]: List of search results sorted by similarity score
        """
        # Get the vector store for this repository
        store = self.vector_store_manager.get_store(repository_id)
        
        if store is None:
            logger.warning(
                f"Vector store not found for repository {repository_id}"
            )
            return []
        
        if store.is_empty():
            logger.warning(
                f"Vector store is empty for repository {repository_id}"
            )
            return []
        
        try:
            # Perform FAISS similarity search
            indices, scores = store.search(
                query_embedding=query_embedding,
                top_k=top_k,
            )
            
            # Get chunk metadata for results
            chunks_metadata = store.get_chunks_metadata(indices)
            
            # Create search results
            results = []
            for i, (chunk_metadata, score) in enumerate(zip(chunks_metadata, scores)):
                if chunk_metadata is None:
                    logger.warning(
                        f"Missing metadata for chunk at index {indices[i]} "
                        f"in repository {repository_id}"
                    )
                    continue
                
                result = SearchResult(
                    chunk_id=chunk_metadata.get("id", ""),
                    repository_id=str(repository_id),
                    file_path=chunk_metadata.get("file_path", ""),
                    start_line=chunk_metadata.get("start_line", 0),
                    end_line=chunk_metadata.get("end_line", 0),
                    language=chunk_metadata.get("language", ""),
                    content=chunk_metadata.get("content", ""),
                    score=float(score),
                )
                results.append(result)
            
            logger.debug(
                f"Found {len(results)} results in repository {repository_id}"
            )
            
            return results
            
        except Exception as e:
            logger.error(
                f"Failed to search repository {repository_id}: {e}"
            )
            return []
    
    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        repository_ids: Optional[List[UUID]] = None,
    ) -> List[SearchResult]:
        """
        Perform semantic search across repositories.
        
        This method:
        1. Generates an embedding for the query
        2. Searches specified repositories (or all if none specified)
        3. Returns top-K most similar code chunks with scores
        
        Args:
            query: The natural language query
            top_k: Number of results to return (1-100, default: 10)
            repository_ids: List of repository UUIDs to search.
                          If None, searches all available repositories.
        
        Returns:
            List[SearchResult]: List of search results sorted by similarity score
                               (highest score first)
        
        Raises:
            ValueError: If query is empty or top_k is invalid
            RuntimeError: If search fails
        
        Example:
            >>> retriever = SemanticSearchRetriever()
            >>> results = retriever.search(
            ...     query="authentication middleware",
            ...     top_k=5,
            ...     repository_ids=[repo_uuid]
            ... )
            >>> for result in results:
            ...     print(f"{result.file_path}:{result.start_line} (score: {result.score:.3f})")
        """
        # Validate top_k
        top_k = self._validate_top_k(top_k)
        
        # Generate query embedding
        query_embedding = self._generate_query_embedding(query)
        
        # Determine which repositories to search
        if repository_ids is None:
            # Search all available repositories
            repository_ids = self.vector_store_manager.list_stores()
            logger.info(
                f"No repository filter specified. Searching {len(repository_ids)} "
                f"available repositories."
            )
        else:
            logger.info(
                f"Searching {len(repository_ids)} specified repositories"
            )
        
        if not repository_ids:
            logger.warning("No repositories available to search")
            return []
        
        # Search each repository
        all_results = []
        for repo_id in repository_ids:
            results = self._search_single_repository(
                query_embedding=query_embedding,
                repository_id=repo_id,
                top_k=top_k,
            )
            all_results.extend(results)
        
        # Sort all results by score (descending) and return top K
        all_results.sort(key=lambda r: r.score, reverse=True)
        final_results = all_results[:top_k]
        
        logger.info(
            f"Semantic search for query '{query[:50]}...' returned "
            f"{len(final_results)} results from {len(repository_ids)} repositories"
        )
        
        return final_results
    
    def search_with_threshold(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = 0.0,
        repository_ids: Optional[List[UUID]] = None,
    ) -> List[SearchResult]:
        """
        Perform semantic search with a minimum score threshold.
        
        This method is similar to search() but filters out results below
        the specified similarity score threshold.
        
        Args:
            query: The natural language query
            top_k: Maximum number of results to return (1-100, default: 10)
            score_threshold: Minimum similarity score (0.0-1.0, default: 0.0)
            repository_ids: List of repository UUIDs to search.
                          If None, searches all available repositories.
        
        Returns:
            List[SearchResult]: List of search results with score >= threshold,
                               sorted by similarity score (highest first)
        
        Example:
            >>> retriever = SemanticSearchRetriever()
            >>> results = retriever.search_with_threshold(
            ...     query="error handling",
            ...     top_k=10,
            ...     score_threshold=0.5,
            ... )
        """
        # Perform regular search
        results = self.search(
            query=query,
            top_k=top_k,
            repository_ids=repository_ids,
        )
        
        # Filter by threshold
        filtered_results = [r for r in results if r.score >= score_threshold]
        
        logger.info(
            f"Filtered {len(results)} results to {len(filtered_results)} "
            f"with score_threshold={score_threshold}"
        )
        
        return filtered_results
    
    def get_similar_chunks(
        self,
        chunk_id: str,
        repository_id: UUID,
        top_k: int = DEFAULT_TOP_K,
    ) -> List[SearchResult]:
        """
        Find similar code chunks to a given chunk.
        
        This method retrieves the embedding for a specific chunk and finds
        other similar chunks in the same repository.
        
        Args:
            chunk_id: UUID of the reference chunk
            repository_id: UUID of the repository
            top_k: Number of similar chunks to return (1-100, default: 10)
        
        Returns:
            List[SearchResult]: List of similar chunks sorted by similarity score
        
        Raises:
            ValueError: If chunk or repository not found
        """
        # Validate top_k
        top_k = self._validate_top_k(top_k)
        
        # Get the vector store
        store = self.vector_store_manager.get_store(repository_id)
        
        if store is None:
            raise ValueError(
                f"Vector store not found for repository {repository_id}"
            )
        
        # Find the chunk in metadata
        chunk_index = None
        for i, chunk_metadata in enumerate(store.metadata.chunks):
            if chunk_metadata.get("id") == chunk_id:
                chunk_index = i
                break
        
        if chunk_index is None:
            raise ValueError(
                f"Chunk {chunk_id} not found in repository {repository_id}"
            )
        
        # Get the chunk's embedding from the index
        # Note: FAISS doesn't provide direct access to stored vectors,
        # so we need to reconstruct the embedding from the chunk content
        chunk_metadata = store.metadata.chunks[chunk_index]
        chunk_content = chunk_metadata.get("content", "")
        
        # Generate embedding for the chunk
        chunk_embedding = self.embedding_service.embed_text(
            text=chunk_content,
            normalize=True,
        )
        
        # Search for similar chunks
        results = self._search_single_repository(
            query_embedding=chunk_embedding,
            repository_id=repository_id,
            top_k=top_k + 1,  # +1 to account for the chunk itself
        )
        
        # Filter out the original chunk
        filtered_results = [r for r in results if r.chunk_id != chunk_id][:top_k]
        
        logger.info(
            f"Found {len(filtered_results)} similar chunks to {chunk_id} "
            f"in repository {repository_id}"
        )
        
        return filtered_results
    
    def __repr__(self) -> str:
        """String representation of the retriever."""
        return (
            f"SemanticSearchRetriever("
            f"embedding_service={self.embedding_service}, "
            f"vector_store_manager={self.vector_store_manager})"
        )


# ============================================================================
# Global Retriever Instance
# ============================================================================

_semantic_search_retriever: Optional[SemanticSearchRetriever] = None


def get_semantic_search_retriever(
    embedding_service: Optional[EmbeddingService] = None,
    vector_store_manager: Optional[VectorStoreManager] = None,
) -> SemanticSearchRetriever:
    """
    Get the global semantic search retriever instance.
    
    This function creates a singleton retriever instance on first call
    and returns the cached instance on subsequent calls.
    
    Args:
        embedding_service: Service for generating embeddings.
                         If None, uses the global embedding service.
        vector_store_manager: Manager for vector stores.
                            If None, uses the global vector store manager.
    
    Returns:
        SemanticSearchRetriever: The global retriever instance
    """
    global _semantic_search_retriever
    
    if _semantic_search_retriever is None:
        _semantic_search_retriever = SemanticSearchRetriever(
            embedding_service=embedding_service,
            vector_store_manager=vector_store_manager,
        )
    
    return _semantic_search_retriever


def reload_semantic_search_retriever(
    embedding_service: Optional[EmbeddingService] = None,
    vector_store_manager: Optional[VectorStoreManager] = None,
) -> SemanticSearchRetriever:
    """
    Reload the semantic search retriever with new parameters.
    
    This function forces a reload of the retriever, useful for
    testing or when configuration has changed.
    
    Args:
        embedding_service: Service for generating embeddings.
                         If None, uses the global embedding service.
        vector_store_manager: Manager for vector stores.
                            If None, uses the global vector store manager.
    
    Returns:
        SemanticSearchRetriever: The newly loaded retriever instance
    """
    global _semantic_search_retriever
    _semantic_search_retriever = SemanticSearchRetriever(
        embedding_service=embedding_service,
        vector_store_manager=vector_store_manager,
    )
    return _semantic_search_retriever
