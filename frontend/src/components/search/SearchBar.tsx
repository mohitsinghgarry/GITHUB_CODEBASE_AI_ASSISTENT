/**
 * SearchBar Component
 * 
 * Search input with autocomplete suggestions from search history.
 * 
 * Features:
 * - Auto-expanding input
 * - Search history autocomplete
 * - Keyboard shortcuts (Enter to search, Escape to clear)
 * - Clear button
 * - Loading state
 */

'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Search, X, Loader2, Clock, TrendingUp } from 'lucide-react';
import { fadeInDown, staggerContainer, staggerItem } from '@/lib/animation-presets';

interface SearchBarProps {
  /**
   * Current search query
   */
  value: string;
  
  /**
   * Callback when query changes
   */
  onChange: (value: string) => void;
  
  /**
   * Callback when user submits search
   */
  onSearch: (query: string) => void;
  
  /**
   * Search history items for autocomplete
   */
  searchHistory?: SearchHistoryItem[];
  
  /**
   * Whether search is in progress
   */
  isSearching?: boolean;
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Whether the input is disabled
   */
  disabled?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface SearchHistoryItem {
  query: string;
  timestamp: string;
  resultCount: number;
}

export function SearchBar({
  value,
  onChange,
  onSearch,
  searchHistory = [],
  isSearching = false,
  placeholder = 'Search code...',
  disabled = false,
  className,
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Filter search history based on current input
  const filteredHistory = searchHistory
    .filter((item) =>
      item.query.toLowerCase().includes(value.toLowerCase()) &&
      item.query.toLowerCase() !== value.toLowerCase()
    )
    .slice(0, 5); // Show max 5 suggestions

  // Show suggestions when focused and has filtered results
  useEffect(() => {
    setShowSuggestions(isFocused && filteredHistory.length > 0 && value.length > 0);
  }, [isFocused, filteredHistory.length, value]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = () => {
    const trimmedQuery = value.trim();
    if (!trimmedQuery || isSearching || disabled) return;

    onSearch(trimmedQuery);
    setShowSuggestions(false);
    inputRef.current?.blur();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onChange('');
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

  const handleSuggestionClick = (query: string) => {
    onChange(query);
    setShowSuggestions(false);
    onSearch(query);
  };

  const handleClear = () => {
    onChange('');
    inputRef.current?.focus();
  };

  const canSearch = value.trim().length > 0 && !isSearching && !disabled;

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {/* Search Input Container */}
      <div
        className={cn(
          'flex items-center gap-3 px-4 py-3 rounded-xl',
          'bg-surface-container-low border border-outline-variant/15',
          'transition-all duration-150',
          isFocused && 'border-primary ring-2 ring-primary/20',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Search Icon */}
        <Search
          className={cn(
            'w-5 h-5 flex-shrink-0 transition-colors duration-150',
            isFocused ? 'text-primary' : 'text-text-tertiary'
          )}
        />

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            'flex-1 bg-transparent',
            'text-body-md text-text-primary placeholder:text-text-tertiary',
            'focus:outline-none',
            'disabled:cursor-not-allowed'
          )}
        />

        {/* Loading Indicator */}
        {isSearching && (
          <Loader2 className="w-5 h-5 text-primary animate-spin flex-shrink-0" />
        )}

        {/* Clear Button */}
        {value && !isSearching && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="h-8 w-8 flex-shrink-0"
          >
            <X className="w-4 h-4" />
          </Button>
        )}

        {/* Search Button */}
        <Button
          onClick={handleSearch}
          disabled={!canSearch}
          size="sm"
          className="flex-shrink-0"
        >
          Search
        </Button>
      </div>

      {/* Autocomplete Suggestions */}
      <AnimatePresence>
        {showSuggestions && (
          <motion.div
            variants={fadeInDown}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={cn(
              'absolute top-full left-0 right-0 mt-2 z-50',
              'bg-surface-container-high rounded-xl border border-outline-variant/15',
              'shadow-float overflow-hidden'
            )}
          >
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
              className="py-2"
            >
              {/* Header */}
              <div className="px-4 py-2 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-text-tertiary" />
                <span className="text-label-sm uppercase tracking-widest text-text-tertiary">
                  Recent Searches
                </span>
              </div>

              {/* Suggestions */}
              {filteredHistory.map((item, index) => (
                <motion.button
                  key={`${item.query}-${item.timestamp}`}
                  variants={staggerItem}
                  onClick={() => handleSuggestionClick(item.query)}
                  className={cn(
                    'w-full px-4 py-2.5 flex items-center gap-3',
                    'hover:bg-surface-container transition-colors duration-150',
                    'text-left'
                  )}
                >
                  <TrendingUp className="w-4 h-4 text-text-tertiary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-body-md text-text-primary truncate">
                      {item.query}
                    </p>
                    <p className="text-label-sm text-text-tertiary">
                      {item.resultCount} results
                    </p>
                  </div>
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Keyboard Hint */}
      {isFocused && !showSuggestions && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-full left-0 right-0 mt-2 px-1"
        >
          <p className="text-label-sm text-text-tertiary">
            <kbd className="px-1.5 py-0.5 rounded bg-surface-container-low border border-outline-variant/15 font-mono text-label-sm">
              Enter
            </kbd>{' '}
            to search,{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-surface-container-low border border-outline-variant/15 font-mono text-label-sm">
              Esc
            </kbd>{' '}
            to clear
          </p>
        </motion.div>
      )}
    </div>
  );
}
