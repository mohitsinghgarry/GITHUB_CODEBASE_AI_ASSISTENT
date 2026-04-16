"""
Tests for search API endpoints.

This module tests the search endpoints including semantic search,
keyword search, and hybrid search.
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.repository import Repository
from app.models.orm.code_chunk import CodeChunk


@pytest.fixture
async def test_repository(db_session: AsyncSession) -> Repository:
    """Create a test repository."""
    repo = Repository(
        url="https://github.com/test/repo",
        owner="test",
        name="repo",
        status="completed",
        chunk_count=2,
    )
    db_session.add(repo)
    await db_session.commit()
    await db_session.refresh(repo)
    return repo


@pytest.fixture
async def test_chunks(db_session: AsyncSession, test_repository: Repository) -> list[CodeChunk]:
    """Create test code chunks."""
    chunks = [
        CodeChunk(
            repository_id=test_repository.id,
            file_path="src/main.py",
            start_line=1,
            end_line=10,
            language="python",
            content="def hello_world():\n    print('Hello, World!')",
        ),
        CodeChunk(
            repository_id=test_repository.id,
            file_path="src/utils.py",
            start_line=1,
            end_line=15,
            language="python",
            content="def authenticate_user(username, password):\n    return True",
        ),
    ]
    
    for chunk in chunks:
        db_session.add(chunk)
    
    await db_session.commit()
    
    for chunk in chunks:
        await db_session.refresh(chunk)
    
    return chunks


class TestSemanticSearchEndpoint:
    """Tests for semantic search endpoint."""
    
    async def test_semantic_search_success(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test successful semantic search."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "authentication function",
                "top_k": 10,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_results" in data
        assert "query" in data
        assert data["query"] == "authentication function"
        assert isinstance(data["results"], list)
    
    async def test_semantic_search_with_repository_filter(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test semantic search with repository filtering."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "hello world",
                "top_k": 5,
                "repository_ids": [str(test_repository.id)],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_semantic_search_with_filters(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test semantic search with multi-criteria filters."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "function",
                "top_k": 10,
                "file_extensions": [".py"],
                "languages": ["python"],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_semantic_search_empty_query(self, client: AsyncClient):
        """Test semantic search with empty query."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "",
                "top_k": 10,
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_semantic_search_invalid_top_k(self, client: AsyncClient):
        """Test semantic search with invalid top_k."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test",
                "top_k": 0,  # Invalid: must be >= 1
            }
        )
        
        assert response.status_code == 422  # Validation error
        
        response = await client.post(
            "/api/v1/search/semantic",
            json={
                "query": "test",
                "top_k": 101,  # Invalid: must be <= 100
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestKeywordSearchEndpoint:
    """Tests for keyword search endpoint."""
    
    async def test_keyword_search_success(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test successful keyword search."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "hello",
                "top_k": 10,
                "mode": "case_insensitive",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_results" in data
        assert "query" in data
        assert data["query"] == "hello"
        assert isinstance(data["results"], list)
    
    async def test_keyword_search_exact_mode(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test keyword search with exact mode."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "Hello",
                "top_k": 10,
                "mode": "exact",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_keyword_search_regex_mode(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test keyword search with regex mode."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "def \\w+\\(",
                "top_k": 10,
                "mode": "regex",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_keyword_search_boolean_query(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test keyword search with boolean operators."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "def AND hello",
                "top_k": 10,
                "use_boolean": True,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_keyword_search_with_filters(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test keyword search with multi-criteria filters."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "def",
                "top_k": 10,
                "file_extensions": [".py"],
                "directory_paths": ["src/"],
                "languages": ["python"],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_keyword_search_invalid_mode(self, client: AsyncClient):
        """Test keyword search with invalid mode."""
        response = await client.post(
            "/api/v1/search/keyword",
            json={
                "query": "test",
                "top_k": 10,
                "mode": "invalid_mode",
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestHybridSearchEndpoint:
    """Tests for hybrid search endpoint."""
    
    async def test_hybrid_search_success(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test successful hybrid search."""
        response = await client.post(
            "/api/v1/search/hybrid",
            json={
                "query": "authentication",
                "top_k": 10,
                "bm25_weight": 0.5,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_results" in data
        assert "query" in data
        assert "bm25_weight" in data
        assert data["query"] == "authentication"
        assert data["bm25_weight"] == 0.5
        assert isinstance(data["results"], list)
    
    async def test_hybrid_search_with_repository_filter(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test hybrid search with repository filtering."""
        response = await client.post(
            "/api/v1/search/hybrid",
            json={
                "query": "function",
                "top_k": 5,
                "repository_ids": [str(test_repository.id)],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_hybrid_search_with_filters(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test hybrid search with multi-criteria filters."""
        response = await client.post(
            "/api/v1/search/hybrid",
            json={
                "query": "code",
                "top_k": 10,
                "file_extensions": [".py"],
                "languages": ["python"],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    async def test_hybrid_search_invalid_bm25_weight(self, client: AsyncClient):
        """Test hybrid search with invalid bm25_weight."""
        response = await client.post(
            "/api/v1/search/hybrid",
            json={
                "query": "test",
                "top_k": 10,
                "bm25_weight": 1.5,  # Invalid: must be <= 1.0
            }
        )
        
        assert response.status_code == 422  # Validation error
        
        response = await client.post(
            "/api/v1/search/hybrid",
            json={
                "query": "test",
                "top_k": 10,
                "bm25_weight": -0.1,  # Invalid: must be >= 0.0
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestSearchEndpointsIntegration:
    """Integration tests for search endpoints."""
    
    async def test_all_search_modes_return_consistent_structure(
        self,
        client: AsyncClient,
        test_repository: Repository,
        test_chunks: list[CodeChunk],
    ):
        """Test that all search modes return consistent response structure."""
        query = "function"
        
        # Semantic search
        semantic_response = await client.post(
            "/api/v1/search/semantic",
            json={"query": query, "top_k": 5}
        )
        
        # Keyword search
        keyword_response = await client.post(
            "/api/v1/search/keyword",
            json={"query": query, "top_k": 5}
        )
        
        # Hybrid search
        hybrid_response = await client.post(
            "/api/v1/search/hybrid",
            json={"query": query, "top_k": 5}
        )
        
        # All should succeed
        assert semantic_response.status_code == 200
        assert keyword_response.status_code == 200
        assert hybrid_response.status_code == 200
        
        # All should have consistent structure
        for response in [semantic_response, keyword_response, hybrid_response]:
            data = response.json()
            assert "results" in data
            assert "total_results" in data
            assert "query" in data
            assert isinstance(data["results"], list)
            
            # Check result structure if results exist
            if data["results"]:
                result = data["results"][0]
                assert "chunk" in result
                assert "score" in result
                assert "matches" in result
                assert "highlighted_content" in result
                
                # Check chunk structure
                chunk = result["chunk"]
                assert "id" in chunk
                assert "repository_id" in chunk
                assert "file_path" in chunk
                assert "start_line" in chunk
                assert "end_line" in chunk
                assert "language" in chunk
                assert "content" in chunk
