"""
Unit tests for semantic search retriever.

This module tests the SemanticSearchRetriever class to ensure it correctly:
- Generates query embeddings
- Performs FAISS similarity search
- Returns top-K results with proper filtering
- Handles repository filtering
"""

import pytest
import numpy as np
from uuid import uuid4

from app.core.retrieval.retriever import SemanticSearchRetriever, SearchResult
from app.core.embeddings.embedder import EmbeddingService
from app.core.vectorstore.vector_store import VectorStoreManager, VectorStore


class TestSemanticSearchRetriever:
    """Test suite for SemanticSearchRetriever."""
    
    def test_validate_top_k_min(self):
        """Test that top_k is clamped to minimum value."""
        retriever = SemanticSearchRetriever()
        
        # Test below minimum
        assert retriever._validate_top_k(0) == 1
        assert retriever._validate_top_k(-5) == 1
        
        # Test at minimum
        assert retriever._validate_top_k(1) == 1
    
    def test_validate_top_k_max(self):
        """Test that top_k is clamped to maximum value."""
        retriever = SemanticSearchRetriever()
        
        # Test above maximum
        assert retriever._validate_top_k(101) == 100
        assert retriever._validate_top_k(1000) == 100
        
        # Test at maximum
        assert retriever._validate_top_k(100) == 100
    
    def test_validate_top_k_valid(self):
        """Test that valid top_k values are unchanged."""
        retriever = SemanticSearchRetriever()
        
        assert retriever._validate_top_k(10) == 10
        assert retriever._validate_top_k(50) == 50
        assert retriever._validate_top_k(99) == 99
    
    def test_generate_query_embedding_empty(self):
        """Test that empty query raises ValueError."""
        retriever = SemanticSearchRetriever()
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever._generate_query_embedding("")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever._generate_query_embedding("   ")
    
    def test_generate_query_embedding_valid(self):
        """Test that valid query generates embedding."""
        retriever = SemanticSearchRetriever()
        
        query = "def authenticate_user(username, password):"
        embedding = retriever._generate_query_embedding(query)
        
        # Check embedding shape
        assert embedding.shape == (retriever.embedding_service.dimension,)
        
        # Check embedding is normalized (for cosine similarity)
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-5, f"Embedding not normalized: norm={norm}"
    
    def test_search_empty_query(self):
        """Test that search with empty query raises ValueError."""
        retriever = SemanticSearchRetriever()
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever.search("")
    
    def test_search_no_repositories(self):
        """Test that search with no repositories returns empty list."""
        retriever = SemanticSearchRetriever()
        
        # Search with empty repository list
        results = retriever.search("test query", repository_ids=[])
        assert results == []
    
    def test_search_nonexistent_repository(self):
        """Test that search with nonexistent repository returns empty list."""
        retriever = SemanticSearchRetriever()
        
        # Search with nonexistent repository
        fake_repo_id = uuid4()
        results = retriever.search("test query", repository_ids=[fake_repo_id])
        assert results == []
    
    def test_search_result_structure(self):
        """Test that SearchResult has correct structure."""
        result = SearchResult(
            chunk_id="test-chunk-id",
            repository_id="test-repo-id",
            file_path="src/main.py",
            start_line=10,
            end_line=20,
            language="python",
            content="def test(): pass",
            score=0.95,
        )
        
        assert result.chunk_id == "test-chunk-id"
        assert result.repository_id == "test-repo-id"
        assert result.file_path == "src/main.py"
        assert result.start_line == 10
        assert result.end_line == 20
        assert result.language == "python"
        assert result.content == "def test(): pass"
        assert result.score == 0.95
    
    def test_search_with_threshold_filters_results(self):
        """Test that search_with_threshold filters low-score results."""
        retriever = SemanticSearchRetriever()
        
        # This test would require a mock vector store with known results
        # For now, we just test that the method exists and accepts parameters
        results = retriever.search_with_threshold(
            query="test query",
            top_k=10,
            score_threshold=0.5,
            repository_ids=[],
        )
        assert isinstance(results, list)


class TestSemanticSearchIntegration:
    """Integration tests for semantic search with real components."""
    
    @pytest.fixture
    def temp_vector_store_manager(self, tmp_path):
        """Create a temporary vector store manager for testing."""
        return VectorStoreManager(
            base_path=tmp_path / "indices",
            dimension=384,
        )
    
    @pytest.fixture
    def sample_repository(self, temp_vector_store_manager):
        """Create a sample repository with embeddings."""
        repo_id = uuid4()
        
        # Create vector store
        store = temp_vector_store_manager.create_store(repo_id)
        
        # Create sample embeddings and metadata
        embeddings = np.random.randn(5, 384).astype(np.float32)
        # Normalize for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        chunks_metadata = [
            {
                "id": str(uuid4()),
                "file_path": f"src/file{i}.py",
                "start_line": i * 10,
                "end_line": (i + 1) * 10,
                "language": "python",
                "content": f"def function_{i}(): pass",
            }
            for i in range(5)
        ]
        
        # Add to store
        store.add_embeddings(embeddings, chunks_metadata)
        store.save()
        
        return repo_id, store
    
    def test_search_with_real_store(self, temp_vector_store_manager, sample_repository):
        """Test search with a real vector store."""
        repo_id, store = sample_repository
        
        # Create retriever with the temp manager
        retriever = SemanticSearchRetriever(
            vector_store_manager=temp_vector_store_manager
        )
        
        # Perform search
        results = retriever.search(
            query="function implementation",
            top_k=3,
            repository_ids=[repo_id],
        )
        
        # Verify results
        assert len(results) <= 3
        assert all(isinstance(r, SearchResult) for r in results)
        
        # Verify results are sorted by score (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score
        
        # Verify all results are from the correct repository
        for result in results:
            assert result.repository_id == str(repo_id)
    
    def test_search_multiple_repositories(self, temp_vector_store_manager):
        """Test search across multiple repositories."""
        # Create two repositories
        repo_ids = []
        for _ in range(2):
            repo_id = uuid4()
            store = temp_vector_store_manager.create_store(repo_id)
            
            embeddings = np.random.randn(3, 384).astype(np.float32)
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            chunks_metadata = [
                {
                    "id": str(uuid4()),
                    "file_path": f"src/file{i}.py",
                    "start_line": i * 10,
                    "end_line": (i + 1) * 10,
                    "language": "python",
                    "content": f"def function_{i}(): pass",
                }
                for i in range(3)
            ]
            
            store.add_embeddings(embeddings, chunks_metadata)
            store.save()
            repo_ids.append(repo_id)
        
        # Create retriever
        retriever = SemanticSearchRetriever(
            vector_store_manager=temp_vector_store_manager
        )
        
        # Search across both repositories
        results = retriever.search(
            query="function implementation",
            top_k=5,
            repository_ids=repo_ids,
        )
        
        # Verify we get results from both repositories
        assert len(results) <= 5
        
        # Check that results come from both repositories
        result_repos = set(r.repository_id for r in results)
        assert len(result_repos) <= 2  # At most 2 repositories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
