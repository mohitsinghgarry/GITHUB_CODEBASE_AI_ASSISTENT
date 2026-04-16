# Embeddings Module

This module provides the embedding service for converting text into dense vector representations using sentence-transformers models.

## Overview

The `EmbeddingService` class wraps a sentence-transformers model and provides methods for embedding single texts, batches of texts, and queries. It handles device configuration (CPU/GPU/MPS) and model loading.

## Features

- **Single Text Embedding**: Generate embeddings for individual texts
- **Batch Embedding**: Efficiently process multiple texts in batches
- **Query Embedding**: Specialized method for query text (API consistency)
- **Device Support**: Automatic device configuration (CPU, CUDA, MPS)
- **Normalization**: Optional L2 normalization of embedding vectors
- **Singleton Pattern**: Global service instance for efficient resource usage

## Usage

### Basic Usage

```python
from app.core.embeddings import get_embedding_service

# Get the global embedding service instance
service = get_embedding_service()

# Embed a single text
text = "def hello_world():\n    print('Hello, World!')"
embedding = service.embed_text(text)
print(embedding.shape)  # (384,)

# Embed a batch of texts
texts = [
    "def foo():\n    pass",
    "class Bar:\n    pass",
    "import numpy as np",
]
embeddings = service.embed_batch(texts)
print(embeddings.shape)  # (3, 384)

# Embed a query
query = "how to implement authentication"
query_embedding = service.embed_query(query)
print(query_embedding.shape)  # (384,)
```

### Custom Configuration

```python
from app.core.embeddings import EmbeddingService

# Create a custom service instance
service = EmbeddingService(
    model_name="sentence-transformers/all-mpnet-base-v2",
    device="cuda",
    batch_size=64
)

# Use the custom service
embedding = service.embed_text("example text")
```

### Device Configuration

The service automatically configures the device based on availability:

```python
# Request CUDA (falls back to CPU if unavailable)
service = EmbeddingService(device="cuda")

# Request MPS for Apple Silicon (falls back to CPU if unavailable)
service = EmbeddingService(device="mps")

# Explicitly use CPU
service = EmbeddingService(device="cpu")
```

## Configuration

The embedding service uses the following configuration from `app/core/config.py`:

- `embedding_model`: Model name (default: "sentence-transformers/all-MiniLM-L6-v2")
- `embedding_dimension`: Vector dimension (default: 384)
- `embedding_batch_size`: Batch size for processing (default: 32)
- `embedding_device`: Device for inference (default: "cpu")

## API Reference

### EmbeddingService

#### Methods

- `embed_text(text: str, normalize: bool = True) -> np.ndarray`
  - Generate embedding for a single text
  - Returns: Embedding vector of shape (dimension,)

- `embed_batch(texts: List[str], batch_size: Optional[int] = None, normalize: bool = True, show_progress: bool = False) -> np.ndarray`
  - Generate embeddings for a batch of texts
  - Returns: Array of embeddings of shape (len(texts), dimension)

- `embed_query(query: str, normalize: bool = True) -> np.ndarray`
  - Generate embedding optimized for query text
  - Returns: Query embedding vector of shape (dimension,)

- `get_dimension() -> int`
  - Get the embedding dimension

- `get_model_name() -> str`
  - Get the model name

- `get_device() -> str`
  - Get the device being used for inference

- `get_max_sequence_length() -> int`
  - Get the maximum sequence length supported by the model

### Global Functions

- `get_embedding_service(...) -> EmbeddingService`
  - Get the global embedding service instance (singleton)

- `reload_embedding_service(...) -> EmbeddingService`
  - Reload the embedding service with new parameters

## Implementation Details

### Model Loading

The service loads the sentence-transformers model on initialization. The model is cached in memory for efficient reuse.

### Device Selection

The service automatically selects the best available device:
1. If CUDA is requested and available, use CUDA
2. If MPS is requested and available, use MPS
3. Otherwise, fall back to CPU

### Batch Processing

Batch embedding processes texts in configurable batch sizes to balance memory usage and performance. Empty texts are filtered out and replaced with zero vectors in the output.

### Normalization

By default, embeddings are L2-normalized to unit length. This is recommended for cosine similarity search. Normalization can be disabled by setting `normalize=False`.

## Testing

Run the simple test script to verify the implementation:

```bash
cd backend
python test_embedder_simple.py
```

Run the full test suite:

```bash
cd backend
pytest tests/unit/test_embedder.py -v
```

## Requirements

- Python 3.11+
- sentence-transformers
- torch
- numpy

## Performance Considerations

- **GPU Acceleration**: Use CUDA or MPS for faster inference on large batches
- **Batch Size**: Adjust batch size based on available memory
- **Model Selection**: Smaller models (e.g., MiniLM) are faster but less accurate than larger models (e.g., MPNet)

## Error Handling

The service raises appropriate exceptions for common errors:
- `ValueError`: Empty text or invalid parameters
- `RuntimeError`: Model loading failure or inference errors

## Future Enhancements

- Support for custom embedding models
- Caching of frequently embedded texts
- Async embedding generation
- Model quantization for faster inference
