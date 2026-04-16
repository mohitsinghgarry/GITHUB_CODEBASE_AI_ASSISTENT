"""
FAISS vector store manager for per-repository index management.

This module provides a unified interface for managing FAISS indices on a
per-repository basis. It handles index creation, loading, saving, and search
operations with metadata management for chunk information.

Requirements:
- 2.7: Store embeddings to a repository-specific FAISS_Index
- 2.8: Create a separate FAISS_Index for each repository
- 2.13: Persist the FAISS_Index to disk with repository metadata
- 14.1: Persist all embeddings and metadata to disk
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import faiss
import numpy as np

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class VectorStoreMetadata:
    """
    Metadata for a FAISS vector store.
    
    This class manages the metadata associated with a FAISS index,
    including chunk information and index statistics.
    
    Attributes:
        repository_id: UUID of the repository
        chunk_count: Number of chunks in the index
        dimension: Embedding vector dimension
        created_at: ISO timestamp when index was created
        updated_at: ISO timestamp when index was last updated
        chunks: List of chunk metadata dictionaries
    """
    
    def __init__(
        self,
        repository_id: UUID,
        dimension: int,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        chunks: Optional[List[Dict]] = None,
    ):
        """
        Initialize vector store metadata.
        
        Args:
            repository_id: UUID of the repository
            dimension: Embedding vector dimension
            created_at: ISO timestamp when index was created (auto-generated if None)
            updated_at: ISO timestamp when index was last updated (auto-generated if None)
            chunks: List of chunk metadata dictionaries
        """
        from datetime import datetime
        
        self.repository_id = repository_id
        self.dimension = dimension
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.chunks = chunks or []
        self.chunk_count = len(self.chunks)
    
    def add_chunk(self, chunk_metadata: Dict) -> int:
        """
        Add chunk metadata to the store.
        
        Args:
            chunk_metadata: Dictionary containing chunk information
                           (id, file_path, start_line, end_line, language, content)
        
        Returns:
            int: The index position of the added chunk
        """
        from datetime import datetime
        
        self.chunks.append(chunk_metadata)
        self.chunk_count = len(self.chunks)
        self.updated_at = datetime.utcnow().isoformat()
        return self.chunk_count - 1
    
    def add_chunks(self, chunks_metadata: List[Dict]) -> List[int]:
        """
        Add multiple chunk metadata entries to the store.
        
        Args:
            chunks_metadata: List of chunk metadata dictionaries
        
        Returns:
            List[int]: List of index positions for the added chunks
        """
        from datetime import datetime
        
        start_idx = len(self.chunks)
        self.chunks.extend(chunks_metadata)
        self.chunk_count = len(self.chunks)
        self.updated_at = datetime.utcnow().isoformat()
        return list(range(start_idx, self.chunk_count))
    
    def get_chunk(self, index: int) -> Optional[Dict]:
        """
        Get chunk metadata by index.
        
        Args:
            index: Index position in the chunks list
        
        Returns:
            Optional[Dict]: Chunk metadata dictionary or None if index is invalid
        """
        if 0 <= index < len(self.chunks):
            return self.chunks[index]
        return None
    
    def get_chunks(self, indices: List[int]) -> List[Dict]:
        """
        Get multiple chunk metadata entries by indices.
        
        Args:
            indices: List of index positions
        
        Returns:
            List[Dict]: List of chunk metadata dictionaries
        """
        return [self.get_chunk(idx) for idx in indices if self.get_chunk(idx) is not None]
    
    def to_dict(self) -> Dict:
        """
        Convert metadata to dictionary for JSON serialization.
        
        Returns:
            Dict: Metadata as dictionary
        """
        return {
            "repository_id": str(self.repository_id),
            "chunk_count": self.chunk_count,
            "dimension": self.dimension,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "chunks": self.chunks,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "VectorStoreMetadata":
        """
        Create metadata from dictionary.
        
        Args:
            data: Dictionary containing metadata
        
        Returns:
            VectorStoreMetadata: Metadata instance
        """
        return cls(
            repository_id=UUID(data["repository_id"]),
            dimension=data["dimension"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            chunks=data.get("chunks", []),
        )


class VectorStore:
    """
    FAISS vector store for a single repository.
    
    This class manages a FAISS index and associated metadata for a specific
    repository. It provides methods for adding embeddings, searching, and
    persisting the index to disk.
    
    Attributes:
        repository_id: UUID of the repository
        index: FAISS index instance
        metadata: Vector store metadata
        dimension: Embedding vector dimension
        index_path: Path to the FAISS index file
        metadata_path: Path to the metadata JSON file
    """
    
    def __init__(
        self,
        repository_id: UUID,
        dimension: int,
        index_path: Path,
        metadata_path: Path,
        index: Optional[faiss.Index] = None,
        metadata: Optional[VectorStoreMetadata] = None,
    ):
        """
        Initialize vector store.
        
        Args:
            repository_id: UUID of the repository
            dimension: Embedding vector dimension
            index_path: Path to the FAISS index file
            metadata_path: Path to the metadata JSON file
            index: Existing FAISS index (creates new if None)
            metadata: Existing metadata (creates new if None)
        """
        self.repository_id = repository_id
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Create or use provided index
        if index is None:
            # Use IndexFlatIP for cosine similarity (inner product on normalized vectors)
            self.index = faiss.IndexFlatIP(dimension)
            logger.info(
                f"Created new FAISS IndexFlatIP with dimension {dimension} "
                f"for repository {repository_id}"
            )
        else:
            self.index = index
            logger.info(f"Using existing FAISS index for repository {repository_id}")
        
        # Create or use provided metadata
        if metadata is None:
            self.metadata = VectorStoreMetadata(
                repository_id=repository_id,
                dimension=dimension,
            )
        else:
            self.metadata = metadata
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        chunks_metadata: List[Dict],
    ) -> List[int]:
        """
        Add embeddings and their metadata to the store.
        
        Args:
            embeddings: Array of embeddings of shape (n, dimension)
            chunks_metadata: List of chunk metadata dictionaries (length n)
        
        Returns:
            List[int]: List of index positions for the added embeddings
        
        Raises:
            ValueError: If embeddings shape doesn't match dimension or
                       if number of embeddings doesn't match metadata count
        """
        # Validate embeddings shape
        if embeddings.ndim != 2:
            raise ValueError(
                f"Embeddings must be 2D array, got shape {embeddings.shape}"
            )
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embeddings dimension ({embeddings.shape[1]}) doesn't match "
                f"index dimension ({self.dimension})"
            )
        
        # Validate metadata count
        if len(chunks_metadata) != embeddings.shape[0]:
            raise ValueError(
                f"Number of embeddings ({embeddings.shape[0]}) doesn't match "
                f"number of metadata entries ({len(chunks_metadata)})"
            )
        
        # Ensure embeddings are float32 and C-contiguous
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Add metadata
        indices = self.metadata.add_chunks(chunks_metadata)
        
        logger.info(
            f"Added {len(embeddings)} embeddings to vector store for "
            f"repository {self.repository_id}"
        )
        
        return indices
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
    ) -> Tuple[List[int], List[float]]:
        """
        Search for similar embeddings using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector of shape (dimension,) or (1, dimension)
            top_k: Number of results to return
        
        Returns:
            Tuple[List[int], List[float]]: Tuple of (indices, scores)
                - indices: List of chunk indices
                - scores: List of similarity scores (higher is more similar)
        
        Raises:
            ValueError: If query embedding dimension doesn't match index dimension
            RuntimeError: If index is empty
        """
        # Validate index is not empty
        if self.index.ntotal == 0:
            raise RuntimeError("Cannot search empty index")
        
        # Reshape query embedding if needed
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Validate query embedding shape
        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Query embedding dimension ({query_embedding.shape[1]}) doesn't match "
                f"index dimension ({self.dimension})"
            )
        
        # Ensure query is float32 and C-contiguous
        query_embedding = np.ascontiguousarray(query_embedding, dtype=np.float32)
        
        # Limit top_k to index size
        effective_top_k = min(top_k, self.index.ntotal)
        
        # Search
        scores, indices = self.index.search(query_embedding, effective_top_k)
        
        # Convert to lists (FAISS returns 2D arrays)
        indices_list = indices[0].tolist()
        scores_list = scores[0].tolist()
        
        logger.debug(
            f"Search returned {len(indices_list)} results for "
            f"repository {self.repository_id}"
        )
        
        return indices_list, scores_list
    
    def get_chunk_metadata(self, index: int) -> Optional[Dict]:
        """
        Get chunk metadata by index.
        
        Args:
            index: Index position in the chunks list
        
        Returns:
            Optional[Dict]: Chunk metadata dictionary or None if index is invalid
        """
        return self.metadata.get_chunk(index)
    
    def get_chunks_metadata(self, indices: List[int]) -> List[Dict]:
        """
        Get multiple chunk metadata entries by indices.
        
        Args:
            indices: List of index positions
        
        Returns:
            List[Dict]: List of chunk metadata dictionaries
        """
        return self.metadata.get_chunks(indices)
    
    def save(self) -> None:
        """
        Save the index and metadata to disk.
        
        This method persists both the FAISS index and the metadata JSON file.
        
        Raises:
            RuntimeError: If saving fails
        """
        try:
            # Ensure parent directories exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            logger.info(f"Saved FAISS index to {self.index_path}")
            
            # Save metadata
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Saved metadata to {self.metadata_path}")
            
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            raise RuntimeError(f"Failed to save vector store: {e}") from e
    
    def get_size(self) -> int:
        """
        Get the number of vectors in the index.
        
        Returns:
            int: Number of vectors
        """
        return self.index.ntotal
    
    def is_empty(self) -> bool:
        """
        Check if the index is empty.
        
        Returns:
            bool: True if index is empty, False otherwise
        """
        return self.index.ntotal == 0
    
    def __repr__(self) -> str:
        """String representation of the vector store."""
        return (
            f"VectorStore(repository_id={self.repository_id}, "
            f"dimension={self.dimension}, size={self.get_size()})"
        )


class VectorStoreManager:
    """
    Manager for per-repository FAISS vector stores.
    
    This class manages multiple vector stores, one per repository. It handles
    creation, loading, saving, and deletion of vector stores.
    
    Attributes:
        base_path: Base directory for storing indices
        dimension: Embedding vector dimension
        stores: Dictionary mapping repository IDs to VectorStore instances
    """
    
    def __init__(
        self,
        base_path: Optional[Path] = None,
        dimension: Optional[int] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize vector store manager.
        
        Args:
            base_path: Base directory for storing indices.
                      If None, uses path from settings.
            dimension: Embedding vector dimension.
                      If None, uses dimension from settings.
            settings: Settings instance. If None, uses global settings.
        """
        self.settings = settings or get_settings()
        self.base_path = base_path or self.settings.faiss_index_path
        self.dimension = dimension or self.settings.embedding_dimension
        self.stores: Dict[UUID, VectorStore] = {}
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Initialized VectorStoreManager with base_path={self.base_path}, "
            f"dimension={self.dimension}"
        )
    
    def _get_index_path(self, repository_id: UUID) -> Path:
        """Get the path to the FAISS index file for a repository."""
        return self.base_path / f"{repository_id}.faiss"
    
    def _get_metadata_path(self, repository_id: UUID) -> Path:
        """Get the path to the metadata JSON file for a repository."""
        return self.base_path / f"{repository_id}.metadata.json"
    
    def create_store(self, repository_id: UUID) -> VectorStore:
        """
        Create a new vector store for a repository.
        
        Args:
            repository_id: UUID of the repository
        
        Returns:
            VectorStore: The created vector store
        
        Raises:
            ValueError: If a store already exists for this repository
        """
        if repository_id in self.stores:
            raise ValueError(
                f"Vector store already exists for repository {repository_id}"
            )
        
        index_path = self._get_index_path(repository_id)
        metadata_path = self._get_metadata_path(repository_id)
        
        store = VectorStore(
            repository_id=repository_id,
            dimension=self.dimension,
            index_path=index_path,
            metadata_path=metadata_path,
        )
        
        self.stores[repository_id] = store
        
        logger.info(f"Created vector store for repository {repository_id}")
        
        return store
    
    def load_store(self, repository_id: UUID) -> VectorStore:
        """
        Load an existing vector store from disk.
        
        Args:
            repository_id: UUID of the repository
        
        Returns:
            VectorStore: The loaded vector store
        
        Raises:
            FileNotFoundError: If index or metadata files don't exist
            RuntimeError: If loading fails
        """
        index_path = self._get_index_path(repository_id)
        metadata_path = self._get_metadata_path(repository_id)
        
        # Check if files exist
        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index file not found: {index_path}"
            )
        
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )
        
        try:
            # Load FAISS index
            index = faiss.read_index(str(index_path))
            logger.info(f"Loaded FAISS index from {index_path}")
            
            # Load metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata_dict = json.load(f)
            metadata = VectorStoreMetadata.from_dict(metadata_dict)
            logger.info(f"Loaded metadata from {metadata_path}")
            
            # Create store
            store = VectorStore(
                repository_id=repository_id,
                dimension=self.dimension,
                index_path=index_path,
                metadata_path=metadata_path,
                index=index,
                metadata=metadata,
            )
            
            self.stores[repository_id] = store
            
            logger.info(
                f"Loaded vector store for repository {repository_id} "
                f"with {store.get_size()} vectors"
            )
            
            return store
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise RuntimeError(f"Failed to load vector store: {e}") from e
    
    def get_store(self, repository_id: UUID, create_if_missing: bool = False) -> Optional[VectorStore]:
        """
        Get a vector store by repository ID.
        
        Args:
            repository_id: UUID of the repository
            create_if_missing: If True, create a new store if it doesn't exist
        
        Returns:
            Optional[VectorStore]: The vector store or None if not found
        """
        # Check if already loaded in memory
        if repository_id in self.stores:
            return self.stores[repository_id]
        
        # Try to load from disk
        index_path = self._get_index_path(repository_id)
        if index_path.exists():
            try:
                return self.load_store(repository_id)
            except Exception as e:
                logger.error(f"Failed to load store from disk: {e}")
                if not create_if_missing:
                    return None
        
        # Create new store if requested
        if create_if_missing:
            return self.create_store(repository_id)
        
        return None
    
    def save_store(self, repository_id: UUID) -> None:
        """
        Save a vector store to disk.
        
        Args:
            repository_id: UUID of the repository
        
        Raises:
            ValueError: If store doesn't exist
        """
        store = self.stores.get(repository_id)
        if store is None:
            raise ValueError(
                f"Vector store not found for repository {repository_id}"
            )
        
        store.save()
    
    def save_all_stores(self) -> None:
        """Save all loaded vector stores to disk."""
        for repository_id, store in self.stores.items():
            try:
                store.save()
            except Exception as e:
                logger.error(
                    f"Failed to save store for repository {repository_id}: {e}"
                )
    
    def delete_store(self, repository_id: UUID) -> None:
        """
        Delete a vector store from memory and disk.
        
        Args:
            repository_id: UUID of the repository
        
        Raises:
            FileNotFoundError: If index or metadata files don't exist
        """
        # Remove from memory
        if repository_id in self.stores:
            del self.stores[repository_id]
            logger.info(f"Removed vector store from memory for repository {repository_id}")
        
        # Delete files from disk
        index_path = self._get_index_path(repository_id)
        metadata_path = self._get_metadata_path(repository_id)
        
        if index_path.exists():
            index_path.unlink()
            logger.info(f"Deleted FAISS index file: {index_path}")
        
        if metadata_path.exists():
            metadata_path.unlink()
            logger.info(f"Deleted metadata file: {metadata_path}")
    
    def store_exists(self, repository_id: UUID) -> bool:
        """
        Check if a vector store exists (in memory or on disk).
        
        Args:
            repository_id: UUID of the repository
        
        Returns:
            bool: True if store exists, False otherwise
        """
        # Check memory
        if repository_id in self.stores:
            return True
        
        # Check disk
        index_path = self._get_index_path(repository_id)
        return index_path.exists()
    
    def list_stores(self) -> List[UUID]:
        """
        List all repository IDs with vector stores on disk.
        
        Returns:
            List[UUID]: List of repository IDs
        """
        repository_ids = []
        
        # Find all .faiss files
        for index_path in self.base_path.glob("*.faiss"):
            try:
                # Extract repository ID from filename
                repo_id_str = index_path.stem
                repository_id = UUID(repo_id_str)
                repository_ids.append(repository_id)
            except ValueError:
                logger.warning(f"Invalid repository ID in filename: {index_path.name}")
        
        return repository_ids
    
    def get_store_stats(self, repository_id: UUID) -> Optional[Dict]:
        """
        Get statistics for a vector store.
        
        Args:
            repository_id: UUID of the repository
        
        Returns:
            Optional[Dict]: Dictionary with store statistics or None if not found
        """
        store = self.get_store(repository_id)
        if store is None:
            return None
        
        return {
            "repository_id": str(repository_id),
            "dimension": store.dimension,
            "vector_count": store.get_size(),
            "chunk_count": store.metadata.chunk_count,
            "created_at": store.metadata.created_at,
            "updated_at": store.metadata.updated_at,
            "index_path": str(store.index_path),
            "metadata_path": str(store.metadata_path),
        }
    
    def __repr__(self) -> str:
        """String representation of the vector store manager."""
        return (
            f"VectorStoreManager(base_path={self.base_path}, "
            f"dimension={self.dimension}, loaded_stores={len(self.stores)})"
        )


# ============================================================================
# Global Vector Store Manager Instance
# ============================================================================

_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager(
    base_path: Optional[Path] = None,
    dimension: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> VectorStoreManager:
    """
    Get the global vector store manager instance.
    
    This function creates a singleton vector store manager instance on first call
    and returns the cached instance on subsequent calls.
    
    Args:
        base_path: Base directory for storing indices.
                  If None, uses path from settings.
        dimension: Embedding vector dimension.
                  If None, uses dimension from settings.
        settings: Settings instance. If None, uses global settings.
    
    Returns:
        VectorStoreManager: The global vector store manager instance
    """
    global _vector_store_manager
    
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager(
            base_path=base_path,
            dimension=dimension,
            settings=settings,
        )
    
    return _vector_store_manager


def reload_vector_store_manager(
    base_path: Optional[Path] = None,
    dimension: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> VectorStoreManager:
    """
    Reload the vector store manager with new parameters.
    
    This function forces a reload of the vector store manager, useful for
    testing or when configuration has changed.
    
    Args:
        base_path: Base directory for storing indices.
                  If None, uses path from settings.
        dimension: Embedding vector dimension.
                  If None, uses dimension from settings.
        settings: Settings instance. If None, uses global settings.
    
    Returns:
        VectorStoreManager: The newly loaded vector store manager instance
    """
    global _vector_store_manager
    _vector_store_manager = VectorStoreManager(
        base_path=base_path,
        dimension=dimension,
        settings=settings,
    )
    return _vector_store_manager
