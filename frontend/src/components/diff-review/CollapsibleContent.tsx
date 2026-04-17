'use client';

import React, { useState } from 'react';

interface CollapsibleContentProps {
  content: string;
  maxLength: number;
  isMarkdown?: boolean;
  children?: React.ReactNode;
}

/**
 * CollapsibleContent Component
 * 
 * Provides expand/collapse functionality for long content sections.
 * Used within MarkdownDescription to handle truncation of lengthy issue descriptions.
 * 
 * Features:
 * - Automatic truncation at configurable character threshold
 * - Smooth expand/collapse animation using Tailwind transitions
 * - Chevron icons indicating current state
 * - Accessible with proper ARIA attributes
 * - Follows "Obsidian Intelligence" design system
 * 
 * Design System Compliance:
 * - Uses duration-normal (250ms) and ease-quart for animations
 * - Typography: text-label-md for button text
 * - Colors: text-primary with hover:text-primary-dim
 * - Spacing: 4px grid system (gap-1, mt-2)
 * - Icons: material-symbols-outlined (expand_more/expand_less)
 * 
 * @param content - The text content to display (used for length calculation)
 * @param maxLength - Character threshold for collapsing (default: 200)
 * @param isMarkdown - Whether the content is markdown (affects truncation strategy)
 * @param children - The rendered content to display (can be markdown or plain text)
 */
export const CollapsibleContent: React.FC<CollapsibleContentProps> = ({
  content,
  maxLength,
  children,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Determine if content should be collapsible
  const shouldCollapse = content.length > maxLength;

  // If content is short enough, just render it without collapse functionality
  if (!shouldCollapse) {
    return <div className="collapsible-content">{children}</div>;
  }

  return (
    <div className="collapsible-content">
      {/* Content container with smooth height transition */}
      <div
        className={`overflow-hidden transition-all duration-normal ease-quart ${
          isExpanded ? 'max-h-[2000px]' : 'max-h-24'
        }`}
      >
        {children}
      </div>

      {/* Expand/Collapse button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? 'Show less' : 'Show more'}
        className="flex items-center gap-1 text-primary hover:text-primary-dim transition-colors duration-normal ease-quart mt-2 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded"
        type="button"
      >
        <span className="text-label-md font-medium">
          {isExpanded ? 'Show less' : 'Show more'}
        </span>
        <span className="material-symbols-outlined text-sm">
          {isExpanded ? 'expand_less' : 'expand_more'}
        </span>
      </button>
    </div>
  );
};
