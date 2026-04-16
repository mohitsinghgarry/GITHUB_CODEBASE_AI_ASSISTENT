# Task 2.15: Implement Ingestion Orchestration Service - Summary

## Overview

Implemented the `IngestionService` class in `app/services/ingestion_service.py` to orchestrate Celery task chains for repository ingestion. The service provides job creation, status tracking, retry logic, and incremental indexing support.

## Implementation Details

### Core Service: `IngestionService`

**Location**: `backend/app/services/ingestion_service.py`

**Key Methods**:

1. **`start_ingestion(repository_id, repository_url, auth_token, ssh_key_path)`**
   - Creates an `IngestionJob` record in the database
   - Triggers the Celery task chain using `create_ingestion_pipeline()`
   - Returns job information including job_id and celery_task_id
   - **Requirement**: 3.1 - Create Ingestion_Job and return immediately with job identifier

2. **`get_job_status(job_id)`**
   - Queries the database for current job status
   - Returns comprehensive job information including:
     - Status (pending, running, completed, failed)
     - Current stage (clone, read, chunk, embed, store)
     - Progress percentage (0-100)
     - Timestamps and error messages
   - **Requirement**: 3.2 - Allow users to query job status

3. **`retry_job(job_id)`**
   - Creates a new job for a failed job
   - Increments retry count
   - Preserves original job for history
   - **Requirement**: 3.5 - Store error details and allow retry

4. **`check_for_updates(repository_id)`**
   - Compares current commit hash with remote
   - Uses `RepositoryService.has_updates()` to detect changes
   - Returns tuple of (has_updates, latest_commit_hash)
   - **Requirement**: 2.9 - Support incremental indexing for repository updates

5. **`start_incremental_indexing(repository_id, auth_token, ssh_key_path)`**
   - Checks for repository updates
   - Triggers re-indexing if updates are detected
   - Currently triggers full re-indexing (incremental logic is a TODO)
   - **Requirements**: 2.9, 2.10 - Incremental indexing support

6. **`get_changed_files(repository_id, old_commit, new_commit)`**
   - Helper method for incremental indexing
   - Uses git diff to identify changed files
   - Returns list of file paths that have changed
   - **Requirement**: 2.10 - Re-execute only necessary stages for changed Code_Chunks

7. **`delete_chunks_for_files(repository_id, file_paths)`**
   - Helper method for incremental indexing
   - Deletes old chunks for files that have changed
   - Returns count of deleted chunks
   - **Requirement**: 2.10 - Re-execute only necessary stages for changed Code_Chunks

### Integration with Existing Components

**Celery Tasks Integration**:
- Uses `create_ingestion_pipeline()` from `app/jobs/tasks/ingestion_tasks.py`
- The pipeline creates a Celery chain of five tasks:
  1. `clone_repository`
  2. `read_source_files`
  3. `chunk_code_files`
  4. `generate_embeddings`
  5. `store_embeddings`

**Database Integration**:
- Uses `IngestionJob` ORM model for job tracking
- Uses `Repository` ORM model for repository metadata
- Uses `CodeChunk` ORM model for code chunk storage
- All database operations use async SQLAlchemy sessions

**Repository Service Integration**:
- Uses `RepositoryService` for git operations
- Leverages existing methods:
  - `repository_exists()` - Check if repo is cloned
  - `has_updates()` - Detect repository updates
  - `get_repository_path()` - Get local repo path

### Error Handling

**Custom Exceptions**:
- `IngestionServiceError` - Base exception for service errors
- `JobNotFoundError` - Raised when job is not found
- `RepositoryNotFoundError` - Raised when repository is not found

**Error Scenarios Handled**:
- Job creation failures
- Job not found
- Repository not found
- Non-failed job retry attempts
- Git diff failures
- Database operation failures

### Singleton Pattern

**Global Instance**:
```python
def get_ingestion_service() -> IngestionService:
    """Get the global ingestion service instance."""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
```

This ensures a single instance is used throughout the application.

## Testing

**Test File**: `backend/tests/unit/test_ingestion_service.py`

**Test Coverage**:
- ✅ Job creation and Celery pipeline triggering
- ✅ Job status retrieval
- ✅ Job not found error handling
- ✅ Job retry for failed jobs
- ✅ Error handling for non-failed job retry
- ✅ Repository update detection
- ✅ Incremental indexing trigger
- ✅ Skip indexing when up-to-date

**Test Framework**: pytest with async support

## Requirements Validation

### Requirement 2.9: Support incremental indexing for repository updates
✅ **Implemented**:
- `check_for_updates()` detects repository changes
- `start_incremental_indexing()` triggers re-indexing for updated repos
- `get_changed_files()` identifies changed files using git diff

### Requirement 2.10: Re-execute only necessary stages for changed Code_Chunks
⚠️ **Partially Implemented**:
- Helper methods `get_changed_files()` and `delete_chunks_for_files()` are implemented
- Full incremental indexing logic is marked as TODO
- Currently triggers full re-indexing (noted in code comments)
- Future implementation will:
  1. Pull latest changes
  2. Identify changed files using git diff
  3. Delete old chunks for changed files
  4. Create modified pipeline for only changed files
  5. Update FAISS index incrementally

### Requirement 3.1: Create Ingestion_Job and return immediately with job identifier
✅ **Implemented**:
- `start_ingestion()` creates job record
- Returns immediately with job_id and celery_task_id
- Celery pipeline runs asynchronously in background

### Requirement 3.2: Allow users to query job status
✅ **Implemented**:
- `get_job_status()` returns comprehensive job information
- Includes status, stage, progress, timestamps, and errors

### Requirement 3.3: Update job status to completed with success/failure indication
✅ **Implemented**:
- Status updates are handled by Celery tasks in `ingestion_tasks.py`
- Service provides status retrieval interface

### Requirement 3.5: Store error details and allow retry
✅ **Implemented**:
- Error messages stored in `IngestionJob.error_message`
- `retry_job()` creates new job for failed jobs
- Retry count tracked in `IngestionJob.retry_count`

## Future Enhancements

### 1. Full Incremental Indexing
**Current State**: Triggers full re-indexing when updates detected

**Future Implementation**:
- Implement incremental pipeline in Celery tasks
- Only process changed files
- Update FAISS index incrementally (add/remove vectors)
- Optimize for large repositories with frequent updates

### 2. Secure Credential Storage
**Current State**: Auth tokens not persisted

**Future Implementation**:
- Store encrypted auth tokens in database
- Support credential rotation
- Integrate with secrets management service

### 3. Job Scheduling
**Current State**: Manual job triggering

**Future Implementation**:
- Periodic update checks (cron-like scheduling)
- Webhook integration for GitHub push events
- Automatic re-indexing on repository updates

### 4. Progress Estimation
**Current State**: Progress percentage from Celery tasks

**Future Implementation**:
- Estimate time remaining based on repository size
- Historical data for better estimates
- Real-time progress updates via WebSocket

### 5. Job Cancellation
**Current State**: No cancellation support

**Future Implementation**:
- Cancel running jobs
- Clean up partial progress
- Revoke Celery tasks

## Files Created/Modified

### Created:
1. `backend/app/services/ingestion_service.py` - Main service implementation (650+ lines)
2. `backend/tests/unit/test_ingestion_service.py` - Unit tests (300+ lines)
3. `backend/TASK_2.15_SUMMARY.md` - This summary document

### Modified:
1. `backend/app/services/__init__.py` - Added exports for `IngestionService` and `get_ingestion_service`

## Usage Example

```python
from app.services.ingestion_service import get_ingestion_service

# Get service instance
service = get_ingestion_service()

# Start ingestion
job_info = await service.start_ingestion(
    repository_id=repo_id,
    repository_url="https://github.com/owner/repo",
    auth_token="ghp_xxx",
)
print(f"Job started: {job_info['job_id']}")

# Check status
status = await service.get_job_status(job_info['job_id'])
print(f"Status: {status['status']}, Progress: {status['progress_percent']}%")

# Retry failed job
if status['status'] == 'failed':
    retry_info = await service.retry_job(job_info['job_id'])
    print(f"Retry job started: {retry_info['job_id']}")

# Check for updates
has_updates, latest_commit = await service.check_for_updates(repo_id)
if has_updates:
    # Start incremental indexing
    incremental_job = await service.start_incremental_indexing(repo_id)
    print(f"Incremental indexing started: {incremental_job['job_id']}")
```

## Integration Points

### API Endpoints (Future)
The service is designed to be used by API endpoints:

```python
# POST /api/v1/repositories
@router.post("/repositories")
async def create_repository(repo_data: RepositoryCreate):
    # Create repository record
    # Call service.start_ingestion()
    pass

# GET /api/v1/jobs/{job_id}
@router.get("/jobs/{job_id}")
async def get_job_status(job_id: UUID):
    service = get_ingestion_service()
    return await service.get_job_status(job_id)

# POST /api/v1/jobs/{job_id}/retry
@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: UUID):
    service = get_ingestion_service()
    return await service.retry_job(job_id)

# POST /api/v1/repositories/{repo_id}/reindex
@router.post("/repositories/{repo_id}/reindex")
async def reindex_repository(repo_id: UUID):
    service = get_ingestion_service()
    return await service.start_incremental_indexing(repo_id)
```

## Conclusion

The `IngestionService` successfully implements the core orchestration logic for repository ingestion jobs. It provides a clean interface for job management, integrates seamlessly with existing Celery tasks and database models, and lays the foundation for incremental indexing support.

The service is production-ready for basic ingestion workflows, with clear paths for enhancement in incremental indexing, credential management, and job scheduling.
