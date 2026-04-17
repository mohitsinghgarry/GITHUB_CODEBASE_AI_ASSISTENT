/**
 * FileExplorerDemo Component
 * 
 * Example implementation showing how to use all file explorer components together.
 * This is a reference implementation for the file explorer pages.
 */

'use client';

import { useState } from 'react';
import { FileTree, FileHeader, FileSummaryCard, FileTreeNode } from './index';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';

// Example tree data
const exampleTreeData: FileTreeNode[] = [
  {
    id: '1',
    name: 'src',
    path: 'src',
    type: 'directory',
    children: [
      {
        id: '2',
        name: 'components',
        path: 'src/components',
        type: 'directory',
        children: [
          {
            id: '3',
            name: 'FileTree.tsx',
            path: 'src/components/FileTree.tsx',
            type: 'file',
            language: 'typescript',
            size: 5120,
            lineCount: 250,
          },
          {
            id: '4',
            name: 'FileNode.tsx',
            path: 'src/components/FileNode.tsx',
            type: 'file',
            language: 'typescript',
            size: 3840,
            lineCount: 180,
          },
        ],
      },
      {
        id: '5',
        name: 'lib',
        path: 'src/lib',
        type: 'directory',
        children: [
          {
            id: '6',
            name: 'utils.ts',
            path: 'src/lib/utils.ts',
            type: 'file',
            language: 'typescript',
            size: 2048,
            lineCount: 100,
          },
        ],
      },
      {
        id: '7',
        name: 'index.ts',
        path: 'src/index.ts',
        type: 'file',
        language: 'typescript',
        size: 1024,
        lineCount: 50,
      },
    ],
  },
  {
    id: '8',
    name: 'package.json',
    path: 'package.json',
    type: 'file',
    language: 'json',
    size: 512,
    lineCount: 25,
  },
  {
    id: '9',
    name: 'README.md',
    path: 'README.md',
    type: 'file',
    language: 'markdown',
    size: 2560,
    lineCount: 120,
  },
];

// Example summary data
const exampleSummaries: Record<string, {
  summary: string;
  keyElements: Array<{
    name: string;
    type: 'function' | 'class' | 'interface' | 'type' | 'constant';
    description?: string;
  }>;
}> = {
  'src/components/FileTree.tsx': {
    summary: 'This component implements a hierarchical file tree structure with expand/collapse functionality, language filtering, and file selection. It uses framer-motion for smooth animations and supports both loading and empty states.',
    keyElements: [
      {
        name: 'FileTree',
        type: 'function',
        description: 'Main component that renders the file tree',
      },
      {
        name: 'buildNodeMap',
        type: 'function',
        description: 'Builds a flat map of all nodes for quick lookup',
      },
      {
        name: 'filterTreeByLanguage',
        type: 'function',
        description: 'Filters tree nodes by selected languages',
      },
    ],
  },
  'src/components/FileNode.tsx': {
    summary: 'Individual file or directory node component with expand/collapse animations, selection states, and metadata display. Supports nested rendering for directory hierarchies.',
    keyElements: [
      {
        name: 'FileNode',
        type: 'function',
        description: 'Renders a single file or directory node',
      },
      {
        name: 'getFileIcon',
        type: 'function',
        description: 'Returns appropriate icon based on file type',
      },
      {
        name: 'getLanguageColor',
        type: 'function',
        description: 'Returns color class for language badge',
      },
    ],
  },
  'src/lib/utils.ts': {
    summary: 'Utility functions for common operations including class name merging, byte formatting, relative time formatting, text truncation, and debouncing.',
    keyElements: [
      {
        name: 'cn',
        type: 'function',
        description: 'Merges Tailwind CSS classes using clsx and tailwind-merge',
      },
      {
        name: 'formatBytes',
        type: 'function',
        description: 'Formats bytes to human-readable string',
      },
      {
        name: 'debounce',
        type: 'function',
        description: 'Debounces function calls',
      },
    ],
  },
};

export function FileExplorerDemo() {
  const [selectedFile, setSelectedFile] = useState<FileTreeNode | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  
  const handleFileSelect = (node: FileTreeNode) => {
    if (node.type === 'file') {
      setSelectedFile(node);
      
      // Simulate loading summary
      setIsLoadingSummary(true);
      setTimeout(() => {
        setIsLoadingSummary(false);
      }, 1000);
    }
  };
  
  const handleRegenerateSummary = () => {
    setIsLoadingSummary(true);
    setTimeout(() => {
      setIsLoadingSummary(false);
    }, 1000);
  };
  
  const summaryData = selectedFile ? exampleSummaries[selectedFile.path] : undefined;
  
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <motion.h1
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="text-headline-lg text-text-primary font-semibold mb-8"
        >
          File Explorer Demo
        </motion.h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Tree */}
          <div className="lg:col-span-1">
            <FileTree
              nodes={exampleTreeData}
              onFileSelect={handleFileSelect}
              selectedPath={selectedFile?.path}
              showLanguageFilter={true}
            />
          </div>
          
          {/* File Details */}
          <div className="lg:col-span-2">
            {selectedFile ? (
              <div className="space-y-6">
                <FileHeader
                  path={selectedFile.path}
                  language={selectedFile.language}
                  size={selectedFile.size}
                  lineCount={selectedFile.lineCount}
                  lastModified={new Date()}
                  lastModifiedBy="john.doe"
                  repositoryUrl="https://github.com/example/repo"
                />
                
                <FileSummaryCard
                  summary={summaryData?.summary}
                  keyElements={summaryData?.keyElements}
                  isLoading={isLoadingSummary}
                  onRegenerate={handleRegenerateSummary}
                  collapsible={true}
                />
                
                {/* File Content Placeholder */}
                <motion.div
                  variants={fadeInUp}
                  initial="hidden"
                  animate="visible"
                  className="p-6 bg-surface-container-lowest rounded-lg border border-outline/15"
                >
                  <pre className="text-body-md text-text-primary font-mono overflow-x-auto">
                    <code>
                      {`// File content would be displayed here
// with syntax highlighting

function example() {
  console.log('Hello, world!');
}`}
                    </code>
                  </pre>
                </motion.div>
              </div>
            ) : (
              <motion.div
                variants={fadeInUp}
                initial="hidden"
                animate="visible"
                className="flex flex-col items-center justify-center h-96 bg-surface-container rounded-lg border border-outline/15"
              >
                <p className="text-body-lg text-text-secondary">
                  Select a file to view details
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
