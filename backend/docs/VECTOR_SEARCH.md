# Vector Semantic Search Documentation

## Overview

The vector semantic search functionality enables natural language queries over code repositories using FAISS vector similarity search. This implementation satisfies requirements 4.1-4.5 from the design specification.

## Architecture

### Components

1. **SemanticSearchRetriever** (`app/core/retrieval/retriever.py`)
   - Core retrieval logic using FAISS similarity search
   - Query embedding generation
   - Repository filtering
   - Top-K result selection with configurable limits (1-100)

2. **VectorSearchService** (`app/services/search_service.py`)
   - Service layer wrapper for semantic search
   - Async interface for FastAPI integration
   - Score threshold filtering

3. **UnifiedSearchService** (`app/services/search_service.py`)
   - Unified interface for BM25, vector, and hybrid search
   - Combines multiple search modes in a single service

## Features

### 1. Query Embedding Generation (Requirement 4.1)

The system automatically generates embeddings for user queries using the configured sentence-transformers model:

```python
from app.core.retrieval.retriever import SemanticSearchRetriever

retriever = SemanticSearchRetriever()
results = retriever.search(
    query="authentication middleware function",
    top_k=10,
)
```

**Implementation Details:**
- Uses `sentence-transformers` for embedding generation
- Embeddings are normalized for cosine similarity
- Default model: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Supports CPU, CUDA, and MPS (Apple Silicon) devices

### 2. Vector Similarity Search (Requirement 4.2)

Performs FAISS similarity search against repository-specific indices:

```python
# Search returns results sorted by similarity score
results = retriever.search(
    query="database connection pool",
    top_k=5,
)

for result in results:
    print(f"{result.file_path}:{result.start_line} - Score: {result.score:.4f}")
```

**Implementation Details:**
- Uses FAISS `IndexFlatIP` for inner product similarity
- Separate index per repository for efficient updates
- Cosine similarity via normalized vectors
- Returns chunk metadata with similarity scores

### 3. Top-K Results with Scores (Requirement 4.3)

Returns the most relevant code chunks with similarity scores:

```python
results = retriever.search(query="error handling", top_k=10)

# Results are sorted by score (highest first)
for i, result in enumerate(results, 1):
    print(f"{i}. {result.file_path}")
    print(f"   Score: {result.score:.4f}")
    print(f"   Content: {result.content[:100]}...")
```

**Result Structure:**
```python
@dataclass
class SearchResult:
    chunk_id: str           # UUID of the code chunk
    repository_id: str      # UUID of the repository
    file_path: str          # Path to source file
    start_line: int         # Starting line number
    end_line: int           # Ending line number
    language: str           # Programming language
    content: str            # Code content
    score: float            # Similarity score (0.0-1.0)
```

### 4. Configurable Result Limits (Requirement 4.4)

Supports result limits between 1 and 100 chunks:

```python
# Minimum: 1 result
results = retriever.search(query="main function", top_k=1)

# Maximum: 100 results
results = retriever.search(query="utility functions", top_k=100)

# Values outside range are automatically clamped
results = retriever.search(query="test", top_k=0)    # Clamped to 1
results = retriever.search(query="test", top_k=200)  # Clamped to 100
```

### 5. Repository Filtering (Requirement 4.5)

Filter search results by specific repositories:

```python
from uuid import UUID

# Search specific repositories
repo_ids = [
    UUID("12345678-1234-5678-1234-567812345678"),
    UUID("87654321-4321-8765-4321-876543218765"),
]

results = retriever.search(
    query="API endpoint",
    top_k=10,
    repository_ids=repo_ids,
)

# Search all repositories (default)
results = retriever.search(
    query="API endpoint",
    top_k=10,
    repository_ids=None,  # Searches all available repositories
)
```

## Advanced Features

### Score Threshold Filtering

Filter results by minimum similarity score:

```python
# Only return results with score >= 0.7
results = retriever.search_with_threshold(
    query="authentication",
    top_k=20,
    score_threshold=0.7,
)
```

### Finding Similar Chunks

Find code chunks similar to a reference chunk:

```python
similar_chunks = retriever.get_similar_chunks(
    chunk_id="chunk-uuid",
    repository_id=UUID("repo-uuid"),
    top_k=5,
)
```

## Service Layer Integration

### VectorSearchService

Async service wrapper for FastAPI integration:

```python
from app.services.search_service import VectorSearchService

service = VectorSearchService()

# Async search
results = await service.search(
    query="database query",
    top_k=10,
    repository_ids=[repo_uuid],
    score_threshold=0.5,
)
```

### UnifiedSearchService

Unified interface for all search modes:

```python
from fastapi import Depends
from app.database import get_db
from app.services.search_service import UnifiedSearchService

@app.post("/search/semantic")
async def search_semantic(
    query: str,
    top_k: int = 10,
    db: AsyncSession = Depends(get_db),
):
    service = UnifiedSearchService(db)
    results = await service.search_semantic(
        query=query,
        top_k=top_k,
    )
    return results
```

## Performance Considerations

### Embedding Generation

- **Batch Processing**: Use `embed_batch()` for multiple texts
- **Device Selection**: Configure GPU/CPU via settings
- **Model Selection**: Balance between speed and accuracy

```python
# Configure in settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast, 384-dim
EMBEDDING_DEVICE = "cuda"  # or "cpu", "mps"
EMBEDDING_BATCH_SIZE = 32
```

### FAISS Search

- **Index Type**: `IndexFlatIP` provides exact search (no approximation)
- **Per-Repository Indices**: Enables efficient updates and deletion
- **Memory Usage**: ~1.5KB per chunk (384-dim float32 + metadata)

### Scaling

For large repositories (>100K chunks):
1. Consider using FAISS approximate indices (IVF, HNSW)
2. Implement index sharding across multiple files
3. Use GPU for faster similarity search

## Error Handling

### Common Errors

1. **Empty Query**
```python
try:
    results = retriever.search("")
except ValueError as e:
    print(f"Error: {e}")  # "Query cannot be empty"
```

2. **Repository Not Found**
```python
results = retriever.search(
    query="test",
    repository_ids=[UUID("nonexistent-uuid")],
)
# Returns empty list (no error)
```

3. **Empty Index**
```python
# Searching an empty repository returns empty list
results = retriever.search(
    query="test",
    repository_ids=[empty_repo_uuid],
)
# Returns []
```

## Testing

### Unit Tests

Run unit tests for semantic search:

```bash
cd backend
python -m pytest tests/unit/test_semantic_search.py -v
```

### Integration Tests

Test with real vector stores:

```python
# See tests/unit/test_semantic_search.py for examples
def test_search_with_real_store(temp_vector_store_manager, sample_repository):
    repo_id, store = sample_repository
    retriever = SemanticSearchRetriever(
        vector_store_manager=temp_vector_store_manager
    )
    results = retriever.search(
        query="function implementation",
        top_k=3,
        repository_ids=[repo_id],
    )
    assert len(results) <= 3
```

## Configuration

### Environment Variables

```bash
# Embedding model configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

# FAISS index storage
FAISS_INDEX_PATH=./data/indices
```

### Settings Class

```python
from app.core.config import Settings

settings = Settings(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    embedding_dimension=384,
    embedding_device="cuda",
    faiss_index_path=Path("./data/indices"),
)
```

## API Endpoints

### Semantic Search Endpoint

```python
@router.post("/search/semantic")
async def search_semantic(
    query: str,
    top_k: int = 10,
    repository_ids: Optional[List[UUID]] = None,
    score_threshold: float = 0.0,
    db: AsyncSession = Depends(get_db),
):
    """
    Perform semantic search across repositories.
    
    Args:
        query: Natural language query
        top_k: Number of results (1-100)
        repository_ids: Filter by repositories (optional)
        score_threshold: Minimum similarity score (optional)
    
    Returns:
        List of search results with similarity scores
    """
    service = UnifiedSearchService(db)
    results = await service.search_semantic(
        query=query,
        top_k=top_k,
        repository_ids=repository_ids,
        score_threshold=score_threshold,
    )
    return results
```

## Examples

See `backend/examples/vector_search_example.py` for complete examples:

1. Basic semantic search
2. Filtered search by repository
3. Search with score threshold
4. Using VectorSearchService
5. Using UnifiedSearchService
6. Finding similar chunks

## References

- **Requirements**: 4.1, 4.2, 4.3, 4.4, 4.5
- **Design Document**: `.kiro/specs/github-codebase-rag-assistant/design.md`
- **FAISS Documentation**: https://github.com/facebookresearch/faiss
- **sentence-transformers**: https://www.sbert.net/

## Future Enhancements

1. **Approximate Search**: Implement FAISS IVF/HNSW for large-scale search
2. **Query Expansion**: Add query rewriting for better retrieval
3. **Re-ranking**: Implement cross-encoder re-ranking for top results
4. **Caching**: Add Redis caching for frequent queries
5. **Analytics**: Track query performance and result quality
