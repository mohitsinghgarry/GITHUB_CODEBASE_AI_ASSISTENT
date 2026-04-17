/**
 * File Detail Page
 * 
 * Display individual file content with:
 * - File metadata (path, language, size, lines)
 * - Syntax-highlighted code viewer
 * - AI-generated file summary
 * - Navigation breadcrumbs
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { FileHeader } from '@/components/files/FileHeader';
import { FileSummaryCard } from '@/components/files/FileSummaryCard';
import { CodeViewer } from '@/components/code/CodeViewer';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorBanner } from '@/components/common/ErrorBanner';
import { Button } from '@/components/ui/button';
import { ChevronLeft, MessageSquare } from 'lucide-react';
import { useRepositoryStore } from '@/store/repositoryStore';
import { apiClient } from '@/lib/api';
import type { Repository, CodeChunk } from '@/types';

interface FileDetailPageProps {
  params: {
    repoId: string;
    filePath: string[];
  };
}

/**
 * Reconstruct file content from chunks
 */
function reconstructFileContent(chunks: CodeChunk[]): string {
  // Sort chunks by start line
  const sortedChunks = [...chunks].sort((a, b) => a.startLine - b.startLine);
  
  // Merge overlapping or adjacent chunks
  const lines: string[] = [];
  let lastEndLine = 0;
  
  sortedChunks.forEach((chunk) => {
    const chunkLines = chunk.content.split('\n');
    
    // If there's a gap, add empty lines
    if (chunk.startLine > lastEndLine + 1) {
      for (let i = lastEndLine + 1; i < chunk.startLine; i++) {
        lines.push('');
      }
    }
    
    // Add chunk lines
    chunkLines.forEach((line, index) => {
      const lineNumber = chunk.startLine + index;
      if (lineNumber > lastEndLine) {
        lines.push(line);
        lastEndLine = lineNumber;
      }
    });
  });
  
  return lines.join('\n');
}

/**
 * Calculate file size from content
 */
function calculateFileSize(content: string): number {
  return new Blob([content]).size;
}

/**
 * Generate breadcrumb items from file path
 */
function generateBreadcrumbs(filePath: string): Array<{ label: string; path: string }> {
  const parts = filePath.split('/');
  const breadcrumbs: Array<{ label: string; path: string }> = [];
  
  parts.forEach((part, index) => {
    const path = parts.slice(0, index + 1).join('/');
    breadcrumbs.push({ label: part, path });
  });
  
  return breadcrumbs;
}

export default function FileDetailPage({ params }: FileDetailPageProps) {
  const router = useRouter();
  const { getRepositoryById } = useRepositoryStore();
  
  const [repository, setRepository] = useState<Repository | null>(null);
  const [chunks, setChunks] = useState<CodeChunk[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [summary, setSummary] = useState<string>('');
  
  // Decode file path from URL params
  const filePath = decodeURIComponent(params.filePath.join('/'));
  
  // Fetch file chunks
  useEffect(() => {
    const fetchFile = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch repository
        const repo = await apiClient.repositories.get(params.repoId);
        setRepository(repo);
        
        // Search for chunks matching this file path
        const results = await apiClient.search.keyword({
          query: filePath,
          repositoryIds: [params.repoId],
          topK: 1000,
          filters: {
            // Note: This is a simplified approach
            // In production, you'd want a dedicated endpoint to fetch file by path
          },
        });
        
        // Filter to exact file path matches
        const fileChunks = results
          .map((r) => r.chunk)
          .filter((chunk) => chunk.filePath === filePath);
        
        if (fileChunks.length === 0) {
          setError('File not found');
        } else {
          setChunks(fileChunks);
        }
      } catch (err: any) {
        console.error('Failed to fetch file:', err);
        setError(err.message || 'Failed to load file');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchFile();
  }, [params.repoId, filePath]);
  
  // Reconstruct file content
  const fileContent = useMemo(() => {
    if (chunks.length === 0) return '';
    return reconstructFileContent(chunks);
  }, [chunks]);
  
  // Calculate file metadata
  const fileMetadata = useMemo(() => {
    if (chunks.length === 0) return null;
    
    const firstChunk = chunks[0];
    const lineCount = fileContent.split('\n').length;
    const size = calculateFileSize(fileContent);
    
    return {
      language: firstChunk.language,
      lineCount,
      size,
    };
  }, [chunks, fileContent]);
  
  // Generate breadcrumbs
  const breadcrumbs = useMemo(() => {
    return generateBreadcrumbs(filePath);
  }, [filePath]);
  
  const handleGenerateSummary = async () => {
    if (!repository) return;
    
    try {
      setIsGeneratingSummary(true);
      
      // Use chat API to generate summary
      const response = await apiClient.chat.send(
        `Please provide a brief summary of what this file does: ${filePath}`,
        undefined,
        [repository.id],
        'technical'
      );
      
      setSummary(response.message.content);
    } catch (err: any) {
      console.error('Failed to generate summary:', err);
      setError(err.message || 'Failed to generate summary');
    } finally {
      setIsGeneratingSummary(false);
    }
  };
  
  const handleAskAboutFile = () => {
    if (!repository) return;
    
    // Navigate to chat with pre-filled question about this file
    router.push(
      `/repos/${repository.id}/chat?message=${encodeURIComponent(
        `Tell me about the file ${filePath}`
      )}`
    );
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
  
  if (!repository || chunks.length === 0) {
    return (
      <div className="container mx-auto px-6 py-8">
        <ErrorBanner message="File not found" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-6 py-8">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Back Button */}
        <motion.div variants={fadeInUp}>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push(`/repos/${params.repoId}/files`)}
            className="mb-4"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back to Files
          </Button>
        </motion.div>
        
        {/* Breadcrumbs */}
        <motion.div variants={fadeInUp}>
          <div className="flex items-center gap-2 text-body-sm text-text-secondary">
            <button
              onClick={() => router.push(`/repos/${params.repoId}/files`)}
              className="hover:text-text-primary transition-colors"
            >
              {repository.name}
            </button>
            {breadcrumbs.map((crumb, index) => (
              <div key={crumb.path} className="flex items-center gap-2">
                <span>/</span>
                {index === breadcrumbs.length - 1 ? (
                  <span className="text-text-primary font-medium">{crumb.label}</span>
                ) : (
                  <button
                    onClick={() => router.push(`/repos/${params.repoId}/files`)}
                    className="hover:text-text-primary transition-colors"
                  >
                    {crumb.label}
                  </button>
                )}
              </div>
            ))}
          </div>
        </motion.div>
        
        {/* File Header */}
        <motion.div variants={fadeInUp}>
          <FileHeader
            path={filePath}
            language={fileMetadata?.language}
            size={fileMetadata?.size}
            lineCount={fileMetadata?.lineCount}
            repositoryUrl={repository.url}
            showCopyPath={true}
            showExternalLink={true}
          />
        </motion.div>
        
        {/* Actions */}
        <motion.div variants={fadeInUp}>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleAskAboutFile}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Ask About This File
            </Button>
            
            {!summary && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerateSummary}
                disabled={isGeneratingSummary}
              >
                {isGeneratingSummary ? 'Generating...' : 'Generate Summary'}
              </Button>
            )}
          </div>
        </motion.div>
        
        {/* File Summary */}
        {(summary || isGeneratingSummary) && (
          <motion.div variants={fadeInUp}>
            <FileSummaryCard
              summary={summary}
              onRegenerate={handleGenerateSummary}
              isLoading={isGeneratingSummary}
            />
          </motion.div>
        )}
        
        {/* Code Viewer */}
        <motion.div variants={fadeInUp}>
          <CodeViewer
            code={fileContent}
            language={fileMetadata?.language}
            showLineNumbers={true}
            filePath={filePath.split('/').pop()}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}
