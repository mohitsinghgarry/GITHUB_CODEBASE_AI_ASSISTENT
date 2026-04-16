"""
Search service for BM25 keyword search, vector semantic search, and hybrid search.

This module implements:
- BM25-based keyword search with support for exact match, case-insensitive match,
  regex patterns, boolean operators, and match highlighting
- Vector semantic search using FAISS similarity search
- Hybrid search combining BM25 and vector search with Reciprocal Rank Fusion (RRF)

Requirements:
- 4.1: Generate an embedding for the query
- 4.2: Perform vector similarity search against the Embedding_Store
- 4.3: Return the top K most relevant Code_Chunks with similarity scores
- 4.4: Support configurable result limits between 1 and 100 chunks
- 4.5: Support filtering results by repository
- 5.1: Perform text-based search across indexed code chunks
- 5.2: Support exact match, case-insensitive match, and regex pattern matching
- 5.3: Return matching code chunks with match locations highlighted
- 5.4: Support boolean operators (AND, OR, NOT) for complex queries
- 5.5: Merge and rank results from BM25 and vector search using RRF
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.code_chunk import CodeChunk
from app.core.retrieval.retriever import (
    SemanticSearchRetriever,
    get_semantic_search_retriever,
    SearchResult as SemanticSearchResult,
)


class SearchMode(str, Enum):
    """Search mode enumeration."""
    EXACT = "exact"
    CASE_INSENSITIVE = "case_insensitive"
    REGEX = "regex"


class BooleanOperator(str, Enum):
    """Boolean operator enumeration."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


@dataclass
class MatchLocation:
    """
    Represents a match location within a code chunk.
    
    Attributes:
        start: Start position of the match in the content
        end: End position of the match in the content
        matched_text: The actual matched text
        line_number: Line number within the chunk where match occurs
    """
    start: int
    end: int
    matched_text: str
    line_number: int


@dataclass
class SearchResult:
    """
    Represents a search result with match information.
    
    Attributes:
        chunk: The code chunk that matched
        score: BM25 relevance score
        matches: List of match locations within the chunk
        highlighted_content: Content with matches highlighted
    """
    chunk: CodeChunk
    score: float
    matches: List[MatchLocation]
    highlighted_content: str


class BM25SearchService:
    """
    BM25-based keyword search service.
    
    This service provides keyword search functionality with support for:
    - Exact match, case-insensitive match, and regex patterns
    - Boolean operators (AND, OR, NOT)
    - Match location highlighting
    - Repository filtering
    - File extension, directory path, and language filtering
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the BM25 search service.
        
        Args:
            db: Async database session
        """
        self.db = db
        self._bm25_index: Optional[BM25Okapi] = None
        self._chunks: List[CodeChunk] = []
        self._tokenized_corpus: List[List[str]] = []
    
    async def _load_chunks(
        self,
        repository_ids: Optional[List[UUID]] = None,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> None:
        """
        Load code chunks from database with optional filtering.
        
        Args:
            repository_ids: Filter by repository IDs
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])
            directory_paths: Filter by directory paths (e.g., ['src/', 'lib/'])
            languages: Filter by programming languages (e.g., ['python', 'javascript'])
        """
        query = select(CodeChunk)
        
        # Apply repository filter
        if repository_ids:
            query = query.where(CodeChunk.repository_id.in_(repository_ids))
        
        # Apply file extension filter
        if file_extensions:
            conditions = [
                CodeChunk.file_path.endswith(ext) for ext in file_extensions
            ]
            query = query.where(or_(*conditions))
        
        # Apply directory path filter
        if directory_paths:
            conditions = [
                CodeChunk.file_path.startswith(path) for path in directory_paths
            ]
            query = query.where(or_(*conditions))
        
        # Apply language filter
        if languages:
            query = query.where(CodeChunk.language.in_(languages))
        
        result = await self.db.execute(query)
        self._chunks = list(result.scalars().all())
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25 indexing.
        
        Uses simple whitespace and punctuation-based tokenization suitable for code.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Split on whitespace and common code delimiters
        tokens = re.findall(r'\w+|[^\w\s]', text.lower())
        return tokens
    
    def _build_bm25_index(self) -> None:
        """Build BM25 index from loaded chunks."""
        self._tokenized_corpus = [
            self._tokenize(chunk.content) for chunk in self._chunks
        ]
        self._bm25_index = BM25Okapi(self._tokenized_corpus)
    
    def _find_matches(
        self,
        content: str,
        query: str,
        mode: SearchMode = SearchMode.CASE_INSENSITIVE,
    ) -> List[MatchLocation]:
        """
        Find all match locations in content.
        
        Args:
            content: Content to search in
            query: Query string to search for
            mode: Search mode (exact, case_insensitive, regex)
            
        Returns:
            List of match locations
        """
        matches = []
        
        if mode == SearchMode.EXACT:
            pattern = re.escape(query)
            flags = 0
        elif mode == SearchMode.CASE_INSENSITIVE:
            pattern = re.escape(query)
            flags = re.IGNORECASE
        elif mode == SearchMode.REGEX:
            pattern = query
            flags = re.IGNORECASE
        else:
            raise ValueError(f"Invalid search mode: {mode}")
        
        try:
            for match in re.finditer(pattern, content, flags):
                start = match.start()
                end = match.end()
                matched_text = match.group()
                
                # Calculate line number
                line_number = content[:start].count('\n') + 1
                
                matches.append(MatchLocation(
                    start=start,
                    end=end,
                    matched_text=matched_text,
                    line_number=line_number,
                ))
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        return matches
    
    def _highlight_matches(
        self,
        content: str,
        matches: List[MatchLocation],
        highlight_start: str = "<<<",
        highlight_end: str = ">>>",
    ) -> str:
        """
        Highlight matches in content.
        
        Args:
            content: Original content
            matches: List of match locations
            highlight_start: String to insert before match
            highlight_end: String to insert after match
            
        Returns:
            Content with highlighted matches
        """
        if not matches:
            return content
        
        # Sort matches by start position (reverse order for insertion)
        sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)
        
        highlighted = content
        for match in sorted_matches:
            highlighted = (
                highlighted[:match.start] +
                highlight_start +
                highlighted[match.start:match.end] +
                highlight_end +
                highlighted[match.end:]
            )
        
        return highlighted
    
    def _parse_boolean_query(self, query: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Parse boolean query into AND, OR, and NOT terms.
        
        Supports simple boolean syntax:
        - "term1 AND term2" - both terms must be present
        - "term1 OR term2" - at least one term must be present
        - "NOT term1" - term must not be present
        - "term1 term2" - treated as OR by default
        
        Args:
            query: Boolean query string
            
        Returns:
            Tuple of (and_terms, or_terms, not_terms)
        """
        and_terms = []
        or_terms = []
        not_terms = []
        
        # Split by boolean operators
        parts = re.split(r'\s+(AND|OR|NOT)\s+', query, flags=re.IGNORECASE)
        
        current_operator = "OR"  # Default operator
        
        for i, part in enumerate(parts):
            part = part.strip()
            
            if not part:
                continue
            
            # Check if this is an operator
            if part.upper() in ["AND", "OR", "NOT"]:
                current_operator = part.upper()
                continue
            
            # Add term to appropriate list
            if current_operator == "AND":
                and_terms.append(part)
            elif current_operator == "OR":
                or_terms.append(part)
            elif current_operator == "NOT":
                not_terms.append(part)
            else:
                or_terms.append(part)  # Default to OR
        
        return and_terms, or_terms, not_terms
    
    def _evaluate_boolean_query(
        self,
        content: str,
        and_terms: List[str],
        or_terms: List[str],
        not_terms: List[str],
        mode: SearchMode = SearchMode.CASE_INSENSITIVE,
    ) -> bool:
        """
        Evaluate if content matches boolean query.
        
        Args:
            content: Content to evaluate
            and_terms: Terms that must all be present
            or_terms: Terms where at least one must be present
            not_terms: Terms that must not be present
            mode: Search mode
            
        Returns:
            True if content matches query, False otherwise
        """
        content_lower = content.lower() if mode == SearchMode.CASE_INSENSITIVE else content
        
        # Check NOT terms (must not be present)
        for term in not_terms:
            term_check = term.lower() if mode == SearchMode.CASE_INSENSITIVE else term
            if mode == SearchMode.REGEX:
                if re.search(term, content, re.IGNORECASE if mode == SearchMode.CASE_INSENSITIVE else 0):
                    return False
            else:
                if term_check in content_lower:
                    return False
        
        # Check AND terms (all must be present)
        for term in and_terms:
            term_check = term.lower() if mode == SearchMode.CASE_INSENSITIVE else term
            if mode == SearchMode.REGEX:
                if not re.search(term, content, re.IGNORECASE if mode == SearchMode.CASE_INSENSITIVE else 0):
                    return False
            else:
                if term_check not in content_lower:
                    return False
        
        # Check OR terms (at least one must be present)
        if or_terms:
            found = False
            for term in or_terms:
                term_check = term.lower() if mode == SearchMode.CASE_INSENSITIVE else term
                if mode == SearchMode.REGEX:
                    if re.search(term, content, re.IGNORECASE if mode == SearchMode.CASE_INSENSITIVE else 0):
                        found = True
                        break
                else:
                    if term_check in content_lower:
                        found = True
                        break
            if not found:
                return False
        
        return True
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        mode: SearchMode = SearchMode.CASE_INSENSITIVE,
        use_boolean: bool = False,
        repository_ids: Optional[List[UUID]] = None,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Perform BM25 keyword search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            mode: Search mode (exact, case_insensitive, regex)
            use_boolean: Whether to parse query as boolean expression
            repository_ids: Filter by repository IDs
            file_extensions: Filter by file extensions
            directory_paths: Filter by directory paths
            languages: Filter by programming languages
            
        Returns:
            List of search results sorted by relevance score
        """
        # Load chunks with filters
        await self._load_chunks(
            repository_ids=repository_ids,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
        
        if not self._chunks:
            return []
        
        # Build BM25 index
        self._build_bm25_index()
        
        # Parse boolean query if enabled
        if use_boolean:
            and_terms, or_terms, not_terms = self._parse_boolean_query(query)
        else:
            and_terms, or_terms, not_terms = [], [query], []
        
        # Get BM25 scores
        tokenized_query = self._tokenize(query)
        scores = self._bm25_index.get_scores(tokenized_query)
        
        # Create results with match information
        results = []
        for i, (chunk, score) in enumerate(zip(self._chunks, scores)):
            # Evaluate boolean query if enabled
            if use_boolean:
                if not self._evaluate_boolean_query(
                    chunk.content, and_terms, or_terms, not_terms, mode
                ):
                    continue
            
            # Find matches in content
            all_matches = []
            search_terms = and_terms + or_terms
            
            for term in search_terms:
                matches = self._find_matches(chunk.content, term, mode)
                all_matches.extend(matches)
            
            # Skip if no matches found
            if not all_matches:
                continue
            
            # Highlight matches
            highlighted = self._highlight_matches(chunk.content, all_matches)
            
            results.append(SearchResult(
                chunk=chunk,
                score=score,
                matches=all_matches,
                highlighted_content=highlighted,
            ))
        
        # Sort by score and return top K
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
    
    async def search_simple(
        self,
        query: str,
        top_k: int = 10,
        repository_ids: Optional[List[UUID]] = None,
    ) -> List[SearchResult]:
        """
        Perform simple case-insensitive keyword search.
        
        Convenience method for basic keyword search without advanced features.
        
        Args:
            query: Search query
            top_k: Number of results to return
            repository_ids: Filter by repository IDs
            
        Returns:
            List of search results sorted by relevance score
        """
        return await self.search(
            query=query,
            top_k=top_k,
            mode=SearchMode.CASE_INSENSITIVE,
            use_boolean=False,
            repository_ids=repository_ids,
        )


# Import for SQLAlchemy or_ function
from sqlalchemy import or_


class VectorSearchService:
    """
    Vector semantic search service wrapper.
    
    This service provides a simplified interface for vector semantic search
    that integrates with the existing search service architecture.
    
    Attributes:
        retriever: The semantic search retriever instance
    """
    
    def __init__(self, retriever: Optional[SemanticSearchRetriever] = None):
        """
        Initialize the vector search service.
        
        Args:
            retriever: Semantic search retriever instance.
                      If None, uses the global retriever.
        """
        self.retriever = retriever or get_semantic_search_retriever()
    
    def _apply_filters(
        self,
        results: List[SemanticSearchResult],
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SemanticSearchResult]:
        """
        Apply multi-criteria filters to search results.
        
        Args:
            results: Search results to filter
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])
            directory_paths: Filter by directory paths (e.g., ['src/', 'lib/'])
            languages: Filter by programming languages (e.g., ['python', 'javascript'])
        
        Returns:
            Filtered search results
        """
        filtered_results = results
        
        # Apply file extension filter
        if file_extensions:
            filtered_results = [
                r for r in filtered_results
                if any(r.file_path.endswith(ext) for ext in file_extensions)
            ]
        
        # Apply directory path filter
        if directory_paths:
            filtered_results = [
                r for r in filtered_results
                if any(r.file_path.startswith(path) for path in directory_paths)
            ]
        
        # Apply language filter
        if languages:
            filtered_results = [
                r for r in filtered_results
                if r.language in languages
            ]
        
        return filtered_results
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        repository_ids: Optional[List[UUID]] = None,
        score_threshold: float = 0.0,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SemanticSearchResult]:
        """
        Perform vector semantic search with multi-criteria filtering.
        
        Args:
            query: Natural language query
            top_k: Number of results to return (1-100)
            repository_ids: Filter by repository IDs
            score_threshold: Minimum similarity score (0.0-1.0)
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])
            directory_paths: Filter by directory paths (e.g., ['src/', 'lib/'])
            languages: Filter by programming languages (e.g., ['python', 'javascript'])
        
        Returns:
            List[SemanticSearchResult]: List of search results sorted by similarity score
        
        Raises:
            ValueError: If query is empty or parameters are invalid
            RuntimeError: If search fails
        
        Requirements:
            - 5.6: Support filtering by file extension, directory path, and programming language
        """
        # Retrieve more results if filters are applied to ensure we get enough after filtering
        retrieval_multiplier = 3 if (file_extensions or directory_paths or languages) else 1
        retrieval_top_k = top_k * retrieval_multiplier
        
        # Perform search
        if score_threshold > 0.0:
            results = self.retriever.search_with_threshold(
                query=query,
                top_k=retrieval_top_k,
                score_threshold=score_threshold,
                repository_ids=repository_ids,
            )
        else:
            results = self.retriever.search(
                query=query,
                top_k=retrieval_top_k,
                repository_ids=repository_ids,
            )
        
        # Apply multi-criteria filters
        filtered_results = self._apply_filters(
            results=results,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
        
        # Return top K after filtering
        return filtered_results[:top_k]
    
    async def search_simple(
        self,
        query: str,
        top_k: int = 10,
        repository_ids: Optional[List[UUID]] = None,
    ) -> List[SemanticSearchResult]:
        """
        Perform simple vector semantic search.
        
        Convenience method for basic semantic search without advanced features.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            repository_ids: Filter by repository IDs
        
        Returns:
            List[SemanticSearchResult]: List of search results sorted by similarity score
        """
        return self.retriever.search(
            query=query,
            top_k=top_k,
            repository_ids=repository_ids,
        )


class UnifiedSearchService:
    """
    Unified search service providing BM25, vector, and hybrid search.
    
    This service combines BM25 keyword search and vector semantic search
    into a single interface, supporting multiple search modes.
    
    Attributes:
        bm25_service: BM25 keyword search service
        vector_service: Vector semantic search service
    """
    
    def __init__(
        self,
        db: AsyncSession,
        bm25_service: Optional[BM25SearchService] = None,
        vector_service: Optional[VectorSearchService] = None,
    ):
        """
        Initialize the unified search service.
        
        Args:
            db: Async database session
            bm25_service: BM25 search service. If None, creates a new instance.
            vector_service: Vector search service. If None, creates a new instance.
        """
        self.db = db
        self.bm25_service = bm25_service or BM25SearchService(db)
        self.vector_service = vector_service or VectorSearchService()
    
    async def search_semantic(
        self,
        query: str,
        top_k: int = 10,
        repository_ids: Optional[List[UUID]] = None,
        score_threshold: float = 0.0,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SemanticSearchResult]:
        """
        Perform semantic search using vector similarity with multi-criteria filtering.
        
        Args:
            query: Natural language query
            top_k: Number of results to return (1-100)
            repository_ids: Filter by repository IDs
            score_threshold: Minimum similarity score (0.0-1.0)
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])
            directory_paths: Filter by directory paths (e.g., ['src/', 'lib/'])
            languages: Filter by programming languages (e.g., ['python', 'javascript'])
        
        Returns:
            List[SemanticSearchResult]: List of search results sorted by similarity score
        
        Requirements:
            - 5.6: Support filtering by file extension, directory path, and programming language
        """
        return await self.vector_service.search(
            query=query,
            top_k=top_k,
            repository_ids=repository_ids,
            score_threshold=score_threshold,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
    
    async def search_keyword(
        self,
        query: str,
        top_k: int = 10,
        mode: SearchMode = SearchMode.CASE_INSENSITIVE,
        use_boolean: bool = False,
        repository_ids: Optional[List[UUID]] = None,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """
        Perform keyword search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return
            mode: Search mode (exact, case_insensitive, regex)
            use_boolean: Whether to parse query as boolean expression
            repository_ids: Filter by repository IDs
            file_extensions: Filter by file extensions
            directory_paths: Filter by directory paths
            languages: Filter by programming languages
        
        Returns:
            List[SearchResult]: List of search results sorted by relevance score
        """
        return await self.bm25_service.search(
            query=query,
            top_k=top_k,
            mode=mode,
            use_boolean=use_boolean,
            repository_ids=repository_ids,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        
        Args:
            scores: List of raw scores
            
        Returns:
            List of normalized scores in [0, 1] range
        """
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        # Handle case where all scores are the same
        if max_score == min_score:
            return [1.0] * len(scores)
        
        # Min-max normalization
        normalized = [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]
        
        return normalized
    
    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[SearchResult],
        vector_results: List[SemanticSearchResult],
        k: int = 60,
    ) -> Dict[str, float]:
        """
        Combine search results using Reciprocal Rank Fusion (RRF).
        
        RRF formula: RRF(d) = Σ 1 / (k + rank(d))
        where k is a constant (typically 60) and rank(d) is the rank of document d
        in each result list.
        
        This method is more robust than score-based fusion because it doesn't
        depend on the scale or distribution of the original scores.
        
        Args:
            bm25_results: BM25 search results (ranked by relevance)
            vector_results: Vector search results (ranked by similarity)
            k: RRF constant (default 60, as recommended in literature)
            
        Returns:
            Dict mapping chunk keys to RRF scores
        """
        rrf_scores: Dict[str, float] = {}
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results):
            key = f"{result.chunk.file_path}:{result.chunk.start_line}"
            # RRF score contribution from BM25 ranking
            rrf_scores[key] = 1.0 / (k + rank + 1)
        
        # Process vector results
        for rank, result in enumerate(vector_results):
            key = f"{result.file_path}:{result.start_line}"
            # Add RRF score contribution from vector ranking
            rrf_contribution = 1.0 / (k + rank + 1)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + rrf_contribution
        
        return rrf_scores
    
    async def search_hybrid(
        self,
        query: str,
        top_k: int = 10,
        repository_ids: Optional[List[UUID]] = None,
        rrf_k: int = 60,
        retrieval_multiplier: int = 2,
        file_extensions: Optional[List[str]] = None,
        directory_paths: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining BM25 and vector search with RRF fusion
        and multi-criteria filtering.
        
        This method implements Reciprocal Rank Fusion (RRF) to combine results
        from both BM25 keyword search and vector semantic search. RRF is more
        robust than score-based fusion because it only depends on the ranking
        of results, not their absolute scores.
        
        RRF Formula: RRF(d) = Σ 1 / (k + rank(d))
        
        Args:
            query: Search query
            top_k: Number of results to return
            repository_ids: Filter by repository IDs
            rrf_k: RRF constant (default 60, as recommended in literature).
                   Higher values reduce the impact of top-ranked results.
            retrieval_multiplier: Multiplier for initial retrieval size.
                                 Retrieves (top_k * retrieval_multiplier) results
                                 from each search method before fusion.
            file_extensions: Filter by file extensions (e.g., ['.py', '.js'])
            directory_paths: Filter by directory paths (e.g., ['src/', 'lib/'])
            languages: Filter by programming languages (e.g., ['python', 'javascript'])
        
        Returns:
            List[Dict]: List of combined search results sorted by RRF score
            
        Requirements:
            - 5.5: Merge and rank results from BM25 and vector search by relevance
            - 5.6: Support filtering by file extension, directory path, and programming language
        
        References:
            Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009).
            "Reciprocal rank fusion outperforms condorcet and individual rank
            learning methods." SIGIR '09.
        """
        # Retrieve more results initially for better fusion
        retrieval_size = top_k * retrieval_multiplier
        
        # Perform both searches in parallel with multi-criteria filtering
        bm25_results = await self.search_keyword(
            query=query,
            top_k=retrieval_size,
            repository_ids=repository_ids,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
        
        vector_results = await self.search_semantic(
            query=query,
            top_k=retrieval_size,
            repository_ids=repository_ids,
            file_extensions=file_extensions,
            directory_paths=directory_paths,
            languages=languages,
        )
        
        # Apply Reciprocal Rank Fusion
        rrf_scores = self._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            k=rrf_k,
        )
        
        # Build combined results with metadata from both searches
        combined_results: Dict[str, Dict[str, Any]] = {}
        
        # Add BM25 results with metadata
        for rank, result in enumerate(bm25_results):
            key = f"{result.chunk.file_path}:{result.chunk.start_line}"
            combined_results[key] = {
                "chunk": result.chunk,
                "chunk_id": result.chunk.id,
                "repository_id": result.chunk.repository_id,
                "file_path": result.chunk.file_path,
                "start_line": result.chunk.start_line,
                "end_line": result.chunk.end_line,
                "language": result.chunk.language,
                "content": result.chunk.content,
                "bm25_score": result.score,
                "bm25_rank": rank + 1,
                "vector_score": 0.0,
                "vector_rank": None,
                "rrf_score": rrf_scores.get(key, 0.0),
                "matches": result.matches,
                "highlighted_content": result.highlighted_content,
            }
        
        # Add/update with vector results
        for rank, result in enumerate(vector_results):
            key = f"{result.file_path}:{result.start_line}"
            
            if key in combined_results:
                # Update existing entry with vector information
                combined_results[key]["vector_score"] = result.score
                combined_results[key]["vector_rank"] = rank + 1
            else:
                # Create new entry (vector-only result)
                combined_results[key] = {
                    "chunk_id": result.chunk_id,
                    "repository_id": result.repository_id,
                    "file_path": result.file_path,
                    "start_line": result.start_line,
                    "end_line": result.end_line,
                    "language": result.language,
                    "content": result.content,
                    "bm25_score": 0.0,
                    "bm25_rank": None,
                    "vector_score": result.score,
                    "vector_rank": rank + 1,
                    "rrf_score": rrf_scores.get(key, 0.0),
                    "matches": [],
                    "highlighted_content": result.content,
                }
        
        # Sort by RRF score (higher is better) and return top K
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x["rrf_score"],
            reverse=True,
        )
        
        return sorted_results[:top_k]
