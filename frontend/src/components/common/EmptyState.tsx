/**
 * EmptyState Component
 * 
 * A reusable empty state component with icon, message, and optional action button.
 * Uses fadeInUp animation for smooth appearance.
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  /**
   * Icon to display (Lucide icon component)
   */
  icon: LucideIcon;
  
  /**
   * Title text
   */
  title: string;
  
  /**
   * Description text
   */
  description?: string;
  
  /**
   * Action button label
   */
  actionLabel?: string;
  
  /**
   * Action button click handler
   */
  onAction?: () => void;
  
  /**
   * Secondary action button label
   */
  secondaryActionLabel?: string;
  
  /**
   * Secondary action button click handler
   */
  onSecondaryAction?: () => void;
  
  /**
   * Additional CSS classes for the container
   */
  className?: string;
  
  /**
   * Size variant
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';
}

const sizeConfig = {
  sm: {
    container: 'py-8',
    icon: 'w-12 h-12',
    title: 'text-title-sm',
    description: 'text-body-sm',
  },
  md: {
    container: 'py-12',
    icon: 'w-16 h-16',
    title: 'text-title-lg',
    description: 'text-body-md',
  },
  lg: {
    container: 'py-16',
    icon: 'w-20 h-20',
    title: 'text-headline-sm',
    description: 'text-body-lg',
  },
};

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  className,
  size = 'md',
}: EmptyStateProps) {
  const config = sizeConfig[size];

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn(
        'flex flex-col items-center justify-center text-center',
        config.container,
        className
      )}
    >
      {/* Icon */}
      <div
        className={cn(
          'mb-4 text-text-tertiary',
          config.icon
        )}
      >
        <Icon className="w-full h-full" strokeWidth={1.5} />
      </div>

      {/* Title */}
      <h3
        className={cn(
          'font-semibold text-text-primary mb-2',
          config.title
        )}
      >
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p
          className={cn(
            'text-text-secondary max-w-md mb-6',
            config.description
          )}
        >
          {description}
        </p>
      )}

      {/* Actions */}
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex items-center gap-3">
          {actionLabel && onAction && (
            <Button
              onClick={onAction}
              size={size === 'sm' ? 'sm' : 'default'}
            >
              {actionLabel}
            </Button>
          )}
          
          {secondaryActionLabel && onSecondaryAction && (
            <Button
              onClick={onSecondaryAction}
              variant="outline"
              size={size === 'sm' ? 'sm' : 'default'}
            >
              {secondaryActionLabel}
            </Button>
          )}
        </div>
      )}
    </motion.div>
  );
}

/**
 * Preset empty state variants for common use cases
 */

import {
  FolderOpen,
  Search,
  MessageSquare,
  FileCode,
  Database,
  AlertCircle,
} from 'lucide-react';

export function NoRepositoriesEmpty({ onAction }: { onAction?: () => void }) {
  return (
    <EmptyState
      icon={FolderOpen}
      title="No repositories yet"
      description="Add your first repository to start exploring and chatting with your codebase."
      actionLabel="Add Repository"
      onAction={onAction}
    />
  );
}

export function NoSearchResultsEmpty() {
  return (
    <EmptyState
      icon={Search}
      title="No results found"
      description="Try adjusting your search query or filters to find what you're looking for."
      size="sm"
    />
  );
}

export function NoChatHistoryEmpty() {
  return (
    <EmptyState
      icon={MessageSquare}
      title="Start a conversation"
      description="Ask questions about your codebase and get instant answers with code references."
      size="sm"
    />
  );
}

export function NoFilesEmpty() {
  return (
    <EmptyState
      icon={FileCode}
      title="No files found"
      description="This repository doesn't contain any indexed files yet."
      size="sm"
    />
  );
}

export function NoDataEmpty() {
  return (
    <EmptyState
      icon={Database}
      title="No data available"
      description="There's no data to display at the moment."
      size="sm"
    />
  );
}

export function ErrorEmpty({
  title = 'Something went wrong',
  description = 'An error occurred while loading the data.',
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <EmptyState
      icon={AlertCircle}
      title={title}
      description={description}
      actionLabel={onRetry ? 'Try Again' : undefined}
      onAction={onRetry}
      size="sm"
    />
  );
}
