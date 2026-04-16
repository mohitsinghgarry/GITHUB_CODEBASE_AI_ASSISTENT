"""
Pydantic schemas package for request/response models.

This package contains Pydantic schemas for API request and response validation.
"""

from app.models.schemas.search import (
    MatchLocationSchema,
    CodeChunkSchema,
    SearchResultSchema,
    KeywordSearchRequest,
    KeywordSearchResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    HybridSearchRequest,
    HybridSearchResponse,
)
from app.models.schemas.code import (
    IssueSeverity,
    IssueCategory,
    ReviewCriteria,
    CodeIssueSchema,
    ReviewSummarySchema,
    CodeReviewRequest,
    CodeReviewResponse,
    CodeImprovementRequest,
    CodeImprovementResponse,
    CodeImprovementSchema,
    DiffLineSchema,
    DiffHunkSchema,
    DiffFileSchema,
    DiffReviewRequest,
    DiffReviewResponse,
)
from app.models.schemas.job import (
    JobStatus,
    JobStage,
    IngestionJobSchema,
    JobStatusResponse,
    JobRetryResponse,
    JobErrorDetail,
    JobErrorResponse,
)

__all__ = [
    "MatchLocationSchema",
    "CodeChunkSchema",
    "SearchResultSchema",
    "KeywordSearchRequest",
    "KeywordSearchResponse",
    "SemanticSearchRequest",
    "SemanticSearchResponse",
    "HybridSearchRequest",
    "HybridSearchResponse",
    "IssueSeverity",
    "IssueCategory",
    "ReviewCriteria",
    "CodeIssueSchema",
    "ReviewSummarySchema",
    "CodeReviewRequest",
    "CodeReviewResponse",
    "CodeImprovementRequest",
    "CodeImprovementResponse",
    "CodeImprovementSchema",
    "DiffLineSchema",
    "DiffHunkSchema",
    "DiffFileSchema",
    "DiffReviewRequest",
    "DiffReviewResponse",
    "JobStatus",
    "JobStage",
    "IngestionJobSchema",
    "JobStatusResponse",
    "JobRetryResponse",
    "JobErrorDetail",
    "JobErrorResponse",
]
