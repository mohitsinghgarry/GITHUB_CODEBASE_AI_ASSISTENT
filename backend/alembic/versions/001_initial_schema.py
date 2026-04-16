"""Initial schema with repositories, ingestion_jobs, and code_chunks tables

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with repositories, ingestion_jobs, and code_chunks tables."""
    
    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('owner', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('default_branch', sa.Text(), nullable=True),
        sa.Column('last_commit_hash', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('index_path', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    
    # Create indexes for repositories table
    op.create_index('idx_repo_owner_name', 'repositories', ['owner', 'name'])
    op.create_index('idx_repo_status', 'repositories', ['status'])
    op.create_index(op.f('ix_repositories_url'), 'repositories', ['url'], unique=True)
    
    # Create ingestion_jobs table
    op.create_table(
        'ingestion_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, server_default='pending'),
        sa.Column('stage', sa.Text(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for ingestion_jobs table
    op.create_index('idx_job_repo_status', 'ingestion_jobs', ['repository_id', 'status'])
    op.create_index('idx_job_status', 'ingestion_jobs', ['status'])
    op.create_index(op.f('ix_ingestion_jobs_repository_id'), 'ingestion_jobs', ['repository_id'])
    
    # Create code_chunks table
    op.create_table(
        'code_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('language', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for code_chunks table
    op.create_index('idx_chunks_repo', 'code_chunks', ['repository_id'])
    op.create_index('idx_chunks_file', 'code_chunks', ['file_path'])
    op.create_index('idx_chunks_repo_file', 'code_chunks', ['repository_id', 'file_path'])
    op.create_index(op.f('ix_code_chunks_file_path'), 'code_chunks', ['file_path'])
    op.create_index(op.f('ix_code_chunks_repository_id'), 'code_chunks', ['repository_id'])


def downgrade() -> None:
    """Drop all tables and indexes."""
    
    # Drop code_chunks table and its indexes
    op.drop_index(op.f('ix_code_chunks_repository_id'), table_name='code_chunks')
    op.drop_index(op.f('ix_code_chunks_file_path'), table_name='code_chunks')
    op.drop_index('idx_chunks_repo_file', table_name='code_chunks')
    op.drop_index('idx_chunks_file', table_name='code_chunks')
    op.drop_index('idx_chunks_repo', table_name='code_chunks')
    op.drop_table('code_chunks')
    
    # Drop ingestion_jobs table and its indexes
    op.drop_index(op.f('ix_ingestion_jobs_repository_id'), table_name='ingestion_jobs')
    op.drop_index('idx_job_status', table_name='ingestion_jobs')
    op.drop_index('idx_job_repo_status', table_name='ingestion_jobs')
    op.drop_table('ingestion_jobs')
    
    # Drop repositories table and its indexes
    op.drop_index(op.f('ix_repositories_url'), table_name='repositories')
    op.drop_index('idx_repo_status', table_name='repositories')
    op.drop_index('idx_repo_owner_name', table_name='repositories')
    op.drop_table('repositories')
