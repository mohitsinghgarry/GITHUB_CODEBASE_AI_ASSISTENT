'use client';

import { useState, useEffect } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { api, SearchResult } from '@/lib/api';

type SearchMode = 'semantic' | 'keyword' | 'hybrid';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<SearchMode>('hybrid');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setHasSearched(true);

    try {
      let searchResults;
      
      if (searchMode === 'semantic') {
        searchResults = await api.searchSemantic({ query, top_k: 20 });
      } else if (searchMode === 'keyword') {
        searchResults = await api.searchKeyword({ query, top_k: 20, mode: 'case_insensitive' });
      } else {
        searchResults = await api.searchHybrid({ query, top_k: 20, bm25_weight: 0.5 });
      }

      setResults(searchResults.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Search Head */}
        <div className="mb-12">
          <form onSubmit={handleSearch} className="flex flex-col gap-6">
            <div className="relative group">
              <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-primary">search</span>
              </div>
              <input
                className="w-full h-[56px] pl-14 pr-[200px] bg-surface-container-low border border-outline-variant/15 rounded-xl text-on-surface placeholder-outline focus:ring-1 focus:ring-primary focus:border-primary/50 transition-all text-lg shadow-2xl shadow-black/50"
                placeholder="Search for code, concepts, or patterns..."
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isSearching}
              />
              <div className="absolute right-3 inset-y-0 flex items-center">
                <div className="flex p-1 bg-surface-container-highest rounded-lg border border-outline-variant/10">
                  <button
                    type="button"
                    onClick={() => setSearchMode('semantic')}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                      searchMode === 'semantic'
                        ? 'bg-primary text-on-primary'
                        : 'text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Semantic
                  </button>
                  <button
                    type="button"
                    onClick={() => setSearchMode('keyword')}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                      searchMode === 'keyword'
                        ? 'bg-primary text-on-primary'
                        : 'text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Keyword
                  </button>
                  <button
                    type="button"
                    onClick={() => setSearchMode('hybrid')}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                      searchMode === 'hybrid'
                        ? 'bg-primary text-on-primary'
                        : 'text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Hybrid
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-4 bg-error/10 border border-error/20 rounded-xl flex items-start gap-3">
            <span className="material-symbols-outlined text-error">error</span>
            <div className="flex-1">
              <p className="text-error font-medium">Search failed</p>
              <p className="text-error/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Search Results */}
        {hasSearched && (
          <section className="mb-16">
            <h3 className="text-sm font-semibold text-outline uppercase tracking-widest mb-6 px-1">
              {isSearching ? 'Searching...' : `${results.length} Results`}
            </h3>
            
            {isSearching ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-12">
                <span className="material-symbols-outlined text-outline text-5xl mb-4">search_off</span>
                <p className="text-on-surface-variant">No results found for &quot;{query}&quot;</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className="p-6 bg-surface-container hover:bg-surface-container-high border border-outline-variant/5 rounded-xl transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary">description</span>
                        <div>
                          <p className="text-on-surface font-medium">{result.chunk.file_path}</p>
                          <p className="text-xs text-on-surface-variant mt-1">
                            Lines {result.chunk.start_line}-{result.chunk.end_line} • {result.chunk.language}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-tertiary">
                          {Math.round(result.score * 100)}% match
                        </span>
                      </div>
                    </div>
                    
                    <div className="bg-surface-container-lowest rounded-lg p-4 font-mono text-sm overflow-x-auto">
                      <pre className="text-on-surface-variant whitespace-pre-wrap">
                        {result.chunk.content}
                      </pre>
                    </div>

                    {result.matches && result.matches.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {result.matches.slice(0, 3).map((match, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-md font-mono"
                          >
                            Line {match.line_number}: {match.matched_text}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Search Tips - Only show when no search has been performed */}
        {!hasSearched && (
          <section>
            <h3 className="text-sm font-semibold text-outline uppercase tracking-widest mb-6 px-1">Search Tips</h3>
            <div className="grid grid-cols-1 gap-6">
              <div className="flex items-start gap-4 p-6 bg-surface-container-low border-l-2 border-primary/40 rounded-r-xl">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <span className="material-symbols-outlined text-primary text-xl">lightbulb</span>
                </div>
                <div>
                  <h4 className="text-on-surface font-medium mb-1">Semantic Search</h4>
                  <p className="text-on-surface-variant text-sm leading-relaxed">
                    Describe what you want to find in plain English. For example, &quot;find where the database connection is initialized&quot; or &quot;how do we handle error logging&quot;.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-6 bg-surface-container-low border-l-2 border-secondary/40 rounded-r-xl">
                <div className="p-2 bg-secondary/10 rounded-lg">
                  <span className="material-symbols-outlined text-secondary text-xl">code</span>
                </div>
                <div>
                  <h4 className="text-on-surface font-medium mb-1">Hybrid Search</h4>
                  <p className="text-on-surface-variant text-sm leading-relaxed">
                    Combines semantic understanding with keyword matching for the best results. Great for most searches.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </AppShell>
  );
}
