/**
 * SearchResultCard Component
 * 
 * Card displaying a single search result with file info and code preview.
 * 
 * Features:
 * - File metadata (path, language, line numbers)
 * - Syntax-highlighted code preview
 * - Relevance score indicator
 * - Highlighted matches
 * - Click to view in context
 * - Copy code button
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { staggerItem, hoverScale } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { CopyButton } from '@/components/common/CopyButton';
import {
  FileCode,
  ExternalLink,
  TrendingUp,
  Hash,
} from 'lucide-react';
import type { SearchResult } from '@/types';

interface SearchResultCardProps {
  /**
   * Search result data
   */
  result: SearchResult;
  
  /**
   * Click handler to view in context
   */
  onViewInContext?: () => void;
  
  /**
   * Show relevance score
   * @default true
   */
  showScore?: boolean;
  
  /**
   * Maximum lines to show in preview
   * @default 10
   */
  maxPreviewLines?: number;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

export function SearchResultCard({
  result,
  onViewInContext,
  showScore = true,
  maxPreviewLines = 10,
  className,
}: SearchResultCardProps) {
  const { chunk, score, highlights } = result;
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate line count
  const lineCount = chunk.endLine - chunk.startLine + 1;
  const shouldTruncate = lineCount > maxPreviewLines && !isExpanded;

  // Get preview content
  const lines = chunk.content.split('\n');
  const previewLines = shouldTruncate ? lines.slice(0, maxPreviewLines) : lines;
  const previewContent = previewLines.join('\n');

  // Format score as percentage
  const scorePercent = Math.round(score * 100);

  // Get language badge color
  const getLanguageColor = (language: string) => {
    const colors: Record<string, string> = {
      python: 'bg-tertiary/10 text-tertiary',
      javascript: 'bg-secondary/10 text-secondary',
      typescript: 'bg-primary/10 text-primary',
      java: 'bg-error/10 text-error',
      go: 'bg-tertiary/10 text-tertiary',
      rust: 'bg-error/10 text-error',
      cpp: 'bg-primary/10 text-primary',
      c: 'bg-primary/10 text-primary',
    };
    return colors[language.toLowerCase()] || 'bg-surface-container-high text-text-secondary';
  };

  return (
    <motion.div
      variants={staggerItem}
      whileHover="hover"
      className={cn(
        'bg-surface-container rounded-xl border border-outline-variant/15',
        'transition-all duration-150',
        'hover:bg-surface-container-high hover:border-outline-variant/30',
        className
      )}
    >
      <motion.div variants={hoverScale}>
        {/* Header */}
        <div className="p-5 pb-4 border-b border-outline-variant/15">
          <div className="flex items-start justify-between gap-4">
            {/* File Info */}
            <div className="flex items-start gap-3 flex-1 min-w-0">
              {/* Icon */}
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
                <FileCode className="w-5 h-5 text-primary" />
              </div>

              {/* Path and Metadata */}
              <div className="flex-1 min-w-0">
                <h3 className="text-title-sm text-text-primary font-medium truncate">
                  {chunk.filePath.split('/').pop()}
                </h3>
                <p className="text-body-sm text-text-tertiary mt-0.5 truncate font-mono">
                  {chunk.filePath}
                </p>
                
                {/* Metadata Row */}
                <div className="flex flex-wrap items-center gap-3 mt-2">
                  {/* Language Badge */}
                  <span
                    className={cn(
                      'px-2 py-0.5 rounded text-label-sm font-medium',
                      getLanguageColor(chunk.language)
                    )}
                  >
                    {chunk.language}
                  </span>

                  {/* Line Numbers */}
                  <div className="flex items-center gap-1.5 text-body-sm text-text-tertiary">
                    <Hash className="w-3.5 h-3.5" />
                    <span className="font-mono">
                      {chunk.startLine}–{chunk.endLine}
                    </span>
                  </div>

                  {/* Score */}
                  {showScore && (
                    <div className="flex items-center gap-1.5 text-body-sm text-text-tertiary">
                      <TrendingUp className="w-3.5 h-3.5" />
                      <span>{scorePercent}% match</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <CopyButton text={chunk.content} size="sm" />
              {onViewInContext && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onViewInContext}
                >
                  <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                  View
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Code Preview */}
        <div className="p-5 pt-4">
          <div className="relative">
            {/* Code Block */}
            <pre
              className={cn(
                'bg-surface-container-lowest rounded-lg p-4 overflow-x-auto',
                'border border-outline-variant/15'
              )}
            >
              <code className="text-body-sm font-mono text-text-primary">
                {previewContent}
              </code>
            </pre>

            {/* Expand/Collapse Button */}
            {lineCount > maxPreviewLines && (
              <div className="mt-3 flex justify-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                >
                  {isExpanded ? 'Show Less' : `Show ${lineCount - maxPreviewLines} More Lines`}
                </Button>
              </div>
            )}
          </div>

          {/* Highlights */}
          {highlights && highlights.length > 0 && (
            <div className="mt-4 pt-4 border-t border-outline-variant/15">
              <p className="text-label-sm uppercase tracking-widest text-text-tertiary mb-2">
                Matched Terms
              </p>
              <div className="flex flex-wrap gap-2">
                {highlights.map((highlight, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 rounded bg-primary/10 text-primary text-label-md font-mono"
                  >
                    {highlight}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
