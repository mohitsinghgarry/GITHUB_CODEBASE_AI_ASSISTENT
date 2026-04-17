/**
 * RepoCard Component
 * 
 * Card component for displaying repository information in a list.
 * 
 * Features:
 * - Repository metadata display
 * - Status indicator
 * - Hover and tap animations
 * - Click to navigate
 * - Action buttons (delete, reindex)
 */

'use client';

import { motion } from 'framer-motion';
import { staggerItem, hoverScale } from '@/lib/animation-presets';
import { cn, formatRelativeTime } from '@/lib/utils';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import {
  Github,
  GitBranch,
  FileText,
  Layers,
  MoreVertical,
  Trash2,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import type { Repository } from '@/types';

interface RepoCardProps {
  /**
   * Repository data
   */
  repository: Repository;
  
  /**
   * Click handler for card
   */
  onClick?: () => void;
  
  /**
   * Delete handler
   */
  onDelete?: () => void;
  
  /**
   * Reindex handler
   */
  onReindex?: () => void;
  
  /**
   * Show actions menu
   * @default true
   */
  showActions?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

export function RepoCard({
  repository,
  onClick,
  onDelete,
  onReindex,
  showActions = true,
  className,
}: RepoCardProps) {
  const {
    name,
    owner,
    url,
    status,
    defaultBranch,
    chunkCount,
    updatedAt,
    errorMessage,
  } = repository;

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete();
    }
  };

  const handleReindex = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onReindex) {
      onReindex();
    }
  };

  const handleOpenGitHub = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <motion.div
      variants={staggerItem}
      whileHover="hover"
      whileTap="tap"
      onClick={handleCardClick}
      className={cn(
        'bg-surface-container rounded-xl p-5 border border-outline-variant/15',
        'transition-all duration-150',
        'hover:bg-surface-container-high hover:border-outline-variant/30',
        onClick && 'cursor-pointer',
        className
      )}
    >
      <motion.div variants={hoverScale}>
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            {/* Icon */}
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
              <Github className="w-5 h-5 text-primary" />
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h3 className="text-title-md text-text-primary font-medium truncate">
                {name}
              </h3>
              <p className="text-body-sm text-text-secondary mt-0.5 truncate">
                {owner}
              </p>
            </div>
          </div>

          {/* Status Badge */}
          <StatusBadge
            status={
              status === 'completed'
                ? 'completed'
                : status === 'failed'
                ? 'failed'
                : status === 'pending'
                ? 'pending'
                : 'running'
            }
            label={
              status === 'cloning'
                ? 'Cloning'
                : status === 'reading'
                ? 'Reading'
                : status === 'chunking'
                ? 'Chunking'
                : status === 'embedding'
                ? 'Embedding'
                : undefined
            }
            size="sm"
            animate={false}
          />
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-4 mb-4">
          {/* Branch */}
          {defaultBranch && (
            <div className="flex items-center gap-1.5 text-body-sm text-text-secondary">
              <GitBranch className="w-3.5 h-3.5 text-text-tertiary" />
              <code className="text-label-sm font-mono text-text-primary">
                {defaultBranch}
              </code>
            </div>
          )}

          {/* Chunk Count */}
          {chunkCount > 0 && (
            <div className="flex items-center gap-1.5 text-body-sm text-text-secondary">
              <Layers className="w-3.5 h-3.5 text-text-tertiary" />
              <span>{chunkCount.toLocaleString()} chunks</span>
            </div>
          )}

          {/* Updated Time */}
          {updatedAt && (
            <div className="flex items-center gap-1.5 text-body-sm text-text-tertiary">
              <span>Updated {formatRelativeTime(updatedAt)}</span>
            </div>
          )}
        </div>

        {/* Error Message */}
        {status === 'failed' && errorMessage && (
          <div className="mb-4 p-3 rounded-lg bg-error/5 border border-error/20">
            <p className="text-body-sm text-error line-clamp-2">
              {errorMessage}
            </p>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="flex items-center gap-2 pt-4 border-t border-outline-variant/15">
            {/* Open in GitHub */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleOpenGitHub}
              className="flex-1"
            >
              <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
              GitHub
            </Button>

            {/* Reindex */}
            {onReindex && status === 'completed' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleReindex}
                className="flex-1"
              >
                <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                Reindex
              </Button>
            )}

            {/* Delete */}
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="text-error hover:text-error hover:bg-error/10"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </Button>
            )}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
