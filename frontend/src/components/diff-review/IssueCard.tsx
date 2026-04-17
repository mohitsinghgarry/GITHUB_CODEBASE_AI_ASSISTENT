'use client';

import React from 'react';
import { MarkdownDescription } from './MarkdownDescription';
import { SuggestionSection } from './SuggestionSection';
import type { CodeIssue } from '@/lib/api';

interface IssueCardProps {
  issue: CodeIssue;
  index: number;
}

/**
 * Severity configuration mapping
 * Maps severity levels to their visual representation (colors, icons, labels)
 */
const severityConfig = {
  critical: {
    color: 'text-error',
    bgColor: 'bg-error/10',
    icon: 'error',
    label: 'Critical',
  },
  high: {
    color: 'text-warning',
    bgColor: 'bg-warning/10',
    icon: 'warning',
    label: 'High',
  },
  medium: {
    color: 'text-caution',
    bgColor: 'bg-caution/10',
    icon: 'info',
    label: 'Medium',
  },
  low: {
    color: 'text-info',
    bgColor: 'bg-info/10',
    icon: 'info',
    label: 'Low',
  },
  info: {
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    icon: 'info',
    label: 'Info',
  },
};

/**
 * IssueCard Component
 * 
 * Displays a single code review issue with enhanced formatting and visual hierarchy.
 * Integrates MarkdownDescription, CollapsibleContent, and SuggestionSection components.
 * 
 * Features:
 * - Severity badge with color-coded visual treatment
 * - Markdown-rendered descriptions with collapsible behavior
 * - Conditional line number display
 * - Conditional suggestion section
 * - Follows "Obsidian Intelligence" design system
 * - Memoized for performance optimization
 * 
 * Design System Compliance:
 * - No-Line Rule: Uses background color shifts instead of borders
 * - 4px Grid: All spacing in multiples of 4px
 * - Typography Scale: title-md, body-md, label-sm
 * - Surface Hierarchy: container-low for card background
 * - Tonal Layering: Severity badges use color/10 opacity
 * 
 * Requirements: 1.1, 2.1, 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 5.4, 6.1
 * 
 * @param issue - The code issue to display
 * @param index - The index of the issue in the list (for accessibility)
 */
const IssueCardComponent: React.FC<IssueCardProps> = ({ issue, index }) => {
  const {
    severity = 'info',
    title = 'Untitled Issue',
    description = '',
    line_number,
    suggestion,
  } = issue;

  const config = severityConfig[severity] || severityConfig.info;

  return (
    <div
      className="bg-surface-container-low rounded-lg p-6 space-y-4"
      role="article"
      aria-labelledby={`issue-title-${index}`}
    >
      {/* Issue Header: Severity Badge + Title */}
      <div className="flex items-start gap-4">
        {/* Severity Badge */}
        <span
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bgColor} flex-shrink-0`}
          role="status"
          aria-label={`Severity: ${config.label}`}
        >
          <span className={`material-symbols-outlined text-base ${config.color}`}>
            {config.icon}
          </span>
          <span className={`text-xs font-bold uppercase tracking-wide ${config.color}`}>
            {config.label}
          </span>
        </span>

        {/* Line Number Badge (conditional) */}
        {line_number !== undefined && (
          <div
            className="px-2.5 py-1 rounded bg-surface-container-lowest text-on-surface-variant text-xs font-mono flex-shrink-0"
            aria-label={`Line ${line_number}`}
          >
            L{line_number}
          </div>
        )}
      </div>

      {/* Issue Title */}
      <h3
        id={`issue-title-${index}`}
        className="text-title-md font-semibold text-on-surface leading-snug"
      >
        {title}
      </h3>

      {/* Issue Description with Collapsible Behavior */}
      <div className="text-on-surface-variant">
        <MarkdownDescription content={description} maxLength={200} />
      </div>

      {/* Suggestion Section (conditional) */}
      {suggestion && (
        <div className="pt-2">
          <SuggestionSection suggestion={suggestion} />
        </div>
      )}
    </div>
  );
};

/**
 * Memoized IssueCard for performance optimization
 * Prevents unnecessary re-renders when parent component updates
 */
export const IssueCard = React.memo(IssueCardComponent);
