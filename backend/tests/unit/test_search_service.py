"""
Unit tests for BM25 search service.

This module tests the BM25 keyword search functionality including:
- Exact match, case-insensitive match, and regex patterns
- Boolean operators (AND, OR, NOT)
- Match location highlighting
- Repository and file filtering
"""

import pytest
from uuid import uuid4

from app.services.search_service import (
    BM25SearchService,
    SearchMode,
    MatchLocation,
)
from app.models.orm.code_chunk import CodeChunk


class TestBM25SearchService:
    """Test suite for BM25SearchService."""
    
    def test_tokenize(self):
        """Test text tokenization."""
        service = BM25SearchService(db=None)
        
        # Test simple text
        tokens = service._tokenize("hello world")
        assert tokens == ["hello", "world"]
        
        # Test code with punctuation
        tokens = service._tokenize("def hello_world():")
        assert "def" in tokens
        assert "hello_world" in tokens
        
        # Test mixed case (should be lowercased)
        tokens = service._tokenize("HelloWorld")
        assert tokens == ["helloworld"]
    
    def test_find_matches_exact(self):
        """Test exact match finding."""
        service = BM25SearchService(db=None)
        
        content = "def hello():\n    print('Hello, World!')"
        query = "hello"
        
        matches = service._find_matches(content, query, SearchMode.EXACT)
        
        # Should find only lowercase 'hello'
        assert len(matches) == 1
        assert matches[0].matched_text == "hello"
        assert matches[0].line_number == 1
    
    def test_find_matches_case_insensitive(self):
        """Test case-insensitive match finding."""
        service = BM25SearchService(db=None)
        
        content = "def hello():\n    print('Hello, World!')"
        query = "hello"
        
        matches = service._find_matches(content, query, SearchMode.CASE_INSENSITIVE)
        
        # Should find both 'hello' and 'Hello'
        assert len(matches) == 2
        assert matches[0].matched_text == "hello"
        assert matches[1].matched_text == "Hello"
    
    def test_find_matches_regex(self):
        """Test regex pattern matching."""
        service = BM25SearchService(db=None)
        
        content = "def hello():\n    print('Hello, World!')\n    return hello_world"
        query = r"hello\w*"
        
        matches = service._find_matches(content, query, SearchMode.REGEX)
        
        # Should find 'hello', 'Hello', and 'hello_world'
        assert len(matches) >= 3
        matched_texts = [m.matched_text for m in matches]
        assert "hello" in matched_texts
        assert "Hello" in matched_texts
        assert "hello_world" in matched_texts
    
    def test_find_matches_line_numbers(self):
        """Test that line numbers are correctly calculated."""
        service = BM25SearchService(db=None)
        
        content = "line 1\nline 2 test\nline 3\nline 4 test"
        query = "test"
        
        matches = service._find_matches(content, query, SearchMode.CASE_INSENSITIVE)
        
        assert len(matches) == 2
        assert matches[0].line_number == 2
        assert matches[1].line_number == 4
    
    def test_highlight_matches(self):
        """Test match highlighting."""
        service = BM25SearchService(db=None)
        
        content = "hello world hello"
        matches = [
            MatchLocation(start=0, end=5, matched_text="hello", line_number=1),
            MatchLocation(start=12, end=17, matched_text="hello", line_number=1),
        ]
        
        highlighted = service._highlight_matches(content, matches)
        
        assert highlighted == "<<<hello>>> world <<<hello>>>"
    
    def test_highlight_matches_custom_markers(self):
        """Test match highlighting with custom markers."""
        service = BM25SearchService(db=None)
        
        content = "hello world"
        matches = [
            MatchLocation(start=0, end=5, matched_text="hello", line_number=1),
        ]
        
        highlighted = service._highlight_matches(
            content, matches, highlight_start="**", highlight_end="**"
        )
        
        assert highlighted == "**hello** world"
    
    def test_parse_boolean_query_and(self):
        """Test parsing AND boolean queries."""
        service = BM25SearchService(db=None)
        
        and_terms, or_terms, not_terms = service._parse_boolean_query("term1 AND term2")
        
        assert "term1" in and_terms or "term1" in or_terms
        assert "term2" in and_terms
        assert len(not_terms) == 0
    
    def test_parse_boolean_query_or(self):
        """Test parsing OR boolean queries."""
        service = BM25SearchService(db=None)
        
        and_terms, or_terms, not_terms = service._parse_boolean_query("term1 OR term2")
        
        assert "term1" in or_terms
        assert "term2" in or_terms
        assert len(and_terms) == 0
        assert len(not_terms) == 0
    
    def test_parse_boolean_query_not(self):
        """Test parsing NOT boolean queries."""
        service = BM25SearchService(db=None)
        
        and_terms, or_terms, not_terms = service._parse_boolean_query("term1 NOT term2")
        
        assert "term1" in or_terms
        assert "term2" in not_terms
    
    def test_parse_boolean_query_complex(self):
        """Test parsing complex boolean queries."""
        service = BM25SearchService(db=None)
        
        and_terms, or_terms, not_terms = service._parse_boolean_query(
            "term1 AND term2 OR term3 NOT term4"
        )
        
        assert "term2" in and_terms
        assert "term1" in or_terms or "term1" in and_terms
        assert "term3" in or_terms
        assert "term4" in not_terms
    
    def test_evaluate_boolean_query_and(self):
        """Test evaluating AND boolean queries."""
        service = BM25SearchService(db=None)
        
        content = "this is a test with multiple terms"
        
        # Both terms present - should match
        result = service._evaluate_boolean_query(
            content,
            and_terms=["test", "multiple"],
            or_terms=[],
            not_terms=[],
        )
        assert result is True
        
        # One term missing - should not match
        result = service._evaluate_boolean_query(
            content,
            and_terms=["test", "missing"],
            or_terms=[],
            not_terms=[],
        )
        assert result is False
    
    def test_evaluate_boolean_query_or(self):
        """Test evaluating OR boolean queries."""
        service = BM25SearchService(db=None)
        
        content = "this is a test"
        
        # At least one term present - should match
        result = service._evaluate_boolean_query(
            content,
            and_terms=[],
            or_terms=["test", "missing"],
            not_terms=[],
        )
        assert result is True
        
        # No terms present - should not match
        result = service._evaluate_boolean_query(
            content,
            and_terms=[],
            or_terms=["missing1", "missing2"],
            not_terms=[],
        )
        assert result is False
    
    def test_evaluate_boolean_query_not(self):
        """Test evaluating NOT boolean queries."""
        service = BM25SearchService(db=None)
        
        content = "this is a test"
        
        # Excluded term not present - should match
        result = service._evaluate_boolean_query(
            content,
            and_terms=[],
            or_terms=["test"],
            not_terms=["missing"],
        )
        assert result is True
        
        # Excluded term present - should not match
        result = service._evaluate_boolean_query(
            content,
            and_terms=[],
            or_terms=["test"],
            not_terms=["test"],
        )
        assert result is False
    
    def test_evaluate_boolean_query_case_insensitive(self):
        """Test case-insensitive boolean query evaluation."""
        service = BM25SearchService(db=None)
        
        content = "This Is A Test"
        
        result = service._evaluate_boolean_query(
            content,
            and_terms=["test"],
            or_terms=[],
            not_terms=[],
            mode=SearchMode.CASE_INSENSITIVE,
        )
        assert result is True
    
    def test_evaluate_boolean_query_regex(self):
        """Test regex boolean query evaluation."""
        service = BM25SearchService(db=None)
        
        content = "def hello_world():"
        
        result = service._evaluate_boolean_query(
            content,
            and_terms=[r"hello\w+"],
            or_terms=[],
            not_terms=[],
            mode=SearchMode.REGEX,
        )
        assert result is True
    
    def test_invalid_regex_pattern(self):
        """Test that invalid regex patterns raise ValueError."""
        service = BM25SearchService(db=None)
        
        content = "test content"
        
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            service._find_matches(content, "[invalid(", SearchMode.REGEX)
    
    def test_empty_content(self):
        """Test searching in empty content."""
        service = BM25SearchService(db=None)
        
        matches = service._find_matches("", "test", SearchMode.CASE_INSENSITIVE)
        assert len(matches) == 0
    
    def test_empty_query(self):
        """Test searching with empty query."""
        service = BM25SearchService(db=None)
        
        matches = service._find_matches("test content", "", SearchMode.CASE_INSENSITIVE)
        # Empty query should match at every position (regex behavior)
        # We just verify it doesn't crash
        assert isinstance(matches, list)
    
    def test_special_characters_in_query(self):
        """Test searching for special characters."""
        service = BM25SearchService(db=None)
        
        content = "def test():"
        query = "()"
        
        matches = service._find_matches(content, query, SearchMode.EXACT)
        assert len(matches) == 1
        assert matches[0].matched_text == "()"
    
    def test_multiline_content(self):
        """Test searching in multiline content."""
        service = BM25SearchService(db=None)
        
        content = """def hello():
    print('Hello')
    return hello_world()
"""
        query = "hello"
        
        matches = service._find_matches(content, query, SearchMode.CASE_INSENSITIVE)
        
        # Should find matches on different lines
        assert len(matches) >= 3
        line_numbers = [m.line_number for m in matches]
        assert 1 in line_numbers  # def hello()
        assert 2 in line_numbers  # print('Hello')
        assert 3 in line_numbers  # hello_world()


@pytest.mark.asyncio
class TestBM25SearchServiceAsync:
    """Async test suite for BM25SearchService database operations."""
    
    # Note: These tests would require a test database setup
    # They are placeholders for integration tests
    
    async def test_load_chunks_with_repository_filter(self):
        """Test loading chunks with repository filter."""
        # TODO: Implement with test database
        pass
    
    async def test_load_chunks_with_file_extension_filter(self):
        """Test loading chunks with file extension filter."""
        # TODO: Implement with test database
        pass
    
    async def test_load_chunks_with_language_filter(self):
        """Test loading chunks with language filter."""
        # TODO: Implement with test database
        pass
    
    async def test_search_returns_top_k_results(self):
        """Test that search returns correct number of results."""
        # TODO: Implement with test database
        pass
    
    async def test_search_with_no_matches(self):
        """Test search with no matching results."""
        # TODO: Implement with test database
        pass
