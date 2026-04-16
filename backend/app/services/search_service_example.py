"""
Example usage of BM25SearchService.

This module demonstrates how to use the BM25 keyword search service
with various search modes and filters.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.search_service import BM25SearchService, SearchMode


async def example_basic_search(db: AsyncSession):
    """
    Example: Basic case-insensitive keyword search.
    
    This is the simplest way to search for keywords in code chunks.
    """
    service = BM25SearchService(db)
    
    # Simple search for "hello" in all repositories
    results = await service.search_simple(
        query="hello",
        top_k=10,
    )
    
    for result in results:
        print(f"File: {result.chunk.file_path}")
        print(f"Score: {result.score}")
        print(f"Matches: {len(result.matches)}")
        print(f"Content:\n{result.highlighted_content}\n")


async def example_exact_match_search(db: AsyncSession):
    """
    Example: Exact match search (case-sensitive).
    
    Use this when you need to find exact occurrences of a term.
    """
    service = BM25SearchService(db)
    
    results = await service.search(
        query="HelloWorld",
        top_k=10,
        mode=SearchMode.EXACT,
    )
    
    # Will only match "HelloWorld" exactly, not "helloworld" or "HELLOWORLD"
    for result in results:
        print(f"Found exact match in: {result.chunk.file_path}")


async def example_regex_search(db: AsyncSession):
    """
    Example: Regex pattern search.
    
    Use this for complex pattern matching like finding all function names
    that start with "get_" or "set_".
    """
    service = BM25SearchService(db)
    
    # Find all getter/setter functions
    results = await service.search(
        query=r"(get|set)_\w+",
        top_k=20,
        mode=SearchMode.REGEX,
    )
    
    for result in results:
        print(f"Found pattern in: {result.chunk.file_path}")
        for match in result.matches:
            print(f"  - {match.matched_text} at line {match.line_number}")


async def example_boolean_search(db: AsyncSession):
    """
    Example: Boolean query search.
    
    Use this to combine multiple search terms with AND, OR, NOT operators.
    """
    service = BM25SearchService(db)
    
    # Find code that has "async" AND "await" but NOT "sleep"
    results = await service.search(
        query="async AND await NOT sleep",
        top_k=10,
        mode=SearchMode.CASE_INSENSITIVE,
        use_boolean=True,
    )
    
    for result in results:
        print(f"Found in: {result.chunk.file_path}")


async def example_filtered_search(db: AsyncSession, repo_id: UUID):
    """
    Example: Search with filters.
    
    Use this to narrow down search results by repository, file type,
    directory, or programming language.
    """
    service = BM25SearchService(db)
    
    # Search only in Python files within the "src/" directory
    results = await service.search(
        query="class",
        top_k=10,
        repository_ids=[repo_id],
        file_extensions=[".py"],
        directory_paths=["src/"],
        languages=["python"],
    )
    
    for result in results:
        print(f"Found in: {result.chunk.file_path}")


async def example_multi_repository_search(db: AsyncSession, repo_ids: list[UUID]):
    """
    Example: Search across multiple repositories.
    
    Use this to find code patterns across different projects.
    """
    service = BM25SearchService(db)
    
    results = await service.search(
        query="authentication",
        top_k=20,
        repository_ids=repo_ids,
    )
    
    # Group results by repository
    by_repo = {}
    for result in results:
        repo_id = result.chunk.repository_id
        if repo_id not in by_repo:
            by_repo[repo_id] = []
        by_repo[repo_id].append(result)
    
    for repo_id, repo_results in by_repo.items():
        print(f"\nRepository {repo_id}: {len(repo_results)} results")


async def example_match_analysis(db: AsyncSession):
    """
    Example: Analyze match locations.
    
    Use this to understand where and how many times a term appears in code.
    """
    service = BM25SearchService(db)
    
    results = await service.search(
        query="import",
        top_k=5,
    )
    
    for result in results:
        print(f"\nFile: {result.chunk.file_path}")
        print(f"Total matches: {len(result.matches)}")
        
        # Group matches by line number
        by_line = {}
        for match in result.matches:
            if match.line_number not in by_line:
                by_line[match.line_number] = []
            by_line[match.line_number].append(match.matched_text)
        
        for line_num, matches in sorted(by_line.items()):
            print(f"  Line {line_num}: {', '.join(matches)}")


async def example_custom_highlighting(db: AsyncSession):
    """
    Example: Custom match highlighting.
    
    The default highlighting uses <<< >>> markers, but you can customize this.
    """
    service = BM25SearchService(db)
    
    results = await service.search(
        query="function",
        top_k=5,
    )
    
    for result in results:
        # Re-highlight with custom markers (e.g., for HTML)
        custom_highlighted = service._highlight_matches(
            result.chunk.content,
            result.matches,
            highlight_start="<mark>",
            highlight_end="</mark>",
        )
        print(custom_highlighted)


# API endpoint example
async def search_endpoint_example(
    db: AsyncSession,
    query: str,
    mode: str = "case_insensitive",
    use_boolean: bool = False,
    top_k: int = 10,
):
    """
    Example: How to use the search service in a FastAPI endpoint.
    
    This shows the typical pattern for integrating the search service
    into your API routes.
    """
    service = BM25SearchService(db)
    
    # Convert string mode to enum
    search_mode = SearchMode(mode)
    
    try:
        results = await service.search(
            query=query,
            top_k=top_k,
            mode=search_mode,
            use_boolean=use_boolean,
        )
        
        return {
            "results": [
                {
                    "chunk_id": str(result.chunk.id),
                    "file_path": result.chunk.file_path,
                    "score": result.score,
                    "matches": len(result.matches),
                    "highlighted_content": result.highlighted_content,
                }
                for result in results
            ],
            "total_results": len(results),
            "query": query,
        }
    except ValueError as e:
        # Handle invalid regex or mode
        return {"error": str(e)}, 400
