/**
 * CitationNavigator Component
 * 
 * Navigation controls for browsing multiple citations in a message.
 * Features:
 * - Current index and total count display (e.g., "1 / 3")
 * - Previous/next navigation buttons with icons
 * - Disabled states at navigation boundaries
 * - Hover effects and accessibility support
 * 
 * Requirements: 1.8
 */

'use client';

import { cn } from '@/lib/utils';

interface CitationNavigatorProps {
  /**
   * Current citation index (0-based)
   */
  currentIndex: number;
  
  /**
   * Total number of citations
   */
  totalCount: number;
  
  /**
   * Callback when next button is clicked
   */
  onNext: () => void;
  
  /**
   * Callback when previous button is clicked
   */
  onPrevious: () => void;
}

export function CitationNavigator({
  currentIndex,
  totalCount,
  onNext,
  onPrevious,
}: CitationNavigatorProps) {
  const isFirstCitation = currentIndex === 0;
  const isLastCitation = currentIndex === totalCount - 1;

  return (
    <div
      className={cn(
        'flex items-center justify-between gap-3 px-4 py-2',
        'bg-surface-container-low border-b border-outline-variant/10'
      )}
    >
      {/* Citation Counter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-on-surface font-medium">
          {currentIndex + 1} / {totalCount}
        </span>
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center gap-1">
        {/* Previous Button */}
        <button
          onClick={onPrevious}
          disabled={isFirstCitation}
          aria-label="Previous citation"
          className={cn(
            'flex items-center justify-center w-8 h-8 rounded-lg',
            'transition-all duration-150',
            'focus:outline-none focus:ring-2 focus:ring-primary/20',
            isFirstCitation
              ? 'bg-surface-container text-on-surface-variant cursor-not-allowed opacity-50'
              : 'bg-surface-container text-on-surface hover:bg-surface-container-high hover:text-primary cursor-pointer'
          )}
        >
          <span className="material-symbols-outlined text-[18px]">
            chevron_left
          </span>
        </button>

        {/* Next Button */}
        <button
          onClick={onNext}
          disabled={isLastCitation}
          aria-label="Next citation"
          className={cn(
            'flex items-center justify-center w-8 h-8 rounded-lg',
            'transition-all duration-150',
            'focus:outline-none focus:ring-2 focus:ring-primary/20',
            isLastCitation
              ? 'bg-surface-container text-on-surface-variant cursor-not-allowed opacity-50'
              : 'bg-surface-container text-on-surface hover:bg-surface-container-high hover:text-primary cursor-pointer'
          )}
        >
          <span className="material-symbols-outlined text-[18px]">
            chevron_right
          </span>
        </button>
      </div>
    </div>
  );
}
