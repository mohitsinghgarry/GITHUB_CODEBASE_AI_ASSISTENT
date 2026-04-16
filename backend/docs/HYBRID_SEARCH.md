# Hybrid Search with Reciprocal Rank Fusion (RRF)

## Overview

The GitHub Codebase RAG Assistant implements hybrid search that combines BM25 keyword search and vector semantic search using Reciprocal Rank Fusion (RRF). This approach provides the best of both worlds: the precision of keyword matching and the semantic understanding of vector search.

## Architecture

### Components

1. **BM25 Keyword Search**: Text-based search using the BM25 ranking algorithm
   - Excellent for exact term matching
   - Supports boolean operators (AND, OR, NOT)
   - Provides match highlighting

2. **Vector Semantic Search**: Embedding-based similarity search using FAISS
   - Captures semantic meaning beyond exact keywords
   - Handles synonyms and related concepts
   - Uses cosine similarity for ranking

3. **Reciprocal Rank Fusion (RRF)**: Combines results from both search methods
   - Rank-based fusion (independent of score scales)
   - Robust to different scoring distributions
   - Simple and effective

## Reciprocal Rank Fusion (RRF)

### Formula

For each document `d`, the RRF score is calculated as:

```
RRF(d) = Σ 1 / (k + rank(d))
```

Where:
- `k` is a constant (typically 60, as recommended in literature)
- `rank(d)` is the rank of document `d` in each result list (1-indexed)
- The sum is over all result lists (BM25 and vector search)

### Why RRF?

RRF has several advantages over score-based fusion:

1. **Scale Independence**: Works with different scoring scales (BM25 scores vs. cosine similarity)
2. **Distribution Independence**: Doesn't depend on score distributions
3. **Simplicity**: No need to normalize or calibrate scores
4. **Robustness**: Proven effective in information retrieval research
5. **Rank-Based**: Only depends on the relative ordering of results

### Example

Consider a query that returns:

**BM25 Results** (ranked by relevance):
1. Document A (score: 10.5)
2. Document B (score: 8.2)
3. Document C (score: 5.1)

**Vector Results** (ranked by similarity):
1. Document C (score: 0.92)
2. Document A (score: 0.87)
3. Document D (score: 0.81)

**RRF Scores** (with k=60):
- Document A: 1/(60+1) + 1/(60+2) = 0.0164 + 0.0161 = **0.0325**
- Document B: 1/(60+2) = **0.0161**
- Document C: 1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = **0.0323**
- Document D: 1/(60+3) = **0.0159**

**Final Ranking**: A > C > B > D

Notice how Document A, which ranked high in both searches, gets the highest RRF score.

## Implementation

### API Usage

```python
from app.services.search_service import UnifiedSearchService

# Initialize service
service = UnifiedSearchService(db=db_session)

# Perform hybrid search
results = await service.search_hybrid(
    query="authentication middleware",
    top_k=10,
    repository_ids=[repo_id],
    rrf_k=60,  # RRF constant (default: 60)
    retrieval_multiplier=2,  # Retrieve 2x results initially
)

# Results contain:
# - chunk: Code chunk object
# - bm25_score: BM25 relevance score
# - bm25_rank: Rank in BM25 results
# - vector_score: Vector similarity score
# - vector_rank: Rank in vector results
# - rrf_score: Combined RRF score
# - matches: Match locations (from BM25)
# - highlighted_content: Content with matches highlighted
```

### Parameters

- **query** (str): Search query
- **top_k** (int): Number of results to return (default: 10)
- **repository_ids** (Optional[List[UUID]]): Filter by repository IDs
- **rrf_k** (int): RRF constant (default: 60)
  - Higher values reduce the impact of top-ranked results
  - Lower values give more weight to top results
  - Recommended: 60 (from literature)
- **retrieval_multiplier** (int): Multiplier for initial retrieval (default: 2)
  - Retrieves `top_k * retrieval_multiplier` results from each search
  - Provides more candidates for fusion
  - Improves result quality

### Result Structure

Each result is a dictionary containing:

```python
{
    "chunk": CodeChunk,           # SQLAlchemy model
    "chunk_id": UUID,              # Chunk identifier
    "repository_id": UUID,         # Repository identifier
    "file_path": str,              # File path
    "start_line": int,             # Start line number
    "end_line": int,               # End line number
    "language": str,               # Programming language
    "content": str,                # Code content
    "bm25_score": float,           # BM25 score (0 if not in BM25 results)
    "bm25_rank": Optional[int],    # Rank in BM25 results (None if not present)
    "vector_score": float,         # Vector similarity score (0 if not in vector results)
    "vector_rank": Optional[int],  # Rank in vector results (None if not present)
    "rrf_score": float,            # Combined RRF score
    "matches": List[MatchLocation], # Match locations (from BM25)
    "highlighted_content": str,    # Content with matches highlighted
}
```

## Performance Considerations

### Retrieval Multiplier

The `retrieval_multiplier` parameter controls how many results are retrieved from each search method before fusion:

- **Higher values** (e.g., 3-5):
  - More candidates for fusion
  - Better result quality
  - Higher computational cost
  - Recommended for important queries

- **Lower values** (e.g., 1-2):
  - Fewer candidates
  - Faster execution
  - May miss some relevant results
  - Recommended for quick searches

### RRF Constant (k)

The `k` parameter controls the weight distribution:

- **k = 60** (recommended):
  - Balanced weight distribution
  - Proven effective in research
  - Good default for most use cases

- **Lower k** (e.g., 10-30):
  - More weight to top-ranked results
  - Sharper ranking differences
  - Use when top results are highly reliable

- **Higher k** (e.g., 100-200):
  - More uniform weight distribution
  - Flatter ranking differences
  - Use when result quality varies

## Testing

The implementation includes comprehensive tests:

### Unit Tests

```bash
# Test RRF calculation
pytest tests/unit/test_hybrid_search.py::TestReciprocalRankFusion -v

# Test score normalization
pytest tests/unit/test_hybrid_search.py::TestReciprocalRankFusion::test_normalize_scores_basic -v

# Test RRF formula
pytest tests/unit/test_hybrid_search.py::TestReciprocalRankFusion::test_rrf_formula -v
```

### Integration Tests

```bash
# Test hybrid search integration
pytest tests/unit/test_hybrid_search.py::TestHybridSearchIntegration -v
```

## References

1. Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). "Reciprocal rank fusion outperforms condorcet and individual rank learning methods." SIGIR '09.

2. Benham, R., & Culpepper, J. S. (2017). "Risk-reward trade-offs in rank fusion." ADCS '17.

3. Montague, M., & Aslam, J. A. (2002). "Condorcet fusion for improved retrieval." CIKM '02.

## Requirements Satisfied

- **Requirement 5.5**: Merge and rank results from BM25 and vector search by relevance
  - ✅ Implements Reciprocal Rank Fusion (RRF)
  - ✅ Combines BM25 and vector search results
  - ✅ Ranks by combined RRF score
  - ✅ Preserves metadata from both searches

## Future Enhancements

1. **Adaptive k**: Automatically tune `k` based on query characteristics
2. **Weighted RRF**: Allow different weights for BM25 vs. vector search
3. **Query-Dependent Fusion**: Use different fusion strategies based on query type
4. **Learning to Rank**: Train a model to optimize fusion weights
5. **Multi-Stage Retrieval**: Add re-ranking stage after RRF fusion
