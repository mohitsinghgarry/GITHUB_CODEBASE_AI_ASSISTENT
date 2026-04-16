# Database Setup Guide

This guide explains how to set up and manage the PostgreSQL database for the GitHub Codebase RAG Assistant.

## Prerequisites

- PostgreSQL 14 or higher installed and running
- Python 3.11+ with virtual environment activated
- Environment variables configured in `.env.development`

## Database Schema

The application uses three main tables:

### 1. repositories
Stores GitHub repository metadata and indexing status.

```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    default_branch TEXT,
    last_commit_hash TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT,
    chunk_count INTEGER DEFAULT 0,
    index_path TEXT
);
```

### 2. ingestion_jobs
Tracks background ingestion job progress and status.

```sql
CREATE TABLE ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    stage TEXT,
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);
```

### 3. code_chunks
Stores indexed code segments with metadata.

```sql
CREATE TABLE code_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    language TEXT,
    content TEXT NOT NULL,
    embedding_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Setup Instructions

### 1. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE github_rag_dev;

# Create user (optional)
CREATE USER github_rag WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE github_rag_dev TO github_rag;

# Exit psql
\q
```

### 2. Configure Environment

Edit `.env.development` with your database credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/github_rag_dev
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5
```

### 3. Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

### 4. Verify Setup

```bash
# Run the test script
python test_migration.py
```

Expected output:
```
============================================================
Database Migration Test
============================================================
Testing database connection...
✓ Database connection successful

Testing table creation...
✓ Dropped existing tables
✓ Created all tables
✓ Tables created: code_chunks, ingestion_jobs, repositories
✓ All expected tables present

============================================================
✓ All tests passed!
============================================================
```

## Alembic Commands

### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Upgrade one version
alembic upgrade +1
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade all
alembic downgrade base
```

### View Migration History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Database Connection Management

The application uses SQLAlchemy's async engine with connection pooling:

```python
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

async def example_function(db: AsyncSession = Depends(get_db)):
    # Use the database session
    result = await db.execute(select(Repository))
    repositories = result.scalars().all()
    return repositories
```

### Connection Pool Settings

- **pool_size**: 10 (default) - Number of connections to maintain
- **max_overflow**: 5 (default) - Additional connections allowed beyond pool_size
- **pool_pre_ping**: True - Verify connections before use
- **pool_recycle**: 3600 seconds - Recycle connections after 1 hour

## Troubleshooting

### Connection Refused

```
Error: connection refused
```

**Solution**: Ensure PostgreSQL is running:
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Check status
pg_isready
```

### Authentication Failed

```
Error: password authentication failed
```

**Solution**: Verify credentials in `.env.development` match your PostgreSQL setup.

### Database Does Not Exist

```
Error: database "github_rag_dev" does not exist
```

**Solution**: Create the database:
```bash
createdb github_rag_dev
```

### Migration Conflicts

```
Error: Target database is not up to date
```

**Solution**: Check current version and apply pending migrations:
```bash
alembic current
alembic upgrade head
```

## Production Considerations

### 1. Connection Pooling

For production, increase pool size based on expected load:

```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### 2. SSL Connections

Enable SSL for production databases:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### 3. Backup Strategy

Set up regular backups:

```bash
# Backup
pg_dump github_rag_prod > backup_$(date +%Y%m%d).sql

# Restore
psql github_rag_prod < backup_20240115.sql
```

### 4. Monitoring

Monitor database performance:
- Connection pool usage
- Query execution time
- Table sizes and indexes
- Lock contention

### 5. Indexes

The schema includes indexes for common queries:
- `repositories.url` (unique)
- `repositories.status`
- `repositories.owner, name`
- `ingestion_jobs.repository_id, status`
- `code_chunks.repository_id`
- `code_chunks.file_path`
- `code_chunks.repository_id, file_path`

## Testing

Run database tests:

```bash
# Unit tests
pytest tests/unit/test_database_models.py -v

# Integration tests (requires running database)
pytest tests/integration/test_database.py -v
```

## Additional Resources

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
