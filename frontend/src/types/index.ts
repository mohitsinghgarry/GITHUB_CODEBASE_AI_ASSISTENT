/**
 * Common TypeScript types for the application
 */

// Repository types
export interface Repository {
  id: string;
  url: string;
  owner: string;
  name: string;
  defaultBranch: string;
  lastCommitHash: string;
  status: RepositoryStatus;
  createdAt: string;
  updatedAt: string;
  errorMessage?: string;
  chunkCount: number;
  indexPath?: string;
}

export type RepositoryStatus =
  | 'pending'
  | 'cloning'
  | 'reading'
  | 'chunking'
  | 'embedding'
  | 'completed'
  | 'failed';

// Ingestion job types
export interface IngestionJob {
  id: string;
  repositoryId: string;
  status: JobStatus;
  stage?: IngestionStage;
  progressPercent: number;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
  retryCount: number;
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed';

export type IngestionStage = 'clone' | 'read' | 'chunk' | 'embed' | 'store';

// Code chunk types
export interface CodeChunk {
  id: string;
  repositoryId: string;
  filePath: string;
  startLine: number;
  endLine: number;
  language: string;
  content: string;
  embeddingId?: number;
  createdAt: string;
}

// Search types
export interface SearchResult {
  chunk: CodeChunk;
  score: number;
  highlights?: string[];
}

export interface SearchRequest {
  query: string;
  repositoryIds?: string[];
  topK?: number;
  filters?: SearchFilters;
}

export interface SearchFilters {
  fileExtension?: string[];
  directoryPath?: string;
  language?: string[];
}

export type SearchMode = 'semantic' | 'keyword' | 'hybrid';

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
}

export interface Citation {
  chunkId: string;
  filePath: string;
  startLine: number;
  endLine: number;
  content: string;
}

export interface ChatSession {
  id: string;
  repositoryIds: string[];
  messages: ChatMessage[];
  explanationMode: ExplanationMode;
  createdAt: string;
  updatedAt: string;
}

export type ExplanationMode = 'beginner' | 'technical' | 'interview';

// Code review types
export interface ReviewRequest {
  code: string;
  filePath?: string;
  language?: string;
}

export interface ReviewFeedback {
  issues: ReviewIssue[];
  summary: string;
}

export interface ReviewIssue {
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  lineNumber?: number;
  suggestion?: string;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// UI state types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}
