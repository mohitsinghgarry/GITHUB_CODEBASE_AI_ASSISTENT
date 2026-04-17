/**
 * LanguageFilter Component
 * 
 * Multi-select filter for programming languages.
 * Displays language chips with selection states and animations.
 */

'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { fadeIn, scaleIn, staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Filter, X, Check } from 'lucide-react';
import { useState } from 'react';

interface LanguageFilterProps {
  /**
   * Available languages
   */
  languages: string[];
  
  /**
   * Currently selected languages
   */
  selectedLanguages: string[];
  
  /**
   * Callback when selection changes
   */
  onSelectionChange: (languages: string[]) => void;
  
  /**
   * Show filter icon
   * @default true
   */
  showIcon?: boolean;
  
  /**
   * Show clear all button
   * @default true
   */
  showClearAll?: boolean;
  
  /**
   * Show select all button
   * @default true
   */
  showSelectAll?: boolean;
  
  /**
   * Collapsible
   * @default false
   */
  collapsible?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get language display name
 */
function getLanguageDisplayName(language: string): string {
  const displayNames: Record<string, string> = {
    typescript: 'TypeScript',
    javascript: 'JavaScript',
    python: 'Python',
    java: 'Java',
    go: 'Go',
    rust: 'Rust',
    cpp: 'C++',
    c: 'C',
    csharp: 'C#',
    ruby: 'Ruby',
    php: 'PHP',
    swift: 'Swift',
    kotlin: 'Kotlin',
    scala: 'Scala',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    markdown: 'Markdown',
    sql: 'SQL',
    shell: 'Shell',
    bash: 'Bash',
  };
  
  return displayNames[language.toLowerCase()] || language;
}

/**
 * Get language color
 */
function getLanguageColor(language: string): string {
  const colors: Record<string, string> = {
    typescript: 'bg-primary/20 text-primary border-primary/30',
    javascript: 'bg-secondary/20 text-secondary border-secondary/30',
    python: 'bg-tertiary/20 text-tertiary border-tertiary/30',
    java: 'bg-error/20 text-error border-error/30',
    go: 'bg-primary/20 text-primary border-primary/30',
    rust: 'bg-secondary/20 text-secondary border-secondary/30',
    cpp: 'bg-primary/20 text-primary border-primary/30',
    c: 'bg-primary/20 text-primary border-primary/30',
  };
  
  return colors[language.toLowerCase()] || 'bg-surface-container-high text-text-secondary border-outline/30';
}

export function LanguageFilter({
  languages,
  selectedLanguages,
  onSelectionChange,
  showIcon = true,
  showClearAll = true,
  showSelectAll = true,
  collapsible = false,
  className,
}: LanguageFilterProps) {
  const [isExpanded, setIsExpanded] = useState(!collapsible);
  
  const handleToggleLanguage = (language: string) => {
    if (selectedLanguages.includes(language)) {
      onSelectionChange(selectedLanguages.filter((l) => l !== language));
    } else {
      onSelectionChange([...selectedLanguages, language]);
    }
  };
  
  const handleSelectAll = () => {
    onSelectionChange(languages);
  };
  
  const handleClearAll = () => {
    onSelectionChange([]);
  };
  
  const allSelected = selectedLanguages.length === languages.length;
  const noneSelected = selectedLanguages.length === 0;
  
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className={cn(
        'p-4 bg-surface-container rounded-lg border border-outline/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {showIcon && <Filter className="w-4 h-4 text-text-secondary" />}
          <h3 className="text-label-lg text-text-primary font-semibold uppercase tracking-wider">
            Filter by Language
          </h3>
          {!noneSelected && (
            <motion.span
              variants={scaleIn}
              initial="hidden"
              animate="visible"
              className="px-2 py-0.5 bg-primary/20 text-primary rounded-full text-label-sm"
            >
              {selectedLanguages.length}
            </motion.span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* Select All */}
          {showSelectAll && !allSelected && (
            <motion.button
              onClick={handleSelectAll}
              className={cn(
                'text-label-md text-primary hover:text-primary-dim',
                'transition-colors',
                'focus:outline-none focus-visible:underline'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Select All
            </motion.button>
          )}
          
          {/* Clear All */}
          {showClearAll && !noneSelected && (
            <motion.button
              onClick={handleClearAll}
              className={cn(
                'text-label-md text-text-secondary hover:text-text-primary',
                'transition-colors',
                'focus:outline-none focus-visible:underline'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Clear All
            </motion.button>
          )}
          
          {/* Collapse Toggle */}
          {collapsible && (
            <motion.button
              onClick={() => setIsExpanded(!isExpanded)}
              className={cn(
                'p-1 rounded-md transition-colors',
                'hover:bg-surface-container-high',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <X
                className={cn(
                  'w-4 h-4 text-text-secondary transition-transform',
                  isExpanded ? 'rotate-0' : 'rotate-45'
                )}
              />
            </motion.button>
          )}
        </div>
      </div>
      
      {/* Language Chips */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={collapsible ? { opacity: 0, height: 0 } : false}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
              className="flex flex-wrap gap-2"
            >
              {languages.map((language) => {
                const isSelected = selectedLanguages.includes(language);
                
                return (
                  <motion.button
                    key={language}
                    variants={staggerItem}
                    onClick={() => handleToggleLanguage(language)}
                    className={cn(
                      'flex items-center gap-1.5 px-3 py-1.5 rounded-full',
                      'text-label-md font-medium transition-all',
                      'border',
                      'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20',
                      isSelected
                        ? getLanguageColor(language)
                        : 'bg-surface-container-low text-text-secondary border-outline/20 hover:bg-surface-container-high'
                    )}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isSelected && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                      >
                        <Check className="w-3.5 h-3.5" />
                      </motion.div>
                    )}
                    <span>{getLanguageDisplayName(language)}</span>
                  </motion.button>
                );
              })}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
