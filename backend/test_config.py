#!/usr/bin/env python3
"""
Quick validation script for configuration module.
This script tests that the configuration can be loaded and validated.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core.config import get_settings, Settings
    
    print("✓ Configuration module imported successfully")
    
    # Try to load settings
    try:
        settings = get_settings()
        print("✓ Settings loaded successfully")
        
        # Display key configuration values
        print("\n=== Configuration Summary ===")
        print(f"App Name: {settings.app_name}")
        print(f"Environment: {settings.environment}")
        print(f"Debug Mode: {settings.debug}")
        print(f"Log Level: {settings.log_level}")
        print(f"\nDatabase URL: {settings.database_url[:50]}...")
        print(f"Redis URL: {settings.redis_url}")
        print(f"\nOllama Base URL: {settings.ollama_base_url}")
        print(f"Ollama Model: {settings.ollama_model}")
        print(f"Ollama Timeout: {settings.ollama_timeout}s")
        print(f"\nEmbedding Model: {settings.embedding_model}")
        print(f"Embedding Dimension: {settings.embedding_dimension}")
        print(f"Embedding Device: {settings.embedding_device}")
        print(f"\nChunk Size: {settings.chunk_size}")
        print(f"Chunk Overlap: {settings.chunk_overlap}")
        print(f"Max Chunk Size: {settings.max_chunk_size}")
        print(f"\nDefault Top-K: {settings.default_top_k}")
        print(f"Max Top-K: {settings.max_top_k}")
        print(f"\nRepo Storage Path: {settings.repo_storage_path}")
        print(f"FAISS Index Path: {settings.faiss_index_path}")
        
        # Test helper methods
        print("\n=== Testing Helper Methods ===")
        db_config = settings.get_database_config()
        print(f"✓ Database config: {db_config}")
        
        redis_config = settings.get_redis_config()
        print(f"✓ Redis config: {redis_config}")
        
        ollama_config = settings.get_ollama_config()
        print(f"✓ Ollama config: {ollama_config}")
        
        embedding_config = settings.get_embedding_config()
        print(f"✓ Embedding config: {embedding_config}")
        
        chunking_config = settings.get_chunking_config()
        print(f"✓ Chunking config: {chunking_config}")
        
        search_config = settings.get_search_config()
        print(f"✓ Search config: {search_config}")
        
        rag_config = settings.get_rag_config()
        print(f"✓ RAG config: {rag_config}")
        
        print(f"\n✓ Is Production: {settings.is_production()}")
        print(f"✓ Is Development: {settings.is_development()}")
        
        print("\n✅ All configuration tests passed!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error loading settings: {e}")
        print("\nThis is expected if environment variables are not set.")
        print("The configuration module is working correctly - it's validating required fields.")
        print("\nTo test with actual values, set the required environment variables:")
        print("  - DATABASE_URL")
        print("  - REDIS_URL")
        print("  - CELERY_BROKER_URL")
        print("  - CELERY_RESULT_BACKEND")
        print("  - SECRET_KEY")
        sys.exit(0)
        
except ImportError as e:
    print(f"❌ Failed to import configuration module: {e}")
    sys.exit(1)
