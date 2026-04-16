# Vector Store Module

This module provides FAISS-based vector storage for per-repository code embeddings.

## Overview

The vector store module manages FAISS indices on a per-repository basis, with each repository having its own isolated index and metadata file. This design enables efficient updates, deletions, and searches while maintaining clear separation between repositories.

## Architecture

### Components

1. **VectorStoreMetadata**: Manages metadata for a FAISS index
   - Stores chunk information (file path, line numbers, language, content)
   - Tracks index statistics (chunk count, dimension, timestamps)
   - Provides JSON serialization/deserialization

2. **VectorStore**: Manages a single repository's FAISS index
   - Handles embedding addition and search operations
   - Maintains index-to-metadata mapping
   - Supports persistence to disk

3. **VectorStoreManager**: Manages multiple vector stores
   - Creates, loads, saves, and deletes stores
   - Provides singleton access pattern
   - Lists and queries store statistics

## Usage

### Basic Usage

```python
from app.core.vectorstore import get_vector_store_manager
from uuid import UUID

# Get the global manager instance
manager = get_vector_store_manager()

# Create a new store for a repository
repo_id = UUID("12345678-1234-5678-1234-567812345678")
store = manager.create_store(repo_id)

# Add embeddings with metadata
import numpy as np

embeddings = np.random.rand(10, 384).astype(np.float32)
chunks_metadata = [
    {
        "id": str(UUID("...")),
        "file_path": "src/main.py",
        "start_line": 1,
        "end_line": 10,
        "language": "python",
        "content": "def hello():\n    print('Hello')"
    }
    # ... 9 more chunks
]

indices = store.add_embeddings(embeddings, chunks_metadata)

# Save to disk
store.save()

# Search for similar code
query_embedding = np.random.rand(384).astype(np.float32)
indices, scores = store.search(query_embedding, top_k=5)

# Get chunk metadata for results
for idx, score in zip(indices, scores):
    chunk = store.get_chunk_metadata(idx)
    print(f"Score: {score:.4f}, File: {chunk['file_path']}")
```

### Loading Existing Stores

```python
# Load from disk
store = manager.load_store(repo_id)

# Or get with auto-load
store = manager.get_store(repo_id)

# Or get with auto-create if missing
store = manager.get_store(repo_id, create_if_missing=True)
```

### Managing Stores

```python
# Check if store exists
if manager.store_exists(repo_id):
    print("Store exists")

# List all stores
repo_ids = manager.list_stores()

# Get store statistics
stats = manager.get_store_stats(repo_id)
print(f"Vector count: {stats['vector_count']}")
print(f"Created at: {stats['created_at']}")

# Delete a store
manager.delete_store(repo_id)

# Save all loaded stores
manager.save_all_stores()
```

## Index Type

The module uses **FAISS IndexFlatIP** (Inner Product) for cosine similarity search:

- **IndexFlatIP**: Computes inner product between query and stored vectors
- **Cosine Similarity**: Assumes vectors are L2-normalized before storage
- **Exact Search**: No approximation, returns exact nearest neighbors
- **Memory**: Stores all vectors in RAM for fast search

### Why IndexFlatIP?

1. **Exact Results**: No approximation errors
2. **Simplicity**: No training required
3. **Cosine Similarity**: Natural metric for semantic similarity
4. **Small-Medium Scale**: Efficient for repositories with <1M chunks

For larger repositories, consider using approximate indices like:
- `IndexIVFFlat`: Inverted file index with exact search
- `IndexHNSWFlat`: Hierarchical Navigable Small World graph

## File Structure

Each repository has two files:

```
data/indices/
├── {repo_id}.faiss          # FAISS index binary
└── {repo_id}.metadata.json  # Chunk metadata JSON
```

### Metadata Format

```json
{
  "repository_id": "12345678-1234-5678-1234-567812345678",
  "chunk_count": 1523,
  "dimension": 384,
  "created_at": "2026-04-15T10:30:00.000000",
  "updated_at": "2026-04-15T10:35:00.000000",
  "chunks": [
    {
      "id": "chunk-uuid-1",
      "file_path": "src/main.py",
      "start_line": 1,
      "end_line": 10,
      "language": "python",
      "content": "def hello():\n    print('Hello')"
    }
    // ... more chunks
  ]
}
```

## Requirements Satisfied

- **2.7**: Store embeddings to a repository-specific FAISS_Index
- **2.8**: Create a separate FAISS_Index for each repository
- **2.13**: Persist the FAISS_Index to disk with repository metadata
- **14.1**: Persist all embeddings and metadata to disk

## Performance Considerations

### Memory Usage

- Each float32 vector: `dimension * 4 bytes`
- For 384-dim vectors: ~1.5 KB per vector
- 100K vectors: ~150 MB RAM
- 1M vectors: ~1.5 GB RAM

### Search Performance

- IndexFlatIP: O(n*d) where n=vectors, d=dimension
- 100K vectors, 384-dim: ~10-50ms per query
- 1M vectors, 384-dim: ~100-500ms per query

### Optimization Tips

1. **Batch Operations**: Use `add_embeddings()` with batches instead of single additions
2. **Normalize Vectors**: Ensure embeddings are L2-normalized for cosine similarity
3. **Limit top_k**: Use smaller top_k values for faster search
4. **Lazy Loading**: Only load stores when needed
5. **Periodic Saves**: Save stores periodically during ingestion

## Error Handling

The module raises specific exceptions:

- `ValueError`: Invalid input (wrong dimensions, empty data, etc.)
- `FileNotFoundError`: Index or metadata files not found
- `RuntimeError`: FAISS operations failed, save/load errors

Always wrap operations in try-except blocks:

```python
try:
    store = manager.load_store(repo_id)
except FileNotFoundError:
    print("Store not found, creating new one")
    store = manager.create_store(repo_id)
except RuntimeError as e:
    print(f"Failed to load store: {e}")
```

## Testing

See `tests/unit/test_vector_store.py` for comprehensive unit tests covering:

- Store creation and loading
- Embedding addition and search
- Metadata management
- Persistence and recovery
- Error handling

## Future Enhancements

1. **Approximate Indices**: Support for IVF and HNSW indices
2. **GPU Support**: FAISS GPU indices for faster search
3. **Incremental Updates**: Efficient updates without full rebuild
4. **Compression**: Quantization for reduced memory usage
5. **Distributed Storage**: Support for remote index storage (S3, GCS)
