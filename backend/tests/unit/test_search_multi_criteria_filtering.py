"""
Unit tests for multi-criteria filtering in search service.

This module tests the multi-criteria filtering functionality for:
- File extension filtering
- Directory path filtering
- Programming language filtering
- Combining multiple filters

Requirements:
- 5.6: Support filtering by file extension, directory path, and programming language
"""

import pytest
from uuid import uuid4

from app.services.search_service import VectorSearchService
from app.core.retrieval.retriever import SearchResult as SemanticSearchResult


class TestMultiCriteriaFiltering:
    """Test multi-criteria filtering functionality."""
    
    @pytest.fixture
    def sample_results(self):
        """Create sample search results for testing."""
        repo_id = str(uuid4())
        
        return [
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=repo_id,
                file_path="src/main.py",
                start_line=1,
                end_line=10,
                language="python",
                content="def main():\n    pass",
                score=0.95,
            ),
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=repo_id,
                file_path="src/utils.js",
                start_line=1,
                end_line=10,
                language="javascript",
                content="function utils() {}",
                score=0.90,
            ),
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=repo_id,
                file_path="lib/helper.py",
                start_line=1,
                end_line=10,
                language="python",
                content="def helper():\n    pass",
                score=0.85,
            ),
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=repo_id,
                file_path="tests/test_main.py",
                start_line=1,
                end_line=10,
                language="python",
                content="def test_main():\n    pass",
                score=0.80,
            ),
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=repo_id,
                file_path="src/app.ts",
                start_line=1,
                end_line=10,
                language="typescript",
                content="function app() {}",
                score=0.75,
            ),
        ]
    
    def test_filter_by_file_extension_single(self, sample_results):
        """Test filtering by a single file extension."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py"],
        )
        
        assert len(filtered) == 3
        assert all(r.file_path.endswith(".py") for r in filtered)
    
    def test_filter_by_file_extension_multiple(self, sample_results):
        """Test filtering by multiple file extensions."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py", ".js"],
        )
        
        assert len(filtered) == 4
        assert all(
            r.file_path.endswith(".py") or r.file_path.endswith(".js")
            for r in filtered
        )
    
    def test_filter_by_directory_path_single(self, sample_results):
        """Test filtering by a single directory path."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            directory_paths=["src/"],
        )
        
        assert len(filtered) == 3
        assert all(r.file_path.startswith("src/") for r in filtered)
    
    def test_filter_by_directory_path_multiple(self, sample_results):
        """Test filtering by multiple directory paths."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            directory_paths=["src/", "lib/"],
        )
        
        assert len(filtered) == 4
        assert all(
            r.file_path.startswith("src/") or r.file_path.startswith("lib/")
            for r in filtered
        )
    
    def test_filter_by_language_single(self, sample_results):
        """Test filtering by a single programming language."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            languages=["python"],
        )
        
        assert len(filtered) == 3
        assert all(r.language == "python" for r in filtered)
    
    def test_filter_by_language_multiple(self, sample_results):
        """Test filtering by multiple programming languages."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            languages=["python", "javascript"],
        )
        
        assert len(filtered) == 4
        assert all(r.language in ["python", "javascript"] for r in filtered)
    
    def test_combine_file_extension_and_directory(self, sample_results):
        """Test combining file extension and directory path filters."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py"],
            directory_paths=["src/"],
        )
        
        assert len(filtered) == 1
        assert filtered[0].file_path == "src/main.py"
    
    def test_combine_all_filters(self, sample_results):
        """Test combining all three filter types."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py"],
            directory_paths=["src/", "lib/"],
            languages=["python"],
        )
        
        assert len(filtered) == 2
        assert all(r.file_path.endswith(".py") for r in filtered)
        assert all(
            r.file_path.startswith("src/") or r.file_path.startswith("lib/")
            for r in filtered
        )
        assert all(r.language == "python" for r in filtered)
    
    def test_filter_no_matches(self, sample_results):
        """Test filtering with no matching results."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".go"],
        )
        
        assert len(filtered) == 0
    
    def test_filter_no_filters_applied(self, sample_results):
        """Test that no filtering returns all results."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
        )
        
        assert len(filtered) == len(sample_results)
        assert filtered == sample_results
    
    def test_filter_preserves_order(self, sample_results):
        """Test that filtering preserves the original order of results."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py"],
        )
        
        # Check that scores are in descending order (original order preserved)
        scores = [r.score for r in filtered]
        assert scores == sorted(scores, reverse=True)
    
    def test_filter_empty_results(self):
        """Test filtering with empty results list."""
        service = VectorSearchService()
        
        filtered = service._apply_filters(
            results=[],
            file_extensions=[".py"],
        )
        
        assert len(filtered) == 0
    
    def test_filter_case_sensitive_extensions(self, sample_results):
        """Test that file extension filtering is case-sensitive."""
        service = VectorSearchService()
        
        # Add a result with uppercase extension
        sample_results.append(
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=str(uuid4()),
                file_path="src/Main.PY",
                start_line=1,
                end_line=10,
                language="python",
                content="def main():\n    pass",
                score=0.70,
            )
        )
        
        filtered = service._apply_filters(
            results=sample_results,
            file_extensions=[".py"],
        )
        
        # Should not match .PY (uppercase)
        assert not any(r.file_path == "src/Main.PY" for r in filtered)
    
    def test_filter_partial_directory_match(self, sample_results):
        """Test that directory filtering uses startswith (prefix match)."""
        service = VectorSearchService()
        
        # Add a result with nested directory
        sample_results.append(
            SemanticSearchResult(
                chunk_id=str(uuid4()),
                repository_id=str(uuid4()),
                file_path="src/components/button.py",
                start_line=1,
                end_line=10,
                language="python",
                content="class Button:\n    pass",
                score=0.70,
            )
        )
        
        filtered = service._apply_filters(
            results=sample_results,
            directory_paths=["src/"],
        )
        
        # Should match nested directories under src/
        assert any(r.file_path == "src/components/button.py" for r in filtered)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
