"""
Simple test script to verify the embedding service works.

This script can be run directly without pytest to verify the implementation.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.core.embeddings import EmbeddingService
    
    print("✓ Successfully imported EmbeddingService")
    
    # Test initialization
    print("\nTesting initialization...")
    service = EmbeddingService(device="cpu")
    print(f"✓ Initialized service: {service}")
    print(f"  - Model: {service.get_model_name()}")
    print(f"  - Device: {service.get_device()}")
    print(f"  - Dimension: {service.get_dimension()}")
    print(f"  - Max sequence length: {service.get_max_sequence_length()}")
    
    # Test single text embedding
    print("\nTesting single text embedding...")
    text = "def hello_world():\n    print('Hello, World!')"
    embedding = service.embed_text(text)
    print(f"✓ Generated embedding for text")
    print(f"  - Shape: {embedding.shape}")
    print(f"  - Type: {embedding.dtype}")
    print(f"  - First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    print("\nTesting batch embedding...")
    texts = [
        "def foo():\n    pass",
        "class Bar:\n    pass",
        "import numpy as np",
    ]
    embeddings = service.embed_batch(texts)
    print(f"✓ Generated embeddings for batch")
    print(f"  - Shape: {embeddings.shape}")
    print(f"  - Type: {embeddings.dtype}")
    
    # Test query embedding
    print("\nTesting query embedding...")
    query = "how to implement authentication in Python"
    query_embedding = service.embed_query(query)
    print(f"✓ Generated embedding for query")
    print(f"  - Shape: {query_embedding.shape}")
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
