/**
 * Repository Dashboard Page
 * 
 * Main dashboard for a repository showing:
 * - Repository information and status
 * - Indexing progress (if in progress)
 * - Repository statistics
 * - Quick action buttons
 * - Language breakdown
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { RepoStats } from '@/components/repo/RepoStats';
import { IndexingProgress } from '@/components/repo/IndexingProgress';
import { LanguageChart } from '@/components/repo/LanguageChart';
import { DeleteConfirmationModal } from '@/components/common/DeleteConfirmationModal';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorBanner } from '@/components/common/ErrorBanner';
import {
  MessageSquare,
  Search,
  FileCode,
  FolderGit2,
  RefreshCw,
  Trash2,
  ExternalLink,
} from 'lucide-react';
import { useRepositoryStore } from '@/store/repositoryStore';
import { apiClient } from '@/lib/api';
import type { Repository, IngestionJob } from '@/types';

interface RepositoryPageProps {
  params: {
    repoId: string;
  };
}

export default function RepositoryPage({ params }: RepositoryPageProps) {
  const router = useRouter();
  const { updateRepository, removeRepository, updateIngestionJob, getJobsByRepositoryId } =
    useRepositoryStore();

  const [repository, setRepository] = useState<Repository | null>(null);
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Fetch repository data
  useEffect(() => {
    const fetchRepository = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const repo = await apiClient.repositories.get(params.repoId);
        setRepository(repo);
        updateRepository(repo.id, repo);

        // Fetch active job if repository is not completed
        if (repo.status !== 'completed' && repo.status !== 'failed') {
          const jobs = await apiClient.jobs.get(params.repoId);
          if (jobs) {
            setJob(jobs);
          }
        }
      } catch (err: any) {
        console.error('Failed to fetch repository:', err);
        setError(err.message || 'Failed to load repository');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRepository();
  }, [params.repoId]);

  // Poll job status if in progress
  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'failed') {
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updatedJob = await apiClient.jobs.get(job.id);
        setJob(updatedJob);
        updateIngestionJob(updatedJob.id, updatedJob);

        if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
          const updatedRepo = await apiClient.repositories.get(params.repoId);
          setRepository(updatedRepo);
          updateRepository(updatedRepo.id, updatedRepo);
        }
      } catch (err) {
        console.error('Failed to poll job status:', err);
      }
    }, 2000);

    setPollingInterval(interval);

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [job?.id, job?.status]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleDelete = async () => {
    if (!repository) return;

    try {
      setIsDeleting(true);
      await apiClient.repositories.delete(repository.id);
      removeRepository(repository.id);
      router.push('/');
    } catch (err: any) {
      console.error('Failed to delete repository:', err);
      setError(err.message || 'Failed to delete repository');
      setShowDeleteModal(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleReindex = async () => {
    if (!repository) return;

    try {
      setIsReindexing(true);
      setError(null);
      const response = await apiClient.repositories.reindex(repository.id);
      const newJob = await apiClient.jobs.get(response.jobId);
      setJob(newJob);
      updateIngestionJob(newJob.id, newJob);
    } catch (err: any) {
      console.error('Failed to reindex repository:', err);
      setError(err.message || 'Failed to start reindexing');
    } finally {
      setIsReindexing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  if (error && !repository) {
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

  const isIndexing = repository.status !== 'completed' && repository.status !== 'failed';
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
        <motion.div variants={fadeInUp} className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 flex-shrink-0">
              <FolderGit2 className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-headline-lg text-text-primary font-semibold">
                {repository.name}
              </h1>
              <p className="text-body-md text-text-secondary mt-1">
                {repository.owner}
              </p>
              <a
                href={repository.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-body-sm text-primary hover:underline mt-2"
              >
                View on GitHub
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReindex}
              disabled={isIndexing || isReindexing}
            >
              <RefreshCw className={cn('w-4 h-4 mr-2', isReindexing && 'animate-spin')} />
              Reindex
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDeleteModal(true)}
              disabled={isDeleting}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </motion.div>

        {/* Error Banner */}
        {error && (
          <motion.div variants={fadeInUp}>
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          </motion.div>
        )}

        {/* Indexing Progress */}
        {isIndexing && job && (
          <motion.div variants={fadeInUp}>
            <IndexingProgress
              stage={job.stage}
              status={job.status}
              progressPercent={job.progressPercent}
              errorMessage={job.errorMessage}
            />
          </motion.div>
        )}

        {/* Repository Stats */}
        {isCompleted && (
          <motion.div variants={fadeInUp}>
            <RepoStats
              fileCount={repository.chunkCount || 0}
              chunkCount={repository.chunkCount}
              languageCount={5} // TODO: Get from API
              lastUpdated={repository.updatedAt}
              defaultBranch={repository.defaultBranch}
            />
          </motion.div>
        )}

        {/* Quick Actions */}
        {isCompleted && (
          <motion.div variants={fadeInUp}>
            <h2 className="text-title-md text-text-primary font-medium mb-4">
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Chat */}
              <button
                onClick={() => router.push(`/repos/${repository.id}/chat`)}
                className={cn(
                  'flex items-start gap-4 p-4 rounded-lg',
                  'bg-surface-container border border-outline-variant/15',
                  'hover:bg-surface-container-high hover:border-primary/30',
                  'transition-all duration-200',
                  'text-left'
                )}
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
                  <MessageSquare className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-label-lg text-text-primary font-medium">
                    Chat with Codebase
                  </h3>
                  <p className="text-body-sm text-text-secondary mt-1">
                    Ask questions about the code using natural language
                  </p>
                </div>
              </button>

              {/* Search */}
              <button
                onClick={() => router.push(`/repos/${repository.id}/search`)}
                className={cn(
                  'flex items-start gap-4 p-4 rounded-lg',
                  'bg-surface-container border border-outline-variant/15',
                  'hover:bg-surface-container-high hover:border-primary/30',
                  'transition-all duration-200',
                  'text-left'
                )}
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-secondary/10 flex-shrink-0">
                  <Search className="w-5 h-5 text-secondary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-label-lg text-text-primary font-medium">
                    Search Code
                  </h3>
                  <p className="text-body-sm text-text-secondary mt-1">
                    Find code using semantic or keyword search
                  </p>
                </div>
              </button>

              {/* Files */}
              <button
                onClick={() => router.push(`/repos/${repository.id}/files`)}
                className={cn(
                  'flex items-start gap-4 p-4 rounded-lg',
                  'bg-surface-container border border-outline-variant/15',
                  'hover:bg-surface-container-high hover:border-primary/30',
                  'transition-all duration-200',
                  'text-left'
                )}
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-tertiary/10 flex-shrink-0">
                  <FileCode className="w-5 h-5 text-tertiary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-label-lg text-text-primary font-medium">
                    Browse Files
                  </h3>
                  <p className="text-body-sm text-text-secondary mt-1">
                    Explore the repository file structure
                  </p>
                </div>
              </button>
            </div>
          </motion.div>
        )}

        {/* Language Breakdown */}
        {isCompleted && (
          <motion.div variants={fadeInUp}>
            <LanguageChart
              languages={[
                { name: 'TypeScript', percentage: 45.2, fileCount: 120 },
                { name: 'JavaScript', percentage: 30.5, fileCount: 85 },
                { name: 'Python', percentage: 15.3, fileCount: 42 },
                { name: 'CSS', percentage: 6.0, fileCount: 18 },
                { name: 'HTML', percentage: 3.0, fileCount: 10 },
              ]}
            />
          </motion.div>
        )}
      </motion.div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title="Delete Repository"
        description="Are you sure you want to delete this repository? This will remove all indexed data, embeddings, and chat history."
        itemName={`${repository.owner}/${repository.name}`}
        isDeleting={isDeleting}
      />
    </div>
  );
}
