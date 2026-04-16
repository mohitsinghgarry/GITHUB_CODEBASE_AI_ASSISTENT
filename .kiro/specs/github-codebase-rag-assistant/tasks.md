# Implementation Plan: GitHub Codebase RAG Assistant

## Overview

This implementation plan breaks down the GitHub Codebase RAG Assistant into discrete, incremental coding tasks organized into 5 clear phases. The system is a production-grade RAG application with FastAPI backend, Next.js frontend, PostgreSQL metadata storage, Redis caching, FAISS vector indices, and Ollama LLM integration.

## Tasks

- [x] Phase 1: Foundation
  - [x] 1.1 Set up project structure and core infrastructure
    - Create directory structure for backend (FastAPI) and frontend (Next.js)
    - Initialize Python virtual environment and install core dependencies (FastAPI, SQLAlchemy, Celery, Redis, sentence-transformers, FAISS, Ollama client)
    - Initialize Next.js project with TypeScript, TailwindCSS, and shadcn/ui
    - Set up environment configuration files (.env.development, .env.production)
    - _Requirements: 10.1, 10.2, 11.1, 13.1_

  - [x] 1.2 Write property test for configuration validation
    - **Property 27: Configuration Validation**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.6, 13.8**

  - [x] 1.3 Create Pydantic settings model for configuration management
    - Implement `app/core/config.py` with all configuration fields (database URL, Redis URL, Ollama settings, embedding model, chunk size/overlap)
    - Add validation for required fields, value ranges, and type checking
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.8_

  - [x] 1.4 Set up PostgreSQL database schema and models
    - Create SQLAlchemy models for `repositories`, `ingestion_jobs`, and `code_chunks` tables
    - Implement database connection management with connection pooling
    - Create Alembic migration scripts for initial schema
    - _Requirements: 14.2, 14.5_

  - [x] 1.5 Implement Redis client wrapper
    - Create `app/core/redis_client.py` with connection pool management
    - Implement helper methods for session storage, caching, and job status
    - Add TTL configuration for different data types
    - _Requirements: 6.6, 14.2_

  - [x] 1.6 Write unit tests for database models and Redis client
    - Test model validation, relationships, and constraints
    - Test Redis connection handling and data serialization
    - _Requirements: 14.2_

  - [x] 1.7 Create Docker Compose configuration
    - Implement `docker-compose.yml` with services for PostgreSQL, Redis, Ollama, NGINX, Prometheus, and Grafana
    - Configure volumes for persistent data (postgres_data, redis_data, faiss_indices, repo_storage, ollama_models)
    - Set up service dependencies and health checks
    - _Requirements: 10.1, 11.1, 14.1, 14.2_

  - [x] 1.8 Create backend Dockerfile
    - Write `backend/Dockerfile` with Python 3.11 base image
    - Install dependencies and copy application code
    - Configure entrypoint for FastAPI server
    - _Requirements: 10.1_

  - [x] 1.9 Create frontend Dockerfile
    - Write `frontend/Dockerfile` with Node.js base image
    - Install dependencies and build Next.js application
    - Configure entrypoint for Next.js server
    - _Requirements: 11.1_

  - [x] 1.10 Checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

- [x] Phase 2: Backend Core
  - [x] 2.1 Create embedding service wrapper
    - Implement `app/core/embeddings.py` using sentence-transformers
    - Add methods for single text embedding, batch embedding, and query embedding
    - Configure model loading with CPU/GPU support
    - _Requirements: 2.6_

  - [ ]* 2.2 Write unit tests for embedding service
    - Test embedding generation for various text inputs
    - Test batch processing and error handling
    - _Requirements: 2.6_

  - [x] 2.3 Implement FAISS vector store manager
    - Create `app/core/vector_store.py` for per-repository FAISS index management
    - Implement index creation, loading, saving, and search operations
    - Add metadata file management (JSON) for chunk information
    - Support IndexFlatIP for cosine similarity search
    - _Requirements: 2.7, 2.8, 2.13, 14.1_

  - [ ]* 2.4 Write property test for index persistence round-trip
    - **Property 7: Index Persistence Round-Trip**
    - **Validates: Requirements 2.13**

  - [x] 2.5 Create repository loader service
    - Implement `app/services/repository_service.py` with GitHub cloning logic
    - Add URL validation, authentication support (PAT, SSH keys)
    - Implement repository metadata extraction (owner, name, branch, commit hash)
    - Add update detection and incremental pull logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 2.6 Implement file filtering logic
    - Create file filter to exclude binary files, dependencies (node_modules, venv, target), and build artifacts
    - Add language detection for source files
    - _Requirements: 1.7, 2.3, 2.11_

  - [ ]* 2.7 Write property test for file filtering
    - **Property 1: File Filtering Preserves Source Code**
    - **Validates: Requirements 1.7, 2.3**

  - [ ]* 2.8 Write property test for language detection
    - **Property 6: Language Detection Consistency**
    - **Validates: Requirements 2.11**

  - [ ]* 2.9 Write unit tests for repository loader
    - Test URL validation with valid and invalid formats
    - Test authentication error handling
    - Test metadata extraction
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.10 Create code chunking service
    - Implement `app/services/chunking_service.py` with configurable chunk size and overlap
    - Add language-aware chunking that respects function/class boundaries
    - Preserve file path, line numbers, and language metadata for each chunk
    - _Requirements: 2.4, 2.5_

  - [ ]* 2.11 Write property test for chunking content preservation
    - **Property 4: Chunking Preserves Content**
    - **Validates: Requirements 2.4**

  - [ ]* 2.12 Write property test for chunking metadata preservation
    - **Property 5: Chunking Metadata Preservation**
    - **Validates: Requirements 2.5**

  - [ ]* 2.13 Write unit tests for chunking edge cases
    - Test small files (< chunk size)
    - Test exact chunk size boundaries
    - Test empty files
    - _Requirements: 2.4, 2.5_

  - [x] 2.14 Create Celery task definitions for ingestion stages
    - Implement `app/workers/ingestion_tasks.py` with five tasks: clone_repository, read_source_files, chunk_code_files, generate_embeddings, store_embeddings
    - Add progress tracking and status updates to PostgreSQL
    - Implement error handling and stage failure logic
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.12_

  - [x] 2.15 Implement ingestion orchestration service
    - Create `app/services/ingestion_service.py` to orchestrate Celery task chains
    - Add job creation, status tracking, and retry logic
    - Implement incremental indexing for repository updates
    - _Requirements: 2.9, 2.10, 3.1, 3.2, 3.3, 3.5_

  - [ ]* 2.16 Write property test for repository index isolation
    - **Property 2: Repository Index Isolation**
    - **Validates: Requirements 2.8, 8.4**

  - [ ]* 2.17 Write property test for incremental indexing efficiency
    - **Property 3: Incremental Indexing Efficiency**
    - **Validates: Requirements 2.9, 2.10**

  - [ ]* 2.18 Write integration tests for ingestion pipeline
    - Test complete pipeline with test repository
    - Test stage failure and recovery
    - Test progress tracking
    - _Requirements: 2.1-2.13, 3.1-3.7_

  - [x] 2.19 Implement BM25 keyword search
    - Create `app/services/search_service.py` with BM25 implementation using rank-bm25 library
    - Add support for exact match, case-insensitive match, and regex patterns
    - Implement boolean operators (AND, OR, NOT)
    - Add match location highlighting
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 2.20 Implement vector semantic search
    - Add FAISS similarity search with configurable top-K
    - Implement query embedding generation
    - Add repository filtering support
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 2.21 Implement hybrid search with RRF fusion
    - Combine BM25 and vector search results using Reciprocal Rank Fusion
    - Implement score normalization and ranking
    - _Requirements: 5.5_

  - [x] 2.22 Add multi-criteria filtering
    - Implement filters for file extension, directory path, and programming language
    - Support combining multiple filters
    - _Requirements: 5.6_

  - [ ]* 2.23 Write property test for repository filtering
    - **Property 8: Repository Filtering Correctness**
    - **Validates: Requirements 4.5, 8.3**

  - [ ]* 2.24 Write property test for top-K result selection
    - **Property 9: Top-K Result Selection**
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 2.25 Write property test for result structure completeness
    - **Property 10: Result Structure Completeness**
    - **Validates: Requirements 4.6**

  - [ ]* 2.26 Write property test for hybrid search score fusion
    - **Property 11: Hybrid Search Score Fusion**
    - **Validates: Requirements 5.5**

  - [ ]* 2.27 Write property test for boolean query evaluation
    - **Property 12: Boolean Query Evaluation**
    - **Validates: Requirements 5.4**

  - [ ]* 2.28 Write property test for multi-criteria filtering
    - **Property 13: Multi-Criteria Filtering**
    - **Validates: Requirements 5.6**

  - [ ]* 2.29 Write property test for match location accuracy
    - **Property 14: Match Location Accuracy**
    - **Validates: Requirements 5.3**

  - [ ]* 2.30 Write unit tests for search edge cases
    - Test empty query, no results, single result
    - Test invalid repository IDs
    - Test filter combinations
    - _Requirements: 4.7, 5.1-5.6_

  - [x] 2.31 Create Ollama client wrapper
    - Implement `app/services/llm_service.py` with Ollama HTTP client
    - Add methods for generate (streaming and non-streaming) and list_models
    - Implement timeout handling and exponential backoff retry
    - Add system prompt configuration for explanation modes (Beginner, Technical, Interview)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [x] 2.32 Implement chat service with RAG prompt construction
    - Create `app/services/chat_service.py` for session management and prompt construction
    - Implement RAG prompt builder that includes system instruction, retrieved chunks, and user question
    - Add citation linking to source chunks
    - Implement session history management with Redis
    - Add token limit truncation logic
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 2.33 Write property test for RAG prompt construction completeness
    - **Property 15: RAG Prompt Construction Completeness**
    - **Validates: Requirements 6.3**

  - [ ]* 2.34 Write property test for citation linking correctness
    - **Property 16: Citation Linking Correctness**
    - **Validates: Requirements 6.5**

  - [ ]* 2.35 Write property test for session history preservation
    - **Property 17: Session History Preservation**
    - **Validates: Requirements 6.6**

  - [ ]* 2.36 Write property test for token limit truncation
    - **Property 18: Token Limit Truncation**
    - **Validates: Requirements 6.7**

  - [ ]* 2.37 Write property test for system prompt inclusion
    - **Property 25: System Prompt Inclusion**
    - **Validates: Requirements 9.4**

  - [ ]* 2.38 Write property test for exponential backoff retry pattern
    - **Property 26: Exponential Backoff Retry Pattern**
    - **Validates: Requirements 9.5**

  - [ ]* 2.39 Write integration tests for Ollama integration
    - Test model inference with test Ollama instance
    - Test streaming responses
    - Test error handling (connection refused, timeout, model not found)
    - _Requirements: 9.1-9.8_

  - [x] 2.40 Create code review service
    - Implement `app/services/review_service.py` for code analysis
    - Add structured feedback generation with issue descriptions, severity levels, and line numbers
    - Implement diff parsing and analysis for pull requests
    - Add context extraction for changed lines
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ]* 2.41 Write property test for review feedback structure
    - **Property 19: Review Feedback Structure**
    - **Validates: Requirements 7.3**

  - [ ]* 2.42 Write property test for diff parsing completeness
    - **Property 20: Diff Parsing Completeness**
    - **Validates: Requirements 7.5**

  - [ ]* 2.43 Write property test for diff context extraction
    - **Property 21: Diff Context Extraction**
    - **Validates: Requirements 7.6**

  - [ ]* 2.44 Write unit tests for code review service
    - Test review request handling
    - Test improvement suggestion generation
    - Test diff analysis
    - _Requirements: 7.1-7.7_

  - [x] 2.45 Checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

- [ ] Phase 3: API Layer
  - [x] 3.1 Create repository management endpoints
    - Implement `app/api/repositories.py` with POST /repositories, GET /repositories, GET /repositories/{id}, DELETE /repositories/{id}, POST /repositories/{id}/reindex
    - Add request validation using Pydantic models
    - Implement error handling and appropriate HTTP status codes
    - _Requirements: 8.1, 8.2, 8.3, 8.5, 8.7, 10.1, 10.2, 10.3_

  - [x] 3.2 Create search endpoints
    - Implement `app/api/search.py` with POST /search/semantic, POST /search/keyword, POST /search/hybrid
    - Add request validation and repository filtering
    - _Requirements: 4.1-4.7, 5.1-5.6, 10.1, 10.2_

  - [x] 3.3 Create chat endpoints
    - Implement `app/api/chat.py` with POST /chat (streaming), GET /chat/sessions/{id}, DELETE /chat/sessions/{id}
    - Add streaming response support using FastAPI StreamingResponse
    - _Requirements: 6.1-6.8, 10.1, 10.2_

  - [x] 3.4 Create job management endpoints
    - Implement `app/api/jobs.py` with GET /jobs/{job_id}, POST /jobs/{job_id}/retry
    - Add job status tracking and progress updates
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6, 10.1, 10.2_

  - [x] 3.5 Create code review endpoints
    - Implement `app/api/review.py` with POST /review, POST /improve
    - _Requirements: 7.1-7.7, 10.1, 10.2_

  - [x] 3.6 Create health and monitoring endpoints
    - Implement `app/api/health.py` with GET /health, GET /metrics, GET /models
    - Add dependency health checks (PostgreSQL, Redis, Ollama, FAISS)
    - Implement Prometheus metrics export
    - _Requirements: 9.8, 10.8, 10.9, 12.1-12.10_

  - [ ]* 3.7 Write property test for repository metadata completeness
    - **Property 22: Repository Metadata Completeness**
    - **Validates: Requirements 8.2**

  - [ ]* 3.8 Write property test for cascade deletion completeness
    - **Property 23: Cascade Deletion Completeness**
    - **Validates: Requirements 8.5**

  - [ ]* 3.9 Write property test for repository namespace uniqueness
    - **Property 24: Repository Namespace Uniqueness**
    - **Validates: Requirements 8.6**

  - [ ]* 3.10 Write integration tests for API endpoints
    - Test all endpoints with valid and invalid inputs
    - Test authentication and authorization
    - Test error responses
    - _Requirements: 10.1-10.9_

  - [x] 3.11 Create main application entry point
    - Implement `app/main.py` with FastAPI app initialization
    - Register all routers (repositories, search, chat, jobs, review, health)
    - Add CORS middleware configuration
    - Add rate limiting middleware
    - Add request logging middleware
    - Implement lifespan events for startup and shutdown
    - _Requirements: 10.1, 10.4, 10.5, 10.6, 10.8, 10.9_

  - [x] 3.12 Implement error handling middleware
    - Add global exception handlers for common errors
    - Implement consistent error response format
    - Add request ID tracking for debugging
    - _Requirements: 10.2, 10.3, 15.7_

  - [ ]* 3.13 Write integration tests for middleware
    - Test CORS configuration
    - Test rate limiting
    - Test error handling
    - _Requirements: 10.4, 10.5, 10.6_

  - [x] 3.14 Set up structured logging
    - Configure Python logging with JSON formatter
    - Add contextual logging (request ID, user ID, repository ID)
    - Implement log level configuration
    - _Requirements: 12.3, 12.4, 12.5_

  - [x] 3.15 Implement Prometheus metrics
    - Add metrics for request count, latency, error rate
    - Add metrics for ingestion job queue length and processing time
    - Add metrics for FAISS query latency and Ollama inference time
    - _Requirements: 12.1, 12.2, 12.6, 12.7_

  - [ ]* 3.16 Write unit tests for logging and metrics
    - Test log formatting
    - Test metric collection
    - _Requirements: 12.1-12.10_

  - [x] 3.17 Implement retry logic with exponential backoff
    - Create utility function for retryable operations
    - Add configuration for max attempts and delays
    - _Requirements: 9.5, 15.1, 15.2_

  - [x] 3.18 Implement circuit breaker pattern
    - Create circuit breaker class for external service calls
    - Add configuration for failure threshold and timeout
    - _Requirements: 15.6_

  - [x] 3.19 Implement graceful degradation
    - Add fallback logic for Redis unavailability (disable caching)
    - Add fallback logic for Ollama unavailability (disable chat, keep search)
    - _Requirements: 15.5_

  - [ ]* 3.20 Write unit tests for resilience patterns
    - Test retry logic with mock failures
    - Test circuit breaker state transitions
    - Test graceful degradation scenarios
    - _Requirements: 15.1-15.8_

  - [x] 3.21 Checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

- [ ] Phase 4: Frontend
  - [ ] 4.1 Fetch and analyze RepoMind Assistant Stitch design
    - Access the RepoMind Assistant Stitch project
    - Export design specifications (colors, typography, spacing, components)
    - Take screenshots of all screens for reference
    - Document component states (hover, active, disabled, loading)
    - Note animation behaviors and transitions
    - Create design reference document
    - _Requirements: 11.1, 11.7_

  - [ ] 4.2 Set up Next.js App Router structure
    - Create app directory with layout.tsx and page.tsx
    - Set up routing for /repositories, /repositories/[id], /chat, /search
    - Configure TailwindCSS with custom design tokens from Stitch
    - Install and configure framer-motion for animations
    - Import shadcn/ui components
    - _Requirements: 11.1, 11.7_

  - [ ] 4.3 Configure design system from Stitch tokens
    - Create `lib/design-tokens.ts` with extracted values from RepoMind Assistant
    - Update colors (background, text, accent, semantic) from Stitch palette
    - Update spacing system from Stitch measurements
    - Update typography (fonts, sizes, weights) from Stitch
    - Update border radius and shadows from Stitch
    - Create `lib/animation-presets.ts` with framer-motion variants
    - Configure `tailwind.config.ts` with RepoMind Assistant theme
    - _Requirements: 11.7_

  - [ ] 4.3 Create Zustand stores for state management
    - Implement `store/repositoryStore.ts` for repository state
    - Implement `store/chatStore.ts` for chat session state
    - Implement `store/searchStore.ts` for search state
    - Implement `store/settingsStore.ts` for theme and preferences
    - _Requirements: 11.10_

  - [ ] 4.4 Create API client wrapper
    - Implement `lib/api.ts` with typed API client for all backend endpoints
    - Add error handling and request/response interceptors
    - _Requirements: 11.9_

  - [ ] 4.5 Implement layout components
    - Create `AppShell.tsx` with responsive layout structure
    - Create `Sidebar.tsx` with navigation and repo selector
    - Create `Header.tsx` with breadcrumbs and user menu
    - Create `CommandPalette.tsx` with ⌘K quick actions
    - Add framer-motion animations (fadeIn, slideIn)
    - _Requirements: 11.1, 11.7_

  - [ ] 4.6 Implement common components
    - Create `LoadingSkeleton.tsx` with pulse animation
    - Create `EmptyState.tsx` with icon and action button
    - Create `ErrorBanner.tsx` with retry functionality
    - Create `StatusBadge.tsx` with status-based colors
    - Create `CopyButton.tsx` with success feedback
    - Add framer-motion animations (scaleIn, slideUp)
    - _Requirements: 11.9_

  - [ ] 4.7 Create repository management components
    - Create `RepoInputCard.tsx` with URL validation and loading states
    - Create `IndexingProgress.tsx` with 5-stage progress indicator
    - Create `RepoStats.tsx` with stats cards (files, chunks, languages)
    - Create `RepoCard.tsx` for repository list items
    - Create `LanguageChart.tsx` with visual language breakdown
    - Map Stitch designs to React components with TailwindCSS
    - Add hover and tap animations with framer-motion
    - _Requirements: 11.1, 11.2_

  - [ ] 4.8 Create repository pages
    - Implement `app/load/page.tsx` with RepoInputCard
    - Implement `app/repos/[repoId]/page.tsx` with dashboard
    - Implement `app/repos/[repoId]/layout.tsx` with sidebar
    - Add real-time progress updates via polling
    - Add delete confirmation modal with animations
    - _Requirements: 11.1, 11.2_

  - [ ] 4.9 Create chat interface components
    - Create `ChatPanel.tsx` with full-height layout
    - Create `MessageList.tsx` with auto-scroll and virtualization
    - Create `UserMessage.tsx` with right-aligned bubble
    - Create `AssistantMessage.tsx` with left-aligned bubble
    - Create `CodeSnippetCard.tsx` with syntax highlighting
    - Create `SourceCitations.tsx` with clickable file chips
    - Create `ChatInput.tsx` with send button and controls
    - Create `ModeSelector.tsx` for explanation modes
    - Create `SuggestedQuestions.tsx` for empty state
    - Map Stitch chat designs to components
    - Add message animations (slideIn, staggerContainer)
    - _Requirements: 11.3, 11.4_

  - [ ] 4.10 Implement chat page
    - Implement `app/repos/[repoId]/chat/page.tsx`
    - Add streaming response display with real-time updates
    - Implement session management (new, load, delete)
    - Add explanation mode persistence
    - _Requirements: 11.3_

  - [ ] 4.11 Create file explorer components
    - Create `FileTree.tsx` with hierarchical structure
    - Create `FileNode.tsx` with expand/collapse animations
    - Create `FileHeader.tsx` with file metadata
    - Create `FileSummaryCard.tsx` with AI-generated summary
    - Create `LanguageFilter.tsx` with multi-select
    - Add tree animations (slideIn, fadeIn)
    - _Requirements: 11.1_

  - [ ] 4.12 Implement file explorer pages
    - Implement `app/repos/[repoId]/files/page.tsx`
    - Implement `app/repos/[repoId]/files/[fileId]/page.tsx`
    - Add file content viewer with syntax highlighting
    - _Requirements: 11.1_

  - [ ] 4.13 Create search interface components
    - Create `SearchBar.tsx` with autocomplete
    - Create `SearchModeToggle.tsx` for Semantic/Keyword/Hybrid
    - Create `SearchResultCard.tsx` with file info and code preview
    - Create `SearchFilters.tsx` for language and directory filters
    - Map Stitch search designs to components
    - Add result animations (scaleIn, staggerContainer)
    - _Requirements: 11.5, 11.6_

  - [ ] 4.14 Implement search page
    - Implement `app/repos/[repoId]/search/page.tsx`
    - Add tabbed interface with mode switching
    - Add result export functionality (JSON/CSV)
    - Add "View in context" navigation
    - _Requirements: 11.5, 11.6_

  - [ ] 4.15 Create code review components
    - Create `CodeViewer.tsx` with syntax highlighting and copy button
    - Create `CodeEditor.tsx` for input code
    - Create `ReviewResultCard.tsx` with issue details
    - Create `ReviewSummaryBar.tsx` with severity counts
    - Create `DiffViewer.tsx` for before/after comparison
    - Create `ImprovementPanel.tsx` with refactored code
    - Add code animations (fadeIn, slideUp)
    - _Requirements: 11.1_

  - [ ] 4.16 Implement code review pages
    - Implement `app/repos/[repoId]/review/page.tsx`
    - Implement `app/repos/[repoId]/improve/page.tsx`
    - Add structured feedback display
    - Add improvement explanations
    - _Requirements: 11.1_

  - [ ] 4.17 Implement theme support
    - Create theme toggle component with sun/moon icons
    - Implement theme persistence in localStorage
    - Add smooth theme transition animations
    - Configure TailwindCSS dark: variant throughout
    - Test all components in both light and dark modes
    - _Requirements: 11.7_

  - [ ] 4.18 Ensure responsive design
    - Test all layouts on mobile (320px-768px)
    - Test all layouts on tablet (768px-1024px)
    - Test all layouts on desktop (1024px+)
    - Adjust spacing and typography for each breakpoint
    - Ensure touch targets are at least 44x44px on mobile
    - _Requirements: 11.8_

  - [ ] 4.19 Add micro-interactions and polish
    - Add hover states to all interactive elements
    - Add loading states with skeleton loaders
    - Add success/error toast notifications
    - Add page transition animations
    - Add focus states for keyboard navigation
    - Test animations performance (60fps target)
    - _Requirements: 11.9_

  - [ ] 4.20 Checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

- [ ] Phase 5: DevOps
  - [ ] 5.1 Create NGINX configuration
    - Write `nginx.conf` with reverse proxy rules for /api/* → backend, / → frontend
    - Add WebSocket support for streaming
    - _Requirements: 10.1, 11.1_

  - [ ] 5.2 Create Prometheus configuration
    - Write `prometheus.yml` with scrape configs for backend metrics
    - _Requirements: 12.1, 12.2_

  - [ ] 5.3 Create Grafana dashboard configuration
    - Create dashboard JSON for key metrics visualization
    - _Requirements: 12.1, 12.2_

  - [ ] 5.4 Create Alembic migration scripts
    - Initialize Alembic in backend project
    - Create initial migration for repositories, ingestion_jobs, code_chunks tables
    - Add indexes for performance
    - _Requirements: 14.2, 14.5_

  - [ ] 5.5 Add migration execution to startup
    - Add automatic migration execution in FastAPI lifespan event
    - _Requirements: 14.5_

  - [ ] 5.6 Create PostgreSQL backup script
    - Write script for daily full backup and WAL archiving
    - _Requirements: 14.6_

  - [ ] 5.7 Create FAISS index backup script
    - Write script to backup indices to object storage
    - _Requirements: 14.6_

  - [ ] 5.8 Create restore scripts
    - Write scripts for database and index restoration
    - _Requirements: 14.6_

  - [ ] 5.9 Create CI/CD pipeline configuration
    - Set up GitHub Actions or GitLab CI for automated testing
    - Add linting, type checking, and test execution
    - Configure deployment automation
    - _Requirements: 12.1-12.10_

  - [ ]* 5.10 Write end-to-end tests for complete user workflows
    - Test: Add repository → Wait for indexing → Search code → Chat with codebase
    - Test: Multi-repository workflow with filtering
    - Test: Code review workflow
    - Test: Error recovery scenarios
    - _Requirements: All requirements_

  - [ ] 5.11 Perform manual testing
    - Test all UI flows in browser
    - Test with real GitHub repositories
    - Test with different Ollama models
    - Verify monitoring dashboards

  - [ ] 5.12 Final checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

  - [ ] 5.13 Write README.md
    - Add project overview, architecture diagram, setup instructions
    - Document environment variables and configuration
    - Add usage examples and API documentation links

  - [ ] 5.14 Write deployment guide
    - Document production deployment steps
    - Add security hardening checklist
    - Document backup and recovery procedures

  - [ ] 5.15 Write developer guide
    - Document development setup
    - Add contribution guidelines
    - Document testing strategy

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate external service interactions
- End-to-end tests validate complete user workflows
- All code uses Python for backend (FastAPI, Celery) and TypeScript for frontend (Next.js)
- The system uses PostgreSQL for metadata, Redis for caching/sessions, FAISS for vector storage, and Ollama for LLM inference

## Phase Summary

**Phase 1: Foundation** - Project structure, configuration, database models, Redis setup, Docker infrastructure

**Phase 2: Backend Core** - Ingestion pipeline (clone, read, chunk, embed, store), chunking system, embeddings, vector store, retrieval system (BM25 + vector + hybrid), RAG pipeline

**Phase 3: API Layer** - All REST endpoints (repos, search, chat, code, sessions, health), middleware (rate limiting, logging, error handling), background jobs (Celery)

**Phase 4: Frontend** - Layout components, chat UI, file explorer, search UI, code review UI

**Phase 5: DevOps** - Monitoring (Prometheus + Grafana), CI/CD pipelines, deployment scripts, backup and recovery
