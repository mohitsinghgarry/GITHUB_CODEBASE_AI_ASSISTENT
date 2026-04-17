/**
 * FileHeader Component
 * 
 * Displays file metadata including path, language, size, and line count.
 * Used at the top of file viewers and editors.
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  File,
  FileCode,
  FileJson,
  FileText,
  Copy,
  ExternalLink,
  Calendar,
  User,
} from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { useState } from 'react';

interface FileHeaderProps {
  /**
   * File path
   */
  path: string;
  
  /**
   * Programming language
   */
  language?: string;
  
  /**
   * File size in bytes
   */
  size?: number;
  
  /**
   * Number of lines
   */
  lineCount?: number;
  
  /**
   * Last modified date
   */
  lastModified?: Date | string;
  
  /**
   * Last modified by (author)
   */
  lastModifiedBy?: string;
  
  /**
   * Repository URL (for external link)
   */
  repositoryUrl?: string;
  
  /**
   * Show copy path button
   * @default true
   */
  showCopyPath?: boolean;
  
  /**
   * Show external link button
   * @default true
   */
  showExternalLink?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get file icon based on file extension
 */
function getFileIcon(path: string): typeof File {
  const ext = path.split('.').pop()?.toLowerCase();
  
  switch (ext) {
    case 'json':
    case 'jsonc':
      return FileJson;
    case 'md':
    case 'mdx':
    case 'txt':
      return FileText;
    case 'js':
    case 'jsx':
    case 'ts':
    case 'tsx':
    case 'py':
    case 'java':
    case 'go':
    case 'rs':
    case 'cpp':
    case 'c':
    case 'h':
    case 'hpp':
      return FileCode;
    default:
      return File;
  }
}

/**
 * Format file size
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Format date
 */
function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Get file name from path
 */
function getFileName(path: string): string {
  return path.split('/').pop() || path;
}

/**
 * Get directory path from full path
 */
function getDirectoryPath(path: string): string {
  const parts = path.split('/');
  parts.pop();
  return parts.join('/') || '/';
}

export function FileHeader({
  path,
  language,
  size,
  lineCount,
  lastModified,
  lastModifiedBy,
  repositoryUrl,
  showCopyPath = true,
  showExternalLink = true,
  className,
}: FileHeaderProps) {
  const [copied, setCopied] = useState(false);
  
  const Icon = getFileIcon(path);
  const fileName = getFileName(path);
  const directoryPath = getDirectoryPath(path);
  
  const handleCopyPath = async () => {
    try {
      await navigator.clipboard.writeText(path);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy path:', error);
    }
  };
  
  const handleExternalLink = () => {
    if (repositoryUrl) {
      window.open(`${repositoryUrl}/blob/main/${path}`, '_blank');
    }
  };
  
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn(
        'flex flex-col gap-4 p-6 bg-surface-container rounded-lg border border-outline/15',
        className
      )}
    >
      {/* Top Row: Icon, Name, Actions */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <Icon className="w-6 h-6 text-primary flex-shrink-0 mt-0.5" />
          
          <div className="flex-1 min-w-0">
            <h2 className="text-title-lg text-text-primary font-semibold truncate">
              {fileName}
            </h2>
            <p className="text-body-md text-text-secondary truncate mt-1">
              {directoryPath}
            </p>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {showCopyPath && (
            <motion.button
              onClick={handleCopyPath}
              className={cn(
                'p-2 rounded-md transition-colors',
                'hover:bg-surface-container-high',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20',
                copied && 'text-tertiary'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title={copied ? 'Copied!' : 'Copy path'}
            >
              <Copy className="w-4 h-4" />
            </motion.button>
          )}
          
          {showExternalLink && repositoryUrl && (
            <motion.button
              onClick={handleExternalLink}
              className={cn(
                'p-2 rounded-md transition-colors',
                'hover:bg-surface-container-high',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="View on GitHub"
            >
              <ExternalLink className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>
      
      {/* Metadata Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Language */}
        {language && (
          <div className="flex flex-col gap-1">
            <span className="text-label-md text-text-tertiary uppercase tracking-wider">
              Language
            </span>
            <StatusBadge
              status="info"
              label={language}
              variant="subtle"
              size="sm"
              animate={false}
            />
          </div>
        )}
        
        {/* Line Count */}
        {lineCount !== undefined && (
          <div className="flex flex-col gap-1">
            <span className="text-label-md text-text-tertiary uppercase tracking-wider">
              Lines
            </span>
            <span className="text-body-lg text-text-primary font-medium">
              {lineCount.toLocaleString()}
            </span>
          </div>
        )}
        
        {/* File Size */}
        {size !== undefined && (
          <div className="flex flex-col gap-1">
            <span className="text-label-md text-text-tertiary uppercase tracking-wider">
              Size
            </span>
            <span className="text-body-lg text-text-primary font-medium">
              {formatFileSize(size)}
            </span>
          </div>
        )}
        
        {/* Last Modified */}
        {lastModified && (
          <div className="flex flex-col gap-1">
            <span className="text-label-md text-text-tertiary uppercase tracking-wider">
              Modified
            </span>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-text-secondary" />
              <span className="text-body-md text-text-primary">
                {formatDate(lastModified)}
              </span>
            </div>
          </div>
        )}
        
        {/* Last Modified By */}
        {lastModifiedBy && (
          <div className="flex flex-col gap-1">
            <span className="text-label-md text-text-tertiary uppercase tracking-wider">
              Author
            </span>
            <div className="flex items-center gap-1.5">
              <User className="w-4 h-4 text-text-secondary" />
              <span className="text-body-md text-text-primary truncate">
                {lastModifiedBy}
              </span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
