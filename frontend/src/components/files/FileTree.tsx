/**
 * FileTree Component
 * 
 * Hierarchical file tree structure with expand/collapse functionality.
 * Displays repository files in a tree view with language filtering.
 */

'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { FileNode } from './FileNode';
import { LanguageFilter } from './LanguageFilter';
import { Folder, File } from 'lucide-react';

export interface FileTreeNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  language?: string;
  size?: number;
  children?: FileTreeNode[];
  lineCount?: number;
}

interface FileTreeProps {
  /**
   * Root nodes of the file tree
   */
  nodes: FileTreeNode[];
  
  /**
   * Callback when a file is selected
   */
  onFileSelect?: (node: FileTreeNode) => void;
  
  /**
   * Currently selected file path
   */
  selectedPath?: string;
  
  /**
   * Show language filter
   * @default true
   */
  showLanguageFilter?: boolean;
  
  /**
   * Available languages in the repository
   */
  languages?: string[];
  
  /**
   * Loading state
   */
  isLoading?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Build a flat map of all nodes for quick lookup
 */
function buildNodeMap(nodes: FileTreeNode[]): Map<string, FileTreeNode> {
  const map = new Map<string, FileTreeNode>();
  
  function traverse(node: FileTreeNode) {
    map.set(node.path, node);
    if (node.children) {
      node.children.forEach(traverse);
    }
  }
  
  nodes.forEach(traverse);
  return map;
}

/**
 * Filter tree nodes by language
 */
function filterTreeByLanguage(
  nodes: FileTreeNode[],
  selectedLanguages: string[]
): FileTreeNode[] {
  if (selectedLanguages.length === 0) {
    return nodes;
  }
  
  function filterNode(node: FileTreeNode): FileTreeNode | null {
    if (node.type === 'file') {
      // Include file if its language is selected
      if (node.language && selectedLanguages.includes(node.language)) {
        return node;
      }
      return null;
    }
    
    // For directories, recursively filter children
    if (node.children) {
      const filteredChildren = node.children
        .map(filterNode)
        .filter((child): child is FileTreeNode => child !== null);
      
      // Include directory if it has any matching children
      if (filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren,
        };
      }
    }
    
    return null;
  }
  
  return nodes
    .map(filterNode)
    .filter((node): node is FileTreeNode => node !== null);
}

/**
 * Extract unique languages from tree
 */
function extractLanguages(nodes: FileTreeNode[]): string[] {
  const languages = new Set<string>();
  
  function traverse(node: FileTreeNode) {
    if (node.type === 'file' && node.language) {
      languages.add(node.language);
    }
    if (node.children) {
      node.children.forEach(traverse);
    }
  }
  
  nodes.forEach(traverse);
  return Array.from(languages).sort();
}

/**
 * Count total files and directories
 */
function countNodes(nodes: FileTreeNode[]): { files: number; directories: number } {
  let files = 0;
  let directories = 0;
  
  function traverse(node: FileTreeNode) {
    if (node.type === 'file') {
      files++;
    } else {
      directories++;
    }
    if (node.children) {
      node.children.forEach(traverse);
    }
  }
  
  nodes.forEach(traverse);
  return { files, directories };
}

export function FileTree({
  nodes,
  onFileSelect,
  selectedPath,
  showLanguageFilter = true,
  languages: providedLanguages,
  isLoading = false,
  className,
}: FileTreeProps) {
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  
  // Extract languages from tree if not provided
  const availableLanguages = useMemo(
    () => providedLanguages || extractLanguages(nodes),
    [providedLanguages, nodes]
  );
  
  // Filter tree by selected languages
  const filteredNodes = useMemo(
    () => filterTreeByLanguage(nodes, selectedLanguages),
    [nodes, selectedLanguages]
  );
  
  // Count nodes
  const { files, directories } = useMemo(
    () => countNodes(filteredNodes),
    [filteredNodes]
  );
  
  // Build node map for quick lookup
  const nodeMap = useMemo(() => buildNodeMap(nodes), [nodes]);
  
  const handleFileSelect = (node: FileTreeNode) => {
    if (node.type === 'file' && onFileSelect) {
      onFileSelect(node);
    }
  };
  
  if (isLoading) {
    return (
      <div className={cn('flex flex-col gap-4', className)}>
        {showLanguageFilter && (
          <div className="h-10 bg-surface-container animate-pulse rounded-md" />
        )}
        <div className="space-y-2">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="h-8 bg-surface-container animate-pulse rounded-md"
              style={{ width: `${60 + Math.random() * 40}%` }}
            />
          ))}
        </div>
      </div>
    );
  }
  
  if (nodes.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <Folder className="w-12 h-12 text-text-tertiary mb-4" />
        <p className="text-body-md text-text-secondary">No files found</p>
      </div>
    );
  }
  
  return (
    <div className={cn('flex flex-col gap-4', className)}>
      {/* Language Filter */}
      {showLanguageFilter && availableLanguages.length > 0 && (
        <LanguageFilter
          languages={availableLanguages}
          selectedLanguages={selectedLanguages}
          onSelectionChange={setSelectedLanguages}
        />
      )}
      
      {/* File Count Summary */}
      <div className="flex items-center gap-4 text-label-md text-text-tertiary">
        <div className="flex items-center gap-1.5">
          <Folder className="w-4 h-4" />
          <span>{directories} {directories === 1 ? 'folder' : 'folders'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <File className="w-4 h-4" />
          <span>{files} {files === 1 ? 'file' : 'files'}</span>
        </div>
      </div>
      
      {/* Tree Nodes */}
      {filteredNodes.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8">
          <File className="w-10 h-10 text-text-tertiary mb-3" />
          <p className="text-body-md text-text-secondary">
            No files match the selected languages
          </p>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-1"
        >
          <AnimatePresence mode="popLayout">
            {filteredNodes.map((node) => (
              <motion.div
                key={node.path}
                variants={staggerItem}
                layout
              >
                <FileNode
                  node={node}
                  onSelect={handleFileSelect}
                  selectedPath={selectedPath}
                  level={0}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
}
