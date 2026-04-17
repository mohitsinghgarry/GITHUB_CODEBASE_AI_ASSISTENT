/**
 * RepoStats Component
 * 
 * Display repository statistics in card format.
 * Shows: files count, chunks count, languages breakdown
 * 
 * Features:
 * - Animated stat cards with icons
 * - Hover effects
 * - Responsive grid layout
 */

'use client';

import { motion } from 'framer-motion';
import { staggerContainer, staggerItem, hoverScale } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { FileText, Layers, Code2, GitBranch, Clock, LucideIcon } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';

interface RepoStatsProps {
  /**
   * Number of files indexed
   */
  fileCount: number;
  
  /**
   * Number of code chunks
   */
  chunkCount: number;
  
  /**
   * Number of programming languages detected
   */
  languageCount: number;
  
  /**
   * Last updated timestamp
   */
  lastUpdated?: string;
  
  /**
   * Default branch name
   */
  defaultBranch?: string;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  iconColor: string;
  iconBg: string;
}

function StatCard({ icon: Icon, label, value, iconColor, iconBg }: StatCardProps) {
  return (
    <motion.div
      variants={staggerItem}
      whileHover="hover"
      whileTap="tap"
      className={cn(
        'bg-surface-container rounded-lg p-4 border border-outline-variant/15',
        'transition-colors hover:bg-surface-container-high'
      )}
    >
      <motion.div variants={hoverScale} className="flex items-start gap-3">
        {/* Icon */}
        <div className={cn('flex items-center justify-center w-10 h-10 rounded-lg', iconBg)}>
          <Icon className={cn('w-5 h-5', iconColor)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-label-md text-text-secondary uppercase">
            {label}
          </p>
          <p className="text-headline-sm text-text-primary font-semibold mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}

export function RepoStats({
  fileCount,
  chunkCount,
  languageCount,
  lastUpdated,
  defaultBranch,
  className,
}: RepoStatsProps) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={cn('space-y-4', className)}
    >
      {/* Title */}
      <motion.h3
        variants={staggerItem}
        className="text-title-md text-text-primary font-medium"
      >
        Repository Statistics
      </motion.h3>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Files Count */}
        <StatCard
          icon={FileText}
          label="Files"
          value={fileCount}
          iconColor="text-primary"
          iconBg="bg-primary/10"
        />

        {/* Chunks Count */}
        <StatCard
          icon={Layers}
          label="Chunks"
          value={chunkCount}
          iconColor="text-secondary"
          iconBg="bg-secondary/10"
        />

        {/* Languages Count */}
        <StatCard
          icon={Code2}
          label="Languages"
          value={languageCount}
          iconColor="text-tertiary"
          iconBg="bg-tertiary/10"
        />
      </div>

      {/* Additional Info */}
      {(defaultBranch || lastUpdated) && (
        <motion.div
          variants={staggerItem}
          className="flex flex-wrap items-center gap-4 pt-2"
        >
          {/* Default Branch */}
          {defaultBranch && (
            <div className="flex items-center gap-2 text-body-sm text-text-secondary">
              <GitBranch className="w-4 h-4 text-text-tertiary" />
              <span className="text-text-tertiary">Branch:</span>
              <code className="px-2 py-0.5 rounded bg-surface-container-low text-label-sm font-mono text-text-primary">
                {defaultBranch}
              </code>
            </div>
          )}

          {/* Last Updated */}
          {lastUpdated && (
            <div className="flex items-center gap-2 text-body-sm text-text-secondary">
              <Clock className="w-4 h-4 text-text-tertiary" />
              <span className="text-text-tertiary">Updated:</span>
              <span className="text-text-primary">
                {formatRelativeTime(lastUpdated)}
              </span>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
