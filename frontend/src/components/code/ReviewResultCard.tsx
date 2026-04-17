/**
 * ReviewResultCard Component
 * 
 * Displays a single code review issue with details.
 * Features:
 * - Severity badge with color coding
 * - Issue description
 * - Line number reference
 * - Suggestion (if available)
 * - Fade in up animation
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';
import type { ReviewIssue } from '@/types';

interface ReviewResultCardProps {
  /**
   * Review issue data
   */
  issue: ReviewIssue;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get severity icon and color
 */
function getSeverityConfig(severity: ReviewIssue['severity']) {
  switch (severity) {
    case 'critical':
      return {
        icon: XCircle,
        color: 'text-error',
        bgColor: 'bg-error/10',
        borderColor: 'border-error/20',
        label: 'Critical',
      };
    case 'high':
      return {
        icon: AlertCircle,
        color: 'text-error',
        bgColor: 'bg-error/10',
        borderColor: 'border-error/20',
        label: 'High',
      };
    case 'medium':
      return {
        icon: AlertTriangle,
        color: 'text-secondary',
        bgColor: 'bg-secondary/10',
        borderColor: 'border-secondary/20',
        label: 'Medium',
      };
    case 'low':
      return {
        icon: Info,
        color: 'text-primary',
        bgColor: 'bg-primary/10',
        borderColor: 'border-primary/20',
        label: 'Low',
      };
  }
}

export function ReviewResultCard({ issue, className }: ReviewResultCardProps) {
  const config = getSeverityConfig(issue.severity);
  const Icon = config.icon;

  return (
    <motion.div
      variants={fadeInUp}
      className={cn(
        'rounded-lg p-4',
        'bg-surface-container border',
        config.borderColor,
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className={cn('p-2 rounded-md', config.bgColor)}>
          <Icon className={cn('w-4 h-4', config.color)} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn('text-label-sm uppercase tracking-widest font-medium', config.color)}>
              {config.label}
            </span>
            {issue.lineNumber && (
              <>
                <span className="text-outline-variant">•</span>
                <span className="text-label-sm text-on-surface-variant font-mono">
                  Line {issue.lineNumber}
                </span>
              </>
            )}
          </div>
          
          <p className="text-body-md text-on-surface">
            {issue.description}
          </p>
        </div>
      </div>

      {/* Suggestion */}
      {issue.suggestion && (
        <div className="mt-3 pt-3 border-t border-outline-variant/15">
          <p className="text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">
            Suggestion
          </p>
          <p className="text-body-sm text-on-surface-variant">
            {issue.suggestion}
          </p>
        </div>
      )}
    </motion.div>
  );
}
