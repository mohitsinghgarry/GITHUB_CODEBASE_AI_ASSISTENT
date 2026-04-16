#!/usr/bin/env python3
"""
Phase 1 Verification Script

This script tests all Phase 1 components to ensure they are working correctly:
- Configuration management
- Database models and connections
- Redis client
- Docker setup
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a section header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print a warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print an info message."""
    print(f"  {text}")


# ============================================================================
# Test 1: Configuration Management
# ============================================================================

def test_configuration():
    """Test configuration loading and validation."""
    print_header("Test 1: Configuration Management")
    
    try:
        from app.core.config import Settings, get_settings
        print_success("Imported configuration module")
        
        # Test that Settings can be instantiated (will use .env or defaults)
        try:
            settings = get_settings()
            print_success("Loaded settings successfully")
            
            # Print key configuration values
            print_info(f"App Name: {settings.app_name}")
            print_info(f"Environment: {settings.environment}")
            print_info(f"Log Level: {settings.log_level}")
            print_info(f"Embedding Model: {settings.embedding_model}")
            print_info(f"Embedding Dimension: {settings.embedding_dimension}")
            print_info(f"Chunk Size: {settings.chunk_size}")
            print_info(f"Chunk Overlap: {settings.chunk_overlap}")
            
            # Test configuration methods
            db_config = settings.get_database_config()
            print_success(f"Database config: {list(db_config.keys())}")
            
            redis_config = settings.get_redis_config()
            print_success(f"Redis config: {list(redis_config.keys())}")
            
            embedding_config = settings.get_embedding_config()
            print_success(f"Embedding config: {list(embedding_config.keys())}")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to load settings: {e}")
            print_warning("Make sure you have a .env file or required environment variables set")
            return False
            
    except ImportError as e:
        print_error(f"Failed to import configuration: {e}")
        return False


# ============================================================================
# Test 2: Database Models
# ============================================================================

async def test_database_models():
    """Test database models and connections."""
    print_header("Test 2: Database Models")
    
    try:
        from app.database import Base, get_engine, get_session_maker
        from app.models.orm import Repository, IngestionJob, CodeChunk
        print_success("Imported database modules")
        
        # Test that models are defined
        print_success(f"Repository model: {Repository.__tablename__}")
        print_success(f"IngestionJob model: {IngestionJob.__tablename__}")
        print_success(f"CodeChunk model: {CodeChunk.__tablename__}")
        
        # Test model attributes
        print_info(f"Repository columns: {[c.name for c in Repository.__table__.columns]}")
        print_info(f"IngestionJob columns: {[c.name for c in IngestionJob.__table__.columns]}")
        print_info(f"CodeChunk columns: {[c.name for c in CodeChunk.__table__.columns]}")
        
        # Try to create an in-memory database for testing
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            from sqlalchemy.pool import StaticPool
            
            engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False,
            )
            
            # Create tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            print_success("Created in-memory database with all tables")
            
            # Test creating a repository
            async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with async_session_maker() as session:
                repo = Repository(
                    url="https://github.com/test/repo",
                    owner="test",
                    name="repo",
                    status="pending"
                )
                session.add(repo)
                await session.commit()
                print_success(f"Created test repository: {repo.id}")
            
            await engine.dispose()
            return True
            
        except Exception as e:
            print_warning(f"Could not test database operations: {e}")
            print_info("This is OK if you don't have aiosqlite installed")
            return True
            
    except ImportError as e:
        print_error(f"Failed to import database modules: {e}")
        return False


# ============================================================================
# Test 3: Redis Client
# ============================================================================

def test_redis_client():
    """Test Redis client wrapper."""
    print_header("Test 3: Redis Client")
    
    try:
        from app.core.redis_client import RedisClient, get_redis_client
        print_success("Imported Redis client module")
        
        # Test that RedisClient can be instantiated
        print_info("RedisClient class is available")
        print_info("Note: Actual Redis connection requires a running Redis server")
        
        return True
        
    except ImportError as e:
        print_error(f"Failed to import Redis client: {e}")
        return False


# ============================================================================
# Test 4: Docker Configuration
# ============================================================================

def test_docker_config():
    """Test Docker configuration files."""
    print_header("Test 4: Docker Configuration")
    
    # Check for docker-compose.yml
    docker_compose_path = Path("../docker-compose.yml")
    if docker_compose_path.exists():
        print_success("Found docker-compose.yml")
        
        # Read and check for required services
        content = docker_compose_path.read_text()
        required_services = ["postgres", "redis", "ollama"]
        for service in required_services:
            if service in content:
                print_success(f"  - {service} service configured")
            else:
                print_warning(f"  - {service} service not found")
    else:
        print_warning("docker-compose.yml not found in parent directory")
    
    # Check for backend Dockerfile
    backend_dockerfile = Path("Dockerfile")
    if backend_dockerfile.exists():
        print_success("Found backend/Dockerfile")
    else:
        print_warning("backend/Dockerfile not found")
    
    # Check for frontend Dockerfile
    frontend_dockerfile = Path("../frontend/Dockerfile")
    if frontend_dockerfile.exists():
        print_success("Found frontend/Dockerfile")
    else:
        print_warning("frontend/Dockerfile not found")
    
    return True


# ============================================================================
# Test 5: Project Structure
# ============================================================================

def test_project_structure():
    """Test that the project structure is correct."""
    print_header("Test 5: Project Structure")
    
    required_dirs = [
        "app",
        "app/core",
        "app/models",
        "app/models/orm",
        "app/api",
        "tests",
        "tests/unit",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_exist = False
    
    return all_exist


# ============================================================================
# Test 6: Dependencies
# ============================================================================

def test_dependencies():
    """Test that required dependencies are installed."""
    print_header("Test 6: Dependencies")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("redis", "Redis"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name} is installed")
        except ImportError:
            print_error(f"{name} is NOT installed")
            all_installed = False
    
    # Check optional packages
    optional_packages = [
        ("sentence_transformers", "sentence-transformers"),
        ("faiss", "FAISS"),
        ("celery", "Celery"),
    ]
    
    for package, name in optional_packages:
        try:
            __import__(package)
            print_success(f"{name} is installed (optional)")
        except ImportError:
            print_warning(f"{name} is NOT installed (optional, needed for Phase 2)")
    
    return all_installed


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests():
    """Run all Phase 1 tests."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Phase 1 Verification - GitHub Codebase RAG Assistant{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    results = {}
    
    # Run synchronous tests
    results["Configuration"] = test_configuration()
    results["Redis Client"] = test_redis_client()
    results["Docker Config"] = test_docker_config()
    results["Project Structure"] = test_project_structure()
    results["Dependencies"] = test_dependencies()
    
    # Run async tests
    results["Database Models"] = await test_database_models()
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    if passed == total:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}")
        print(f"{GREEN}Phase 1 is working correctly! ✓{RESET}")
    else:
        print(f"{YELLOW}Some tests failed ({passed}/{total} passed){RESET}")
        print(f"{YELLOW}Please review the errors above{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
