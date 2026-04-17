/**
 * ContextPanel Component
 * 
 * Main context panel that displays referenced code files with syntax highlighting,
 * line numbers, and highlighted line ranges. Integrates ContextPanelHeader,
 * CitationNavigator, and CodeDisplay components.
 * 
 * Features:
 * - Empty state display when no citation is provided
 * - Header with file path and "Open in Viewer" button
 * - Navigation controls for multiple citations
 * - Code display with syntax highlighting and line numbers
 * - Auto-scroll to highlighted line range on content change
 * - Independent scrolling with fixed header
 * 
 * Requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 1.10, 1.11
 */

'use client';

import { useEffect, useRef } from 'react';
import { Citation } from '@/lib/api';
import { ContextPanelHeader } from './ContextPanelHeader';
import { CitationNavigator } from './CitationNavigator';
import { CodeDisplay } from './CodeDisplay';
import { cn } from '@/lib/utils';

interface ContextPanelProps {
  /**
   * Currently selected citation to display
   */
  citation: Citation | null;
  
  /**
   * All citations from the active message
   */
  citations: Citation[];
  
  /**
   * Current citation index (0-based)
   */
  currentIndex: number;
  
  /**
   * Callback when navigating between citations
   */
  onNavigate: (direction: 'next' | 'prev') => void;
  
  /**
   * Callback when "Open in Viewer" button is clicked
   */
  onOpenInViewer: (filePath: string) => void;
  
  /**
   * Whether the panel is in overlay mode (responsive)
   */
  isOverlay?: boolean;
  
  /**
   * Callback when dismiss button is clicked (overlay mode only)
   */
  onDismiss?: () => void;
  
  /**
   * Optional className for styling
   */
  className?: string;
}

export function ContextPanel({
  citation,
  citations,
  currentIndex,
  onNavigate,
  onOpenInViewer,
  isOverlay = false,
  onDismiss,
  className,
}: ContextPanelProps) {
  const codeContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to highlighted line range when content changes
  useEffect(() => {
    if (citation && codeContainerRef.current) {
      // Small delay to ensure content is rendered
      setTimeout(() => {
        // Look for highlighted lines - the highlightColor from CodeDisplay
        const highlightedElement = codeContainerRef.current?.querySelector(
          '[style*="rgba(103, 80, 164, 0.1)"]'
        );
        
        if (highlightedElement) {
          highlightedElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
          });
        }
      }, 100);
    }
  }, [citation?.chunk_id]);

  // Empty state when no citation is provided
  if (!citation) {
    return (
      <div
        className={cn(
          'flex flex-col h-full bg-surface-container-low',
          isOverlay && 'fixed top-0 right-0 bottom-0 z-50 shadow-float',
          className
        )}
        role="region"
        aria-label="Context panel"
      >
        {/* Dismiss button for overlay mode */}
        {isOverlay && onDismiss && (
          <div className="flex justify-end p-4 border-b border-outline-variant/10">
            <button
              onClick={onDismiss}
              className="p-2 rounded-lg hover:bg-surface-container transition-colors"
              aria-label="Close context panel"
            >
              <span className="material-symbols-outlined text-on-surface-variant">close</span>
            </button>
          </div>
        )}
        
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
          <span className="material-symbols-outlined text-6xl text-outline mb-4">
            code
          </span>
          <p className="text-sm text-on-surface-variant max-w-xs">
            No code references yet. Ask a question about the codebase to see relevant code here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex flex-col h-full bg-surface-container-low',
        isOverlay && 'fixed top-0 right-0 bottom-0 z-50 shadow-float',
        className
      )}
      role="region"
      aria-label="Context panel"
      aria-live="polite"
    >
      {/* Dismiss button for overlay mode */}
      {isOverlay && onDismiss && (
        <div className="flex justify-end p-4 border-b border-outline-variant/10">
          <button
            onClick={onDismiss}
            className="p-2 rounded-lg hover:bg-surface-container transition-colors"
            aria-label="Close context panel"
          >
            <span className="material-symbols-outlined text-on-surface-variant">close</span>
          </button>
        </div>
      )}
      
      {/* Header with file path and "Open in Viewer" button */}
      <ContextPanelHeader
        filePath={citation.file_path}
        onOpenInViewer={() => onOpenInViewer(citation.file_path)}
      />

      {/* Navigation controls - only show when multiple citations exist */}
      {citations.length > 1 && (
        <CitationNavigator
          currentIndex={currentIndex}
          totalCount={citations.length}
          onNext={() => onNavigate('next')}
          onPrevious={() => onNavigate('prev')}
        />
      )}

      {/* Code display with independent scrolling */}
      <div
        ref={codeContainerRef}
        className="flex-1 overflow-auto p-4"
      >
        <CodeDisplay
          content={citation.content}
          language={citation.language}
          startLine={citation.start_line}
          endLine={citation.end_line}
        />
      </div>
    </div>
  );
}
