/**
 * IndexingProgress Component
 * 
 * 5-stage progress indicator for repository ingestion pipeline.
 * Stages: clone → read → chunk → embed → store
 * 
 * Features:
 * - Visual progress bar with percentage
 * - Stage-by-stage status indicators
 * - Animated transitions between stages
 * - Error state handling
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { StatusBadge } from '@/components/common/StatusBadge';
import {
  GitBranch,
  FileText,
  Scissors,
  Sparkles,
  Database,
  CheckCircle2,
  XCircle,
  LucideIcon,
} from 'lucide-react';
import type { IngestionStage, JobStatus } from '@/types';

interface IndexingProgressProps {
  /**
   * Current stage of ingestion
   */
  stage?: IngestionStage;
  
  /**
   * Overall job status
   */
  status: JobStatus;
  
  /**
   * Progress percentage (0-100)
   */
  progressPercent: number;
  
  /**
   * Error message (if failed)
   */
  errorMessage?: string;
  
  /**
   * Repository name
   */
  repositoryName?: string;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface Stage {
  id: IngestionStage;
  label: string;
  description: string;
  icon: LucideIcon;
}

const stages: Stage[] = [
  {
    id: 'clone',
    label: 'Clone',
    description: 'Cloning repository',
    icon: GitBranch,
  },
  {
    id: 'read',
    label: 'Read',
    description: 'Reading source files',
    icon: FileText,
  },
  {
    id: 'chunk',
    label: 'Chunk',
    description: 'Chunking code',
    icon: Scissors,
  },
  {
    id: 'embed',
    label: 'Embed',
    description: 'Generating embeddings',
    icon: Sparkles,
  },
  {
    id: 'store',
    label: 'Store',
    description: 'Storing vectors',
    icon: Database,
  },
];

/**
 * Get stage status based on current stage and job status
 */
function getStageStatus(
  stageId: IngestionStage,
  currentStage: IngestionStage | undefined,
  jobStatus: JobStatus
): 'completed' | 'running' | 'pending' | 'failed' {
  if (jobStatus === 'failed') {
    const currentIndex = stages.findIndex((s) => s.id === currentStage);
    const stageIndex = stages.findIndex((s) => s.id === stageId);
    
    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'failed';
    return 'pending';
  }

  if (jobStatus === 'completed') {
    return 'completed';
  }

  if (!currentStage) {
    return 'pending';
  }

  const currentIndex = stages.findIndex((s) => s.id === currentStage);
  const stageIndex = stages.findIndex((s) => s.id === stageId);

  if (stageIndex < currentIndex) return 'completed';
  if (stageIndex === currentIndex) return 'running';
  return 'pending';
}

export function IndexingProgress({
  stage,
  status,
  progressPercent,
  errorMessage,
  repositoryName,
  className,
}: IndexingProgressProps) {
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const isRunning = status === 'running';

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn(
        'bg-surface-container rounded-xl p-6 border border-outline-variant/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-title-md text-text-primary font-medium">
            Indexing Progress
          </h3>
          {repositoryName && (
            <p className="text-body-sm text-text-secondary mt-0.5">
              {repositoryName}
            </p>
          )}
        </div>
        <StatusBadge
          status={
            isCompleted
              ? 'completed'
              : isFailed
              ? 'failed'
              : isRunning
              ? 'running'
              : 'pending'
          }
          size="md"
        />
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-label-md text-text-secondary uppercase">
            Progress
          </span>
          <span className="text-label-lg text-text-primary font-medium">
            {progressPercent}%
          </span>
        </div>
        <div className="h-2 bg-surface-container-low rounded-full overflow-hidden">
          <motion.div
            className={cn(
              'h-full rounded-full',
              isFailed ? 'bg-error' : 'bg-primary'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          />
        </div>
      </div>

      {/* Stages */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-3"
      >
        {stages.map((stageItem) => {
          const stageStatus = getStageStatus(stageItem.id, stage, status);
          const Icon = stageItem.icon;

          return (
            <motion.div
              key={stageItem.id}
              variants={staggerItem}
              className={cn(
                'flex items-center gap-3 p-3 rounded-lg transition-colors',
                stageStatus === 'running' && 'bg-surface-container-high',
                stageStatus === 'completed' && 'bg-tertiary/5',
                stageStatus === 'failed' && 'bg-error/5'
              )}
            >
              {/* Icon */}
              <div
                className={cn(
                  'flex items-center justify-center w-8 h-8 rounded-lg flex-shrink-0',
                  stageStatus === 'completed' && 'bg-tertiary/10',
                  stageStatus === 'running' && 'bg-primary/10',
                  stageStatus === 'failed' && 'bg-error/10',
                  stageStatus === 'pending' && 'bg-surface-container-low'
                )}
              >
                {stageStatus === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4 text-tertiary" />
                ) : stageStatus === 'failed' ? (
                  <XCircle className="w-4 h-4 text-error" />
                ) : (
                  <Icon
                    className={cn(
                      'w-4 h-4',
                      stageStatus === 'running' && 'text-primary',
                      stageStatus === 'pending' && 'text-text-tertiary'
                    )}
                  />
                )}
              </div>

              {/* Label */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      'text-label-lg font-medium',
                      stageStatus === 'completed' && 'text-tertiary',
                      stageStatus === 'running' && 'text-primary',
                      stageStatus === 'failed' && 'text-error',
                      stageStatus === 'pending' && 'text-text-tertiary'
                    )}
                  >
                    {stageItem.label}
                  </span>
                  {stageStatus === 'running' && (
                    <motion.div
                      className="flex gap-1"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <motion.span
                        className="w-1 h-1 rounded-full bg-primary"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                      />
                      <motion.span
                        className="w-1 h-1 rounded-full bg-primary"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                      />
                      <motion.span
                        className="w-1 h-1 rounded-full bg-primary"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                      />
                    </motion.div>
                  )}
                </div>
                <p
                  className={cn(
                    'text-body-sm mt-0.5',
                    stageStatus === 'pending' && 'text-text-tertiary',
                    stageStatus !== 'pending' && 'text-text-secondary'
                  )}
                >
                  {stageItem.description}
                </p>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Error Message */}
      {isFailed && errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 rounded-lg bg-error/5 border border-error/20"
        >
          <div className="flex items-start gap-2">
            <XCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-label-md text-error font-medium">
                Indexing Failed
              </p>
              <p className="text-body-sm text-text-secondary mt-1">
                {errorMessage}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Success Message */}
      {isCompleted && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 rounded-lg bg-tertiary/5 border border-tertiary/20"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-tertiary flex-shrink-0" />
            <p className="text-label-md text-tertiary font-medium">
              Indexing completed successfully
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
