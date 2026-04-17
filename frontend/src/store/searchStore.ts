/**
 * Search Store
 * 
 * Manages search state including:
 * - Search queries and results
 * - Search mode (semantic, keyword, hybrid)
 * - Filters and pagination
 * - Search history
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { SearchResult, SearchMode, SearchFilters } from '@/types';

interface SearchState {
  // State
  query: string;
  mode: SearchMode;
  results: SearchResult[];
  filters: SearchFilters;
  topK: number;
  selectedRepositoryIds: string[];
  isSearching: boolean;
  error: string | null;
  
  // Search history
  searchHistory: SearchHistoryItem[];
  maxHistorySize: number;
  
  // Pagination
  currentPage: number;
  pageSize: number;
  totalResults: number;
  
  // Actions
  setQuery: (query: string) => void;
  setMode: (mode: SearchMode) => void;
  setResults: (results: SearchResult[]) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  clearFilters: () => void;
  setTopK: (topK: number) => void;
  setSelectedRepositoryIds: (ids: string[]) => void;
  
  // Search history actions
  addToHistory: (item: Omit<SearchHistoryItem, 'timestamp'>) => void;
  clearHistory: () => void;
  removeFromHistory: (timestamp: string) => void;
  
  // Pagination actions
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setTotalResults: (total: number) => void;
  
  // Utility actions
  setSearching: (isSearching: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  resetResults: () => void;
}

interface SearchHistoryItem {
  query: string;
  mode: SearchMode;
  filters: SearchFilters;
  resultCount: number;
  timestamp: string;
}

const initialState = {
  query: '',
  mode: 'hybrid' as SearchMode,
  results: [],
  filters: {},
  topK: 10,
  selectedRepositoryIds: [],
  isSearching: false,
  error: null,
  searchHistory: [],
  maxHistorySize: 20,
  currentPage: 1,
  pageSize: 10,
  totalResults: 0,
};

export const useSearchStore = create<SearchState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Query and mode actions
        setQuery: (query) => set({ query }, false, 'setQuery'),

        setMode: (mode) => set({ mode }, false, 'setMode'),

        setResults: (results) =>
          set(
            {
              results,
              totalResults: results.length,
              currentPage: 1,
            },
            false,
            'setResults'
          ),

        // Filter actions
        setFilters: (newFilters) =>
          set(
            (state) => ({
              filters: {
                ...state.filters,
                ...newFilters,
              },
            }),
            false,
            'setFilters'
          ),

        clearFilters: () => set({ filters: {} }, false, 'clearFilters'),

        setTopK: (topK) => set({ topK }, false, 'setTopK'),

        setSelectedRepositoryIds: (ids) =>
          set({ selectedRepositoryIds: ids }, false, 'setSelectedRepositoryIds'),

        // Search history actions
        addToHistory: (item) =>
          set(
            (state) => {
              const newItem: SearchHistoryItem = {
                ...item,
                timestamp: new Date().toISOString(),
              };

              // Remove duplicates based on query and mode
              const filteredHistory = state.searchHistory.filter(
                (h) => !(h.query === item.query && h.mode === item.mode)
              );

              // Add new item to the beginning
              const newHistory = [newItem, ...filteredHistory];

              // Limit history size
              const trimmedHistory = newHistory.slice(0, state.maxHistorySize);

              return { searchHistory: trimmedHistory };
            },
            false,
            'addToHistory'
          ),

        clearHistory: () => set({ searchHistory: [] }, false, 'clearHistory'),

        removeFromHistory: (timestamp) =>
          set(
            (state) => ({
              searchHistory: state.searchHistory.filter(
                (item) => item.timestamp !== timestamp
              ),
            }),
            false,
            'removeFromHistory'
          ),

        // Pagination actions
        setPage: (page) => set({ currentPage: page }, false, 'setPage'),

        setPageSize: (pageSize) =>
          set(
            {
              pageSize,
              currentPage: 1, // Reset to first page when page size changes
            },
            false,
            'setPageSize'
          ),

        setTotalResults: (total) =>
          set({ totalResults: total }, false, 'setTotalResults'),

        // Utility actions
        setSearching: (isSearching) =>
          set({ isSearching }, false, 'setSearching'),

        setError: (error) => set({ error }, false, 'setError'),

        reset: () => set(initialState, false, 'reset'),

        resetResults: () =>
          set(
            {
              results: [],
              totalResults: 0,
              currentPage: 1,
              error: null,
            },
            false,
            'resetResults'
          ),
      }),
      {
        name: 'search-store',
        partialize: (state) => ({
          mode: state.mode,
          filters: state.filters,
          topK: state.topK,
          searchHistory: state.searchHistory,
          pageSize: state.pageSize,
          // Don't persist query, results, loading/error states
        }),
      }
    ),
    { name: 'SearchStore' }
  )
);
