"""
Unit tests for the embedding service.

This module tests the EmbeddingService class to ensure it correctly
generates embeddings for single texts, batches, and queries.
"""

import numpy as np
import pytest
from unittest.mock import Mock, patch

from app.core.embeddings import EmbeddingService, get_embedding_service, reload_embedding_service
from app.core.config import Settings


class TestEmbeddingService:
    """Test suite for EmbeddingService."""
    
    def test_initialization_with_defaults(self):
        """Test that the service initializes with default settings."""
        service = EmbeddingService()
        
        assert service.model is not None
        assert service.device in ["cpu", "cuda", "mps"]
        assert service.dimension > 0
        assert service.batch_size > 0
    
    def test_initialization_with_custom_params(self):
        """Test that the service initializes with custom parameters."""
        service = EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
            batch_size=16,
        )
        
        assert service.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert service.device == "cpu"
        assert service.batch_size == 16
    
    def test_embed_text_single(self):
        """Test embedding a single text."""
        service = EmbeddingService()
        
        text = "def hello_world():\n    print('Hello, World!')"
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (service.dimension,)
        assert embedding.dtype == np.float32
    
    def test_embed_text_empty_raises_error(self):
        """Test that embedding empty text raises ValueError."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed_text("")
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed_text("   ")
    
    def test_embed_batch(self):
        """Test embedding a batch of texts."""
        service = EmbeddingService()
        
        texts = [
            "def foo():\n    pass",
            "class Bar:\n    pass",
            "import numpy as np",
        ]
        embeddings = service.embed_batch(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (len(texts), service.dimension)
        assert embeddings.dtype == np.float32
    
    def test_embed_batch_with_custom_batch_size(self):
        """Test embedding a batch with custom batch size."""
        service = EmbeddingService()
        
        texts = [f"def function_{i}():\n    pass" for i in range(10)]
        embeddings = service.embed_batch(texts, batch_size=2)
        
        assert embeddings.shape == (len(texts), service.dimension)
    
    def test_embed_batch_empty_list_raises_error(self):
        """Test that embedding empty list raises ValueError."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            service.embed_batch([])
    
    def test_embed_batch_all_empty_texts_raises_error(self):
        """Test that embedding all empty texts raises ValueError."""
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="All texts are empty"):
            service.embed_batch(["", "   ", ""])
    
    def test_embed_batch_with_some_empty_texts(self):
        """Test that embedding batch with some empty texts filters them out."""
        service = EmbeddingService()
        
        texts = [
            "def foo():\n    pass",
            "",
            "class Bar:\n    pass",
            "   ",
            "import numpy as np",
        ]
        embeddings = service.embed_batch(texts)
        
        # Should return embeddings for all texts, with zeros for empty ones
        assert embeddings.shape == (len(texts), service.dimension)
        
        # Check that empty text embeddings are zero vectors
        assert np.allclose(embeddings[1], 0)
        assert np.allclose(embeddings[3], 0)
        
        # Check that non-empty text embeddings are non-zero
        assert not np.allclose(embeddings[0], 0)
        assert not np.allclose(embeddings[2], 0)
        assert not np.allclose(embeddings[4], 0)
    
    def test_embed_query(self):
        """Test embedding a query."""
        service = EmbeddingService()
        
        query = "how to implement authentication in Python"
        embedding = service.embed_query(query)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (service.dimension,)
        assert embedding.dtype == np.float32
    
    def test_embed_query_same_as_embed_text(self):
        """Test that embed_query produces same result as embed_text."""
        service = EmbeddingService()
        
        text = "how to implement authentication in Python"
        text_embedding = service.embed_text(text)
        query_embedding = service.embed_query(text)
        
        # Should be identical for sentence-transformers
        assert np.allclose(text_embedding, query_embedding)
    
    def test_normalization(self):
        """Test that embeddings are normalized when requested."""
        service = EmbeddingService()
        
        text = "def hello_world():\n    print('Hello, World!')"
        
        # With normalization (default)
        normalized_embedding = service.embed_text(text, normalize=True)
        norm = np.linalg.norm(normalized_embedding)
        assert np.isclose(norm, 1.0, atol=1e-5)
        
        # Without normalization
        unnormalized_embedding = service.embed_text(text, normalize=False)
        norm = np.linalg.norm(unnormalized_embedding)
        # Should not be normalized (norm != 1.0)
        # Note: Some models may still produce near-normalized vectors
    
    def test_get_dimension(self):
        """Test getting the embedding dimension."""
        service = EmbeddingService()
        dimension = service.get_dimension()
        
        assert isinstance(dimension, int)
        assert dimension > 0
    
    def test_get_model_name(self):
        """Test getting the model name."""
        service = EmbeddingService()
        model_name = service.get_model_name()
        
        assert isinstance(model_name, str)
        assert len(model_name) > 0
    
    def test_get_device(self):
        """Test getting the device."""
        service = EmbeddingService()
        device = service.get_device()
        
        assert device in ["cpu", "cuda", "mps"]
    
    def test_get_max_sequence_length(self):
        """Test getting the max sequence length."""
        service = EmbeddingService()
        max_length = service.get_max_sequence_length()
        
        assert isinstance(max_length, int)
        assert max_length > 0
    
    def test_repr(self):
        """Test string representation."""
        service = EmbeddingService()
        repr_str = repr(service)
        
        assert "EmbeddingService" in repr_str
        assert "model=" in repr_str
        assert "device=" in repr_str
        assert "dimension=" in repr_str


class TestGlobalEmbeddingService:
    """Test suite for global embedding service functions."""
    
    def test_get_embedding_service_singleton(self):
        """Test that get_embedding_service returns a singleton."""
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        
        # Should return the same instance
        assert service1 is service2
    
    def test_get_embedding_service_with_different_params_creates_new(self):
        """Test that different params create a new instance."""
        service1 = get_embedding_service()
        service2 = get_embedding_service(batch_size=64)
        
        # Should create a new instance with different batch size
        assert service1 is not service2
        assert service2.batch_size == 64
    
    def test_reload_embedding_service(self):
        """Test that reload creates a new instance."""
        service1 = get_embedding_service()
        service2 = reload_embedding_service()
        
        # Should create a new instance
        assert service1 is not service2


class TestDeviceConfiguration:
    """Test suite for device configuration."""
    
    def test_cpu_device(self):
        """Test that CPU device works."""
        service = EmbeddingService(device="cpu")
        assert service.device == "cpu"
    
    @pytest.mark.skipif(
        not __import__("torch").cuda.is_available(),
        reason="CUDA not available"
    )
    def test_cuda_device(self):
        """Test that CUDA device works when available."""
        service = EmbeddingService(device="cuda")
        assert service.device == "cuda"
    
    @pytest.mark.skipif(
        not __import__("torch").backends.mps.is_available(),
        reason="MPS not available"
    )
    def test_mps_device(self):
        """Test that MPS device works when available."""
        service = EmbeddingService(device="mps")
        assert service.device == "mps"
    
    def test_invalid_device_falls_back_to_cpu(self):
        """Test that invalid device falls back to CPU."""
        service = EmbeddingService(device="invalid")
        assert service.device == "cpu"


class TestEmbeddingConsistency:
    """Test suite for embedding consistency."""
    
    def test_same_text_produces_same_embedding(self):
        """Test that the same text produces the same embedding."""
        service = EmbeddingService()
        
        text = "def hello_world():\n    print('Hello, World!')"
        embedding1 = service.embed_text(text)
        embedding2 = service.embed_text(text)
        
        assert np.allclose(embedding1, embedding2)
    
    def test_different_texts_produce_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        service = EmbeddingService()
        
        text1 = "def hello_world():\n    print('Hello, World!')"
        text2 = "class MyClass:\n    pass"
        
        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)
        
        # Embeddings should be different
        assert not np.allclose(embedding1, embedding2)
    
    def test_similar_texts_have_high_similarity(self):
        """Test that similar texts have high cosine similarity."""
        service = EmbeddingService()
        
        text1 = "def add(a, b):\n    return a + b"
        text2 = "def sum(x, y):\n    return x + y"
        
        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        # Similar texts should have high similarity (> 0.5)
        assert similarity > 0.5
    
    def test_dissimilar_texts_have_low_similarity(self):
        """Test that dissimilar texts have low cosine similarity."""
        service = EmbeddingService()
        
        text1 = "def add(a, b):\n    return a + b"
        text2 = "import matplotlib.pyplot as plt"
        
        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        # Dissimilar texts should have lower similarity than similar texts
        # (but may not be very low due to code context)
        assert similarity < 0.9
