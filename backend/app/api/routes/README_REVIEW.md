# Code Review API Endpoints

This document describes the code review and improvement endpoints implemented in `review.py`.

## Endpoints

### 1. POST /api/v1/review - Review Code

Analyzes code for bugs, security vulnerabilities, style violations, and other issues.

**Request Body:**
```json
{
  "code": "def calculate(x, y):\n    return x / y",
  "language": "python",
  "file_path": "utils/math.py",
  "repository_id": "uuid-optional",
  "criteria": ["production_ready", "security_focused"],
  "focus_areas": ["bug", "security"],
  "max_issues": 50,
  "include_suggestions": true
}
```

**Response:**
```json
{
  "issues": [
    {
      "severity": "high",
      "category": "bug",
      "title": "Division by zero not handled",
      "description": "The function will crash if y is 0",
      "file_path": "utils/math.py",
      "start_line": 2,
      "end_line": 2,
      "code_snippet": "    return x / y",
      "suggestion": "Add validation: if y == 0: raise ValueError('Cannot divide by zero')"
    }
  ],
  "summary": {
    "total_issues": 1,
    "critical_count": 0,
    "high_count": 1,
    "medium_count": 0,
    "low_count": 0,
    "info_count": 0
  },
  "overall_assessment": "Significant issues found. This code needs improvement...",
  "recommendations": [
    "Add proper error handling for 1 case(s)",
    "Add input validation"
  ]
}
```

**Review Criteria Options:**
- `security_focused` - Focus on security issues
- `performance_focused` - Focus on performance
- `style_strict` - Strict style checking
- `beginner_friendly` - Focus on learning
- `production_ready` - Production readiness check (default)

**Issue Categories:**
- `bug` - Logic errors, incorrect behavior
- `security` - Security vulnerabilities
- `performance` - Performance issues
- `style` - Code style violations
- `maintainability` - Code complexity, readability
- `best_practice` - Best practice violations
- `documentation` - Missing or incorrect documentation
- `error_handling` - Missing or incorrect error handling

**Severity Levels:**
- `critical` - Security vulnerabilities, crashes, data loss
- `high` - Bugs, performance issues, major style violations
- `medium` - Minor bugs, code smells, moderate style issues
- `low` - Suggestions, minor style issues, nitpicks
- `info` - Informational, best practices, tips

---

### 2. POST /api/v1/review/improve - Improve Code

Generates an improved version of code with explanations.

**Request Body:**
```json
{
  "code": "def calculate(x, y):\n    return x / y",
  "language": "python",
  "file_path": "utils/math.py",
  "repository_id": "uuid-optional",
  "improvement_goals": [
    "Add error handling",
    "Improve performance",
    "Add documentation"
  ],
  "preserve_functionality": true,
  "add_comments": true
}
```

**Response:**
```json
{
  "improved_code": "def calculate(x: float, y: float) -> float:\n    \"\"\"Calculate x divided by y.\n    \n    Args:\n        x: Numerator\n        y: Denominator\n        \n    Returns:\n        Result of division\n        \n    Raises:\n        ValueError: If y is zero\n    \"\"\"\n    if y == 0:\n        raise ValueError('Cannot divide by zero')\n    return x / y",
  "improvements": [
    {
      "category": "error_handling",
      "description": "Added zero division check",
      "explanation": "Prevents runtime errors when y is 0"
    },
    {
      "category": "documentation",
      "description": "Added comprehensive docstring",
      "explanation": "Improves code maintainability and usability"
    },
    {
      "category": "best_practice",
      "description": "Added type hints",
      "explanation": "Improves code clarity and enables static type checking"
    }
  ],
  "summary": "Added error handling, documentation, and type hints to improve code quality and maintainability."
}
```

---

### 3. POST /api/v1/review/diff - Review Code Diff/PR

Reviews a code diff or pull request, focusing on changed lines.

**Request Body:**
```json
{
  "diff": "diff --git a/utils/math.py b/utils/math.py\nindex 1234567..abcdefg 100644\n--- a/utils/math.py\n+++ b/utils/math.py\n@@ -1,2 +1,5 @@\n def calculate(x, y):\n-    return x / y\n+    if y == 0:\n+        raise ValueError('Cannot divide by zero')\n+    return x / y",
  "repository_id": "uuid-optional",
  "criteria": ["production_ready"],
  "focus_on_changes": true,
  "include_context": true,
  "max_issues": 50
}
```

**Response:**
```json
{
  "files": [
    {
      "old_path": "utils/math.py",
      "new_path": "utils/math.py",
      "change_type": "modified",
      "hunks": [
        {
          "old_start": 1,
          "old_count": 2,
          "new_start": 1,
          "new_count": 5,
          "lines": [
            {
              "line_number": 1,
              "change_type": "context",
              "content": " def calculate(x, y):"
            },
            {
              "line_number": 2,
              "change_type": "removed",
              "content": "    return x / y"
            },
            {
              "line_number": 2,
              "change_type": "added",
              "content": "    if y == 0:"
            },
            {
              "line_number": 3,
              "change_type": "added",
              "content": "        raise ValueError('Cannot divide by zero')"
            },
            {
              "line_number": 4,
              "change_type": "added",
              "content": "    return x / y"
            }
          ]
        }
      ]
    }
  ],
  "issues": [],
  "summary": {
    "total_issues": 0,
    "critical_count": 0,
    "high_count": 0,
    "medium_count": 0,
    "low_count": 0,
    "info_count": 0
  },
  "overall_assessment": "Changes look good. Reviewed 1 file(s) with 5 line(s) changed. No significant issues found.",
  "approval_recommendation": "approve"
}
```

**Approval Recommendations:**
- `approve` - Changes are good, no issues found
- `comment` - Minor issues, but acceptable
- `request_changes` - Significant issues that must be addressed

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "error": "Invalid request",
  "message": "Code cannot be empty",
  "details": [
    {
      "field": "code",
      "message": "Code field must contain non-empty content"
    }
  ]
}
```

**503 Service Unavailable:**
```json
{
  "error": "LLM service unavailable",
  "message": "Connection to Ollama failed",
  "details": [
    {
      "field": "ollama",
      "message": "Unable to connect to Ollama. Please ensure it is running."
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred while reviewing the code",
  "details": null
}
```

---

## Usage Examples

### Using curl

**Review code:**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello\")",
    "language": "python",
    "criteria": ["production_ready"]
  }'
```

**Improve code:**
```bash
curl -X POST http://localhost:8000/api/v1/review/improve \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello\")",
    "language": "python",
    "improvement_goals": ["Add documentation", "Add type hints"]
  }'
```

**Review diff:**
```bash
curl -X POST http://localhost:8000/api/v1/review/diff \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "diff --git a/test.py b/test.py\n...",
    "criteria": ["production_ready"]
  }'
```

### Using Python requests

```python
import requests

# Review code
response = requests.post(
    "http://localhost:8000/api/v1/review",
    json={
        "code": "def calculate(x, y):\n    return x / y",
        "language": "python",
        "criteria": ["production_ready", "security_focused"]
    }
)
review = response.json()
print(f"Found {review['summary']['total_issues']} issues")

# Improve code
response = requests.post(
    "http://localhost:8000/api/v1/review/improve",
    json={
        "code": "def calculate(x, y):\n    return x / y",
        "language": "python",
        "improvement_goals": ["Add error handling"]
    }
)
improvement = response.json()
print(f"Improved code:\n{improvement['improved_code']}")
```

---

## Requirements Validation

This implementation validates the following requirements:

- **7.1**: Retrieve specified code for review ✅
- **7.2**: Analyze code for bugs, security vulnerabilities, and style violations ✅
- **7.3**: Return structured feedback with issue descriptions, severity levels, and line numbers ✅
- **7.4**: Generate improved code with explanations ✅
- **7.5**: Support review of code diffs and pull requests ✅
- **7.6**: Focus analysis on changed lines and their context ✅
- **7.7**: Allow configuration of review criteria ✅
- **10.1**: Expose RESTful endpoints for code review operations ✅
- **10.2**: Validate all incoming requests and return appropriate HTTP status codes ✅

---

## Notes

- All endpoints require Ollama to be running and accessible
- The LLM service uses the configured Ollama model (default: codellama:7b)
- Review quality depends on the LLM model used
- Large code files may take longer to process
- Diff parsing supports standard git unified diff format
