'use client';

import React from 'react';

interface SuggestionSectionProps {
  suggestion: string;
}

/**
 * SuggestionSection Component
 * 
 * Displays code suggestions with distinct visual treatment to differentiate
 * them from issue descriptions. Uses the "Obsidian Intelligence" design system
 * with surface-container-lowest background and tertiary color accents.
 * 
 * Features:
 * - Distinct background color (surface-container-lowest - true black for code)
 * - Lightbulb icon in tertiary color (emerald for positive action)
 * - Monospace font for suggestion text
 * - "Suggestion" label with proper typography
 * - Consistent padding and border radius (4px grid system)
 * 
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 * 
 * @param suggestion - The suggestion text to display
 */
export const SuggestionSection: React.FC<SuggestionSectionProps> = ({
  suggestion,
}) => {
  return (
    <div className="bg-surface-container-lowest rounded-lg p-4">
      <div className="flex items-start gap-3">
        {/* Lightbulb icon in tertiary color */}
        <span className="material-symbols-outlined text-tertiary text-xl flex-shrink-0 mt-0.5">
          lightbulb
        </span>
        
        <div className="flex-1 min-w-0">
          {/* Suggestion label */}
          <div className="text-label-md font-medium text-tertiary mb-2">
            Suggestion
          </div>
          
          {/* Suggestion text with monospace font */}
          <pre className="font-mono text-sm text-on-surface whitespace-pre-wrap break-words">
            {suggestion}
          </pre>
        </div>
      </div>
    </div>
  );
};
