"""
Pydantic schemas for code review and improvement requests and responses.

This module defines the request and response models for code review and improvement operations.

Requirements:
- 7.1: Retrieve specified code for review
- 7.2: Analyze code for bugs, security vulnerabilities, and style violations
- 7.3: Return structured feedback with issue descriptions, severity levels, and line numbers
- 7.4: Generate improved code with explanations
- 7.5: Support review of code diffs and pull requests
- 7.6: Focus analysis on changed lines and their context
- 7.7: Allow configuration of review criteria
"""

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    
    class Config:
        from_attributes = True


# ============================================================================
# Enums
# ============================================================================


class IssueSeverity(str, Enum):
    """Severity levels for code review issues."""
    
    CRITICAL = "critical"  # Security vulnerabilities, crashes, data loss
    HIGH = "high"          # Bugs, performance issues, major style violations
    MEDIUM = "medium"      # Minor bugs, code smells, moderate style issues
    LOW = "low"            # Suggestions, minor style issues, nitpicks
    INFO = "info"          # Informational, best practices, tips


class IssueCategory(str, Enum):
    """Categories for code review issues."""
    
    BUG = "bug"                          # Logic errors, incorrect behavior
    SECURITY = "security"                # Security vulnerabilities
    PERFORMANCE = "performance"          # Performance issues
    STYLE = "style"                      # Code style violations
    MAINTAINABILITY = "maintainability"  # Code complexity, readability
    BEST_PRACTICE = "best_practice"      # Best practice violations
    DOCUMENTATION = "documentation"      # Missing or incorrect documentation
    ERROR_HANDLING = "error_handling"    # Missing or incorrect error handling
    TESTING = "testing"                  # Testing-related issues


class ReviewCriteria(str, Enum):
    """Review criteria configuration options."""
    
    SECURITY_FOCUSED = "security_focused"      # Focus on security issues
    PERFORMANCE_FOCUSED = "performance_focused"  # Focus on performance
    STYLE_STRICT = "style_strict"              # Strict style checking
    BEGINNER_FRIENDLY = "beginner_friendly"    # Focus on learning
    PRODUCTION_READY = "production_ready"      # Production readiness check


# ============================================================================
# Issue Schemas
# ============================================================================


class CodeIssueSchema(BaseModel):
    """Schema for a single code review issue."""
    
    severity: IssueSeverity = Field(..., description="Issue severity level")
    category: IssueCategory = Field(..., description="Issue category")
    title: str = Field(..., description="Short issue title")
    description: str = Field(..., description="Detailed issue description")
    file_path: Optional[str] = Field(None, description="File path (if applicable)")
    start_line: Optional[int] = Field(None, description="Starting line number")
    end_line: Optional[int] = Field(None, description="Ending line number")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")
    suggestion: Optional[str] = Field(None, description="Suggested fix or improvement")
    
    class Config:
        from_attributes = True


class ReviewSummarySchema(BaseModel):
    """Schema for review summary statistics."""
    
    total_issues: int = Field(..., description="Total number of issues found")
    critical_count: int = Field(0, description="Number of critical issues")
    high_count: int = Field(0, description="Number of high severity issues")
    medium_count: int = Field(0, description="Number of medium severity issues")
    low_count: int = Field(0, description="Number of low severity issues")
    info_count: int = Field(0, description="Number of informational issues")
    
    class Config:
        from_attributes = True


# ============================================================================
# Code Review Request/Response
# ============================================================================


class CodeReviewRequest(BaseModel):
    """Request schema for code review."""
    
    code: str = Field(..., min_length=1, description="Code to review")
    language: Optional[str] = Field(None, description="Programming language")
    file_path: Optional[str] = Field(None, description="File path for context")
    repository_id: Optional[UUID] = Field(None, description="Repository ID for context")
    criteria: List[ReviewCriteria] = Field(
        default_factory=lambda: [ReviewCriteria.PRODUCTION_READY],
        description="Review criteria to apply"
    )
    focus_areas: Optional[List[IssueCategory]] = Field(
        None,
        description="Specific issue categories to focus on"
    )
    max_issues: int = Field(
        50,
        ge=1,
        le=200,
        description="Maximum number of issues to return"
    )
    include_suggestions: bool = Field(
        True,
        description="Include fix suggestions for issues"
    )


class CodeReviewResponse(BaseModel):
    """Response schema for code review."""
    
    issues: List[CodeIssueSchema] = Field(..., description="List of identified issues")
    summary: ReviewSummarySchema = Field(..., description="Review summary statistics")
    overall_assessment: str = Field(..., description="Overall code quality assessment")
    recommendations: List[str] = Field(
        default_factory=list,
        description="High-level recommendations"
    )
    
    class Config:
        from_attributes = True


# ============================================================================
# Code Improvement Request/Response
# ============================================================================


class CodeImprovementRequest(BaseModel):
    """Request schema for code improvement."""
    
    code: str = Field(..., min_length=1, description="Code to improve")
    language: Optional[str] = Field(None, description="Programming language")
    file_path: Optional[str] = Field(None, description="File path for context")
    repository_id: Optional[UUID] = Field(None, description="Repository ID for context")
    improvement_goals: Optional[List[str]] = Field(
        None,
        description="Specific improvement goals (e.g., 'improve performance', 'add error handling')"
    )
    preserve_functionality: bool = Field(
        True,
        description="Ensure improved code maintains original functionality"
    )
    add_comments: bool = Field(
        True,
        description="Add explanatory comments to improved code"
    )


class CodeImprovementSchema(BaseModel):
    """Schema for a single code improvement."""
    
    category: IssueCategory = Field(..., description="Improvement category")
    description: str = Field(..., description="What was improved")
    original_snippet: Optional[str] = Field(None, description="Original code snippet")
    improved_snippet: Optional[str] = Field(None, description="Improved code snippet")
    explanation: str = Field(..., description="Explanation of the improvement")
    
    class Config:
        from_attributes = True


class CodeImprovementResponse(BaseModel):
    """Response schema for code improvement."""
    
    improved_code: str = Field(..., description="The improved code")
    improvements: List[CodeImprovementSchema] = Field(
        ...,
        description="List of improvements made"
    )
    summary: str = Field(..., description="Summary of improvements")
    
    class Config:
        from_attributes = True


# ============================================================================
# Diff Review Request/Response
# ============================================================================


class DiffLineSchema(BaseModel):
    """Schema for a single line in a diff."""
    
    line_number: int = Field(..., description="Line number in the file")
    change_type: str = Field(..., description="Change type: added, removed, or context")
    content: str = Field(..., description="Line content")
    
    class Config:
        from_attributes = True


class DiffHunkSchema(BaseModel):
    """Schema for a diff hunk (contiguous block of changes)."""
    
    old_start: int = Field(..., description="Starting line in old file")
    old_count: int = Field(..., description="Number of lines in old file")
    new_start: int = Field(..., description="Starting line in new file")
    new_count: int = Field(..., description="Number of lines in new file")
    lines: List[DiffLineSchema] = Field(..., description="Lines in the hunk")
    
    class Config:
        from_attributes = True


class DiffFileSchema(BaseModel):
    """Schema for a file in a diff."""
    
    old_path: Optional[str] = Field(None, description="Old file path")
    new_path: str = Field(..., description="New file path")
    change_type: str = Field(
        ...,
        description="Change type: added, modified, deleted, renamed"
    )
    hunks: List[DiffHunkSchema] = Field(..., description="Diff hunks")
    
    class Config:
        from_attributes = True


class DiffReviewRequest(BaseModel):
    """Request schema for diff/PR review."""
    
    diff: str = Field(..., min_length=1, description="Git diff content")
    repository_id: Optional[UUID] = Field(None, description="Repository ID for context")
    criteria: List[ReviewCriteria] = Field(
        default_factory=lambda: [ReviewCriteria.PRODUCTION_READY],
        description="Review criteria to apply"
    )
    focus_on_changes: bool = Field(
        True,
        description="Focus analysis on changed lines only"
    )
    include_context: bool = Field(
        True,
        description="Include surrounding context in analysis"
    )
    max_issues: int = Field(
        50,
        ge=1,
        le=200,
        description="Maximum number of issues to return"
    )


class DiffReviewResponse(BaseModel):
    """Response schema for diff/PR review."""
    
    files: List[DiffFileSchema] = Field(..., description="Parsed diff files")
    issues: List[CodeIssueSchema] = Field(..., description="Issues found in changes")
    summary: ReviewSummarySchema = Field(..., description="Review summary statistics")
    overall_assessment: str = Field(..., description="Overall assessment of changes")
    approval_recommendation: str = Field(
        ...,
        description="Recommendation: approve, request_changes, or comment"
    )
    
    class Config:
        from_attributes = True
