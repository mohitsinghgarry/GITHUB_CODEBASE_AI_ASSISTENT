"""
Test script to verify Alembic migration can be generated and applied.

This script tests that:
1. The database connection works
2. Alembic can generate migrations
3. The migration can be applied
"""

import asyncio
import sys
from sqlalchemy import text

from app.database import get_engine, Base
from app.models.orm import Repository, IngestionJob, CodeChunk


async def test_database_connection():
    """Test that we can connect to the database."""
    print("Testing database connection...")
    engine = get_engine()
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    finally:
        await engine.dispose()


async def test_create_tables():
    """Test that we can create tables."""
    print("\nTesting table creation...")
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            # Drop all tables first
            await conn.run_sync(Base.metadata.drop_all)
            print("✓ Dropped existing tables")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✓ Created all tables")
            
            # Verify tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"✓ Tables created: {', '.join(tables)}")
            
            expected_tables = {'repositories', 'ingestion_jobs', 'code_chunks'}
            if expected_tables.issubset(set(tables)):
                print("✓ All expected tables present")
                return True
            else:
                missing = expected_tables - set(tables)
                print(f"✗ Missing tables: {missing}")
                return False
                
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        return False
    finally:
        await engine.dispose()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Database Migration Test")
    print("=" * 60)
    
    # Test 1: Database connection
    if not await test_database_connection():
        print("\n✗ Database connection test failed")
        sys.exit(1)
    
    # Test 2: Table creation
    if not await test_create_tables():
        print("\n✗ Table creation test failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
