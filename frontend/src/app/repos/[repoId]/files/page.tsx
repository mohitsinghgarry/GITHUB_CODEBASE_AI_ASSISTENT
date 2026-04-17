/**
 * File Explorer Page
 * 
 * Browse repository files in a tree structure with:
 * - Hierarchical file tree
 * - Language filtering
 * - File search
 * - File selection and navigation
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { FileTree, type FileTreeNode } from '@/components/files/FileTree';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorBanner } from '@/components/common/ErrorBanner';
import { EmptyState } from '@/components/common/EmptyState';
import { Input } from '@/components/ui/input';
import { Search, FolderGit2 } from 'lucide-react';
import { useRepositoryStore } from '@/store/repositoryStore';
import { apiClient } from '@/lib/api';
import type { Repository, CodeChunk } from '@/types';

interface FileExplorerPageProps {
  params: {
    repoId: string;
  };
}

/**
 * Build file tree from flat list of chunks
 */
function buildFileTree(chunks: CodeChunk[]): FileTreeNode[] {
  const root: Map<string, FileTreeNode> = new Map();
  
  // Group chunks by file path
  const fileMap = new Map<string, CodeChunk[]>();
  chunks.forEach((chunk) => {
    const existing = fileMap.get(chunk.filePath) || [];
    existing.push(chunk);
    fileMap.set(chunk.filePath, existing);
  });
  
  // Build tree structure
  fileMap.forEach((fileChunks, filePath) => {
    const parts = filePath.split('/');
    let currentMap = root;
    let currentPath = '';
    
    parts.forEach((part, index) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part;
      const isFile = index === parts.length - 1;
      
      if (!currentMap.has(part)) {
        const node: FileTreeNode = {
          id: currentPath,
          name: part,
          path: currentPath,
          type: isFile ? 'file' : 'directory',
          language: isFile ? fileChunks[0]?.language : undefined,
          lineCount: isFile ? fileChunks.reduce((sum, c) => sum + (c.endLine - c.startLine + 1), 0) : undefined,
          children: isFile ? undefined : [],
        };
        currentMap.set(part, node);
      }
      
      if (!isFile) {
        const dirNode = currentMap.get(part)!;
        if (!dirNode.children) {
          dirNode.children = [];
        }
        // Create a new map for children
        const childMap = new Map<string, FileTreeNode>();
        dirNode.children.forEach((child) => {
          childMap.set(child.name, child);
        });
        currentMap = childMap;
      }
    });
  });
  
  // Convert map to array and sort
  const sortNodes = (nodes: FileTreeNode[]): FileTreeNode[] => {
    return nodes.sort((a, b) => {
      // Directories first
      if (a.type !== b.type) {
        return a.type === 'directory' ? -1 : 1;
      }
      // Then alphabetically
      return a.name.localeCompare(b.name);
    }).map((node) => {
      if (node.children) {
        return {
          ...node,
          children: sortNodes(node.children),
        };
      }
      return node;
    });
  };
  
  return sortNodes(Array.from(root.values()));
}

/**
 * Filter tree nodes by search query
 */
function filterTreeBySearch(nodes: FileTreeNode[], query: string): FileTreeNode[] {
  if (!query) return nodes;
  
  const lowerQuery = query.toLowerCase();
  
  function filterNode(node: FileTreeNode): FileTreeNode | null {
    // Check if current node matches
    const matches = node.name.toLowerCase().includes(lowerQuery) ||
                   node.path.toLowerCase().includes(lowerQuery);
    
    if (node.type === 'file') {
      return matches ? node : null;
    }
    
    // For directories, recursively filter children
    if (node.children) {
      const filteredChildren = node.children
        .map(filterNode)
        .filter((child): child is FileTreeNode => child !== null);
      
      // Include directory if it matches or has matching children
      if (matches || filteredChildren.length > 0) {
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

export default function FileExplorerPage({ params }: FileExplorerPageProps) {
  const router = useRouter();
  const { getRepositoryById } = useRepositoryStore();
  
  const [repository, setRepository] = useState<Repository | null>(null);
  const [chunks, setChunks] = useState<CodeChunk[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Get repository from store or fetch
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch repository
        const repo = await apiClient.repositories.get(params.repoId);
        setRepository(repo);
        
        // Fetch all chunks to build file tree
        // Note: In a real implementation, this should be paginated or use a dedicated endpoint
        // For now, we'll use search with empty query to get all chunks
        const results = await apiClient.search.semantic({
          query: '',
          repositoryIds: [params.repoId],
          topK: 10000, // Large number to get all files
        });
        
        setChunks(results.map((r) => r.chunk));
      } catch (err: any) {
        console.error('Failed to fetch file tree:', err);
        setError(err.message || 'Failed to load files');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [params.repoId]);
  
  // Build file tree from chunks
  const fileTree = useMemo(() => {
    if (chunks.length === 0) return [];
    return buildFileTree(chunks);
  }, [chunks]);
  
  // Filter tree by search query
  const filteredTree = useMemo(() => {
    return filterTreeBySearch(fileTree, searchQuery);
  }, [fileTree, searchQuery]);
  
  const handleFileSelect = (node: FileTreeNode) => {
    if (node.type === 'file') {
      // Navigate to file detail page
      router.push(`/repos/${params.repoId}/files/${encodeURIComponent(node.path)}`);
    }
  };
  
  if (isLoading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <LoadingSkeleton />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container mx-auto px-6 py-8">
        <ErrorBanner
          message={error}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }
  
  if (!repository) {
    return (
      <div className="container mx-auto px-6 py-8">
        <ErrorBanner message="Repository not found" />
      </div>
    );
  }
  
  const isCompleted = repository.status === 'completed';
  
  return (
    <div className="container mx-auto px-6 py-8">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Header */}
        <motion.div variants={fadeInUp}>
          <div className="flex items-start gap-4 mb-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-tertiary/10 flex-shrink-0">
              <FolderGit2 className="w-6 h-6 text-tertiary" />
            </div>
            <div>
              <h1 className="text-headline-lg text-text-primary font-semibold">
                File Explorer
              </h1>
              <p className="text-body-md text-text-secondary mt-1">
                Browse and explore files in {repository.name}
              </p>
            </div>
          </div>
        </motion.div>
        
        {/* Search Bar */}
        {isCompleted && fileTree.length > 0 && (
          <motion.div variants={fadeInUp}>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
              <Input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12"
              />
            </div>
          </motion.div>
        )}
        
        {/* File Tree */}
        {!isCompleted ? (
          <motion.div variants={fadeInUp}>
            <EmptyState
              icon={FolderGit2}
              title="Repository Not Ready"
              description="This repository is still being indexed. Please wait for indexing to complete."
            />
          </motion.div>
        ) : fileTree.length === 0 ? (
          <motion.div variants={fadeInUp}>
            <EmptyState
              icon={FolderGit2}
              title="No Files Found"
              description="This repository doesn't have any indexed files yet."
            />
          </motion.div>
        ) : (
          <motion.div variants={fadeInUp}>
            <div className="bg-surface-container rounded-lg border border-outline/15 p-6">
              <FileTree
                nodes={filteredTree}
                onFileSelect={handleFileSelect}
                showLanguageFilter={true}
                isLoading={false}
              />
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
