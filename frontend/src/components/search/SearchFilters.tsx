/**
 * SearchFilters Component
 * 
 * Filter panel for search results with language and directory filters.
 * 
 * Features:
 * - Multi-select language filter
 * - Directory path filter
 * - File extension filter
 * - Clear all filters button
 * - Collapsible sections
 * - Active filter count badge
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Filter,
  X,
  ChevronDown,
  Code,
  FolderTree,
  FileType,
} from 'lucide-react';
import { fadeInUp, expand } from '@/lib/animation-presets';
import type { SearchFilters as SearchFiltersType } from '@/types';

interface SearchFiltersProps {
  /**
   * Current filter values
   */
  filters: SearchFiltersType;
  
  /**
   * Callback when filters change
   */
  onChange: (filters: SearchFiltersType) => void;
  
  /**
   * Available languages (from indexed repositories)
   */
  availableLanguages?: string[];
  
  /**
   * Available file extensions
   */
  availableExtensions?: string[];
  
  /**
   * Whether filters are disabled
   */
  disabled?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

const commonLanguages = [
  'Python',
  'JavaScript',
  'TypeScript',
  'Java',
  'Go',
  'Rust',
  'C++',
  'C',
  'Ruby',
  'PHP',
];

const commonExtensions = [
  '.py',
  '.js',
  '.ts',
  '.jsx',
  '.tsx',
  '.java',
  '.go',
  '.rs',
  '.cpp',
  '.c',
  '.rb',
  '.php',
];

export function SearchFilters({
  filters,
  onChange,
  availableLanguages = commonLanguages,
  availableExtensions = commonExtensions,
  disabled = false,
  className,
}: SearchFiltersProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['languages'])
  );

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const handleLanguageToggle = (language: string) => {
    const currentLanguages = filters.language || [];
    const newLanguages = currentLanguages.includes(language)
      ? currentLanguages.filter((l) => l !== language)
      : [...currentLanguages, language];

    onChange({
      ...filters,
      language: newLanguages.length > 0 ? newLanguages : undefined,
    });
  };

  const handleExtensionToggle = (extension: string) => {
    const currentExtensions = filters.fileExtension || [];
    const newExtensions = currentExtensions.includes(extension)
      ? currentExtensions.filter((e) => e !== extension)
      : [...currentExtensions, extension];

    onChange({
      ...filters,
      fileExtension: newExtensions.length > 0 ? newExtensions : undefined,
    });
  };

  const handleDirectoryChange = (directory: string) => {
    onChange({
      ...filters,
      directoryPath: directory || undefined,
    });
  };

  const handleClearAll = () => {
    onChange({});
  };

  // Count active filters
  const activeFilterCount =
    (filters.language?.length || 0) +
    (filters.fileExtension?.length || 0) +
    (filters.directoryPath ? 1 : 0);

  return (
    <div
      className={cn(
        'bg-surface-container rounded-xl border border-outline-variant/15 overflow-hidden',
        disabled && 'opacity-50 pointer-events-none',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-outline-variant/15">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-tertiary" />
            <h3 className="text-title-sm text-text-primary font-medium">
              Filters
            </h3>
            {activeFilterCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-label-sm font-medium">
                {activeFilterCount}
              </span>
            )}
          </div>

          {activeFilterCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearAll}
              className="text-text-tertiary hover:text-text-primary"
            >
              Clear All
            </Button>
          )}
        </div>
      </div>

      {/* Filter Sections */}
      <div className="divide-y divide-outline-variant/15">
        {/* Languages Filter */}
        <div>
          <button
            onClick={() => toggleSection('languages')}
            className={cn(
              'w-full px-4 py-3 flex items-center justify-between',
              'hover:bg-surface-container-high transition-colors duration-150'
            )}
          >
            <div className="flex items-center gap-2">
              <Code className="w-4 h-4 text-text-tertiary" />
              <span className="text-body-md text-text-primary font-medium">
                Languages
              </span>
              {filters.language && filters.language.length > 0 && (
                <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary text-label-sm">
                  {filters.language.length}
                </span>
              )}
            </div>
            <ChevronDown
              className={cn(
                'w-4 h-4 text-text-tertiary transition-transform duration-150',
                expandedSections.has('languages') && 'rotate-180'
              )}
            />
          </button>

          <AnimatePresence initial={false}>
            {expandedSections.has('languages') && (
              <motion.div
                variants={expand}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
              >
                <div className="px-4 pb-3 space-y-2">
                  {availableLanguages.map((language) => {
                    const isSelected = filters.language?.includes(language);
                    return (
                      <label
                        key={language}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
                          'hover:bg-surface-container-high transition-colors duration-150',
                          isSelected && 'bg-primary/5'
                        )}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleLanguageToggle(language)}
                          className="w-4 h-4 rounded border-outline-variant/30 text-primary focus:ring-2 focus:ring-primary/20"
                        />
                        <span className="text-body-md text-text-primary">
                          {language}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* File Extensions Filter */}
        <div>
          <button
            onClick={() => toggleSection('extensions')}
            className={cn(
              'w-full px-4 py-3 flex items-center justify-between',
              'hover:bg-surface-container-high transition-colors duration-150'
            )}
          >
            <div className="flex items-center gap-2">
              <FileType className="w-4 h-4 text-text-tertiary" />
              <span className="text-body-md text-text-primary font-medium">
                File Extensions
              </span>
              {filters.fileExtension && filters.fileExtension.length > 0 && (
                <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary text-label-sm">
                  {filters.fileExtension.length}
                </span>
              )}
            </div>
            <ChevronDown
              className={cn(
                'w-4 h-4 text-text-tertiary transition-transform duration-150',
                expandedSections.has('extensions') && 'rotate-180'
              )}
            />
          </button>

          <AnimatePresence initial={false}>
            {expandedSections.has('extensions') && (
              <motion.div
                variants={expand}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
              >
                <div className="px-4 pb-3 space-y-2">
                  {availableExtensions.map((extension) => {
                    const isSelected = filters.fileExtension?.includes(extension);
                    return (
                      <label
                        key={extension}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
                          'hover:bg-surface-container-high transition-colors duration-150',
                          isSelected && 'bg-primary/5'
                        )}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleExtensionToggle(extension)}
                          className="w-4 h-4 rounded border-outline-variant/30 text-primary focus:ring-2 focus:ring-primary/20"
                        />
                        <span className="text-body-md text-text-primary font-mono">
                          {extension}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Directory Path Filter */}
        <div>
          <button
            onClick={() => toggleSection('directory')}
            className={cn(
              'w-full px-4 py-3 flex items-center justify-between',
              'hover:bg-surface-container-high transition-colors duration-150'
            )}
          >
            <div className="flex items-center gap-2">
              <FolderTree className="w-4 h-4 text-text-tertiary" />
              <span className="text-body-md text-text-primary font-medium">
                Directory Path
              </span>
              {filters.directoryPath && (
                <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary text-label-sm">
                  1
                </span>
              )}
            </div>
            <ChevronDown
              className={cn(
                'w-4 h-4 text-text-tertiary transition-transform duration-150',
                expandedSections.has('directory') && 'rotate-180'
              )}
            />
          </button>

          <AnimatePresence initial={false}>
            {expandedSections.has('directory') && (
              <motion.div
                variants={expand}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
              >
                <div className="px-4 pb-3">
                  <div className="relative">
                    <input
                      type="text"
                      value={filters.directoryPath || ''}
                      onChange={(e) => handleDirectoryChange(e.target.value)}
                      placeholder="e.g., src/components"
                      className={cn(
                        'w-full px-3 py-2 rounded-lg',
                        'bg-surface-container-low border border-outline-variant/15',
                        'text-body-md text-text-primary placeholder:text-text-tertiary',
                        'focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20',
                        'font-mono'
                      )}
                    />
                    {filters.directoryPath && (
                      <button
                        onClick={() => handleDirectoryChange('')}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-surface-container-high rounded"
                      >
                        <X className="w-3.5 h-3.5 text-text-tertiary" />
                      </button>
                    )}
                  </div>
                  <p className="mt-2 text-label-sm text-text-tertiary">
                    Filter results by directory path
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
