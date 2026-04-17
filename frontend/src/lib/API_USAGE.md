# API Client Usage Guide

This document provides examples and best practices for using the API client in the GitHub Codebase RAG Assistant frontend.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Error Handling](#error-handling)
3. [Interceptors](#interceptors)
4. [React Hooks](#react-hooks)
5. [Streaming Responses](#streaming-responses)
6. [Request Cancellation](#request-cancellation)

## Basic Usage

### Importing the API Client

```typescript
import { apiClient } from '@/lib/api';
```

### Repository Operations

```typescript
// List all repositories
const repositories = await apiClient.repositories.list();

// Get a specific repository
const repo = await apiClient.repositories.get('repo-id');

// Create a new repository
const { repository, jobId } = await apiClient.repositories.create(
  'https://github.com/user/repo'
);

// Delete a repository
await apiClient.repositories.delete('repo-id');

// Trigger re-indexing
const { jobId } = await apiClient.repositories.reindex('repo-id');
```

### Search Operations

```typescript
import type { SearchRequest } from '@/lib/api';

// Semantic search
const request: SearchRequest = {
  query: 'authentication logic',
  repositoryIds: ['repo-id'],
  topK: 10,
  filters: {
    language: ['typescript', 'javascript'],
    fileExtension: ['.ts', '.tsx'],
  },
};

const results = await apiClient.search.semantic(request);

// Keyword search
const keywordResults = await apiClient.search.keyword(request);

// Hybrid search (combines semantic + keyword)
const hybridResults = await apiClient.search.hybrid(request);
```

### Chat Operations

```typescript
// Send a chat message (non-streaming)
const { message, sessionId } = await apiClient.chat.send(
  'How does authentication work?',
  undefined, // sessionId (optional)
  ['repo-id'], // repositoryIds
  'technical' // explanationMode
);

// Get session history
const session = await apiClient.chat.getSession(sessionId);

// Delete a session
await apiClient.chat.deleteSession(sessionId);
```

### Code Review Operations

```typescript
import type { ReviewRequest } from '@/lib/api';

// Analyze code for issues
const request: ReviewRequest = {
  code: 'function example() { ... }',
  filePath: 'src/example.ts',
  language: 'typescript',
};

const feedback = await apiClient.review.analyze(request);

// Get improvement suggestions
const { improved, explanation } = await apiClient.review.improve(request);
```

## Error Handling

### Using Try-Catch

```typescript
import { ApiError } from '@/lib/api';

try {
  const repo = await apiClient.repositories.get('repo-id');
} catch (error) {
  if (error instanceof ApiError) {
    // Check error type
    if (error.isNotFound) {
      console.error('Repository not found');
    } else if (error.isServerError) {
      console.error('Server error:', error.message);
    } else if (error.isNetworkError) {
      console.error('Network error');
    }
    
    // Access error details
    console.error('Status:', error.status);
    console.error('Code:', error.code);
    console.error('Details:', error.details);
  }
}
```

### Error Properties

The `ApiError` class provides convenient properties:

- `isNetworkError`: Network failure (status 0)
- `isServerError`: Server error (status >= 500)
- `isClientError`: Client error (status 400-499)
- `isUnauthorized`: 401 Unauthorized
- `isForbidden`: 403 Forbidden
- `isNotFound`: 404 Not Found
- `isRateLimited`: 429 Too Many Requests

## Interceptors

### Request Interceptor

Add custom headers or modify requests before they're sent:

```typescript
import { apiClient } from '@/lib/api';

// Add authentication token
const removeInterceptor = apiClient.interceptors.request((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

// Remove interceptor when no longer needed
removeInterceptor();
```

### Response Interceptor

Transform responses before they reach your code:

```typescript
apiClient.interceptors.response((response) => {
  // Transform timestamps to Date objects
  if (response && typeof response === 'object') {
    if ('createdAt' in response) {
      response.createdAt = new Date(response.createdAt);
    }
  }
  return response;
});
```

### Error Interceptor

Handle errors globally:

```typescript
import { ApiError } from '@/lib/api';

apiClient.interceptors.error(async (error) => {
  // Redirect to login on 401
  if (error.isUnauthorized) {
    window.location.href = '/login';
  }
  
  // Show toast notification
  if (error.isServerError) {
    showToast('Server error. Please try again later.');
  }
  
  // Always re-throw to allow local handling
  throw error;
});
```

## React Hooks

### useApi Hook

For manual API calls with loading states:

```typescript
import { useApi } from '@/hooks/useApi';
import { apiClient } from '@/lib/api';

function RepositoryList() {
  const { data, isLoading, isError, error, execute } = useApi(
    apiClient.repositories.list,
    {
      onSuccess: (repos) => {
        console.log('Loaded repositories:', repos);
      },
      onError: (error) => {
        console.error('Failed to load:', error);
      },
    }
  );

  return (
    <div>
      <button onClick={() => execute()} disabled={isLoading}>
        Load Repositories
      </button>
      
      {isLoading && <p>Loading...</p>}
      {isError && <p>Error: {error?.message}</p>}
      {data && <ul>{data.map(repo => <li key={repo.id}>{repo.name}</li>)}</ul>}
    </div>
  );
}
```

### useApiQuery Hook

For automatic API calls on mount:

```typescript
import { useApiQuery } from '@/hooks/useApi';
import { apiClient } from '@/lib/api';

function RepositoryDetails({ id }: { id: string }) {
  const { data, isLoading, isError } = useApiQuery(
    () => apiClient.repositories.get(id),
    { enabled: !!id } // Only fetch if id is provided
  );

  if (isLoading) return <p>Loading...</p>;
  if (isError) return <p>Error loading repository</p>;
  if (!data) return null;

  return <div>{data.name}</div>;
}
```

### useApiPolling Hook

For polling endpoints at regular intervals:

```typescript
import { useApiPolling } from '@/hooks/useApi';
import { apiClient } from '@/lib/api';

function JobStatus({ jobId }: { jobId: string }) {
  const { data, isLoading } = useApiPolling(
    () => apiClient.jobs.get(jobId),
    2000, // Poll every 2 seconds
    {
      enabled: !!jobId,
      onSuccess: (job) => {
        // Stop polling when job completes
        if (job.status === 'completed' || job.status === 'failed') {
          // Handle completion
        }
      },
    }
  );

  return (
    <div>
      {data && (
        <>
          <p>Status: {data.status}</p>
          <p>Progress: {data.progressPercent}%</p>
        </>
      )}
    </div>
  );
}
```

## Streaming Responses

### Using the Streaming API

```typescript
import { useStreamingApi } from '@/hooks/useApi';
import { apiClient } from '@/lib/api';
import { useState } from 'react';

function ChatInterface() {
  const [response, setResponse] = useState('');
  
  const { isLoading, execute, cancel } = useStreamingApi(
    () => apiClient.chat.sendStreaming('How does this work?'),
    (chunk) => {
      // Parse SSE chunk
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          try {
            const parsed = JSON.parse(data);
            setResponse((prev) => prev + parsed.content);
          } catch (e) {
            // Ignore parse errors
          }
        }
      }
    },
    {
      onSuccess: () => {
        console.log('Stream completed');
      },
      onError: (error) => {
        console.error('Stream error:', error);
      },
    }
  );

  return (
    <div>
      <button onClick={() => execute()} disabled={isLoading}>
        Send Message
      </button>
      {isLoading && <button onClick={cancel}>Cancel</button>}
      <div>{response}</div>
    </div>
  );
}
```

## Request Cancellation

### Canceling Individual Requests

```typescript
import { apiClient } from '@/lib/api';

// Start a request
const promise = apiClient.repositories.list();

// Cancel it if needed
apiClient.cancelRequest('GET-/repositories-<timestamp>');
```

### Automatic Cancellation with Hooks

The `useApi` hooks automatically cancel pending requests when:
- A new request is made
- The component unmounts

```typescript
function SearchResults({ query }: { query: string }) {
  const { data, execute } = useApi(
    (q: string) => apiClient.search.semantic({ query: q })
  );

  useEffect(() => {
    // Previous request is automatically cancelled
    execute(query);
  }, [query, execute]);

  return <div>{/* render results */}</div>;
}
```

## Best Practices

1. **Use TypeScript**: The API client is fully typed. Let TypeScript guide you.

2. **Handle Errors**: Always handle errors appropriately, either with try-catch or error callbacks.

3. **Use Hooks**: Prefer React hooks for component-based API calls.

4. **Add Interceptors Wisely**: Use interceptors for cross-cutting concerns like authentication, but avoid complex logic.

5. **Cancel Requests**: Cancel requests when they're no longer needed to save bandwidth.

6. **Configure Timeouts**: Set appropriate timeouts for long-running operations.

7. **Retry on Failure**: The client automatically retries server errors. Configure retry counts as needed.

8. **Stream Large Responses**: Use streaming for chat responses to provide better UX.

## Configuration

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Default Timeouts

- Repository operations: 30 seconds
- Search operations: 15 seconds
- Chat operations: 60 seconds
- Health checks: No timeout

### Default Retry Counts

- GET requests: 2 retries
- POST/PUT/DELETE: 1 retry
- Health checks: 0 retries
