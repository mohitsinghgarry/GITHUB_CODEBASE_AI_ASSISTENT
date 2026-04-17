/**
 * ReviewSummaryBar Component
 * 
 * Displays a summary of code review results with severity counts.
 * Features:
 * - Total issue count
 * - Breakdown by severity (critical, high, medium, low)
 * - Color-coded badges
 * - Fade in animation
 */

'use client';

import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { AlertCircle, AlertTriangle, Info, XCircle, CheckCircle } from 'lucide-react';
import type { ReviewIssue } from '@/types';

interface ReviewSummaryBarProps {
  /**
   * Array of review issues
   */
  issues: ReviewIssue[];
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface SeverityCount {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

/**
 * Count issues by severity
 */
function countBySeverity(issues: ReviewIssue[]): SeverityCount {
  return issues.reduce(
    (acc, issue) => {
      acc[issue.severity]++;
      return acc;
    },
    { critical: 0, high: 0, medium: 0, low: 0 }
  );
}

export function ReviewSummaryBar({ issues, className }: ReviewSummaryBarProps) {
  const counts = countBySeverity(issues);
  const totalIssues = issues.length;
  const hasIssues = totalIssues > 0;

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className={cn(
        'rounded-lg p-6',
        'bg-surface-container border border-outline-variant/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          {hasIssues ? (
            <>
              <div className="p-2 rounded-md bg-error/10">
                <AlertCircle className="w-5 h-5 text-error" />
              </div>
              <div>
                <h3 className="text-title-md text-on-surface">
                  {totalIssues} {totalIssues === 1 ? 'Issue' : 'Issues'} Found
                </h3>
                <p className="text-body-sm text-on-surface-variant">
                  Review the issues below and apply suggested fixes
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="p-2 rounded-md bg-tertiary/10">
                <CheckCircle className="w-5 h-5 text-tertiary" />
              </div>
              <div>
                <h3 className="text-title-md text-on-surface">
                  No Issues Found
                </h3>
                <p className="text-body-sm text-on-surface-variant">
                  Your code looks good!
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Severity Breakdown */}
      {hasIssues && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Critical */}
          <div className="flex items-center gap-3 p-3 rounded-md bg-surface-container-low">
            <div className="p-2 rounded-md bg-error/10">
              <XCircle className="w-4 h-4 text-error" />
            </div>
            <div>
              <p className="text-label-sm text-on-surface-variant uppercase tracking-widest">
                Critical
              </p>
              <p className="text-title-md text-on-surface font-semibold">
                {counts.critical}
              </p>
            </div>
          </div>

          {/* High */}
          <div className="flex items-center gap-3 p-3 rounded-md bg-surface-container-low">
            <div className="p-2 rounded-md bg-error/10">
              <AlertCircle className="w-4 h-4 text-error" />
            </div>
            <div>
              <p className="text-label-sm text-on-surface-variant uppercase tracking-widest">
                High
              </p>
              <p className="text-title-md text-on-surface font-semibold">
                {counts.high}
              </p>
            </div>
          </div>

          {/* Medium */}
          <div className="flex items-center gap-3 p-3 rounded-md bg-surface-container-low">
            <div className="p-2 rounded-md bg-secondary/10">
              <AlertTriangle className="w-4 h-4 text-secondary" />
            </div>
            <div>
              <p className="text-label-sm text-on-surface-variant uppercase tracking-widest">
                Medium
              </p>
              <p className="text-title-md text-on-surface font-semibold">
                {counts.medium}
              </p>
            </div>
          </div>

          {/* Low */}
          <div className="flex items-center gap-3 p-3 rounded-md bg-surface-container-low">
            <div className="p-2 rounded-md bg-primary/10">
              <Info className="w-4 h-4 text-primary" />
            </div>
            <div>
              <p className="text-label-sm text-on-surface-variant uppercase tracking-widest">
                Low
              </p>
              <p className="text-title-md text-on-surface font-semibold">
                {counts.low}
              </p>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
