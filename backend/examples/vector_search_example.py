"""
Example usage of vector semantic search functionality.

This example demonstrates how to use the SemanticSearchRetriever and
VectorSearchService to perform semantic code search.
"""

import asyncio
from uuid import UUID

from app.core.retrieval.retriever import SemanticSearchRetriever
from app.services.search_service import VectorSearchService, UnifiedSearchService


async def example_semantic_search():
    """Example: Basic semantic search."""
    print("=" * 60)
    print("Example 1: Basic Semantic Search")
    print("=" * 60)
    
    # Create retriever
    retriever = SemanticSearchRetriever()
    
    # Perform search
    query = "authentication middleware function"
    results = retriever.search(
        query=query,
        top_k=5,
    )
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.file_path}:{result.start_line}-{result.end_line}")
        print(f"   Language: {result.language}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Content preview: {result.content[:100]}...")
        print()


async def example_filtered_search():
    """Example: Semantic search with repository filtering."""
    print("=" * 60)
    print("Example 2: Filtered Semantic Search")
    print("=" * 60)
    
    # Create retriever
    retriever = SemanticSearchRetriever()
    
    # Example repository IDs (replace with actual UUIDs)
    repo_ids = [
        UUID("12345678-1234-5678-1234-567812345678"),
        UUID("87654321-4321-8765-4321-876543218765"),
    ]
    
    # Perform filtered search
    query = "database connection pool"
    results = retriever.search(
        query=query,
        top_k=10,
        repository_ids=repo_ids,
    )
    
    print(f"\nQuery: {query}")
    print(f"Repositories: {len(repo_ids)}")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.file_path} (repo: {result.repository_id[:8]}...)")
        print(f"   Score: {result.score:.4f}")
        print()


async def example_threshold_search():
    """Example: Semantic search with score threshold."""
    print("=" * 60)
    print("Example 3: Search with Score Threshold")
    print("=" * 60)
    
    # Create retriever
    retriever = SemanticSearchRetriever()
    
    # Perform search with threshold
    query = "error handling try catch"
    results = retriever.search_with_threshold(
        query=query,
        top_k=20,
        score_threshold=0.7,  # Only return results with score >= 0.7
    )
    
    print(f"\nQuery: {query}")
    print(f"Score threshold: 0.7")
    print(f"Found {len(results)} high-quality results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.file_path}:{result.start_line}")
        print(f"   Score: {result.score:.4f}")
        print()


async def example_vector_search_service():
    """Example: Using VectorSearchService."""
    print("=" * 60)
    print("Example 4: VectorSearchService")
    print("=" * 60)
    
    # Create service
    service = VectorSearchService()
    
    # Perform search
    query = "API endpoint handler"
    results = await service.search_simple(
        query=query,
        top_k=5,
    )
    
    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.file_path}")
        print(f"   Score: {result.score:.4f}")
        print()


async def example_unified_search():
    """Example: Using UnifiedSearchService for semantic search."""
    print("=" * 60)
    print("Example 5: UnifiedSearchService - Semantic Mode")
    print("=" * 60)
    
    # Note: This example requires a database session
    # In a real application, you would get this from FastAPI dependency injection
    
    print("\nThis example requires a database session.")
    print("In a FastAPI endpoint, you would use:")
    print("""
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
    """)


async def example_similar_chunks():
    """Example: Finding similar code chunks."""
    print("=" * 60)
    print("Example 6: Finding Similar Chunks")
    print("=" * 60)
    
    # Create retriever
    retriever = SemanticSearchRetriever()
    
    # Example chunk and repository IDs (replace with actual UUIDs)
    chunk_id = "12345678-1234-5678-1234-567812345678"
    repo_id = UUID("87654321-4321-8765-4321-876543218765")
    
    try:
        # Find similar chunks
        results = retriever.get_similar_chunks(
            chunk_id=chunk_id,
            repository_id=repo_id,
            top_k=5,
        )
        
        print(f"\nReference chunk: {chunk_id}")
        print(f"Found {len(results)} similar chunks:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.file_path}:{result.start_line}")
            print(f"   Score: {result.score:.4f}")
            print()
    
    except ValueError as e:
        print(f"\nError: {e}")
        print("(This is expected if the chunk/repository doesn't exist)")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Vector Semantic Search Examples")
    print("=" * 60 + "\n")
    
    # Run examples
    asyncio.run(example_semantic_search())
    asyncio.run(example_filtered_search())
    asyncio.run(example_threshold_search())
    asyncio.run(example_vector_search_service())
    asyncio.run(example_unified_search())
    asyncio.run(example_similar_chunks())
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
