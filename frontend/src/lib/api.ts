/**
 * API Client for RepoMind Assistant Backend
 * 
 * Provides type-safe methods for all backend API endpoints.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ============================================================================
// Types
// ============================================================================

export interface Repository {
  id: string;
  url: string;
  owner: string;
  name: string;
  status: 'pending' | 'cloning' | 'reading' | 'chunking' | 'embedding' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  indexed_at?: string;
  error_message?: string;
  total_files?: number;
  total_chunks?: number;
  index_path?: string;
}

export interface IngestionJob {
  id: string;
  repository_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  stage?: 'clone' | 'read' | 'chunk' | 'embed' | 'store';
  progress_percent: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  retry_count: number;
}

export interface ChatSession {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  repository_ids: string[];
  model: string;
  message_count: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: Citation[];
}

export interface Citation {
  chunk_id: string;
  repository_id: string;
  file_path: string;
  start_line: number;
  end_line: number;
  language: string;
  content: string;
  score?: number;
}

export interface SearchResult {
  chunk: {
    id: string;
    repository_id: string;
    file_path: string;
    start_line: number;
    end_line: number;
    language: string;
    content: string;
  };
  score: number;
  matches: Array<{
    start: number;
    end: number;
    matched_text: string;
    line_number: number;
  }>;
  highlighted_content: string;
}

export interface CodeIssue {
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  line_number?: number;
  suggestion?: string;
}

export interface CodeImprovement {
  category: string;
  description: string;
  before_snippet?: string;
  after_snippet?: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  description: string;
}

export interface AvailableModels {
  llm_models: ModelInfo[];
  embedding_models: ModelInfo[];
}

export interface Settings {
  llm_provider: string;
  llm_model: string;
  temperature: number;
  max_context_tokens: number;
  max_response_tokens: number;
  embedding_model: string;
  embedding_dimension: number;
  chunk_size: number;
  chunk_overlap: number;
  default_top_k: number;
  hybrid_search_alpha: number;
}

export interface UpdateSettingsRequest {
  llm_model?: string;
  temperature?: number;
  max_context_tokens?: number;
  max_response_tokens?: number;
  embedding_model?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  default_top_k?: number;
  hybrid_search_alpha?: number;
}

// ============================================================================
// API Client Class
// ============================================================================

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: 'Unknown error',
        message: response.statusText,
      }));
      throw new Error(error.message || error.error || 'API request failed');
    }

    return response.json();
  }

  // ============================================================================
  // Repository Endpoints
  // ============================================================================

  async createRepository(url: string): Promise<{
    repository: Repository;
    job_id: string;
    message: string;
  }> {
    return this.request('/repositories', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async listRepositories(): Promise<{
    repositories: Repository[];
    total: number;
  }> {
    return this.request('/repositories');
  }

  async getRepository(id: string): Promise<Repository> {
    return this.request(`/repositories/${id}`);
  }

  async deleteRepository(id: string): Promise<{
    message: string;
    deleted_repository_id: string;
    deleted_chunks_count: number;
  }> {
    return this.request(`/repositories/${id}`, {
      method: 'DELETE',
    });
  }

  async reindexRepository(id: string): Promise<{
    repository: Repository;
    job_id: string;
    message: string;
  }> {
    return this.request(`/repositories/${id}/reindex`, {
      method: 'POST',
    });
  }

  async getLanguageStats(): Promise<{
    languages: Array<{
      name: string;
      chunk_count: number;
      percentage: number;
    }>;
    total_chunks: number;
  }> {
    return this.request('/repositories/stats/languages');
  }

  // ============================================================================
  // Job Endpoints
  // ============================================================================

  async getJobStatus(jobId: string): Promise<{
    job: IngestionJob;
    estimated_time_remaining?: number;
  }> {
    return this.request(`/jobs/${jobId}`);
  }

  async retryJob(jobId: string): Promise<{
    message: string;
    old_job_id: string;
    new_job_id: string;
    repository_id: string;
  }> {
    return this.request(`/jobs/${jobId}/retry`, {
      method: 'POST',
    });
  }

  // ============================================================================
  // Chat Endpoints
  // ============================================================================

  async chat(params: {
    message: string;
    repository_ids: string[];
    session_id?: string;
    model?: string;
    explanation_mode?: 'beginner' | 'technical' | 'interview';
    top_k?: number;
    include_history?: boolean;
    stream?: boolean;
  }): Promise<{
    response: string;
    citations: Citation[];
    session_id: string;
  }> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: params.message,
        repository_ids: params.repository_ids,
        session_id: params.session_id,
        model: params.model,
        explanation_mode: params.explanation_mode || 'technical',
        top_k: params.top_k || 5,
        include_history: params.include_history !== false,
        stream: params.stream || false,
      }),
    });
  }

  async *chatStream(params: {
    message: string;
    repository_ids: string[];
    session_id?: string;
    model?: string;
    explanation_mode?: 'beginner' | 'technical' | 'interview';
    top_k?: number;
    include_history?: boolean;
  }): AsyncGenerator<{
    chunk: string;
    citations?: Citation[];
    session_id?: string;
    done: boolean;
  }> {
    const url = `${this.baseURL}/chat`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: params.message,
        repository_ids: params.repository_ids,
        session_id: params.session_id,
        model: params.model,
        explanation_mode: params.explanation_mode || 'technical',
        top_k: params.top_k || 5,
        include_history: params.include_history !== false,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error('Chat stream failed');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          yield data;
          
          if (data.done) {
            return;
          }
        }
      }
    }
  }

  async getChatSession(sessionId: string): Promise<{
    session_id: string;
    repository_ids: string[];
    messages: ChatMessage[];
    explanation_mode: string;
    created_at: string;
    updated_at: string;
  }> {
    return this.request(`/chat/sessions/${sessionId}`);
  }

  async deleteChatSession(sessionId: string): Promise<{
    message: string;
    deleted_session_id: string;
  }> {
    return this.request(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async listChatSessions(): Promise<{
    sessions: ChatSession[];
    total: number;
  }> {
    return this.request('/chat/sessions');
  }

  async listRepositoryFiles(repositoryId: string, language?: string): Promise<{
    files: Array<{
      file_path: string;
      language: string | null;
      start_line: number;
      end_line: number;
      chunk_count: number;
    }>;
    total: number;
  }> {
    const params = language ? `?language=${encodeURIComponent(language)}` : '';
    return this.request(`/repositories/${repositoryId}/files${params}`);
  }

  async getFileContent(repositoryId: string, filePath: string): Promise<{
    file_path: string;
    language: string | null;
    content: string;
    start_line: number;
    end_line: number;
    chunk_count: number;
  }> {
    return this.request(`/repositories/${repositoryId}/files/content?file_path=${encodeURIComponent(filePath)}`);
  }

  async getChatModels(): Promise<{
    models: Array<{ id: string; name: string; description: string; provider: string }>;
    provider: string;
    total: number;
  }> {
    return this.request('/chat/models');
  }

  // ============================================================================
  // Search Endpoints
  // ============================================================================

  async searchSemantic(params: {
    query: string;
    top_k?: number;
    repository_ids?: string[];
    file_extensions?: string[];
    directory_paths?: string[];
    languages?: string[];
  }): Promise<{
    results: SearchResult[];
    total_results: number;
    query: string;
  }> {
    return this.request('/search/semantic', {
      method: 'POST',
      body: JSON.stringify({
        query: params.query,
        top_k: params.top_k || 10,
        repository_ids: params.repository_ids,
        file_extensions: params.file_extensions,
        directory_paths: params.directory_paths,
        languages: params.languages,
      }),
    });
  }

  async searchKeyword(params: {
    query: string;
    top_k?: number;
    mode?: 'exact' | 'case_insensitive' | 'regex';
    use_boolean?: boolean;
    repository_ids?: string[];
    file_extensions?: string[];
    directory_paths?: string[];
    languages?: string[];
  }): Promise<{
    results: SearchResult[];
    total_results: number;
    query: string;
  }> {
    return this.request('/search/keyword', {
      method: 'POST',
      body: JSON.stringify({
        query: params.query,
        top_k: params.top_k || 10,
        mode: params.mode || 'case_insensitive',
        use_boolean: params.use_boolean || false,
        repository_ids: params.repository_ids,
        file_extensions: params.file_extensions,
        directory_paths: params.directory_paths,
        languages: params.languages,
      }),
    });
  }

  async searchHybrid(params: {
    query: string;
    top_k?: number;
    bm25_weight?: number;
    repository_ids?: string[];
    file_extensions?: string[];
    directory_paths?: string[];
    languages?: string[];
  }): Promise<{
    results: SearchResult[];
    total_results: number;
    query: string;
    bm25_weight: number;
  }> {
    return this.request('/search/hybrid', {
      method: 'POST',
      body: JSON.stringify({
        query: params.query,
        top_k: params.top_k || 10,
        bm25_weight: params.bm25_weight || 0.5,
        repository_ids: params.repository_ids,
        file_extensions: params.file_extensions,
        directory_paths: params.directory_paths,
        languages: params.languages,
      }),
    });
  }

  // ============================================================================
  // Code Review Endpoints
  // ============================================================================

  async reviewCode(params: {
    code: string;
    language?: string;
    file_path?: string;
    criteria?: string[];
  }): Promise<{
    issues: CodeIssue[];
    summary: {
      total_issues: number;
      critical_count: number;
      high_count: number;
      medium_count: number;
      low_count: number;
      info_count: number;
    };
    overall_assessment: string;
    recommendations: string[];
  }> {
    const body: any = {
      code: params.code,
      language: params.language || 'python',
    };
    
    if (params.file_path) {
      body.file_path = params.file_path;
    }
    
    if (params.criteria) {
      body.criteria = params.criteria;
    }
    
    return this.request('/review', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async improveCode(params: {
    code: string;
    language?: string;
    file_path?: string;
    improvement_goals?: string[];
  }): Promise<{
    improved_code: string;
    improvements: CodeImprovement[];
    summary: string;
  }> {
    const body: any = {
      code: params.code,
      language: params.language || 'python',
    };
    
    if (params.file_path) {
      body.file_path = params.file_path;
    }
    
    if (params.improvement_goals) {
      body.improvement_goals = params.improvement_goals;
    }
    
    return this.request('/review/improve', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async reviewDiff(params: {
    diff: string;
    focus_on_changes?: boolean;
    criteria?: string[];
  }): Promise<{
    files: Array<{
      file_path: string;
      hunks: Array<{
        old_start: number;
        old_count: number;
        new_start: number;
        new_count: number;
        lines: Array<{
          type: 'context' | 'addition' | 'deletion';
          content: string;
          old_line_number?: number;
          new_line_number?: number;
        }>;
      }>;
    }>;
    issues: CodeIssue[];
    summary: {
      total_issues: number;
      critical_count: number;
      high_count: number;
      medium_count: number;
      low_count: number;
      info_count: number;
    };
    overall_assessment: string;
    approval_recommendation: 'approve' | 'request_changes' | 'comment';
  }> {
    const body: any = {
      diff: params.diff,
      focus_on_changes: params.focus_on_changes !== false,
    };
    
    if (params.criteria) {
      body.criteria = params.criteria;
    }
    
    return this.request('/review/diff', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // ============================================================================
  // Settings Endpoints
  // ============================================================================

  async getAvailableModels(): Promise<AvailableModels> {
    return this.request('/settings/models');
  }

  async getSettings(): Promise<Settings> {
    return this.request('/settings');
  }

  async updateSettings(settings: UpdateSettingsRequest): Promise<Settings> {
    return this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // ============================================================================
  // Health Check
  // ============================================================================

  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    version: string;
  }> {
    return this.request('/health');
  }
}

// Export singleton instance
export const api = new APIClient();

// Export class for custom instances
export { APIClient };
