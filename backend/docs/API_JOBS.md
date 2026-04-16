# Job Management API Endpoints

This document describes the job management API endpoints for tracking and managing ingestion jobs.

## Overview

The job management endpoints allow you to:
- Query the status and progress of ingestion jobs
- Retry failed ingestion jobs
- Track estimated time remaining for running jobs

## Endpoints

### GET /api/v1/jobs/{job_id}

Get the current status and progress of an ingestion job.

**Path Parameters:**
- `job_id` (UUID, required): The unique identifier of the ingestion job

**Response (200 OK):**
```json
{
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "repository_id": "660e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "stage": "chunk",
    "progress_percent": 50,
    "started_at": "2026-04-16T10:30:00Z",
    "completed_at": null,
    "error_message": null,
    "retry_count": 0
  },
  "estimated_time_remaining": 600
}
```

**Job Status Values:**
- `pending`: Job is queued and waiting to start
- `running`: Job is currently executing
- `completed`: Job finished successfully
- `failed`: Job failed with an error

**Pipeline Stages:**
- `clone`: Cloning the repository from GitHub
- `read`: Reading source files from the repository
- `chunk`: Splitting code files into chunks
- `embed`: Generating embeddings for chunks
- `store`: Storing embeddings in FAISS index

**Response Fields:**
- `job`: Job details including status, stage, and progress
- `estimated_time_remaining`: Estimated seconds until completion (null if not calculable)

**Error Responses:**

404 Not Found:
```json
{
  "detail": {
    "error": "Job not found",
    "message": "Ingestion job with ID {job_id} does not exist",
    "details": [
      {
        "field": "job_id",
        "message": "No job found with ID {job_id}"
      }
    ]
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

---

### POST /api/v1/jobs/{job_id}/retry

Retry a failed ingestion job by creating a new job.

**Path Parameters:**
- `job_id` (UUID, required): The unique identifier of the failed job to retry

**Response (201 Created):**
```json
{
  "message": "Retry job created successfully for repository test/repo",
  "old_job_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_job_id": "770e8400-e29b-41d4-a716-446655440000",
  "repository_id": "660e8400-e29b-41d4-a716-446655440000"
}
```

**Response Fields:**
- `message`: Success message
- `old_job_id`: ID of the failed job
- `new_job_id`: ID of the newly created retry job
- `repository_id`: ID of the repository being indexed

**Error Responses:**

404 Not Found (Job doesn't exist):
```json
{
  "detail": {
    "error": "Job not found",
    "message": "Ingestion job with ID {job_id} does not exist",
    "details": [
      {
        "field": "job_id",
        "message": "No job found with ID {job_id}"
      }
    ]
  }
}
```

409 Conflict (Job is not failed):
```json
{
  "detail": {
    "error": "Job is not in failed state",
    "message": "Job {job_id} cannot be retried (current status: running)",
    "details": [
      {
        "field": "status",
        "message": "Only failed jobs can be retried. Current status: running"
      }
    ]
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/retry
```

---

## Usage Examples

### Monitoring Job Progress

Poll the job status endpoint to track progress:

```python
import httpx
import asyncio

async def monitor_job(job_id: str):
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
            data = response.json()
            
            job = data["job"]
            status = job["status"]
            progress = job["progress_percent"]
            stage = job["stage"]
            
            print(f"Status: {status} | Stage: {stage} | Progress: {progress}%")
            
            if status in ["completed", "failed"]:
                break
            
            await asyncio.sleep(5)  # Poll every 5 seconds

# Run
asyncio.run(monitor_job("550e8400-e29b-41d4-a716-446655440000"))
```

### Retrying Failed Jobs

Automatically retry failed jobs:

```python
import httpx

async def retry_if_failed(job_id: str):
    async with httpx.AsyncClient() as client:
        # Check job status
        response = await client.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
        data = response.json()
        
        if data["job"]["status"] == "failed":
            # Retry the job
            retry_response = await client.post(
                f"http://localhost:8000/api/v1/jobs/{job_id}/retry"
            )
            retry_data = retry_response.json()
            
            print(f"Retrying job. New job ID: {retry_data['new_job_id']}")
            return retry_data["new_job_id"]
        else:
            print(f"Job is not failed (status: {data['job']['status']})")
            return None
```

---

## Integration with Repository Endpoints

Jobs are created automatically when you add or re-index a repository:

```bash
# Add a repository (creates a job)
curl -X POST http://localhost:8000/api/v1/repositories \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/owner/repo"}'

# Response includes job_id
{
  "repository": {...},
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Repository owner/repo added successfully. Ingestion job started."
}

# Monitor the job
curl http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
```

---

## Requirements Validation

These endpoints validate the following requirements:

- **3.1**: Create an Ingestion_Job and return immediately with a job identifier
- **3.2**: Allow users to query the job status
- **3.3**: Update the job status to completed with success or failure indication
- **3.5**: Store error details and allow retry when an Ingestion_Job fails
- **3.6**: Provide progress updates including percentage complete and estimated time remaining
- **10.1**: Expose RESTful endpoints for job management
- **10.2**: Validate all incoming requests and return appropriate HTTP status codes

---

## Testing

Run the test suite:

```bash
cd backend
pytest tests/api/test_jobs_endpoints.py -v
```

Manual testing with test data:

```bash
# Create test data
python test_jobs_manual.py

# Test the endpoints (server must be running)
# Use the job IDs printed by the script

# Clean up test data
python test_jobs_manual.py cleanup
```
