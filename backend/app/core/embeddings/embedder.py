"""
Embedding service wrapper using sentence-transformers.

This module provides a unified interface for generating embeddings from text
using sentence-transformers models. It supports single text embedding, batch
embedding, and query embedding with CPU/GPU device configuration.

Requirements:
- 2.6: Generate embeddings for all Code_Chunks using the configured embedding model
"""

import logging
from typing import List, Optional, Union

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using sentence-transformers.
    
    This service wraps a sentence-transformers model and provides methods
    for embedding single texts, batches of texts, and queries. It handles
    device configuration (CPU/GPU) and model loading.
    
    Attributes:
        model: The loaded SentenceTransformer model
        device: The device to run inference on (cpu, cuda, mps)
        dimension: The embedding vector dimension
        batch_size: Default batch size for batch processing
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: Optional[int] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to load.
                       If None, uses the model from settings.
            device: Device to run inference on ('cpu', 'cuda', 'mps').
                   If None, uses the device from settings.
            batch_size: Default batch size for batch processing.
                       If None, uses the batch size from settings.
            settings: Settings instance. If None, uses global settings.
        
        Raises:
            RuntimeError: If the model fails to load or device is unavailable
        """
        self.settings = settings or get_settings()
        
        # Use provided values or fall back to settings
        self.model_name = model_name or self.settings.embedding_model
        self.device = device or self.settings.embedding_device
        self.batch_size = batch_size or self.settings.embedding_batch_size
        self.dimension = self.settings.embedding_dimension
        
        # Validate and configure device
        self.device = self._configure_device(self.device)
        
        logger.info(
            f"Initializing EmbeddingService with model='{self.model_name}', "
            f"device='{self.device}', batch_size={self.batch_size}"
        )
        
        # Load the model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(
                f"Successfully loaded embedding model '{self.model_name}' "
                f"on device '{self.device}'"
            )
            
            # Verify embedding dimension matches configuration
            actual_dimension = self.model.get_sentence_embedding_dimension()
            if actual_dimension != self.dimension:
                logger.warning(
                    f"Model embedding dimension ({actual_dimension}) does not match "
                    f"configured dimension ({self.dimension}). Using model dimension."
                )
                self.dimension = actual_dimension
                
        except Exception as e:
            logger.error(f"Failed to load embedding model '{self.model_name}': {e}")
            raise RuntimeError(
                f"Failed to load embedding model '{self.model_name}': {e}"
            ) from e
    
    def _configure_device(self, device: str) -> str:
        """
        Configure and validate the device for inference.
        
        Args:
            device: Requested device ('cpu', 'cuda', 'mps')
        
        Returns:
            str: The validated device string
        
        Raises:
            RuntimeError: If the requested device is not available
        """
        device = device.lower()
        
        if device == "cuda":
            if not torch.cuda.is_available():
                logger.warning(
                    "CUDA requested but not available. Falling back to CPU."
                )
                return "cpu"
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            return "cuda"
        
        elif device == "mps":
            if not torch.backends.mps.is_available():
                logger.warning(
                    "MPS requested but not available. Falling back to CPU."
                )
                return "cpu"
            logger.info("Using MPS (Apple Silicon) device")
            return "mps"
        
        elif device == "cpu":
            logger.info("Using CPU device")
            return "cpu"
        
        else:
            logger.warning(
                f"Unknown device '{device}'. Falling back to CPU."
            )
            return "cpu"
    
    def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        This method is suitable for embedding individual texts or queries.
        For multiple texts, use embed_batch() for better performance.
        
        Args:
            text: The text to embed
            normalize: Whether to normalize the embedding vector (default: True)
        
        Returns:
            np.ndarray: The embedding vector of shape (dimension,)
        
        Raises:
            ValueError: If text is empty
            RuntimeError: If embedding generation fails
        
        Example:
            >>> service = EmbeddingService()
            >>> embedding = service.embed_text("def hello_world():")
            >>> embedding.shape
            (384,)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=False,
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}") from e
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        normalize: bool = True,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        This method is optimized for processing multiple texts efficiently.
        It processes texts in batches to balance memory usage and performance.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing. If None, uses default batch size.
            normalize: Whether to normalize the embedding vectors (default: True)
            show_progress: Whether to show a progress bar (default: False)
        
        Returns:
            np.ndarray: Array of embeddings of shape (len(texts), dimension)
        
        Raises:
            ValueError: If texts list is empty or contains empty strings
            RuntimeError: If embedding generation fails
        
        Example:
            >>> service = EmbeddingService()
            >>> texts = ["def foo():", "class Bar:", "import numpy"]
            >>> embeddings = service.embed_batch(texts)
            >>> embeddings.shape
            (3, 384)
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        if len(valid_texts) < len(texts):
            logger.warning(
                f"Filtered out {len(texts) - len(valid_texts)} empty texts "
                f"from batch of {len(texts)}"
            )
        
        try:
            # Use provided batch size or default
            effective_batch_size = batch_size or self.batch_size
            
            # Generate embeddings
            embeddings = self.model.encode(
                valid_texts,
                batch_size=effective_batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
            )
            
            # If we filtered out empty texts, create full array with zeros for empty texts
            if len(valid_texts) < len(texts):
                full_embeddings = np.zeros((len(texts), self.dimension), dtype=np.float32)
                full_embeddings[valid_indices] = embeddings
                return full_embeddings
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings for batch: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}") from e
    
    def embed_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding optimized for query text.
        
        This method is specifically designed for embedding user queries.
        Some models have different encoding strategies for queries vs documents,
        but sentence-transformers uses the same encoding for both by default.
        
        This method is provided for API consistency and potential future
        optimization with models that support query-specific encoding.
        
        Args:
            query: The query text to embed
            normalize: Whether to normalize the embedding vector (default: True)
        
        Returns:
            np.ndarray: The query embedding vector of shape (dimension,)
        
        Raises:
            ValueError: If query is empty
            RuntimeError: If embedding generation fails
        
        Example:
            >>> service = EmbeddingService()
            >>> query_embedding = service.embed_query("how to implement authentication")
            >>> query_embedding.shape
            (384,)
        """
        # For sentence-transformers, query encoding is the same as text encoding
        # This method exists for API consistency and potential future optimization
        return self.embed_text(query, normalize=normalize)
    
    def get_dimension(self) -> int:
        """
        Get the embedding dimension.
        
        Returns:
            int: The embedding vector dimension
        """
        return self.dimension
    
    def get_model_name(self) -> str:
        """
        Get the model name.
        
        Returns:
            str: The name of the loaded model
        """
        return self.model_name
    
    def get_device(self) -> str:
        """
        Get the device being used for inference.
        
        Returns:
            str: The device string ('cpu', 'cuda', or 'mps')
        """
        return self.device
    
    def get_max_sequence_length(self) -> int:
        """
        Get the maximum sequence length supported by the model.
        
        Returns:
            int: Maximum sequence length in tokens
        """
        return self.model.max_seq_length
    
    def __repr__(self) -> str:
        """String representation of the embedding service."""
        return (
            f"EmbeddingService(model='{self.model_name}', "
            f"device='{self.device}', dimension={self.dimension})"
        )


# ============================================================================
# Global Embedding Service Instance
# ============================================================================

_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
    batch_size: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> EmbeddingService:
    """
    Get the global embedding service instance.
    
    This function creates a singleton embedding service instance on first call
    and returns the cached instance on subsequent calls. If parameters are
    provided that differ from the cached instance, a new instance is created.
    
    Args:
        model_name: Name of the sentence-transformers model to load.
                   If None, uses the model from settings.
        device: Device to run inference on ('cpu', 'cuda', 'mps').
               If None, uses the device from settings.
        batch_size: Default batch size for batch processing.
                   If None, uses the batch size from settings.
        settings: Settings instance. If None, uses global settings.
    
    Returns:
        EmbeddingService: The global embedding service instance
    
    Raises:
        RuntimeError: If the model fails to load or device is unavailable
    """
    global _embedding_service
    
    # Get settings
    settings = settings or get_settings()
    
    # Determine if we need to create a new instance
    needs_new_instance = (
        _embedding_service is None
        or (model_name and model_name != _embedding_service.model_name)
        or (device and device != _embedding_service.device)
        or (batch_size and batch_size != _embedding_service.batch_size)
    )
    
    if needs_new_instance:
        _embedding_service = EmbeddingService(
            model_name=model_name,
            device=device,
            batch_size=batch_size,
            settings=settings,
        )
    
    return _embedding_service


def reload_embedding_service(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
    batch_size: Optional[int] = None,
    settings: Optional[Settings] = None,
) -> EmbeddingService:
    """
    Reload the embedding service with new parameters.
    
    This function forces a reload of the embedding service, useful for
    testing or when configuration has changed.
    
    Args:
        model_name: Name of the sentence-transformers model to load.
                   If None, uses the model from settings.
        device: Device to run inference on ('cpu', 'cuda', 'mps').
               If None, uses the device from settings.
        batch_size: Default batch size for batch processing.
                   If None, uses the batch size from settings.
        settings: Settings instance. If None, uses global settings.
    
    Returns:
        EmbeddingService: The newly loaded embedding service instance
    """
    global _embedding_service
    _embedding_service = EmbeddingService(
        model_name=model_name,
        device=device,
        batch_size=batch_size,
        settings=settings,
    )
    return _embedding_service
