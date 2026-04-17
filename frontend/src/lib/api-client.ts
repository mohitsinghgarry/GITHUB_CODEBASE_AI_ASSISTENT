/**
 * API Client for backend communication
 * Provides typed API methods with error handling and interceptors
 */

import type {
  Repository,
  IngestionJob,
  SearchResult,
  SearchRequest,
  ChatMessage,
  ChatSession,
  ReviewRequest,
  ReviewFeedback,
  ExplanationMode,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Request/Response interceptor types
type RequestInterceptor = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
type ResponseInterceptor = <T>(response: T) => T | Promise<T>;
type ErrorInterceptor = (error: ApiError) => Promise<never>;

interface RequestConfig extends RequestInit {
  url: string;
  params?: Record<string, string | number | boolean>;
  retry?: number;
  timeout?: number;
}

// Custom API Error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }

  get isNetworkError(): boolean {
    return this.status === 0;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }

  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  get isNotFound(): boolean {
    return this.status === 404;
  }

  get isRateLimited(): boolean {
    return this.status === 429;
  }
}

// Interceptor manager
class InterceptorManager {
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];

  addRequestInterceptor(interceptor: RequestInterceptor): () => void {
    this.requestInterceptors.push(interceptor);
    return () => {
      const index = this.requestInterceptors.indexOf(interceptor);
      if (index > -1) {
        this.requestInterceptors.splice(index, 1);
      }
    };
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): () => void {
    this.responseInterceptors.push(interceptor);
    return () => {
      const index = this.responseInterceptors.indexOf(interceptor);
      if (index > -1) {
        this.responseInterceptors.splice(index, 1);
      }
    };
  }

  addErrorInterceptor(interceptor: ErrorInterceptor): () => void {
    this.errorInterceptors.push(interceptor);
    return () => {
      const index = this.errorInterceptors.indexOf(interceptor);
      if (index > -1) {
        this.errorInterceptors.splice(index, 1);
      }
    };
  }

  async runRequestInterceptors(config: RequestConfig): Promise<RequestConfig> {
    let modifiedConfig = config;
    for (const interceptor of this.requestInterceptors) {
      modifiedConfig = await interceptor(modifiedConfig);
    }
    return modifiedConfig;
  }

  async runResponseInterceptors<T>(response: T): Promise<T> {
    let modifiedResponse = response;
    for (const interceptor of this.responseInterceptors) {
      modifiedResponse = await interceptor(modifiedResponse);
    }
    return modifiedResponse;
  }

  async runErrorInterceptors(error: ApiError): Promise<never> {
    for (const interceptor of this.errorInterceptors) {
      await interceptor(error);
    }
    throw error;
  }
}

// HTTP Client with interceptors
class HttpClient {
  private interceptors = new InterceptorManager();
  private abortControllers = new Map<string, AbortController>();

  constructor(private baseURL: string) {
    // Add default request interceptor for logging
    this.interceptors.addRequestInterceptor((config) => {
      if (process.env.NODE_ENV === 'development') {
        console.log(`[API] ${config.method || 'GET'} ${config.url}`);
      }
      return config;
    });

    // Add default error interceptor for logging
    this.interceptors.addErrorInterceptor((error) => {
      if (process.env.NODE_ENV === 'development') {
        console.error('[API Error]', error);
      }
      return Promise.reject(error);
    });
  }

  // Public methods to add interceptors
  addRequestInterceptor(interceptor: RequestInterceptor) {
    return this.interceptors.addRequestInterceptor(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor) {
    return this.interceptors.addResponseInterceptor(interceptor);
  }

  addErrorInterceptor(interceptor: ErrorInterceptor) {
    return this.interceptors.addErrorInterceptor(interceptor);
  }

  // Build URL with query parameters
  private buildUrl(path: string, params?: Record<string, string | number | boolean>): string {
    const url = new URL(path, this.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }
    return url.toString();
  }

  // Handle response with error checking
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: 'An error occurred' };
      }

      throw new ApiError(
        errorData.message || errorData.error || 'Request failed',
        response.status,
        errorData.code,
        errorData.details
      );
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return undefined as T;
    }

    try {
      return await response.json();
    } catch {
      return undefined as T;
    }
  }

  // Retry logic with exponential backoff
  private async retryRequest<T>(
    fn: () => Promise<T>,
    retries: number,
    delay: number = 1000
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retries <= 0 || !(error instanceof ApiError) || !error.isServerError) {
        throw error;
      }

      await new Promise((resolve) => setTimeout(resolve, delay));
      return this.retryRequest(fn, retries - 1, delay * 2);
    }
  }

  // Request with timeout
  private async requestWithTimeout<T>(
    promise: Promise<T>,
    timeout: number,
    requestId: string
  ): Promise<T> {
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        this.cancelRequest(requestId);
        reject(new ApiError('Request timeout', 0, 'TIMEOUT'));
      }, timeout);
    });

    return Promise.race([promise, timeoutPromise]);
  }

  // Cancel a request
  cancelRequest(requestId: string): void {
    const controller = this.abortControllers.get(requestId);
    if (controller) {
      controller.abort();
      this.abortControllers.delete(requestId);
    }
  }

  // Main request method
  async request<T>(config: RequestConfig): Promise<T> {
    try {
      // Run request interceptors
      const modifiedConfig = await this.interceptors.runRequestInterceptors(config);

      // Create abort controller for cancellation
      const requestId = `${modifiedConfig.method || 'GET'}-${modifiedConfig.url}-${Date.now()}`;
      const controller = new AbortController();
      this.abortControllers.set(requestId, controller);

      // Build URL with params
      const url = this.buildUrl(modifiedConfig.url, modifiedConfig.params);

      // Prepare fetch options
      const fetchOptions: RequestInit = {
        ...modifiedConfig,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...modifiedConfig.headers,
        },
      };

      // Execute request with retry and timeout
      const executeRequest = async () => {
        try {
          const response = await fetch(url, fetchOptions);
          const data = await this.handleResponse<T>(response);
          this.abortControllers.delete(requestId);
          return data;
        } catch (error) {
          this.abortControllers.delete(requestId);
          if (error instanceof ApiError) {
            throw error;
          }
          // Network error or fetch failure
          throw new ApiError(
            error instanceof Error ? error.message : 'Network error',
            0,
            'NETWORK_ERROR'
          );
        }
      };

      let result: T;
      if (modifiedConfig.timeout) {
        result = await this.requestWithTimeout(
          this.retryRequest(() => executeRequest(), modifiedConfig.retry || 0),
          modifiedConfig.timeout,
          requestId
        );
      } else {
        result = await this.retryRequest(() => executeRequest(), modifiedConfig.retry || 0);
      }

      // Run response interceptors
      return await this.interceptors.runResponseInterceptors(result);
    } catch (error) {
      if (error instanceof ApiError) {
        return this.interceptors.runErrorInterceptors(error);
      }
      throw error;
    }
  }

  // Convenience methods
  async get<T>(url: string, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({ ...config, url, method: 'GET' });
  }

  async post<T>(url: string, data?: unknown, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      ...config,
      url,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(url: string, data?: unknown, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      ...config,
      url,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(url: string, data?: unknown, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({
      ...config,
      url,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(url: string, config?: Partial<RequestConfig>): Promise<T> {
    return this.request<T>({ ...config, url, method: 'DELETE' });
  }
}

// Create HTTP client instance
const httpClient = new HttpClient(API_BASE_URL);

// API Client with typed methods
export const apiClient = {
  // Expose interceptor methods
  interceptors: {
    request: httpClient.addRequestInterceptor.bind(httpClient),
    response: httpClient.addResponseInterceptor.bind(httpClient),
    error: httpClient.addErrorInterceptor.bind(httpClient),
  },

  // Cancel request method
  cancelRequest: httpClient.cancelRequest.bind(httpClient),

  // Repository endpoints
  repositories: {
    /**
     * List all repositories
     */
    list: async (): Promise<Repository[]> => {
      return httpClient.get<Repository[]>('/repositories', { retry: 2 });
    },

    /**
     * Get repository by ID
     */
    get: async (id: string): Promise<Repository> => {
      return httpClient.get<Repository>(`/repositories/${id}`, { retry: 2 });
    },

    /**
     * Create a new repository
     */
    create: async (url: string): Promise<{ repository: Repository; jobId: string }> => {
      return httpClient.post<{ repository: Repository; jobId: string }>(
        '/repositories',
        { url },
        { timeout: 30000 }
      );
    },

    /**
     * Delete a repository
     */
    delete: async (id: string): Promise<void> => {
      return httpClient.delete<void>(`/repositories/${id}`);
    },

    /**
     * Trigger repository re-indexing
     */
    reindex: async (id: string): Promise<{ jobId: string }> => {
      return httpClient.post<{ jobId: string }>(`/repositories/${id}/reindex`, undefined, {
        timeout: 30000,
      });
    },
  },

  // Job endpoints
  jobs: {
    /**
     * Get job status
     */
    get: async (jobId: string): Promise<IngestionJob> => {
      return httpClient.get<IngestionJob>(`/jobs/${jobId}`, { retry: 2 });
    },

    /**
     * Retry a failed job
     */
    retry: async (jobId: string): Promise<{ jobId: string }> => {
      return httpClient.post<{ jobId: string }>(`/jobs/${jobId}/retry`);
    },
  },

  // Search endpoints
  search: {
    /**
     * Semantic search using vector similarity
     */
    semantic: async (request: SearchRequest): Promise<SearchResult[]> => {
      return httpClient.post<SearchResult[]>('/search/semantic', request, {
        timeout: 15000,
        retry: 1,
      });
    },

    /**
     * Keyword search using BM25
     */
    keyword: async (request: SearchRequest): Promise<SearchResult[]> => {
      return httpClient.post<SearchResult[]>('/search/keyword', request, {
        timeout: 15000,
        retry: 1,
      });
    },

    /**
     * Hybrid search combining semantic and keyword
     */
    hybrid: async (request: SearchRequest): Promise<SearchResult[]> => {
      return httpClient.post<SearchResult[]>('/search/hybrid', request, {
        timeout: 15000,
        retry: 1,
      });
    },
  },

  // Chat endpoints
  chat: {
    /**
     * Send a chat message (non-streaming)
     */
    send: async (
      message: string,
      sessionId?: string,
      repositoryIds?: string[],
      explanationMode?: ExplanationMode
    ): Promise<{ message: ChatMessage; sessionId: string }> => {
      return httpClient.post<{ message: ChatMessage; sessionId: string }>(
        '/chat',
        {
          message,
          sessionId,
          repositoryIds,
          explanationMode,
        },
        { timeout: 60000, retry: 1 }
      );
    },

    /**
     * Send a chat message with streaming response
     * Returns a ReadableStream for streaming responses
     */
    sendStreaming: async (
      message: string,
      sessionId?: string,
      repositoryIds?: string[],
      explanationMode?: ExplanationMode
    ): Promise<ReadableStream<Uint8Array>> => {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          message,
          sessionId,
          repositoryIds,
          explanationMode,
          stream: true,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new ApiError(error.message, response.status, error.code);
      }

      if (!response.body) {
        throw new ApiError('No response body', 500, 'NO_BODY');
      }

      return response.body;
    },

    /**
     * Get chat session history
     */
    getSession: async (sessionId: string): Promise<ChatSession> => {
      return httpClient.get<ChatSession>(`/chat/sessions/${sessionId}`, { retry: 2 });
    },

    /**
     * Delete a chat session
     */
    deleteSession: async (sessionId: string): Promise<void> => {
      return httpClient.delete<void>(`/chat/sessions/${sessionId}`);
    },
  },

  // Code review endpoints
  review: {
    /**
     * Analyze code for issues
     */
    analyze: async (request: ReviewRequest): Promise<ReviewFeedback> => {
      return httpClient.post<ReviewFeedback>('/review', request, {
        timeout: 60000,
        retry: 1,
      });
    },

    /**
     * Get code improvement suggestions
     */
    improve: async (request: ReviewRequest): Promise<{ improved: string; explanation: string }> => {
      return httpClient.post<{ improved: string; explanation: string }>('/improve', request, {
        timeout: 60000,
        retry: 1,
      });
    },
  },

  // Health endpoints
  health: {
    /**
     * Check system health
     */
    check: async (): Promise<{
      status: string;
      dependencies: Record<string, { status: string; message?: string }>;
    }> => {
      return httpClient.get('/health', { retry: 0 });
    },

    /**
     * List available Ollama models
     */
    models: async (): Promise<{ models: string[] }> => {
      return httpClient.get<{ models: string[] }>('/models', { retry: 2 });
    },

    /**
     * Get Prometheus metrics
     */
    metrics: async (): Promise<string> => {
      return httpClient.get<string>('/metrics', { retry: 0 });
    },
  },
};

// Export types
export type { RequestInterceptor, ResponseInterceptor, ErrorInterceptor };

// Default export
export default apiClient;
