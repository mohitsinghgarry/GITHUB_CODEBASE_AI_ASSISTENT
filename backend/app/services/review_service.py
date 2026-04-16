"""
Code Review Service for analyzing code quality and generating improvements.

This module provides functionality for:
- Code review with structured feedback
- Issue detection (bugs, security, style, performance)
- Code improvement suggestions
- Diff/PR review with focus on changed lines
- Context extraction for changed code

Requirements:
- 7.1: Retrieve specified code for review
- 7.2: Analyze code for bugs, security vulnerabilities, and style violations
- 7.3: Return structured feedback with issue descriptions, severity levels, and line numbers
- 7.4: Generate improved code with explanations
- 7.5: Support review of code diffs and pull requests
- 7.6: Focus analysis on changed lines and their context
- 7.7: Allow configuration of review criteria
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.models.schemas.code import (
    CodeImprovementRequest,
    CodeImprovementResponse,
    CodeImprovementSchema,
    CodeIssueSchema,
    CodeReviewRequest,
    CodeReviewResponse,
    DiffFileSchema,
    DiffHunkSchema,
    DiffLineSchema,
    DiffReviewRequest,
    DiffReviewResponse,
    IssueCategory,
    IssueSeverity,
    ReviewCriteria,
    ReviewSummarySchema,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


# ============================================================================
# Prompt Templates
# ============================================================================


REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization. Your task is to analyze code and provide constructive, actionable feedback.

When reviewing code, consider:
- **Bugs**: Logic errors, edge cases, incorrect behavior
- **Security**: Vulnerabilities, injection risks, authentication issues
- **Performance**: Inefficient algorithms, unnecessary operations, resource leaks
- **Style**: Code formatting, naming conventions, readability
- **Maintainability**: Code complexity, duplication, modularity
- **Best Practices**: Language-specific idioms, design patterns
- **Documentation**: Missing or incorrect comments and docstrings
- **Error Handling**: Missing try-catch blocks, unhandled exceptions

Provide specific, actionable feedback with line numbers when possible."""


IMPROVEMENT_SYSTEM_PROMPT = """You are an expert software engineer specializing in code refactoring and optimization. Your task is to improve code while maintaining its functionality.

When improving code, focus on:
- **Correctness**: Ensure the improved code maintains original functionality
- **Readability**: Make code easier to understand
- **Performance**: Optimize algorithms and reduce complexity
- **Maintainability**: Reduce duplication, improve structure
- **Best Practices**: Apply language-specific idioms and patterns
- **Error Handling**: Add proper error handling and validation
- **Documentation**: Add clear comments explaining complex logic

Provide the complete improved code along with explanations of changes."""


DIFF_REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer analyzing pull request changes. Your task is to review code diffs and provide feedback on the changes.

When reviewing diffs, focus on:
- **Changed Lines**: Analyze the specific lines that were added, modified, or removed
- **Context**: Consider how changes affect surrounding code
- **Impact**: Assess the potential impact of changes on the codebase
- **Regressions**: Identify potential bugs or issues introduced by changes
- **Improvements**: Recognize positive changes and improvements

Provide specific feedback on the changes with line numbers."""


# ============================================================================
# Review Service
# ============================================================================


class ReviewService:
    """
    Service for code review and improvement operations.
    
    This service uses an LLM to analyze code, identify issues, and generate
    improvements. It supports full file review, diff review, and code improvement.
    
    Requirements:
    - 7.1: Retrieve specified code for review
    - 7.2: Analyze code for bugs, security vulnerabilities, and style violations
    - 7.3: Return structured feedback with issue descriptions, severity levels, and line numbers
    - 7.4: Generate improved code with explanations
    - 7.5: Support review of code diffs and pull requests
    - 7.6: Focus analysis on changed lines and their context
    - 7.7: Allow configuration of review criteria
    """
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the review service.
        
        Args:
            llm_service: LLM service for code analysis
        """
        self.llm_service = llm_service
        logger.info("Initialized ReviewService")
    
    # ========================================================================
    # Code Review (Requirements 7.1, 7.2, 7.3, 7.7)
    # ========================================================================
    
    async def review_code(
        self,
        request: CodeReviewRequest,
    ) -> CodeReviewResponse:
        """
        Review code and return structured feedback.
        
        Args:
            request: Code review request with code and criteria
            
        Returns:
            CodeReviewResponse: Structured review feedback
            
        Requirements:
        - 7.1: Retrieve specified code for review
        - 7.2: Analyze code for bugs, security vulnerabilities, and style violations
        - 7.3: Return structured feedback with issue descriptions, severity levels, and line numbers
        - 7.7: Allow configuration of review criteria
        """
        logger.info(
            f"Reviewing code: language={request.language}, "
            f"criteria={request.criteria}, "
            f"code_length={len(request.code)}"
        )
        
        # Build review prompt
        prompt = self._build_review_prompt(request)
        
        # Generate review using LLM
        try:
            review_text = await self.llm_service.generate(
                prompt=prompt,
                system_prompt=REVIEW_SYSTEM_PROMPT,
                temperature=0.3,  # Lower temperature for more consistent analysis
            )
            
            # Parse LLM response into structured issues
            issues = self._parse_review_response(review_text, request.code)
            
            # Limit issues to max_issues
            if len(issues) > request.max_issues:
                logger.warning(
                    f"Truncating issues from {len(issues)} to {request.max_issues}"
                )
                issues = issues[:request.max_issues]
            
            # Generate summary statistics
            summary = self._generate_summary(issues)
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(summary, issues)
            
            # Generate high-level recommendations
            recommendations = self._generate_recommendations(issues, request.criteria)
            
            logger.info(
                f"Review complete: {summary.total_issues} issues found "
                f"({summary.critical_count} critical, {summary.high_count} high)"
            )
            
            return CodeReviewResponse(
                issues=issues,
                summary=summary,
                overall_assessment=overall_assessment,
                recommendations=recommendations,
            )
            
        except Exception as e:
            logger.error(f"Code review failed: {e}", exc_info=True)
            raise
    
    def _build_review_prompt(self, request: CodeReviewRequest) -> str:
        """Build the review prompt from request."""
        criteria_desc = ", ".join([c.value for c in request.criteria])
        focus_desc = ""
        if request.focus_areas:
            focus_desc = f"\nFocus specifically on: {', '.join([f.value for f in request.focus_areas])}"
        
        language_info = f" (Language: {request.language})" if request.language else ""
        file_info = f" (File: {request.file_path})" if request.file_path else ""
        
        prompt = f"""Please review the following code{language_info}{file_info}.

Review Criteria: {criteria_desc}{focus_desc}

Code to review:
```
{request.code}
```

Please provide a detailed code review with the following format:

## Issues Found

For each issue, provide:
- **Severity**: critical/high/medium/low/info
- **Category**: bug/security/performance/style/maintainability/best_practice/documentation/error_handling
- **Title**: Brief issue title
- **Description**: Detailed explanation
- **Line**: Line number(s) where the issue occurs
- **Suggestion**: How to fix the issue (if applicable)

## Overall Assessment

Provide a summary of the code quality and main concerns.

## Recommendations

List 3-5 high-level recommendations for improving the code."""
        
        return prompt
    
    def _parse_review_response(
        self,
        review_text: str,
        original_code: str,
    ) -> List[CodeIssueSchema]:
        """
        Parse LLM review response into structured issues.
        
        This is a simplified parser that extracts issues from the LLM response.
        In production, you might want to use a more robust parsing strategy or
        prompt the LLM to return JSON directly.
        """
        issues = []
        
        # Split by issue markers (looking for severity keywords)
        severity_pattern = r'\*\*Severity\*\*:\s*(critical|high|medium|low|info)'
        category_pattern = r'\*\*Category\*\*:\s*(\w+)'
        title_pattern = r'\*\*Title\*\*:\s*(.+?)(?:\n|$)'
        description_pattern = r'\*\*Description\*\*:\s*(.+?)(?=\*\*|$)'
        line_pattern = r'\*\*Line\*\*:\s*(\d+)(?:-(\d+))?'
        suggestion_pattern = r'\*\*Suggestion\*\*:\s*(.+?)(?=\*\*|$)'
        
        # Find all issue blocks
        issue_blocks = re.split(r'\n(?=\*\*Severity\*\*)', review_text)
        
        for block in issue_blocks:
            if not block.strip():
                continue
            
            # Extract fields
            severity_match = re.search(severity_pattern, block, re.IGNORECASE)
            category_match = re.search(category_pattern, block, re.IGNORECASE)
            title_match = re.search(title_pattern, block)
            description_match = re.search(description_pattern, block, re.DOTALL)
            line_match = re.search(line_pattern, block)
            suggestion_match = re.search(suggestion_pattern, block, re.DOTALL)
            
            if not (severity_match and category_match and title_match):
                continue
            
            # Parse severity
            try:
                severity = IssueSeverity(severity_match.group(1).lower())
            except ValueError:
                severity = IssueSeverity.MEDIUM
            
            # Parse category
            try:
                category = IssueCategory(category_match.group(1).lower())
            except ValueError:
                category = IssueCategory.BUG
            
            # Parse line numbers
            start_line = None
            end_line = None
            if line_match:
                start_line = int(line_match.group(1))
                end_line = int(line_match.group(2)) if line_match.group(2) else start_line
            
            # Extract code snippet if line numbers are available
            code_snippet = None
            if start_line and end_line:
                code_snippet = self._extract_code_snippet(
                    original_code, start_line, end_line
                )
            
            # Create issue
            issue = CodeIssueSchema(
                severity=severity,
                category=category,
                title=title_match.group(1).strip(),
                description=description_match.group(1).strip() if description_match else "",
                start_line=start_line,
                end_line=end_line,
                code_snippet=code_snippet,
                suggestion=suggestion_match.group(1).strip() if suggestion_match else None,
            )
            
            issues.append(issue)
        
        return issues
    
    def _extract_code_snippet(
        self,
        code: str,
        start_line: int,
        end_line: int,
        context_lines: int = 2,
    ) -> str:
        """Extract code snippet with context."""
        lines = code.split('\n')
        
        # Add context lines
        snippet_start = max(0, start_line - 1 - context_lines)
        snippet_end = min(len(lines), end_line + context_lines)
        
        snippet_lines = lines[snippet_start:snippet_end]
        return '\n'.join(snippet_lines)
    
    def _generate_summary(self, issues: List[CodeIssueSchema]) -> ReviewSummarySchema:
        """Generate summary statistics from issues."""
        summary = ReviewSummarySchema(
            total_issues=len(issues),
            critical_count=sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL),
            high_count=sum(1 for i in issues if i.severity == IssueSeverity.HIGH),
            medium_count=sum(1 for i in issues if i.severity == IssueSeverity.MEDIUM),
            low_count=sum(1 for i in issues if i.severity == IssueSeverity.LOW),
            info_count=sum(1 for i in issues if i.severity == IssueSeverity.INFO),
        )
        return summary
    
    def _generate_overall_assessment(
        self,
        summary: ReviewSummarySchema,
        issues: List[CodeIssueSchema],
    ) -> str:
        """Generate overall assessment based on issues."""
        if summary.critical_count > 0:
            return (
                f"Critical issues detected. This code requires immediate attention. "
                f"Found {summary.critical_count} critical issue(s) that must be addressed "
                f"before deployment."
            )
        elif summary.high_count > 0:
            return (
                f"Significant issues found. This code needs improvement before production use. "
                f"Found {summary.high_count} high-severity issue(s) that should be addressed."
            )
        elif summary.medium_count > 0:
            return (
                f"Code is generally acceptable but has room for improvement. "
                f"Found {summary.medium_count} medium-severity issue(s) that should be reviewed."
            )
        elif summary.low_count > 0:
            return (
                f"Code quality is good with minor suggestions. "
                f"Found {summary.low_count} low-severity issue(s) for consideration."
            )
        else:
            return "Code quality is excellent. No significant issues found."
    
    def _generate_recommendations(
        self,
        issues: List[CodeIssueSchema],
        criteria: List[ReviewCriteria],
    ) -> List[str]:
        """Generate high-level recommendations."""
        recommendations = []
        
        # Group issues by category
        category_counts: Dict[IssueCategory, int] = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Generate recommendations based on most common categories
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        
        for category, count in sorted_categories[:3]:
            if category == IssueCategory.SECURITY:
                recommendations.append(
                    f"Address {count} security issue(s) to prevent vulnerabilities"
                )
            elif category == IssueCategory.BUG:
                recommendations.append(
                    f"Fix {count} bug(s) to ensure correct behavior"
                )
            elif category == IssueCategory.PERFORMANCE:
                recommendations.append(
                    f"Optimize {count} performance issue(s) for better efficiency"
                )
            elif category == IssueCategory.MAINTAINABILITY:
                recommendations.append(
                    f"Improve {count} maintainability issue(s) for better code quality"
                )
            elif category == IssueCategory.ERROR_HANDLING:
                recommendations.append(
                    f"Add proper error handling for {count} case(s)"
                )
        
        # Add criteria-specific recommendations
        if ReviewCriteria.SECURITY_FOCUSED in criteria:
            recommendations.append("Conduct security audit and penetration testing")
        if ReviewCriteria.PERFORMANCE_FOCUSED in criteria:
            recommendations.append("Profile code and optimize hot paths")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    # ========================================================================
    # Code Improvement (Requirement 7.4)
    # ========================================================================
    
    async def improve_code(
        self,
        request: CodeImprovementRequest,
    ) -> CodeImprovementResponse:
        """
        Generate improved version of code with explanations.
        
        Args:
            request: Code improvement request
            
        Returns:
            CodeImprovementResponse: Improved code with explanations
            
        Requirement 7.4: Generate improved code with explanations
        """
        logger.info(
            f"Improving code: language={request.language}, "
            f"goals={request.improvement_goals}, "
            f"code_length={len(request.code)}"
        )
        
        # Build improvement prompt
        prompt = self._build_improvement_prompt(request)
        
        # Generate improved code using LLM
        try:
            improvement_text = await self.llm_service.generate(
                prompt=prompt,
                system_prompt=IMPROVEMENT_SYSTEM_PROMPT,
                temperature=0.3,
            )
            
            # Parse LLM response
            improved_code, improvements, summary = self._parse_improvement_response(
                improvement_text,
                request.code,
            )
            
            logger.info(
                f"Code improvement complete: {len(improvements)} improvements made"
            )
            
            return CodeImprovementResponse(
                improved_code=improved_code,
                improvements=improvements,
                summary=summary,
            )
            
        except Exception as e:
            logger.error(f"Code improvement failed: {e}", exc_info=True)
            raise
    
    def _build_improvement_prompt(self, request: CodeImprovementRequest) -> str:
        """Build the improvement prompt from request."""
        language_info = f" (Language: {request.language})" if request.language else ""
        file_info = f" (File: {request.file_path})" if request.file_path else ""
        
        goals_desc = ""
        if request.improvement_goals:
            goals_desc = f"\n\nSpecific goals:\n" + "\n".join(
                f"- {goal}" for goal in request.improvement_goals
            )
        
        preserve_note = ""
        if request.preserve_functionality:
            preserve_note = "\n\n**Important**: Preserve the original functionality. Do not change the behavior."
        
        comments_note = ""
        if request.add_comments:
            comments_note = "\n\nAdd clear comments explaining complex logic."
        
        prompt = f"""Please improve the following code{language_info}{file_info}.{goals_desc}{preserve_note}{comments_note}

Original code:
```
{request.code}
```

Please provide:

## Improved Code

```
[Complete improved code here]
```

## Improvements Made

For each improvement:
- **Category**: bug/security/performance/style/maintainability/best_practice/documentation/error_handling
- **Description**: What was improved
- **Explanation**: Why this improvement was made

## Summary

Brief summary of all improvements."""
        
        return prompt
    
    def _parse_improvement_response(
        self,
        improvement_text: str,
        original_code: str,
    ) -> Tuple[str, List[CodeImprovementSchema], str]:
        """Parse LLM improvement response."""
        # Extract improved code
        code_match = re.search(
            r'## Improved Code\s*```(?:\w+)?\s*\n(.*?)\n```',
            improvement_text,
            re.DOTALL,
        )
        improved_code = code_match.group(1).strip() if code_match else original_code
        
        # Extract improvements
        improvements = []
        category_pattern = r'\*\*Category\*\*:\s*(\w+)'
        description_pattern = r'\*\*Description\*\*:\s*(.+?)(?=\*\*|$)'
        explanation_pattern = r'\*\*Explanation\*\*:\s*(.+?)(?=\*\*|$)'
        
        improvement_blocks = re.split(r'\n(?=\*\*Category\*\*)', improvement_text)
        
        for block in improvement_blocks:
            if not block.strip():
                continue
            
            category_match = re.search(category_pattern, block, re.IGNORECASE)
            description_match = re.search(description_pattern, block, re.DOTALL)
            explanation_match = re.search(explanation_pattern, block, re.DOTALL)
            
            if not (category_match and description_match and explanation_match):
                continue
            
            try:
                category = IssueCategory(category_match.group(1).lower())
            except ValueError:
                category = IssueCategory.BEST_PRACTICE
            
            improvement = CodeImprovementSchema(
                category=category,
                description=description_match.group(1).strip(),
                explanation=explanation_match.group(1).strip(),
            )
            improvements.append(improvement)
        
        # Extract summary
        summary_match = re.search(
            r'## Summary\s*\n(.+?)(?=##|$)',
            improvement_text,
            re.DOTALL,
        )
        summary = summary_match.group(1).strip() if summary_match else "Code improved successfully."
        
        return improved_code, improvements, summary
    
    # ========================================================================
    # Diff Review (Requirements 7.5, 7.6)
    # ========================================================================
    
    async def review_diff(
        self,
        request: DiffReviewRequest,
    ) -> DiffReviewResponse:
        """
        Review a code diff/pull request.
        
        Args:
            request: Diff review request
            
        Returns:
            DiffReviewResponse: Review of the diff
            
        Requirements:
        - 7.5: Support review of code diffs and pull requests
        - 7.6: Focus analysis on changed lines and their context
        """
        logger.info(
            f"Reviewing diff: focus_on_changes={request.focus_on_changes}, "
            f"diff_length={len(request.diff)}"
        )
        
        # Parse diff into structured format (Requirement 7.5)
        files = self._parse_diff(request.diff)
        
        # Build diff review prompt (Requirement 7.6)
        prompt = self._build_diff_review_prompt(request, files)
        
        # Generate review using LLM
        try:
            review_text = await self.llm_service.generate(
                prompt=prompt,
                system_prompt=DIFF_REVIEW_SYSTEM_PROMPT,
                temperature=0.3,
            )
            
            # Parse LLM response into structured issues
            issues = self._parse_review_response(review_text, request.diff)
            
            # Limit issues
            if len(issues) > request.max_issues:
                issues = issues[:request.max_issues]
            
            # Generate summary
            summary = self._generate_summary(issues)
            
            # Generate overall assessment
            overall_assessment = self._generate_diff_assessment(summary, issues, files)
            
            # Generate approval recommendation
            approval_recommendation = self._generate_approval_recommendation(summary)
            
            logger.info(
                f"Diff review complete: {summary.total_issues} issues found, "
                f"recommendation: {approval_recommendation}"
            )
            
            return DiffReviewResponse(
                files=files,
                issues=issues,
                summary=summary,
                overall_assessment=overall_assessment,
                approval_recommendation=approval_recommendation,
            )
            
        except Exception as e:
            logger.error(f"Diff review failed: {e}", exc_info=True)
            raise
    
    def _parse_diff(self, diff: str) -> List[DiffFileSchema]:
        """
        Parse git diff into structured format.
        
        Requirement 7.5: Support review of code diffs and pull requests
        """
        files = []
        
        # Split diff by file
        file_pattern = r'diff --git a/(.+?) b/(.+?)\n'
        file_splits = re.split(file_pattern, diff)
        
        # Process each file
        for i in range(1, len(file_splits), 3):
            if i + 2 > len(file_splits):
                break
            
            old_path = file_splits[i]
            new_path = file_splits[i + 1]
            file_diff = file_splits[i + 2]
            
            # Determine change type
            if old_path == "/dev/null":
                change_type = "added"
                old_path = None
            elif new_path == "/dev/null":
                change_type = "deleted"
            elif old_path != new_path:
                change_type = "renamed"
            else:
                change_type = "modified"
            
            # Parse hunks
            hunks = self._parse_hunks(file_diff)
            
            file_schema = DiffFileSchema(
                old_path=old_path,
                new_path=new_path,
                change_type=change_type,
                hunks=hunks,
            )
            files.append(file_schema)
        
        return files
    
    def _parse_hunks(self, file_diff: str) -> List[DiffHunkSchema]:
        """Parse diff hunks from file diff."""
        hunks = []
        
        # Find all hunks
        hunk_pattern = r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@'
        hunk_matches = list(re.finditer(hunk_pattern, file_diff))
        
        for i, match in enumerate(hunk_matches):
            old_start = int(match.group(1))
            old_count = int(match.group(2))
            new_start = int(match.group(3))
            new_count = int(match.group(4))
            
            # Extract hunk content
            hunk_start = match.end()
            hunk_end = hunk_matches[i + 1].start() if i + 1 < len(hunk_matches) else len(file_diff)
            hunk_content = file_diff[hunk_start:hunk_end]
            
            # Parse lines
            lines = []
            for line in hunk_content.split('\n'):
                if not line:
                    continue
                
                if line.startswith('+'):
                    change_type = "added"
                    content = line[1:]
                elif line.startswith('-'):
                    change_type = "removed"
                    content = line[1:]
                else:
                    change_type = "context"
                    content = line[1:] if line.startswith(' ') else line
                
                line_schema = DiffLineSchema(
                    line_number=new_start + len([l for l in lines if l.change_type != "removed"]),
                    change_type=change_type,
                    content=content,
                )
                lines.append(line_schema)
            
            hunk = DiffHunkSchema(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                lines=lines,
            )
            hunks.append(hunk)
        
        return hunks
    
    def _build_diff_review_prompt(
        self,
        request: DiffReviewRequest,
        files: List[DiffFileSchema],
    ) -> str:
        """
        Build diff review prompt.
        
        Requirement 7.6: Focus analysis on changed lines and their context
        """
        criteria_desc = ", ".join([c.value for c in request.criteria])
        
        focus_note = ""
        if request.focus_on_changes:
            focus_note = "\n\n**Focus on changed lines** (additions and deletions) and their immediate context."
        
        prompt = f"""Please review the following code changes (diff/pull request).

Review Criteria: {criteria_desc}{focus_note}

Diff:
```diff
{request.diff}
```

Please provide a detailed review with the following format:

## Issues Found

For each issue in the changes:
- **Severity**: critical/high/medium/low/info
- **Category**: bug/security/performance/style/maintainability/best_practice/documentation/error_handling
- **Title**: Brief issue title
- **Description**: Detailed explanation
- **File**: File path
- **Line**: Line number(s) in the new version
- **Suggestion**: How to fix the issue

## Overall Assessment

Provide a summary of the changes and main concerns.

## Approval Recommendation

Recommend one of: approve, request_changes, or comment"""
        
        return prompt
    
    def _generate_diff_assessment(
        self,
        summary: ReviewSummarySchema,
        issues: List[CodeIssueSchema],
        files: List[DiffFileSchema],
    ) -> str:
        """Generate overall assessment for diff."""
        file_count = len(files)
        change_count = sum(
            len(hunk.lines)
            for file in files
            for hunk in file.hunks
        )
        
        if summary.critical_count > 0:
            return (
                f"Critical issues detected in changes. "
                f"Reviewed {file_count} file(s) with {change_count} line(s) changed. "
                f"Found {summary.critical_count} critical issue(s) that must be addressed."
            )
        elif summary.high_count > 0:
            return (
                f"Significant issues found in changes. "
                f"Reviewed {file_count} file(s) with {change_count} line(s) changed. "
                f"Found {summary.high_count} high-severity issue(s)."
            )
        elif summary.medium_count > 0:
            return (
                f"Changes are generally acceptable with some concerns. "
                f"Reviewed {file_count} file(s) with {change_count} line(s) changed. "
                f"Found {summary.medium_count} medium-severity issue(s)."
            )
        else:
            return (
                f"Changes look good. "
                f"Reviewed {file_count} file(s) with {change_count} line(s) changed. "
                f"No significant issues found."
            )
    
    def _generate_approval_recommendation(self, summary: ReviewSummarySchema) -> str:
        """Generate approval recommendation based on issues."""
        if summary.critical_count > 0 or summary.high_count > 0:
            return "request_changes"
        elif summary.medium_count > 0:
            return "comment"
        else:
            return "approve"


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_review_service(
    llm_service: LLMService,
) -> ReviewService:
    """
    Dependency injection for review service.
    
    Args:
        llm_service: LLM service instance
        
    Returns:
        ReviewService: Initialized review service
    """
    return ReviewService(llm_service=llm_service)
