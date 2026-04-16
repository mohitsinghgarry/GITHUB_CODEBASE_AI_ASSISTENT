"""
Example demonstrating multi-criteria filtering in search service.

This example shows how to use file extension, directory path, and programming
language filters in keyword, semantic, and hybrid search.

Requirements:
- 5.6: Support filtering by file extension, directory path, and programming language
"""

import asyncio
from uuid import UUID

from app.services.search_service import UnifiedSearchService, SearchMode
from app.database import get_async_session


async def example_keyword_search_with_filters():
    """Example: Keyword search with multi-criteria filtering."""
    print("\n=== Keyword Search with Multi-Criteria Filtering ===\n")
    
    async for session in get_async_session():
        search_service = UnifiedSearchService(db=session)
        
        # Example 1: Filter by file extension
        print("1. Search for 'authentication' in Python files only:")
        results = await search_service.search_keyword(
            query="authentication",
            top_k=5,
            file_extensions=[".py"],
        )
        print(f"   Found {len(results)} results in .py files\n")
        
        # Example 2: Filter by directory path
        print("2. Search for 'middleware' in src/ directory:")
        results = await search_service.search_keyword(
            query="middleware",
            top_k=5,
            directory_paths=["src/"],
        )
        print(f"   Found {len(results)} results in src/ directory\n")
        
        # Example 3: Filter by programming language
        print("3. Search for 'async' in JavaScript/TypeScript files:")
        results = await search_service.search_keyword(
            query="async",
            top_k=5,
            languages=["javascript", "typescript"],
        )
        print(f"   Found {len(results)} results in JS/TS files\n")
        
        # Example 4: Combine multiple filters
        print("4. Search for 'test' in Python files under tests/ directory:")
        results = await search_service.search_keyword(
            query="test",
            top_k=5,
            file_extensions=[".py"],
            directory_paths=["tests/"],
            languages=["python"],
        )
        print(f"   Found {len(results)} results matching all criteria\n")
        
        break


async def example_semantic_search_with_filters():
    """Example: Semantic search with multi-criteria filtering."""
    print("\n=== Semantic Search with Multi-Criteria Filtering ===\n")
    
    async for session in get_async_session():
        search_service = UnifiedSearchService(db=session)
        
        # Example 1: Filter by file extension
        print("1. Semantic search for 'database connection' in Python files:")
        results = await search_service.search_semantic(
            query="database connection",
            top_k=5,
            file_extensions=[".py"],
        )
        print(f"   Found {len(results)} results in .py files\n")
        
        # Example 2: Filter by directory and language
        print("2. Semantic search for 'API endpoint' in src/ directory (Python only):")
        results = await search_service.search_semantic(
            query="API endpoint",
            top_k=5,
            directory_paths=["src/", "app/"],
            languages=["python"],
        )
        print(f"   Found {len(results)} results in src/app directories\n")
        
        # Example 3: Multiple file extensions
        print("3. Semantic search for 'error handling' in Python and JavaScript:")
        results = await search_service.search_semantic(
            query="error handling",
            top_k=5,
            file_extensions=[".py", ".js", ".ts"],
            languages=["python", "javascript", "typescript"],
        )
        print(f"   Found {len(results)} results in Python/JS/TS files\n")
        
        break


async def example_hybrid_search_with_filters():
    """Example: Hybrid search with multi-criteria filtering."""
    print("\n=== Hybrid Search with Multi-Criteria Filtering ===\n")
    
    async for session in get_async_session():
        search_service = UnifiedSearchService(db=session)
        
        # Example 1: Hybrid search with file extension filter
        print("1. Hybrid search for 'authentication' in Python files:")
        results = await search_service.search_hybrid(
            query="authentication",
            top_k=5,
            file_extensions=[".py"],
        )
        print(f"   Found {len(results)} results in .py files")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['file_path']} (RRF: {result['rrf_score']:.3f})")
        print()
        
        # Example 2: Hybrid search with directory filter
        print("2. Hybrid search for 'API routes' in api/ directory:")
        results = await search_service.search_hybrid(
            query="API routes",
            top_k=5,
            directory_paths=["app/api/", "src/api/"],
        )
        print(f"   Found {len(results)} results in api directories")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['file_path']} (RRF: {result['rrf_score']:.3f})")
        print()
        
        # Example 3: Hybrid search with all filters combined
        print("3. Hybrid search for 'database query' in Python files under src/:")
        results = await search_service.search_hybrid(
            query="database query",
            top_k=5,
            file_extensions=[".py"],
            directory_paths=["src/", "app/"],
            languages=["python"],
        )
        print(f"   Found {len(results)} results matching all criteria")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['file_path']} (RRF: {result['rrf_score']:.3f})")
        print()
        
        break


async def example_filter_combinations():
    """Example: Various filter combinations."""
    print("\n=== Filter Combination Examples ===\n")
    
    async for session in get_async_session():
        search_service = UnifiedSearchService(db=session)
        
        # Example 1: Multiple file extensions
        print("1. Search in multiple file types (.py, .js, .ts):")
        results = await search_service.search_keyword(
            query="function",
            top_k=5,
            file_extensions=[".py", ".js", ".ts"],
        )
        print(f"   Found {len(results)} results\n")
        
        # Example 2: Multiple directories
        print("2. Search in multiple directories (src/, lib/, app/):")
        results = await search_service.search_keyword(
            query="import",
            top_k=5,
            directory_paths=["src/", "lib/", "app/"],
        )
        print(f"   Found {len(results)} results\n")
        
        # Example 3: Multiple languages
        print("3. Search in multiple languages (Python, JavaScript, TypeScript):")
        results = await search_service.search_keyword(
            query="class",
            top_k=5,
            languages=["python", "javascript", "typescript"],
        )
        print(f"   Found {len(results)} results\n")
        
        # Example 4: All filters combined
        print("4. Search with all filters (extensions + directories + languages):")
        results = await search_service.search_keyword(
            query="test",
            top_k=5,
            file_extensions=[".py", ".js"],
            directory_paths=["tests/", "test/"],
            languages=["python", "javascript"],
        )
        print(f"   Found {len(results)} results matching all criteria\n")
        
        break


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Multi-Criteria Filtering Examples")
    print("=" * 70)
    
    await example_keyword_search_with_filters()
    await example_semantic_search_with_filters()
    await example_hybrid_search_with_filters()
    await example_filter_combinations()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
