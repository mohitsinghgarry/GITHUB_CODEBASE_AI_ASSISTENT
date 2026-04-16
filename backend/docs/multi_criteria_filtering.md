# Multi-Criteria Filtering

## Overview

The search service supports multi-criteria filtering to narrow down search results based on file characteristics. This feature allows you to filter results by:

1. **File Extension** - Filter by file type (e.g., `.py`, `.js`, `.ts`)
2. **Directory Path** - Filter by directory location (e.g., `src/`, `tests/`)
3. **Programming Language** - Filter by detected language (e.g., `python`, `javascript`)

These filters can be combined to create precise search queries that target specific parts of your codebase.

## Requirements

**Requirement 5.6**: The Query_Engine SHALL support filtering by file extension, directory path, and programming language.

## Supported Search Types

Multi-criteria filtering is supported across all search types:

- **Keyword Search (BM25)** - `search_keyword()`
- **Semantic Search (Vector)** - `search_semantic()`
- **Hybrid Search (BM25 + Vector)** - `search_hybrid()`

## Usage

### Basic Filtering

#### Filter by File Extension

```python
from app.services.search_service import UnifiedSearchService

# Search only in Python files
results = await search_service.search_keyword(
    query="authentication",
    file_extensions=[".py"],
)

# Search in multiple file types
results = await search_service.search_keyword(
    query="function",
    file_extensions=[".py", ".js", ".ts"],
)
```

#### Filter by Directory Path

```python
# Search only in src/ directory
results = await search_service.search_keyword(
    query="middleware",
    directory_paths=["src/"],
)

# Search in multiple directories
results = await search_service.search_keyword(
    query="test",
    directory_paths=["tests/", "test/", "spec/"],
)
```

**Note**: Directory filtering uses prefix matching (`startswith`), so `src/` will match:
- `src/main.py`
- `src/utils/helper.py`
- `src/api/routes/users.py`

#### Filter by Programming Language

```python
# Search only in Python code
results = await search_service.search_keyword(
    query="async",
    languages=["python"],
)

# Search in multiple languages
results = await search_service.search_keyword(
    query="class",
    languages=["python", "javascript", "typescript"],
)
```

### Combining Filters

You can combine multiple filter types for precise targeting:

```python
# Search for "test" in Python files under tests/ directory
results = await search_service.search_keyword(
    query="test",
    file_extensions=[".py"],
    directory_paths=["tests/"],
    languages=["python"],
)
```

### Filtering with Different Search Types

#### Keyword Search

```python
results = await search_service.search_keyword(
    query="authentication",
    top_k=10,
    file_extensions=[".py"],
    directory_paths=["src/", "app/"],
    languages=["python"],
)
```

#### Semantic Search

```python
results = await search_service.search_semantic(
    query="database connection handling",
    top_k=10,
    file_extensions=[".py"],
    directory_paths=["src/", "app/"],
    languages=["python"],
)
```

#### Hybrid Search

```python
results = await search_service.search_hybrid(
    query="API endpoint authentication",
    top_k=10,
    file_extensions=[".py"],
    directory_paths=["app/api/"],
    languages=["python"],
)
```

## Filter Behavior

### File Extension Filtering

- **Case-sensitive**: `.py` will not match `.PY`
- **Exact suffix match**: Uses `str.endswith()`
- **Multiple extensions**: Results match ANY of the specified extensions (OR logic)

### Directory Path Filtering

- **Prefix match**: Uses `str.startswith()`
- **Matches subdirectories**: `src/` matches `src/components/button.py`
- **Multiple paths**: Results match ANY of the specified paths (OR logic)
- **Trailing slash recommended**: Use `src/` instead of `src` for clarity

### Language Filtering

- **Exact match**: Language must match exactly (case-sensitive)
- **Multiple languages**: Results match ANY of the specified languages (OR logic)
- **Language detection**: Based on file extension and content analysis

### Combining Filters

When multiple filter types are specified, they are combined with AND logic:

```python
# Result must satisfy ALL conditions:
# - File extension is .py OR .js
# - Directory path starts with src/ OR lib/
# - Language is python OR javascript
results = await search_service.search_keyword(
    query="function",
    file_extensions=[".py", ".js"],      # OR within this filter
    directory_paths=["src/", "lib/"],    # OR within this filter
    languages=["python", "javascript"],  # OR within this filter
)
```

## Performance Considerations

### BM25 Keyword Search

Filters are applied **during database query** for optimal performance:

```python
# Efficient: Filters applied at database level
results = await search_service.search_keyword(
    query="test",
    file_extensions=[".py"],
)
```

### Vector Semantic Search

Filters are applied **after retrieval** from FAISS:

```python
# Retrieves more results initially, then filters
results = await search_service.search_semantic(
    query="authentication",
    top_k=10,
    file_extensions=[".py"],  # Retrieves 30 results, filters, returns top 10
)
```

The service automatically retrieves 3x the requested results when filters are applied to ensure sufficient results after filtering.

### Hybrid Search

Both BM25 and vector results are filtered before fusion:

```python
# Both search methods apply filters before RRF fusion
results = await search_service.search_hybrid(
    query="API endpoint",
    top_k=10,
    file_extensions=[".py"],
)
```

## Examples

### Example 1: Find Tests for a Feature

```python
# Find all test files related to authentication
results = await search_service.search_keyword(
    query="authentication",
    file_extensions=[".py"],
    directory_paths=["tests/"],
    languages=["python"],
)
```

### Example 2: Search API Routes

```python
# Find API route definitions
results = await search_service.search_semantic(
    query="user registration endpoint",
    file_extensions=[".py"],
    directory_paths=["app/api/", "src/api/"],
)
```

### Example 3: Find Frontend Components

```python
# Find React/Vue components
results = await search_service.search_keyword(
    query="button component",
    file_extensions=[".jsx", ".tsx", ".vue"],
    directory_paths=["src/components/", "components/"],
    languages=["javascript", "typescript"],
)
```

### Example 4: Cross-Language Search

```python
# Find error handling across Python and JavaScript
results = await search_service.search_hybrid(
    query="error handling try catch",
    file_extensions=[".py", ".js", ".ts"],
    languages=["python", "javascript", "typescript"],
)
```

## API Reference

### UnifiedSearchService.search_keyword()

```python
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
```

### UnifiedSearchService.search_semantic()

```python
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
```

### UnifiedSearchService.search_hybrid()

```python
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
```

## Common Patterns

### Pattern 1: Language-Specific Search

```python
# Python-only search
python_results = await search_service.search_keyword(
    query="async def",
    languages=["python"],
)

# JavaScript/TypeScript-only search
js_results = await search_service.search_keyword(
    query="async function",
    languages=["javascript", "typescript"],
)
```

### Pattern 2: Directory-Scoped Search

```python
# Search only in source code (exclude tests)
src_results = await search_service.search_semantic(
    query="database connection",
    directory_paths=["src/", "app/", "lib/"],
)

# Search only in tests
test_results = await search_service.search_semantic(
    query="mock database",
    directory_paths=["tests/", "test/", "spec/"],
)
```

### Pattern 3: File Type Search

```python
# Configuration files
config_results = await search_service.search_keyword(
    query="database_url",
    file_extensions=[".env", ".yaml", ".yml", ".json"],
)

# Source code files
code_results = await search_service.search_keyword(
    query="function",
    file_extensions=[".py", ".js", ".ts", ".go", ".rs"],
)
```

## Troubleshooting

### No Results Returned

If filtering returns no results:

1. **Check filter values**: Ensure extensions include the dot (`.py` not `py`)
2. **Verify directory paths**: Use trailing slashes (`src/` not `src`)
3. **Check language names**: Use lowercase (`python` not `Python`)
4. **Broaden filters**: Try removing some filters to see if results exist

### Unexpected Results

If results don't match expectations:

1. **Case sensitivity**: File extensions and languages are case-sensitive
2. **Prefix matching**: Directory paths use prefix matching (not exact match)
3. **OR logic within filters**: Multiple values in one filter use OR logic
4. **AND logic between filters**: Different filter types use AND logic

### Performance Issues

If searches are slow with filters:

1. **Use keyword search for file-based filters**: BM25 applies filters at database level
2. **Reduce retrieval_multiplier**: For semantic/hybrid search with many filters
3. **Be specific with filters**: More specific filters = fewer results to process

## Testing

See `tests/unit/test_search_multi_criteria_filtering.py` for comprehensive test coverage of multi-criteria filtering functionality.

## Related Documentation

- [Search Service Overview](./search_service.md)
- [BM25 Keyword Search](./bm25_search.md)
- [Vector Semantic Search](./semantic_search.md)
- [Hybrid Search](./hybrid_search.md)
