/**
 * React hooks for API interactions
 * Provides convenient hooks for common API patterns
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { ApiError } from '@/lib/api-client';

interface UseApiState<T> {
  data: T | null;
  error: ApiError | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
}

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
  retry?: number;
  retryDelay?: number;
}

/**
 * Hook for making API calls with loading and error states
 */
export function useApi<T, Args extends any[]>(
  apiFunction: (...args: Args) => Promise<T>,
  options?: UseApiOptions
) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
    isError: false,
    isSuccess: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      setState({
        data: null,
        error: null,
        isLoading: true,
        isError: false,
        isSuccess: false,
      });

      try {
        const result = await apiFunction(...args);
        
        setState({
          data: result,
          error: null,
          isLoading: false,
          isError: false,
          isSuccess: true,
        });

        options?.onSuccess?.(result);
        return result;
      } catch (error) {
        const apiError = error instanceof ApiError ? error : new ApiError('Unknown error', 0);
        
        setState({
          data: null,
          error: apiError,
          isLoading: false,
          isError: true,
          isSuccess: false,
        });

        options?.onError?.(apiError);
        throw apiError;
      }
    },
    [apiFunction, options]
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      error: null,
      isLoading: false,
      isError: false,
      isSuccess: false,
    });
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Hook for making API calls that execute immediately on mount
 */
export function useApiQuery<T>(
  apiFunction: () => Promise<T>,
  options?: UseApiOptions & { enabled?: boolean }
) {
  const { enabled = true, ...restOptions } = options || {};
  const api = useApi(apiFunction, restOptions);

  useEffect(() => {
    if (enabled) {
      api.execute();
    }
  }, [enabled]); // eslint-disable-line react-hooks/exhaustive-deps

  return api;
}

/**
 * Hook for polling API endpoints at regular intervals
 */
export function useApiPolling<T>(
  apiFunction: () => Promise<T>,
  interval: number,
  options?: UseApiOptions & { enabled?: boolean }
) {
  const { enabled = true, ...restOptions } = options || {};
  const api = useApi(apiFunction, restOptions);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Execute immediately
    api.execute();

    // Set up polling
    intervalRef.current = setInterval(() => {
      api.execute();
    }, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, interval]); // eslint-disable-line react-hooks/exhaustive-deps

  return api;
}

/**
 * Hook for handling streaming responses
 */
export function useStreamingApi(
  streamFunction: () => Promise<ReadableStream<Uint8Array>>,
  onChunk: (chunk: string) => void,
  options?: UseApiOptions
) {
  const [state, setState] = useState<{
    error: ApiError | null;
    isLoading: boolean;
    isError: boolean;
    isSuccess: boolean;
  }>({
    error: null,
    isLoading: false,
    isError: false,
    isSuccess: false,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const execute = useCallback(async () => {
    // Cancel previous stream if still active
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    setState({
      error: null,
      isLoading: true,
      isError: false,
      isSuccess: false,
    });

    try {
      const stream = await streamFunction();
      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setState({
            error: null,
            isLoading: false,
            isError: false,
            isSuccess: true,
          });
          options?.onSuccess?.(undefined);
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } catch (error) {
      const apiError = error instanceof ApiError ? error : new ApiError('Stream error', 0);
      
      setState({
        error: apiError,
        isLoading: false,
        isError: true,
        isSuccess: false,
      });

      options?.onError?.(apiError);
      throw apiError;
    }
  }, [streamFunction, onChunk, options]);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setState({
        error: null,
        isLoading: false,
        isError: false,
        isSuccess: false,
      });
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    ...state,
    execute,
    cancel,
  };
}
