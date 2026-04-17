/**
 * Search Page
 * 
 * Search interface for querying repository code.
 * Features:
 * - Tabbed interface with mode switching (Semantic, Keyword, Hybrid)
 * - Result export functionality (JSON/CSV)
 * - "View in context" navigation
 * - Search filters (language, file extension, directory)
 * - Search history
 * - Pagination
 * 
 * Requirements: 11.5, 11.6
 * - THE Frontend_App SHALL provide separate interfaces for semantic search and keyword search
 * - THE Frontend_App SHALL display search results with relevance scores and navigation to source files
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeIn, staggerContainer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { SearchBar } from '@/components/search/SearchBar';
import { SearchModeToggle } from '@/components/search/SearchModeToggle';
import { SearchResultCard } from '@/components/search/SearchResultCard';
import { SearchFilters } from '@/components/search/SearchFilters';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorBanner } from '@/components/common/ErrorBanner';
import { EmptyState } from '@/components/common/EmptyState';
import { useSearchStore } from '@/store/searchStore';
import { apiClient } from '@/lib/api-client';
import {
  Download,
  FileJson,
  FileSpreadsheet,
  Search as SearchIcon,
  SlidersHorizontal,
  X,
} from 'lucide-react';
import type { SearchMode, SearchResult } from '@/types';

interface SearchPageProps {
  params: {
    repoId: string;
  };
}

export default function SearchPage({ params }: SearchPageProps) {
  const router = useRouter();
  const {
    query,
    mode,
    results,
    filters,
    topK,
    isSearching,
    error,
    searchHistory,
    currentPage,
    pageSize,
    totalResults,
    setQuery,
    setMode,
    setResults,
    setFilters,
    setTopK,
    addToHistory,
    setSearching,
    setError,
    setPage,
    resetResults,
  } = useSearchStore();

  const [showFilters, setShowFilters] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Perform search
  const performSearch = useCallback(
    async (searchQuery: string, searchMode: SearchMode) => {
      if (!searchQuery.trim()) {
        setError('Please enter a search query');
        return;
      }

      try {
        setSearching(true);
        setError(null);
        resetResults();

        // Build search request
        const searchRequest = {
          query: searchQuery,
          repositoryIds: [params.repoId],
          topK,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
        };

        // Execute search based on mode
        let searchResults: SearchResult[];
        switch (searchMode) {
          case 'semantic':
            searchResults = await apiClient.search.semantic(searchRequest);
            break;
          case 'keyword':
            searchResults = await apiClient.search.keyword(searchRequest);
            break;
          case 'hybrid':
            searchResults = await apiClient.search.hybrid(searchRequest);
            break;
          default:
            throw new Error(`Unknown search mode: ${searchMode}`);
        }

        // Update results
        setResults(searchResults);

        // Add to search history
        addToHistory({
          query: searchQuery,
          mode: searchMode,
          filters,
          resultCount: searchResults.length,
        });
      } catch (err: any) {
        console.error('Search failed:', err);
        setError(err.message || 'Failed to perform search');
      } finally {
        setSearching(false);
      }
    },
    [params.repoId, topK, filters, setSearching, setError, resetResults, setResults, addToHistory]
  );

  // Handle search submission
  const handleSearch = useCallback(
    (searchQuery: string) => {
      performSearch(searchQuery, mode);
    },
    [mode, performSearch]
  );

  // Handle mode change
  const handleModeChange = useCallback(
    (newMode: SearchMode) => {
      setMode(newMode);
      // Re-run search if there's a query
      if (query.trim()) {
        performSearch(query, newMode);
      }
    },
    [query, setMode, performSearch]
  );

  // Handle view in context
  const handleViewInContext = useCallback(
    (result: SearchResult) => {
      // Navigate to file viewer with line numbers
      router.push(
        `/repos/${params.repoId}/files?path=${encodeURIComponent(result.chunk.filePath)}&line=${result.chunk.startLine}`
      );
    },
    [params.repoId, router]
  );

  // Export results as JSON
  const exportAsJSON = useCallback(() => {
    try {
      setIsExporting(true);
      const exportData = {
        query,
        mode,
        filters,
        timestamp: new Date().toISOString(),
        totalResults: results.length,
        results: results.map((result) => ({
          score: result.score,
          filePath: result.chunk.filePath,
          startLine: result.chunk.startLine,
          endLine: result.chunk.endLine,
          language: result.chunk.language,
          content: result.chunk.content,
          highlights: result.highlights,
        })),
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `search-results-${Date.now()}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export JSON:', err);
      setError('Failed to export results as JSON');
    } finally {
      setIsExporting(false);
    }
  }, [query, mode, filters, results, setError]);

  // Export results as CSV
  const exportAsCSV = useCallback(() => {
    try {
      setIsExporting(true);
      // CSV headers
      const headers = ['Score', 'File Path', 'Start Line', 'End Line', 'Language', 'Content'];
      
      // CSV rows
      const rows = results.map((result) => [
        result.score.toFixed(4),
        result.chunk.filePath,
        result.chunk.startLine.toString(),
        result.chunk.endLine.toString(),
        result.chunk.language,
        `"${result.chunk.content.replace(/"/g, '""')}"`, // Escape quotes
      ]);

      // Combine headers and rows
      const csvContent = [
        headers.join(','),
        ...rows.map((row) => row.join(',')),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `search-results-${Date.now()}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export CSV:', err);
      setError('Failed to export results as CSV');
    } finally {
      setIsExporting(false);
    }
  }, [results, setError]);

  // Paginated results
  const paginatedResults = results.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );
  const totalPages = Math.ceil(results.length / pageSize);

  // Handle page change
  const handlePageChange = (page: number) => {
    setPage(page);
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-surface">
      <motion.div
        variants={fadeIn}
        initial="hidden"
        animate="visible"
        className="container mx-auto px-6 py-8"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-headline-lg text-text-primary mb-2">
            Search Code
          </h1>
          <p className="text-body-md text-text-secondary">
            Search through your repository using semantic, keyword, or hybrid search
          </p>
        </div>

        {/* Search Controls */}
        <div className="space-y-6 mb-8">
          {/* Mode Toggle */}
          <SearchModeToggle
            value={mode}
            onChange={handleModeChange}
            showDescriptions
            disabled={isSearching}
          />

          {/* Search Bar */}
          <SearchBar
            value={query}
            onChange={setQuery}
            onSearch={handleSearch}
            searchHistory={searchHistory}
            isSearching={isSearching}
            disabled={isSearching}
          />

          {/* Filters and Actions Row */}
          <div className="flex items-center justify-between gap-4">
            {/* Filter Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'transition-colors duration-150',
                showFilters && 'bg-surface-container-high'
              )}
            >
              <SlidersHorizontal className="w-4 h-4 mr-2" />
              Filters
              {Object.keys(filters).length > 0 && (
                <span className="ml-2 px-1.5 py-0.5 rounded-full bg-primary/10 text-primary text-label-sm">
                  {Object.keys(filters).length}
                </span>
              )}
            </Button>

            {/* Export Actions */}
            {results.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-body-sm text-text-tertiary">
                  {results.length} result{results.length !== 1 ? 's' : ''}
                </span>
                <div className="h-4 w-px bg-outline-variant/30" />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={exportAsJSON}
                  disabled={isExporting}
                >
                  <FileJson className="w-4 h-4 mr-2" />
                  JSON
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={exportAsCSV}
                  disabled={isExporting}
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  CSV
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6">
            <ErrorBanner
              message={error}
              onDismiss={() => setError(null)}
            />
          </div>
        )}

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.15 }}
                className="lg:col-span-1"
              >
                <SearchFilters
                  filters={filters}
                  onChange={setFilters}
                  disabled={isSearching}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results Area */}
          <div className={cn('lg:col-span-3', showFilters && 'lg:col-span-3')}>
            {/* Loading State */}
            {isSearching && (
              <div className="space-y-4">
                <LoadingSkeleton />
                <LoadingSkeleton />
                <LoadingSkeleton />
              </div>
            )}

            {/* Empty State - No Query */}
            {!isSearching && !query && results.length === 0 && (
              <EmptyState
                icon={SearchIcon}
                title="Start Searching"
                description="Enter a query above to search through your repository code"
              />
            )}

            {/* Empty State - No Results */}
            {!isSearching && query && results.length === 0 && !error && (
              <EmptyState
                icon={SearchIcon}
                title="No Results Found"
                description={`No results found for "${query}". Try adjusting your search query or filters.`}
              />
            )}

            {/* Results List */}
            {!isSearching && results.length > 0 && (
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="space-y-4"
              >
                {paginatedResults.map((result) => (
                  <SearchResultCard
                    key={result.chunk.id}
                    result={result}
                    onViewInContext={() => handleViewInContext(result)}
                  />
                ))}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 pt-6">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>

                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                        // Show first page, last page, current page, and pages around current
                        const showPage =
                          page === 1 ||
                          page === totalPages ||
                          Math.abs(page - currentPage) <= 1;

                        if (!showPage) {
                          // Show ellipsis
                          if (page === currentPage - 2 || page === currentPage + 2) {
                            return (
                              <span
                                key={page}
                                className="px-2 text-text-tertiary"
                              >
                                ...
                              </span>
                            );
                          }
                          return null;
                        }

                        return (
                          <Button
                            key={page}
                            variant={page === currentPage ? 'default' : 'ghost'}
                            size="sm"
                            onClick={() => handlePageChange(page)}
                            className="min-w-[2.5rem]"
                          >
                            {page}
                          </Button>
                        );
                      })}
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
