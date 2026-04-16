"""
Unit tests for hybrid search with Reciprocal Rank Fusion (RRF).

This module tests the hybrid search functionality including:
- RRF score calculation
- Score normalization
- Combining BM25 and vector search results
- Ranking by RRF scores

Requirements:
- 5.5: Merge and rank results from BM25 and vector search by relevance
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.search_service import (
    UnifiedSearchService,
    SearchResult,
    MatchLocation,
)
from app.core.retrieval.retriever import SearchResult as SemanticSearchResult
from app.models.orm.code_chunk import CodeChunk


class TestReciprocalRankFusion:
    """Test suite for Reciprocal Rank Fusion implementation."""
    
    def test_normalize_scores_basic(self):
        """Test basic score normalization."""
        service = UnifiedSearchService(db=None)
        
        scores = [1.0, 2.0, 3.0, 4.0, 5.0]
        normalized = service._normalize_scores(scores)
        
        # Check range [0, 1]
        assert all(0.0 <= score <= 1.0 for score in normalized)
        
        # Check min and max
        assert min(normalized) == 0.0
        assert max(normalized) == 1.0
        
        # Check monotonicity
        for i in range(len(normalized) - 1):
            assert normalized[i] <= normalized[i + 1]
    
    def test_normalize_scores_empty(self):
        """Test normalization with empty list."""
        service = UnifiedSearchService(db=None)
        
        normalized = service._normalize_scores([])
        assert normalized == []
    
    def test_normalize_scores_single_value(self):
        """Test normalization with single value."""
        service = UnifiedSearchService(db=None)
        
        normalized = service._normalize_scores([5.0])
        assert normalized == [1.0]
    
    def test_normalize_scores_identical_values(self):
        """Test normalization when all scores are identical."""
        service = UnifiedSearchService(db=None)
        
        scores = [3.0, 3.0, 3.0, 3.0]
        normalized = service._normalize_scores(scores)
        
        # All should be 1.0 when identical
        assert all(score == 1.0 for score in normalized)
    
    def test_normalize_scores_negative_values(self):
        """Test normalization with negative values."""
        service = UnifiedSearchService(db=None)
        
        scores = [-2.0, -1.0, 0.0, 1.0, 2.0]
        normalized = service._normalize_scores(scores)
        
        # Check range [0, 1]
        assert all(0.0 <= score <= 1.0 for score in normalized)
        assert min(normalized) == 0.0
        assert max(normalized) == 1.0
    
    def test_rrf_basic(self):
        """Test basic RRF calculation."""
        service = UnifiedSearchService(db=None)
        
        # Create mock BM25 results
        chunk1 = MagicMock(spec=CodeChunk)
        chunk1.file_path = "file1.py"
        chunk1.start_line = 1
        
        chunk2 = MagicMock(spec=CodeChunk)
        chunk2.file_path = "file2.py"
        chunk2.start_line = 1
        
        bm25_results = [
            SearchResult(
                chunk=chunk1,
                score=10.0,
                matches=[],
                highlighted_content="content1",
            ),
            SearchResult(
                chunk=chunk2,
                score=5.0,
                matches=[],
                highlighted_content="content2",
            ),
        ]
        
        # Create mock vector results (same chunks, different order)
        vector_results = [
            SemanticSearchResult(
                chunk_id=uuid4(),
                repository_id=uuid4(),
                file_path="file2.py",
                start_line=1,
                end_line=10,
                language="python",
                content="content2",
                score=0.9,
            ),
            SemanticSearchResult(
                chunk_id=uuid4(),
                repository_id=uuid4(),
                file_path="file1.py",
                start_line=1,
                end_line=10,
                language="python",
                content="content1",
                score=0.8,
            ),
        ]
        
        # Calculate RRF scores
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=60,
        )
        
        # Both chunks should have RRF scores
        assert "file1.py:1" in rrf_scores
        assert "file2.py:1" in rrf_scores
        
        # RRF scores should be positive
        assert rrf_scores["file1.py:1"] > 0
        assert rrf_scores["file2.py:1"] > 0
        
        # file1.py is rank 1 in BM25 and rank 2 in vector
        # file2.py is rank 2 in BM25 and rank 1 in vector
        # Both should have similar RRF scores due to symmetric ranking
        assert abs(rrf_scores["file1.py:1"] - rrf_scores["file2.py:1"]) < 0.01
    
    def test_rrf_formula(self):
        """Test RRF formula: RRF(d) = 1/(k + rank)."""
        service = UnifiedSearchService(db=None)
        
        chunk = MagicMock(spec=CodeChunk)
        chunk.file_path = "file.py"
        chunk.start_line = 1
        
        bm25_results = [
            SearchResult(
                chunk=chunk,
                score=10.0,
                matches=[],
                highlighted_content="content",
            ),
        ]
        
        vector_results = []
        
        k = 60
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=k,
        )
        
        # RRF score should be 1/(k + rank) where rank is 0-indexed + 1
        expected_score = 1.0 / (k + 1)
        assert abs(rrf_scores["file.py:1"] - expected_score) < 0.0001
    
    def test_rrf_only_bm25_results(self):
        """Test RRF with only BM25 results."""
        service = UnifiedSearchService(db=None)
        
        chunk = MagicMock(spec=CodeChunk)
        chunk.file_path = "file.py"
        chunk.start_line = 1
        
        bm25_results = [
            SearchResult(
                chunk=chunk,
                score=10.0,
                matches=[],
                highlighted_content="content",
            ),
        ]
        
        vector_results = []
        
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=60,
        )
        
        assert "file.py:1" in rrf_scores
        assert rrf_scores["file.py:1"] > 0
    
    def test_rrf_only_vector_results(self):
        """Test RRF with only vector results."""
        service = UnifiedSearchService(db=None)
        
        bm25_results = []
        
        vector_results = [
            SemanticSearchResult(
                chunk_id=uuid4(),
                repository_id=uuid4(),
                file_path="file.py",
                start_line=1,
                end_line=10,
                language="python",
                content="content",
                score=0.9,
            ),
        ]
        
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=60,
        )
        
        assert "file.py:1" in rrf_scores
        assert rrf_scores["file.py:1"] > 0
    
    def test_rrf_empty_results(self):
        """Test RRF with empty results."""
        service = UnifiedSearchService(db=None)
        
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=[],
            vector_results=[],
            k=60,
        )
        
        assert rrf_scores == {}
    
    def test_rrf_different_k_values(self):
        """Test RRF with different k values."""
        service = UnifiedSearchService(db=None)
        
        chunk = MagicMock(spec=CodeChunk)
        chunk.file_path = "file.py"
        chunk.start_line = 1
        
        bm25_results = [
            SearchResult(
                chunk=chunk,
                score=10.0,
                matches=[],
                highlighted_content="content",
            ),
        ]
        
        vector_results = []
        
        # Test with k=60 (standard)
        rrf_scores_60 = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=60,
        )
        
        # Test with k=10 (lower k gives more weight to top results)
        rrf_scores_10 = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=10,
        )
        
        # Lower k should give higher RRF score
        assert rrf_scores_10["file.py:1"] > rrf_scores_60["file.py:1"]
    
    def test_rrf_rank_order_matters(self):
        """Test that RRF gives higher scores to higher-ranked results."""
        service = UnifiedSearchService(db=None)
        
        chunk1 = MagicMock(spec=CodeChunk)
        chunk1.file_path = "file1.py"
        chunk1.start_line = 1
        
        chunk2 = MagicMock(spec=CodeChunk)
        chunk2.file_path = "file2.py"
        chunk2.start_line = 1
        
        chunk3 = MagicMock(spec=CodeChunk)
        chunk3.file_path = "file3.py"
        chunk3.start_line = 1
        
        bm25_results = [
            SearchResult(chunk=chunk1, score=10.0, matches=[], highlighted_content=""),
            SearchResult(chunk=chunk2, score=5.0, matches=[], highlighted_content=""),
            SearchResult(chunk=chunk3, score=1.0, matches=[], highlighted_content=""),
        ]
        
        vector_results = []
        
        rrf_scores = service._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=60,
        )
        
        # Higher-ranked results should have higher RRF scores
        assert rrf_scores["file1.py:1"] > rrf_scores["file2.py:1"]
        assert rrf_scores["file2.py:1"] > rrf_scores["file3.py:1"]


@pytest.mark.asyncio
class TestHybridSearchIntegration:
    """Integration tests for hybrid search."""
    
    async def test_search_hybrid_combines_results(self):
        """Test that hybrid search combines BM25 and vector results."""
        # Mock database session
        db = AsyncMock()
        
        # Create service with mocked dependencies
        service = UnifiedSearchService(db=db)
        
        # Mock BM25 search
        chunk1 = MagicMock(spec=CodeChunk)
        chunk1.id = uuid4()
        chunk1.repository_id = uuid4()
        chunk1.file_path = "file1.py"
        chunk1.start_line = 1
        chunk1.end_line = 10
        chunk1.language = "python"
        chunk1.content = "content1"
        
        bm25_result = SearchResult(
            chunk=chunk1,
            score=10.0,
            matches=[],
            highlighted_content="content1",
        )
        
        service.bm25_service.search = AsyncMock(return_value=[bm25_result])
        
        # Mock vector search
        vector_result = SemanticSearchResult(
            chunk_id=uuid4(),
            repository_id=uuid4(),
            file_path="file2.py",
            start_line=1,
            end_line=10,
            language="python",
            content="content2",
            score=0.9,
        )
        
        service.vector_service.search = AsyncMock(return_value=[vector_result])
        
        # Perform hybrid search
        results = await service.search_hybrid(
            query="test query",
            top_k=10,
        )
        
        # Should have results from both searches
        assert len(results) == 2
        
        # Results should have RRF scores
        assert all("rrf_score" in result for result in results)
        
        # Results should be sorted by RRF score
        for i in range(len(results) - 1):
            assert results[i]["rrf_score"] >= results[i + 1]["rrf_score"]
    
    async def test_search_hybrid_respects_top_k(self):
        """Test that hybrid search returns correct number of results."""
        db = AsyncMock()
        service = UnifiedSearchService(db=db)
        
        # Mock multiple results
        bm25_results = []
        vector_results = []
        
        for i in range(20):
            chunk = MagicMock(spec=CodeChunk)
            chunk.id = uuid4()
            chunk.repository_id = uuid4()
            chunk.file_path = f"file{i}.py"
            chunk.start_line = 1
            chunk.end_line = 10
            chunk.language = "python"
            chunk.content = f"content{i}"
            
            bm25_results.append(
                SearchResult(
                    chunk=chunk,
                    score=20.0 - i,
                    matches=[],
                    highlighted_content=f"content{i}",
                )
            )
            
            vector_results.append(
                SemanticSearchResult(
                    chunk_id=uuid4(),
                    repository_id=uuid4(),
                    file_path=f"file{i}.py",
                    start_line=1,
                    end_line=10,
                    language="python",
                    content=f"content{i}",
                    score=1.0 - (i * 0.05),
                )
            )
        
        service.bm25_service.search = AsyncMock(return_value=bm25_results)
        service.vector_service.search = AsyncMock(return_value=vector_results)
        
        # Request top 5 results
        results = await service.search_hybrid(
            query="test query",
            top_k=5,
        )
        
        # Should return exactly 5 results
        assert len(results) == 5
    
    async def test_search_hybrid_with_repository_filter(self):
        """Test that hybrid search passes repository filter to both searches."""
        db = AsyncMock()
        service = UnifiedSearchService(db=db)
        
        service.bm25_service.search = AsyncMock(return_value=[])
        service.vector_service.search = AsyncMock(return_value=[])
        
        repo_ids = [uuid4(), uuid4()]
        
        await service.search_hybrid(
            query="test query",
            top_k=10,
            repository_ids=repo_ids,
        )
        
        # Verify repository filter was passed to both searches
        service.bm25_service.search.assert_called_once()
        service.vector_service.search.assert_called_once()
        
        bm25_call_kwargs = service.bm25_service.search.call_args.kwargs
        vector_call_kwargs = service.vector_service.search.call_args.kwargs
        
        assert bm25_call_kwargs["repository_ids"] == repo_ids
        assert vector_call_kwargs["repository_ids"] == repo_ids
    
    async def test_search_hybrid_retrieval_multiplier(self):
        """Test that hybrid search retrieves more results initially."""
        db = AsyncMock()
        service = UnifiedSearchService(db=db)
        
        service.bm25_service.search = AsyncMock(return_value=[])
        service.vector_service.search = AsyncMock(return_value=[])
        
        await service.search_hybrid(
            query="test query",
            top_k=10,
            retrieval_multiplier=3,
        )
        
        # Should retrieve top_k * retrieval_multiplier from each search
        bm25_call_kwargs = service.bm25_service.search.call_args.kwargs
        vector_call_kwargs = service.vector_service.search.call_args.kwargs
        
        assert bm25_call_kwargs["top_k"] == 30  # 10 * 3
        assert vector_call_kwargs["top_k"] == 30  # 10 * 3
