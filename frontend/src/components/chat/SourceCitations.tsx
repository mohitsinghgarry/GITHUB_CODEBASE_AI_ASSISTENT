/**
 * SourceCitations Component
 * 
 * Displays clickable file chips for source code citations.
 * Features:
 * - Clickable file chips
 * - File path and line number display
 * - Hover effects
 * - Compact layout
 */

'use client';

import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { FileCode, ExternalLink } from 'lucide-react';
import type { Citation } from '@/types';

interface SourceCitationsProps {
  /**
   * Array of source citations
   */
  citations: Citation[];
  
  /**
   * Callback when a citation is clicked
   */
  onCitationClick?: (citation: Citation) => void;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Extract filename from file path
 */
function getFileName(filePath: string): string {
  const parts = filePath.split('/');
  return parts[parts.length - 1] || filePath;
}

/**
 * Get file extension
 */
function getFileExtension(filePath: string): string {
  const fileName = getFileName(filePath);
  const parts = fileName.split('.');
  return parts.length > 1 ? parts[parts.length - 1] : '';
}

/**
 * Get language color based on file extension
 */
function getLanguageColor(extension: string): string {
  const colorMap: Record<string, string> = {
    js: 'text-yellow-400',
    ts: 'text-blue-400',
    jsx: 'text-cyan-400',
    tsx: 'text-cyan-400',
    py: 'text-blue-500',
    java: 'text-red-400',
    cpp: 'text-pink-400',
    c: 'text-purple-400',
    go: 'text-cyan-500',
    rs: 'text-orange-400',
    rb: 'text-red-500',
    php: 'text-indigo-400',
    swift: 'text-orange-500',
    kt: 'text-purple-500',
    cs: 'text-green-500',
    html: 'text-orange-400',
    css: 'text-blue-400',
    scss: 'text-pink-400',
    json: 'text-yellow-500',
    yaml: 'text-purple-400',
    yml: 'text-purple-400',
    md: 'text-gray-400',
    sql: 'text-orange-500',
    sh: 'text-green-400',
    bash: 'text-green-400',
  };
  
  return colorMap[extension.toLowerCase()] || 'text-text-secondary';
}

export function SourceCitations({
  citations,
  onCitationClick,
  className,
}: SourceCitationsProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <FileCode className="w-3.5 h-3.5 text-text-tertiary" />
        <span className="text-label-sm text-text-tertiary uppercase tracking-wider">
          Sources ({citations.length})
        </span>
      </div>

      {/* Citations */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="flex flex-wrap gap-2"
      >
        {citations.map((citation, index) => {
          const fileName = getFileName(citation.filePath);
          const extension = getFileExtension(citation.filePath);
          const languageColor = getLanguageColor(extension);
          const lineRange =
            citation.startLine === citation.endLine
              ? `L${citation.startLine}`
              : `L${citation.startLine}-${citation.endLine}`;

          return (
            <motion.button
              key={citation.chunkId}
              variants={staggerItem}
              onClick={() => onCitationClick?.(citation)}
              className={cn(
                'group flex items-center gap-2 px-3 py-1.5 rounded-lg',
                'bg-surface-container-low border border-outline-variant/15',
                'hover:bg-surface-container-high hover:border-outline-variant/30',
                'transition-all duration-150',
                'focus:outline-none focus:ring-2 focus:ring-primary/20'
              )}
            >
              {/* File Icon */}
              <FileCode className={cn('w-3.5 h-3.5', languageColor)} />
              
              {/* File Info */}
              <div className="flex items-center gap-1.5 text-label-sm">
                <span className="text-text-primary font-medium">
                  {fileName}
                </span>
                <span className="text-text-tertiary">
                  {lineRange}
                </span>
              </div>

              {/* External Link Icon */}
              <ExternalLink className="w-3 h-3 text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.button>
          );
        })}
      </motion.div>
    </div>
  );
}
