"""
API routes for code review and improvement operations.

This module implements RESTful endpoints for code review, code improvement,
and diff/PR review functionality using LLM-based analysis.

Requirements:
- 7.1: Retrieve specified code for review
- 7.2: Analyze code for bugs, security vulnerabilities, and style violations
- 7.3: Return structured feedback with issue descriptions, severity levels, and line numbers
- 7.4: Generate improved code with explanations
- 7.5: Support review of code diffs and pull requests
- 7.6: Focus analysis on changed lines and their context
- 7.7: Allow configuration of review criteria
- 10.1: Expose RESTful endpoints for code review operations
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas.code import (
    CodeImprovementRequest,
    CodeImprovementResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    DiffReviewRequest,
    DiffReviewResponse,
    ErrorResponse,
)
from app.services.llm_service import LLMService, OllamaConnectionError
from app.services.groq_llm_service import create_llm_service
from app.services.review_service import ReviewService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/review", tags=["code-review"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_review_service() -> ReviewService:
    """
    Dependency injection for review service.
    
    Returns:
        ReviewService: Initialized review service instance
    """
    llm_service = create_llm_service()
    return ReviewService(llm_service=llm_service)


# ============================================================================
# API Endpoints
# ============================================================================


@router.post(
    "",
    response_model=CodeReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Review code",
    description=(
        "Analyze code for bugs, security vulnerabilities, style violations, and other issues. "
        "Returns structured feedback with severity levels, line numbers, and suggestions."
    ),
    responses={
        200: {"description": "Code review completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def review_code(
    request: CodeReviewRequest,
    review_service: ReviewService = Depends(get_review_service),
) -> CodeReviewResponse:
    """
    Review code and return structured feedback.
    
    This endpoint analyzes code for various issues including:
    - **Bugs**: Logic errors, edge cases, incorrect behavior
    - **Security**: Vulnerabilities, injection risks, authentication issues
    - **Performance**: Inefficient algorithms, resource leaks
    - **Style**: Code formatting, naming conventions, readability
    - **Maintainability**: Code complexity, duplication, modularity
    - **Best Practices**: Language-specific idioms, design patterns
    - **Documentation**: Missing or incorrect comments
    - **Error Handling**: Missing try-catch blocks, unhandled exceptions
    
    The response includes:
    - List of issues with severity levels and line numbers
    - Summary statistics (total issues by severity)
    - Overall code quality assessment
    - High-level recommendations for improvement
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.7, 10.1, 10.2**
    
    Args:
        request: Code review request with code and criteria
        review_service: Injected review service
        
    Returns:
        CodeReviewResponse: Structured review feedback
        
    Raises:
        HTTPException: 400 for invalid request, 503 for LLM unavailable, 500 for server error
    """
    try:
        logger.info(
            f"Processing code review request: language={request.language}, "
            f"criteria={request.criteria}, code_length={len(request.code)}"
        )
        
        # Validate request
        if not request.code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid request",
                    "message": "Code cannot be empty",
                    "details": [
                        {
                            "field": "code",
                            "message": "Code field must contain non-empty content"
                        }
                    ]
                }
            )
        
        # Perform code review
        response = await review_service.review_code(request)
        
        logger.info(
            f"Code review completed: {response.summary.total_issues} issues found "
            f"({response.summary.critical_count} critical, {response.summary.high_count} high)"
        )
        
        return response
        
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error during code review: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM service unavailable",
                "message": str(e),
                "details": [
                    {
                        "field": "ollama",
                        "message": "Unable to connect to Ollama. Please ensure it is running."
                    }
                ]
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid code review request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing code review: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while reviewing the code",
                "details": None
            }
        )


@router.post(
    "/improve",
    response_model=CodeImprovementResponse,
    status_code=status.HTTP_200_OK,
    summary="Improve code",
    description=(
        "Generate an improved version of code with explanations. "
        "Focuses on correctness, readability, performance, and best practices."
    ),
    responses={
        200: {"description": "Code improvement completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def improve_code(
    request: CodeImprovementRequest,
    review_service: ReviewService = Depends(get_review_service),
) -> CodeImprovementResponse:
    """
    Generate improved version of code with explanations.
    
    This endpoint refactors and optimizes code while maintaining functionality.
    Improvements focus on:
    - **Correctness**: Ensure improved code maintains original functionality
    - **Readability**: Make code easier to understand
    - **Performance**: Optimize algorithms and reduce complexity
    - **Maintainability**: Reduce duplication, improve structure
    - **Best Practices**: Apply language-specific idioms and patterns
    - **Error Handling**: Add proper error handling and validation
    - **Documentation**: Add clear comments explaining complex logic
    
    The response includes:
    - Complete improved code
    - List of improvements made with explanations
    - Summary of all changes
    
    **Validates: Requirements 7.4, 10.1, 10.2**
    
    Args:
        request: Code improvement request
        review_service: Injected review service
        
    Returns:
        CodeImprovementResponse: Improved code with explanations
        
    Raises:
        HTTPException: 400 for invalid request, 503 for LLM unavailable, 500 for server error
    """
    try:
        logger.info(
            f"Processing code improvement request: language={request.language}, "
            f"goals={request.improvement_goals}, code_length={len(request.code)}"
        )
        
        # Validate request
        if not request.code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid request",
                    "message": "Code cannot be empty",
                    "details": [
                        {
                            "field": "code",
                            "message": "Code field must contain non-empty content"
                        }
                    ]
                }
            )
        
        # Perform code improvement
        response = await review_service.improve_code(request)
        
        logger.info(
            f"Code improvement completed: {len(response.improvements)} improvements made"
        )
        
        return response
        
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error during code improvement: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM service unavailable",
                "message": str(e),
                "details": [
                    {
                        "field": "ollama",
                        "message": "Unable to connect to Ollama. Please ensure it is running."
                    }
                ]
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid code improvement request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing code improvement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while improving the code",
                "details": None
            }
        )


@router.post(
    "/diff",
    response_model=DiffReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Review code diff/PR",
    description=(
        "Review a code diff or pull request. Analyzes changes and provides feedback "
        "focused on modified lines and their context."
    ),
    responses={
        200: {"description": "Diff review completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def review_diff(
    request: DiffReviewRequest,
    review_service: ReviewService = Depends(get_review_service),
) -> DiffReviewResponse:
    """
    Review a code diff or pull request.
    
    This endpoint analyzes code changes in a git diff format and provides
    feedback focused on the modified lines. It's designed for pull request
    reviews and code change analysis.
    
    The analysis focuses on:
    - **Changed Lines**: Specific lines that were added, modified, or removed
    - **Context**: How changes affect surrounding code
    - **Impact**: Potential impact of changes on the codebase
    - **Regressions**: Potential bugs or issues introduced by changes
    - **Improvements**: Recognition of positive changes
    
    The response includes:
    - Parsed diff structure (files, hunks, lines)
    - Issues found in the changes
    - Summary statistics
    - Overall assessment of changes
    - Approval recommendation (approve, request_changes, or comment)
    
    **Validates: Requirements 7.5, 7.6, 7.7, 10.1, 10.2**
    
    Args:
        request: Diff review request with git diff content
        review_service: Injected review service
        
    Returns:
        DiffReviewResponse: Review of the diff with approval recommendation
        
    Raises:
        HTTPException: 400 for invalid request, 503 for LLM unavailable, 500 for server error
    """
    try:
        logger.info(
            f"Processing diff review request: focus_on_changes={request.focus_on_changes}, "
            f"diff_length={len(request.diff)}"
        )
        
        # Validate request
        if not request.diff.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid request",
                    "message": "Diff cannot be empty",
                    "details": [
                        {
                            "field": "diff",
                            "message": "Diff field must contain non-empty content"
                        }
                    ]
                }
            )
        
        # Validate diff format (basic check)
        if not ("diff --git" in request.diff or "@@" in request.diff):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid request",
                    "message": "Invalid diff format. Expected git diff format.",
                    "details": [
                        {
                            "field": "diff",
                            "message": "Diff must be in git diff format (unified diff)"
                        }
                    ]
                }
            )
        
        # Perform diff review
        response = await review_service.review_diff(request)
        
        logger.info(
            f"Diff review completed: {len(response.files)} file(s) reviewed, "
            f"{response.summary.total_issues} issues found, "
            f"recommendation: {response.approval_recommendation}"
        )
        
        return response
        
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error during diff review: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM service unavailable",
                "message": str(e),
                "details": [
                    {
                        "field": "ollama",
                        "message": "Unable to connect to Ollama. Please ensure it is running."
                    }
                ]
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid diff review request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing diff review: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while reviewing the diff",
                "details": None
            }
        )
