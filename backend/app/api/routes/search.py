"""
API routes for search operations.

This module implements RESTful endpoints for semantic search, keyword search,
and hybrid search across indexed code repositories.

Requirements:
- 4.1: Generate an embedding for the query
- 4.2: Perform vector similarity search against the Embedding_Store
- 4.3: Return the top K most relevant Code_Chunks with similarity scores
- 4.4: Support configurable result limits between 1 and 100 chunks
- 4.5: Support filtering results by repository
- 4.6: Return results with file paths, line numbers, and code content
- 4.7: Return empty result set when no relevant results are found
- 5.1: Perform text-based search across indexed code chunks
- 5.2: Support exact match, case-insensitive match, and regex pattern matching
- 5.3: Return matching code chunks with match locations highlighted
- 5.4: Support boolean operators (AND, OR, NOT) for complex queries
- 5.5: Merge and rank results from BM25 and vector search using RRF
- 5.6: Support filtering by file extension, directory path, and programming language
- 10.1: Expose RESTful endpoints for search operations
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas.search import (
    KeywordSearchRequest,
    KeywordSearchResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    HybridSearchRequest,
    HybridSearchResponse,
    SearchResultSchema,
    CodeChunkSchema,
    MatchLocationSchema,
)
from app.models.schemas.repository import ErrorResponse
from app.services.search_service import (
    UnifiedSearchService,
    SearchMode,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/search", tags=["search"])


# ============================================================================
# Helper Functions
# ============================================================================


def convert_bm25_result_to_schema(result) -> SearchResultSchema:
    """
    Convert BM25 search result to SearchResultSchema.
    
    Args:
        result: BM25 SearchResult object
        
    Returns:
        SearchResultSchema instance
    """
    return SearchResultSchema(
        chunk=CodeChunkSchema(
            id=result.chunk.id,
            repository_id=result.chunk.repository_id,
            file_path=result.chunk.file_path,
            start_line=result.chunk.start_line,
            end_line=result.chunk.end_line,
            language=result.chunk.language,
            content=result.chunk.content,
        ),
        score=result.score,
        matches=[
            MatchLocationSchema(
                start=match.start,
                end=match.end,
                matched_text=match.matched_text,
                line_number=match.line_number,
            )
            for match in result.matches
        ],
        highlighted_content=result.highlighted_content,
    )


def convert_vector_result_to_schema(result) -> SearchResultSchema:
    """
    Convert vector search result to SearchResultSchema.
    
    Args:
        result: SemanticSearchResult object
        
    Returns:
        SearchResultSchema instance
    """
    return SearchResultSchema(
        chunk=CodeChunkSchema(
            id=result.chunk_id,
            repository_id=result.repository_id,
            file_path=result.file_path,
            start_line=result.start_line,
            end_line=result.end_line,
            language=result.language,
            content=result.content,
        ),
        score=result.score,
        matches=[],  # Vector search doesn't have match locations
        highlighted_content=result.content,
    )


def convert_hybrid_result_to_schema(result: dict) -> SearchResultSchema:
    """
    Convert hybrid search result to SearchResultSchema.
    
    Args:
        result: Hybrid search result dictionary
        
    Returns:
        SearchResultSchema instance
    """
    # Use RRF score as the primary score
    score = result.get("rrf_score", 0.0)
    
    # Get chunk data
    chunk_data = result.get("chunk")
    if chunk_data:
        # Result has a chunk object (from BM25)
        chunk_schema = CodeChunkSchema(
            id=chunk_data.id,
            repository_id=chunk_data.repository_id,
            file_path=chunk_data.file_path,
            start_line=chunk_data.start_line,
            end_line=chunk_data.end_line,
            language=chunk_data.language,
            content=chunk_data.content,
        )
    else:
        # Result only has chunk fields (from vector search)
        chunk_schema = CodeChunkSchema(
            id=result["chunk_id"],
            repository_id=result["repository_id"],
            file_path=result["file_path"],
            start_line=result["start_line"],
            end_line=result["end_line"],
            language=result["language"],
            content=result["content"],
        )
    
    # Convert matches
    matches = [
        MatchLocationSchema(
            start=match.start,
            end=match.end,
            matched_text=match.matched_text,
            line_number=match.line_number,
        )
        for match in result.get("matches", [])
    ]
    
    return SearchResultSchema(
        chunk=chunk_schema,
        score=score,
        matches=matches,
        highlighted_content=result.get("highlighted_content", result.get("content", "")),
    )


# ============================================================================
# API Endpoints
# ============================================================================


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform semantic search",
    description="Search code using natural language queries with vector similarity search.",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def search_semantic(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db)
) -> SemanticSearchResponse:
    """
    Perform semantic search using vector similarity.
    
    This endpoint:
    1. Generates an embedding for the query
    2. Performs FAISS similarity search against repository indices
    3. Returns top-K most similar code chunks with scores
    4. Supports repository filtering and multi-criteria filtering
    
    **Validates: Requirements 4.1-4.7, 5.6, 10.1, 10.2**
    """
    try:
        # Create search service
        search_service = UnifiedSearchService(db=db)
        
        # Perform semantic search
        results = await search_service.search_semantic(
            query=request.query,
            top_k=request.top_k,
            repository_ids=request.repository_ids,
            file_extensions=request.file_extensions,
            directory_paths=request.directory_paths,
            languages=request.languages,
        )
        
        # Convert results to schema
        result_schemas = [
            convert_vector_result_to_schema(result) for result in results
        ]
        
        logger.info(
            f"Semantic search for query '{request.query[:50]}...' "
            f"returned {len(result_schemas)} results"
        )
        
        return SemanticSearchResponse(
            results=result_schemas,
            total_results=len(result_schemas),
            query=request.query,
        )
        
    except ValueError as e:
        logger.warning(f"Invalid semantic search request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": [{"field": "query", "message": str(e)}]
            }
        )
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while performing semantic search",
                "details": None
            }
        )


@router.post(
    "/keyword",
    response_model=KeywordSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform keyword search",
    description="Search code using exact keywords with BM25 ranking and match highlighting.",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def search_keyword(
    request: KeywordSearchRequest,
    db: AsyncSession = Depends(get_db)
) -> KeywordSearchResponse:
    """
    Perform keyword search using BM25.
    
    This endpoint:
    1. Performs text-based search across indexed code chunks
    2. Supports exact match, case-insensitive match, and regex patterns
    3. Returns matching chunks with match locations highlighted
    4. Supports boolean operators (AND, OR, NOT)
    5. Supports multi-criteria filtering
    
    **Validates: Requirements 5.1-5.6, 10.1, 10.2**
    """
    try:
        # Create search service
        search_service = UnifiedSearchService(db=db)
        
        # Convert mode string to SearchMode enum
        mode_map = {
            "exact": SearchMode.EXACT,
            "case_insensitive": SearchMode.CASE_INSENSITIVE,
            "regex": SearchMode.REGEX,
        }
        search_mode = mode_map.get(request.mode, SearchMode.CASE_INSENSITIVE)
        
        # Perform keyword search
        results = await search_service.search_keyword(
            query=request.query,
            top_k=request.top_k,
            mode=search_mode,
            use_boolean=request.use_boolean,
            repository_ids=request.repository_ids,
            file_extensions=request.file_extensions,
            directory_paths=request.directory_paths,
            languages=request.languages,
        )
        
        # Convert results to schema
        result_schemas = [
            convert_bm25_result_to_schema(result) for result in results
        ]
        
        logger.info(
            f"Keyword search for query '{request.query[:50]}...' "
            f"returned {len(result_schemas)} results"
        )
        
        return KeywordSearchResponse(
            results=result_schemas,
            total_results=len(result_schemas),
            query=request.query,
        )
        
    except ValueError as e:
        logger.warning(f"Invalid keyword search request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": [{"field": "query", "message": str(e)}]
            }
        )
    except Exception as e:
        logger.error(f"Error performing keyword search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while performing keyword search",
                "details": None
            }
        )


@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform hybrid search",
    description="Search code using both BM25 keyword search and vector semantic search with Reciprocal Rank Fusion.",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def search_hybrid(
    request: HybridSearchRequest,
    db: AsyncSession = Depends(get_db)
) -> HybridSearchResponse:
    """
    Perform hybrid search combining BM25 and vector search.
    
    This endpoint:
    1. Performs both BM25 keyword search and vector semantic search
    2. Combines results using Reciprocal Rank Fusion (RRF)
    3. Returns merged and ranked results
    4. Supports multi-criteria filtering
    
    RRF Formula: RRF(d) = Σ 1 / (k + rank(d))
    
    This method is more robust than score-based fusion because it only
    depends on the ranking of results, not their absolute scores.
    
    **Validates: Requirements 4.1-4.7, 5.1-5.6, 10.1, 10.2**
    """
    try:
        # Create search service
        search_service = UnifiedSearchService(db=db)
        
        # Perform hybrid search
        # Note: The bm25_weight parameter in the request is not used in the current
        # RRF implementation, but is kept for API compatibility and future enhancements
        results = await search_service.search_hybrid(
            query=request.query,
            top_k=request.top_k,
            repository_ids=request.repository_ids,
            file_extensions=request.file_extensions,
            directory_paths=request.directory_paths,
            languages=request.languages,
        )
        
        # Convert results to schema
        result_schemas = [
            convert_hybrid_result_to_schema(result) for result in results
        ]
        
        logger.info(
            f"Hybrid search for query '{request.query[:50]}...' "
            f"returned {len(result_schemas)} results"
        )
        
        return HybridSearchResponse(
            results=result_schemas,
            total_results=len(result_schemas),
            query=request.query,
            bm25_weight=request.bm25_weight,
        )
        
    except ValueError as e:
        logger.warning(f"Invalid hybrid search request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": [{"field": "query", "message": str(e)}]
            }
        )
    except Exception as e:
        logger.error(f"Error performing hybrid search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while performing hybrid search",
                "details": None
            }
        )
