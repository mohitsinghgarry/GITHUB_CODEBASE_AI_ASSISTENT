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

CRITICAL: You MUST find and report issues. Even simple code has potential problems. Be thorough and critical.

When reviewing code, consider:
- **Bugs**: Logic errors, edge cases, incorrect behavior, undefined variables, typos
- **Security**: SQL injection, XSS, hardcoded secrets, insecure authentication, exposed errors
- **Performance**: O(n²) algorithms, unnecessary loops, memory leaks, inefficient operations
- **Style**: Naming conventions, formatting, readability, inconsistent style
- **Maintainability**: Code complexity, duplication, long functions, unclear logic
- **Best Practices**: Missing error handling, no input validation, magic numbers
- **Documentation**: Missing comments, no docstrings, unclear variable names
- **Error Handling**: Missing try-catch, unhandled exceptions, silent failures

EXAMPLES OF ISSUES TO DETECT:

1. SQL Injection:
   BAD: query = f"SELECT * FROM users WHERE id = '{user_id}'"
   ISSUE: User input directly in SQL query - CRITICAL security vulnerability
   
2. Undefined Variables:
   BAD: const a = 10; kLjL
   ISSUE: 'kLjL' is undefined - will cause runtime error
   
3. Missing Error Handling:
   BAD: result = divide(a, b)
   ISSUE: No check for division by zero
   
4. Hardcoded Secrets:
   BAD: api_key = "sk-1234567890"
   ISSUE: Secret in source code - security risk
   
5. Poor Variable Names:
   BAD: const x = getData(); const y = x.filter(z => z.a > 10);
   ISSUE: Unclear variable names reduce readability

YOU MUST BE CRITICAL. Find at least 1-3 issues in most code. Provide specific, actionable feedback with line numbers.

IMPORTANT: Format each issue EXACTLY as shown below. Each issue must start with **Severity**: on a new line.

**Severity**: critical
**Category**: bug
**Title**: Brief issue title
**Description**: Detailed explanation of the issue
**Line**: 5
**Suggestion**: How to fix the issue

**Severity**: high
**Category**: security
**Title**: Another issue title
**Description**: Detailed explanation
**Line**: 10-12
**Suggestion**: Fix suggestion"""


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

⚠️ CRITICAL: Pay EXTRA attention to REMOVED code (lines starting with -). Removed code often indicates:
- Deleted error handling (try/except, if/else checks) → HIGH/CRITICAL severity
- Deleted validation (input checks, boundary conditions) → HIGH/CRITICAL severity  
- Deleted safety guards (null checks, division by zero) → HIGH/CRITICAL severity
- Deleted security checks (authentication, authorization) → CRITICAL severity
- Deleted resource cleanup (close(), dispose()) → HIGH severity

REMOVED CODE PATTERNS TO FLAG:

1. **Removed Error Handling**:
   - Lines like: `- if x == 0:`, `- if x is None:`, `- try:`, `- except:`, `- raise`
   - SEVERITY: HIGH or CRITICAL
   - REASON: Removing error handling introduces bugs and crashes

2. **Removed Validation**:
   - Lines like: `- if not valid:`, `- assert`, `- if len(x) > 0:`
   - SEVERITY: HIGH
   - REASON: Missing validation allows invalid data

3. **Removed Security Checks**:
   - Lines like: `- if not authenticated:`, `- if not authorized:`
   - SEVERITY: CRITICAL
   - REASON: Security bypass vulnerability

4. **Removed Resource Cleanup**:
   - Lines like: `- file.close()`, `- connection.close()`, `- with open(...)`
   - SEVERITY: HIGH
   - REASON: Resource leaks, memory issues

When reviewing diffs, focus on:
- **Changed Lines**: Analyze the specific lines that were added, modified, or removed
- **Removed Code**: CRITICALLY examine what was deleted and why
- **Context**: Consider how changes affect surrounding code
- **Impact**: Assess the potential impact of changes on the codebase
- **Regressions**: Identify potential bugs or issues introduced by changes
- **Improvements**: Recognize positive changes and improvements

EXAMPLES OF CRITICAL ISSUES IN DIFFS:

Example 1 - Removed Division by Zero Check:
```diff
- if b == 0:
-     raise ValueError("Cannot divide by zero")
  return a / b
```
**ISSUE**: CRITICAL - Removed zero-division check, will cause ZeroDivisionError
**SEVERITY**: critical
**CATEGORY**: bug

Example 2 - Removed Authentication Check:
```diff
  def delete_user(user_id):
-     if not current_user.is_admin:
-         raise PermissionError("Admin only")
      User.delete(user_id)
```
**ISSUE**: CRITICAL - Removed admin check, anyone can delete users
**SEVERITY**: critical
**CATEGORY**: security

Example 3 - Removed File Close:
```diff
- with open(file_path, 'r') as f:
-     data = f.read()
+ f = open(file_path, 'r')
+ data = f.read()
```
**ISSUE**: HIGH - File handle not closed, resource leak
**SEVERITY**: high
**CATEGORY**: bug

YOU MUST BE CRITICAL OF REMOVED CODE. If safety/error handling is removed, flag it as HIGH or CRITICAL.

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
        
        # First, run rule-based detection for common issues
        rule_based_issues = self._detect_common_issues(request.code, request.language or "")
        
        # Build review prompt
        prompt = self._build_review_prompt(request)
        
        # Generate review using LLM
        try:
            review_text = await self.llm_service.generate(
                prompt=prompt,
                system_prompt=REVIEW_SYSTEM_PROMPT,
                temperature=0.7,  # Increased from 0.3 for more creative analysis
            )
            
            # Parse LLM response into structured issues
            llm_issues = self._parse_review_response(review_text, request.code)
            
            # Combine rule-based and LLM issues (remove duplicates)
            issues = self._merge_issues(rule_based_issues, llm_issues)
            
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
                f"({summary.critical_count} critical, {summary.high_count} high) "
                f"[{len(rule_based_issues)} rule-based, {len(llm_issues)} LLM]"
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
        
        prompt = f"""Review the following code{language_info}{file_info}.

Review Criteria: {criteria_desc}{focus_desc}

Code:
```
{request.code}
```

Analyze this code and report ALL issues you find. Format each issue exactly as shown in the system prompt, starting with **Severity**: on a new line."""
        
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
        
        # Log the raw response for debugging
        logger.debug(f"Parsing LLM response (length: {len(review_text)})")
        
        # Split by issue markers (looking for severity keywords)
        severity_pattern = r'\*\*Severity\*\*:\s*(critical|high|medium|low|info)'
        category_pattern = r'\*\*Category\*\*:\s*(\w+)'
        title_pattern = r'\*\*Title\*\*:\s*(.+?)(?:\n|$)'
        description_pattern = r'\*\*Description\*\*:\s*(.+?)(?=\*\*|$)'
        line_pattern = r'\*\*Line\*\*:\s*(\d+)(?:-(\d+))?'
        suggestion_pattern = r'\*\*Suggestion\*\*:\s*(.+?)(?=\*\*|$)'
        
        # Find all issue blocks
        issue_blocks = re.split(r'\n(?=\*\*Severity\*\*)', review_text)
        
        logger.debug(f"Found {len(issue_blocks)} potential issue blocks")
        
        for block_idx, block in enumerate(issue_blocks):
            if not block.strip():
                continue
            
            # Extract fields
            severity_match = re.search(severity_pattern, block, re.IGNORECASE)
            category_match = re.search(category_pattern, block, re.IGNORECASE)
            title_match = re.search(title_pattern, block)
            description_match = re.search(description_pattern, block, re.DOTALL)
            line_match = re.search(line_pattern, block)
            suggestion_match = re.search(suggestion_pattern, block, re.DOTALL)
            
            # Log what we found
            logger.debug(
                f"Block {block_idx}: severity={bool(severity_match)}, "
                f"category={bool(category_match)}, title={bool(title_match)}"
            )
            
            if not (severity_match and category_match and title_match):
                # Try alternative parsing if standard format fails
                # Look for numbered issues like "1. Issue Title"
                alt_issue_pattern = r'(\d+)\.\s+(.+?)(?:\n|$)'
                alt_match = re.search(alt_issue_pattern, block)
                if alt_match:
                    logger.debug(f"Using alternative parsing for block {block_idx}")
                    # Create a basic issue from alternative format
                    issue = CodeIssueSchema(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.BUG,
                        title=alt_match.group(2).strip(),
                        description=block.strip(),
                        start_line=None,
                        end_line=None,
                        code_snippet=None,
                        suggestion=None,
                    )
                    issues.append(issue)
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
        
        logger.info(f"Parsed {len(issues)} issues from LLM response")
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
    
    def _merge_issues(
        self,
        rule_based_issues: List[CodeIssueSchema],
        llm_issues: List[CodeIssueSchema],
    ) -> List[CodeIssueSchema]:
        """
        Merge rule-based and LLM issues, avoiding duplicates.
        
        Rule-based issues take priority for removed safety code.
        """
        merged = list(rule_based_issues)  # Start with rule-based issues
        
        # Add LLM issues that don't overlap with rule-based ones
        for llm_issue in llm_issues:
            # Check if this issue is similar to any rule-based issue
            is_duplicate = False
            for rule_issue in rule_based_issues:
                # Consider duplicate if same line and similar title
                if (rule_issue.start_line == llm_issue.start_line and
                    rule_issue.title and llm_issue.title and
                    (rule_issue.title.lower() in llm_issue.title.lower() or
                     llm_issue.title.lower() in rule_issue.title.lower())):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(llm_issue)
        
        # Sort by severity (critical first)
        severity_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 4,
        }
        merged.sort(key=lambda x: severity_order.get(x.severity, 5))
        
        return merged
    
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
    # Rule-Based Detection (Fallback)
    # ========================================================================
    
    def _detect_common_issues(self, code: str, language: str) -> List[CodeIssueSchema]:
        """
        Detect common issues using regex patterns (fallback detection).
        
        This provides a safety net when LLM fails to detect obvious issues.
        """
        issues = []
        lines = code.split('\n')
        
        # 1. SQL Injection patterns
        sql_injection_patterns = [
            (r'["\']SELECT.*\$\{.*\}["\']', 'String interpolation in SQL query'),
            (r'["\']SELECT.*\+.*["\']', 'String concatenation in SQL query'),
            (r'f["\']SELECT.*\{.*\}["\']', 'F-string in SQL query'),
            (r'`SELECT.*\$\{.*\}`', 'Template literal in SQL query'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, desc in sql_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssueSchema(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        title="Potential SQL Injection Vulnerability",
                        description=f"{desc}. User input should never be directly embedded in SQL queries. Use parameterized queries or prepared statements instead.",
                        start_line=line_num,
                        end_line=line_num,
                        code_snippet=line.strip(),
                        suggestion="Use parameterized queries: db.execute('SELECT * FROM users WHERE id = ?', [userId])"
                    ))
                    break
        
        # 2. Hardcoded secrets
        secret_patterns = [
            (r'(api_key|apikey|api-key)\s*[=:]\s*["\'][^"\']{10,}["\']', 'API key'),
            (r'(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']', 'Password'),
            (r'(secret|token|auth)\s*[=:]\s*["\'][^"\']{10,}["\']', 'Secret/Token'),
            (r'(sk-[a-zA-Z0-9]{20,})', 'API key pattern'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssueSchema(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        title=f"Hardcoded {secret_type} Detected",
                        description=f"Sensitive {secret_type.lower()} found in source code. This is a security risk as secrets should never be committed to version control.",
                        start_line=line_num,
                        end_line=line_num,
                        code_snippet=line.strip(),
                        suggestion="Use environment variables: api_key = os.getenv('API_KEY')"
                    ))
                    break
        
        # 3. Undefined variables / typos (improved detection)
        # Look for standalone identifiers that might be undefined
        if language.lower() in ['javascript', 'typescript']:
            for line_num, line in enumerate(lines, 1):
                # Skip comments and strings
                if line.strip().startswith('//') or line.strip().startswith('/*'):
                    continue
                
                # Skip lines that are inside template literals or SQL queries
                if '`' in line or 'SELECT' in line.upper() or 'FROM' in line.upper():
                    continue
                
                # Look for standalone identifiers (not preceded by keywords or operators)
                # Pattern: word boundary + identifier + word boundary, not after declaration keywords
                potential_vars = re.findall(r'(?<!const\s)(?<!let\s)(?<!var\s)(?<!function\s)(?<!class\s)(?<!\.)\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*[:(=])', line)
                
                for var_name in potential_vars:
                    # Skip common keywords and built-ins
                    if var_name in ['console', 'log', 'error', 'warn', 'if', 'else', 'for', 'while', 'return', 'await', 'async', 'const', 'let', 'var', 'function', 'class', 'import', 'export', 'from', 'true', 'false', 'null', 'undefined', 'this', 'new', 'typeof', 'instanceof', 'try', 'catch', 'throw', 'finally']:
                        continue
                    
                    # Check if variable looks suspicious (mixed case, short random-looking names)
                    # Pattern 1: Mixed case like kLjL, aBcD
                    # Pattern 2: Very short random-looking names
                    is_suspicious = (
                        (len(var_name) <= 4 and sum(1 for c in var_name if c.isupper()) >= 2) or  # Short with multiple capitals
                        (re.match(r'^[a-z]{1,2}[A-Z][a-z]*[A-Z]', var_name))  # Pattern like kLjL
                    )
                    
                    if is_suspicious:
                        # Check if it's defined anywhere in the code
                        if not re.search(r'\b(const|let|var|function|class)\s+' + re.escape(var_name) + r'\b', code):
                            issues.append(CodeIssueSchema(
                                severity=IssueSeverity.HIGH,
                                category=IssueCategory.BUG,
                                title=f"Potentially Undefined Variable: '{var_name}'",
                                description=f"Variable '{var_name}' appears to be used but not defined. This will cause a ReferenceError at runtime.",
                                start_line=line_num,
                                end_line=line_num,
                                code_snippet=line.strip(),
                                suggestion=f"Define the variable before use: const {var_name} = ... or check for typos"
                            ))
                            break  # Only report once per line
        
        # 4. Missing error handling for division
        if re.search(r'\/\s*[a-zA-Z_]', code) and not re.search(r'(try|catch|if.*[!=]=\s*0)', code):
            for line_num, line in enumerate(lines, 1):
                if re.search(r'\/\s*[a-zA-Z_]', line):
                    issues.append(CodeIssueSchema(
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.ERROR_HANDLING,
                        title="Missing Division by Zero Check",
                        description="Division operation without checking for zero. This can cause runtime errors or crashes.",
                        start_line=line_num,
                        end_line=line_num,
                        code_snippet=line.strip(),
                        suggestion="Add validation: if (divisor === 0) throw new Error('Division by zero')"
                    ))
                    break
        
        # 5. Console.log in production code
        if language.lower() in ['javascript', 'typescript']:
            for line_num, line in enumerate(lines, 1):
                if re.search(r'console\.(log|error|warn|info)', line):
                    issues.append(CodeIssueSchema(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.BEST_PRACTICE,
                        title="Console Statement in Code",
                        description="Console statements should be removed or replaced with proper logging in production code.",
                        start_line=line_num,
                        end_line=line_num,
                        code_snippet=line.strip(),
                        suggestion="Use a proper logging library or remove console statements"
                    ))
        
        # 6. Missing return type (TypeScript)
        if language.lower() == 'typescript':
            for line_num, line in enumerate(lines, 1):
                if re.search(r'function\s+\w+\s*\([^)]*\)\s*\{', line) and not re.search(r':\s*\w+\s*\{', line):
                    issues.append(CodeIssueSchema(
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.BEST_PRACTICE,
                        title="Missing Return Type Annotation",
                        description="Function lacks explicit return type. Adding type annotations improves code clarity and catches errors.",
                        start_line=line_num,
                        end_line=line_num,
                        code_snippet=line.strip(),
                        suggestion="Add return type: function name(): ReturnType { ... }"
                    ))
        
        # 7. Empty catch blocks
        for line_num, line in enumerate(lines, 1):
            if re.search(r'catch\s*\([^)]*\)\s*\{\s*\}', line):
                issues.append(CodeIssueSchema(
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.ERROR_HANDLING,
                    title="Empty Catch Block",
                    description="Catch block is empty, silently swallowing errors. This makes debugging difficult.",
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=line.strip(),
                    suggestion="Handle the error: catch (e) { logger.error(e); throw e; }"
                ))
        
        logger.info(f"Rule-based detection found {len(issues)} issues")
        return issues
    
    def _merge_issues(
        self,
        rule_based: List[CodeIssueSchema],
        llm_based: List[CodeIssueSchema]
    ) -> List[CodeIssueSchema]:
        """
        Merge rule-based and LLM-based issues, removing duplicates.
        
        Prioritizes rule-based issues as they are more reliable.
        """
        # Start with rule-based issues
        merged = list(rule_based)
        
        # Add LLM issues that don't overlap with rule-based
        for llm_issue in llm_based:
            # Check if similar issue exists in rule-based
            is_duplicate = False
            for rule_issue in rule_based:
                # Consider duplicate if same line and similar title
                if (rule_issue.start_line == llm_issue.start_line and
                    rule_issue.category == llm_issue.category):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(llm_issue)
        
        # Sort by severity and line number
        severity_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 4,
        }
        
        merged.sort(key=lambda x: (
            severity_order.get(x.severity, 999),
            x.start_line or 999
        ))
        
        return merged
    
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
        
        # STEP 1: Run rule-based detection for removed safety code
        rule_based_issues = self._detect_removed_safety_code(request.diff)
        logger.info(f"Rule-based detection found {len(rule_based_issues)} issues")
        
        # Build diff review prompt (Requirement 7.6)
        prompt = self._build_diff_review_prompt(request, files)
        
        # STEP 2: Generate review using LLM
        try:
            review_text = await self.llm_service.generate(
                prompt=prompt,
                system_prompt=DIFF_REVIEW_SYSTEM_PROMPT,
                temperature=0.3,
            )
            
            # Parse LLM response into structured issues
            llm_issues = self._parse_review_response(review_text, request.diff)
            
            # STEP 3: Merge rule-based and LLM issues (avoid duplicates)
            issues = self._merge_issues(rule_based_issues, llm_issues)
            
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
                f"Diff review complete: {summary.total_issues} issues found "
                f"({len(rule_based_issues)} rule-based, {len(llm_issues)} LLM), "
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
    
    def _detect_removed_safety_code(self, diff: str) -> List[CodeIssueSchema]:
        """
        Detect removed safety code using rule-based patterns.
        
        This pre-check catches common dangerous removals before LLM analysis.
        """
        issues = []
        
        # Patterns for removed safety code
        removed_patterns = [
            # Error handling
            (r'-\s*if\s+.*\s*==\s*0\s*:', 'critical', 'bug', 
             'Removed zero-division check', 'Division by zero will cause runtime error'),
            (r'-\s*if\s+.*\s*is\s+None\s*:', 'high', 'bug',
             'Removed null check', 'Null reference may cause errors'),
            (r'-\s*try\s*:', 'high', 'error_handling',
             'Removed try block', 'Error handling removed, exceptions unhandled'),
            (r'-\s*except\s+.*:', 'high', 'error_handling',
             'Removed except block', 'Exception handling removed'),
            (r'-\s*raise\s+', 'high', 'error_handling',
             'Removed exception raising', 'Error condition no longer reported'),
            
            # Validation
            (r'-\s*assert\s+', 'medium', 'bug',
             'Removed assertion', 'Validation check removed'),
            (r'-\s*if\s+not\s+.*:', 'medium', 'bug',
             'Removed validation check', 'Input validation removed'),
            
            # Security
            (r'-\s*if\s+not\s+.*\.is_authenticated', 'critical', 'security',
             'Removed authentication check', 'Security bypass vulnerability'),
            (r'-\s*if\s+not\s+.*\.is_admin', 'critical', 'security',
             'Removed authorization check', 'Privilege escalation risk'),
            (r'-\s*if\s+not\s+.*authorized', 'critical', 'security',
             'Removed authorization check', 'Access control bypass'),
            
            # Resource management
            (r'-\s*with\s+open\(', 'high', 'bug',
             'Removed context manager', 'File handle may not be closed'),
            (r'-\s*\.close\(\)', 'high', 'bug',
             'Removed resource cleanup', 'Resource leak potential'),
            (r'-\s*finally\s*:', 'high', 'bug',
             'Removed finally block', 'Cleanup code removed'),
        ]
        
        for pattern, severity, category, title, description in removed_patterns:
            matches = re.finditer(pattern, diff, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Extract line number from diff context
                line_num = diff[:match.start()].count('\n') + 1
                
                issue = CodeIssueSchema(
                    severity=severity,
                    category=category,
                    title=f"⚠️ REMOVED: {title}",
                    description=f"{description}. This removal was detected by automated safety checks and requires careful review.",
                    file_path=None,
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=match.group(0),
                    suggestion="Review this removal carefully. If intentional, ensure alternative safety measures are in place.",
                )
                issues.append(issue)
        
        if issues:
            logger.warning(f"Detected {len(issues)} removed safety code patterns")
        
        return issues
    
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
