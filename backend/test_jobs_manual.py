#!/usr/bin/env python
"""
Manual test script for job management endpoints.

This script demonstrates the job management API endpoints:
- GET /api/v1/jobs/{job_id} - Get job status
- POST /api/v1/jobs/{job_id}/retry - Retry failed job

Run this script with the FastAPI server running to test the endpoints.
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.database import get_session_maker
from app.models.orm.repository import Repository
from app.models.orm.ingestion_job import IngestionJob


async def setup_test_data():
    """Create test data for manual testing."""
    session_maker = get_session_maker()
    
    async with session_maker() as session:
        # Create a test repository
        repository = Repository(
            url="https://github.com/test/manual-test-repo",
            owner="test",
            name="manual-test-repo",
            status="pending",
        )
        session.add(repository)
        await session.commit()
        await session.refresh(repository)
        
        # Create a running job
        running_job = IngestionJob(
            repository_id=repository.id,
            status="running",
            stage="chunk",
            progress_percent=50,
            started_at=datetime.utcnow(),
        )
        session.add(running_job)
        
        # Create a failed job
        failed_job = IngestionJob(
            repository_id=repository.id,
            status="failed",
            stage="clone",
            progress_percent=10,
            error_message="Git clone failed: connection timeout",
            retry_count=0,
        )
        session.add(failed_job)
        
        await session.commit()
        await session.refresh(running_job)
        await session.refresh(failed_job)
        
        print("✅ Test data created successfully!")
        print(f"\n📊 Repository ID: {repository.id}")
        print(f"🔄 Running Job ID: {running_job.id}")
        print(f"❌ Failed Job ID: {failed_job.id}")
        print("\n🧪 Test the endpoints:")
        print(f"   GET  http://localhost:8000/api/v1/jobs/{running_job.id}")
        print(f"   GET  http://localhost:8000/api/v1/jobs/{failed_job.id}")
        print(f"   POST http://localhost:8000/api/v1/jobs/{failed_job.id}/retry")
        print("\n💡 Example curl commands:")
        print(f"   curl http://localhost:8000/api/v1/jobs/{running_job.id}")
        print(f"   curl -X POST http://localhost:8000/api/v1/jobs/{failed_job.id}/retry")


async def cleanup_test_data():
    """Clean up test data."""
    session_maker = get_session_maker()
    
    async with session_maker() as session:
        # Find and delete test repository
        result = await session.execute(
            select(Repository).where(Repository.url == "https://github.com/test/manual-test-repo")
        )
        repository = result.scalar_one_or_none()
        
        if repository:
            await session.delete(repository)
            await session.commit()
            print("✅ Test data cleaned up successfully!")
        else:
            print("ℹ️  No test data found to clean up")


async def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        await cleanup_test_data()
    else:
        await setup_test_data()


if __name__ == "__main__":
    asyncio.run(main())
