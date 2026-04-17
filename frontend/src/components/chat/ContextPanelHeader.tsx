/**
 * ContextPanelHeader Component
 * 
 * Header for the context panel displaying file path and viewer action.
 * Features:
 * - "CONTEXT:" label with file path display
 * - File path truncation with ellipsis for long paths
 * - "Open in Viewer" button with external link icon
 * - Distinct background styling consistent with Material Design 3 theme
 * 
 * Requirements: 1.6, 1.7
 */

'use client';

import { cn } from '@/lib/utils';

interface ContextPanelHeaderProps {
  /**
   * The file path to display
   */
  filePath: string;
  
  /**
   * Callback when "Open in Viewer" button is clicked
   */
  onOpenInViewer: () => void;
}

export function ContextPanelHeader({
  filePath,
  onOpenInViewer,
}: ContextPanelHeaderProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between gap-3 px-4 py-3',
        'bg-surface-container-low border-b border-outline-variant/10'
      )}
    >
      {/* File Path Display */}
      <div className="flex-1 min-w-0">
        <span className="text-[10px] uppercase tracking-widest text-on-surface-variant block mb-1">
          CONTEXT:
        </span>
        <p
          className="text-sm font-mono text-on-surface truncate"
          title={filePath}
        >
          {filePath}
        </p>
      </div>

      {/* Open in Viewer Button */}
      <button
        onClick={onOpenInViewer}
        className={cn(
          'flex items-center gap-1.5 px-3 py-1.5 rounded-lg',
          'bg-surface-container border border-outline-variant/10',
          'hover:bg-surface-container-high hover:border-outline-variant/30',
          'transition-all duration-150',
          'focus:outline-none focus:ring-2 focus:ring-primary/20',
          'flex-shrink-0'
        )}
      >
        <span className="text-sm text-on-surface font-medium whitespace-nowrap">
          Open in Viewer
        </span>
        <span className="material-symbols-outlined text-on-surface-variant text-[16px]">
          open_in_new
        </span>
      </button>
    </div>
  );
}
