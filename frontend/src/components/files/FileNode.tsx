/**
 * FileNode Component
 * 
 * Individual file or directory node in the file tree.
 * Supports expand/collapse animations and selection states.
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { treeNode, fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  File,
  FileCode,
  FileJson,
  FileText,
} from 'lucide-react';
import type { FileTreeNode } from './FileTree';

interface FileNodeProps {
  /**
   * Tree node data
   */
  node: FileTreeNode;
  
  /**
   * Callback when node is selected
   */
  onSelect?: (node: FileTreeNode) => void;
  
  /**
   * Currently selected file path
   */
  selectedPath?: string;
  
  /**
   * Nesting level (for indentation)
   */
  level: number;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get file icon based on file extension or language
 */
function getFileIcon(node: FileTreeNode): typeof File {
  if (node.type === 'directory') {
    return Folder;
  }
  
  const ext = node.name.split('.').pop()?.toLowerCase();
  
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
 * Get language badge color
 */
function getLanguageColor(language?: string): string {
  if (!language) return 'bg-surface-container-high text-text-tertiary';
  
  const colors: Record<string, string> = {
    typescript: 'bg-primary/20 text-primary',
    javascript: 'bg-secondary/20 text-secondary',
    python: 'bg-tertiary/20 text-tertiary',
    java: 'bg-error/20 text-error',
    go: 'bg-primary/20 text-primary',
    rust: 'bg-secondary/20 text-secondary',
    cpp: 'bg-primary/20 text-primary',
    c: 'bg-primary/20 text-primary',
  };
  
  return colors[language.toLowerCase()] || 'bg-surface-container-high text-text-tertiary';
}

/**
 * Format file size
 */
function formatFileSize(bytes?: number): string {
  if (!bytes) return '';
  
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileNode({
  node,
  onSelect,
  selectedPath,
  level,
  className,
}: FileNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isDirectory = node.type === 'directory';
  const hasChildren = isDirectory && node.children && node.children.length > 0;
  const isSelected = selectedPath === node.path;
  
  const Icon = getFileIcon(node);
  const DirectoryIcon = isExpanded ? FolderOpen : Folder;
  const ChevronIcon = isExpanded ? ChevronDown : ChevronRight;
  
  const handleClick = () => {
    if (isDirectory) {
      setIsExpanded(!isExpanded);
    }
    if (onSelect) {
      onSelect(node);
    }
  };
  
  return (
    <div className={cn('select-none', className)}>
      {/* Node Row */}
      <motion.button
        onClick={handleClick}
        className={cn(
          'w-full flex items-center gap-2 px-3 py-2 rounded-md',
          'text-left text-body-md transition-colors',
          'hover:bg-surface-container-high',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20',
          isSelected && 'bg-primary/10 text-primary hover:bg-primary/15',
          !isSelected && 'text-text-primary'
        )}
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
        whileHover={{ x: 2 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Chevron (for directories with children) */}
        {isDirectory && hasChildren && (
          <motion.div
            initial={false}
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronIcon className="w-4 h-4 text-text-tertiary flex-shrink-0" />
          </motion.div>
        )}
        
        {/* Spacer for files or empty directories */}
        {(!isDirectory || !hasChildren) && (
          <div className="w-4" />
        )}
        
        {/* Icon */}
        {isDirectory ? (
          <DirectoryIcon
            className={cn(
              'w-4 h-4 flex-shrink-0',
              isExpanded ? 'text-primary' : 'text-text-secondary'
            )}
          />
        ) : (
          <Icon className="w-4 h-4 text-text-secondary flex-shrink-0" />
        )}
        
        {/* Name */}
        <span className="flex-1 truncate font-medium">
          {node.name}
        </span>
        
        {/* Metadata */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Language Badge */}
          {node.type === 'file' && node.language && (
            <span
              className={cn(
                'px-2 py-0.5 rounded-full text-label-sm uppercase tracking-wider',
                getLanguageColor(node.language)
              )}
            >
              {node.language}
            </span>
          )}
          
          {/* Line Count */}
          {node.type === 'file' && node.lineCount && (
            <span className="text-label-md text-text-tertiary">
              {node.lineCount} lines
            </span>
          )}
          
          {/* File Size */}
          {node.type === 'file' && node.size && (
            <span className="text-label-md text-text-tertiary">
              {formatFileSize(node.size)}
            </span>
          )}
          
          {/* Directory Child Count */}
          {isDirectory && hasChildren && (
            <span className="text-label-md text-text-tertiary">
              {node.children!.length} {node.children!.length === 1 ? 'item' : 'items'}
            </span>
          )}
        </div>
      </motion.button>
      
      {/* Children (for directories) */}
      {isDirectory && hasChildren && (
        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              variants={treeNode}
              initial="collapsed"
              animate="expanded"
              exit="collapsed"
              className="overflow-hidden"
            >
              <div className="space-y-1 mt-1">
                {node.children!.map((child) => (
                  <FileNode
                    key={child.path}
                    node={child}
                    onSelect={onSelect}
                    selectedPath={selectedPath}
                    level={level + 1}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  );
}
