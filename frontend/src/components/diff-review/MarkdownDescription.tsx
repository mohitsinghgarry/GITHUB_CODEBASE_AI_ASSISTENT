'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

interface MarkdownDescriptionProps {
  content: string;
  maxLength?: number;
}

/**
 * MarkdownDescription Component
 * 
 * Renders markdown-formatted issue descriptions with custom styling
 * matching the "Obsidian Intelligence" design system.
 * 
 * Features:
 * - GitHub Flavored Markdown support via remark-gfm
 * - Custom renderers for headings, code blocks, lists, and text formatting
 * - Collapsible content for long descriptions
 * - Error boundary with fallback to plain text
 * - Tailwind CSS styling following 4px grid system
 * 
 * @param content - Markdown-formatted text to render
 * @param maxLength - Character threshold for collapsing (default: 200)
 */
export const MarkdownDescription: React.FC<MarkdownDescriptionProps> = ({
  content,
  maxLength = 200,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Determine if content should be collapsible
  const shouldCollapse = content.length > maxLength;
  const displayContent = shouldCollapse && !isExpanded 
    ? content.slice(0, maxLength) + '...' 
    : content;

  // Custom component renderers matching design system
  const components: Components = {
    h1: ({ children }) => (
      <h1 className="text-title-lg font-semibold text-on-surface mb-4">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-title-md font-semibold text-on-surface mb-3">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-title-sm font-medium text-on-surface mb-2">
        {children}
      </h3>
    ),
    p: ({ children }) => (
      <p className="text-body-md text-on-surface-variant mb-3 leading-relaxed">
        {children}
      </p>
    ),
    code: ({ node, className, children, ...props }) => {
      // In react-markdown v9, detect inline code by checking if parent is not a pre element
      const isInline = !className && !String(children).includes('\n');
      if (isInline) {
        return (
          <code className="px-1.5 py-0.5 bg-surface-container-lowest rounded text-primary font-mono text-sm" {...props}>
            {children}
          </code>
        );
      }
      return (
        <pre className="bg-surface-container-lowest rounded-lg p-4 overflow-x-auto mb-4">
          <code className={`font-mono text-sm text-on-surface ${className || ''}`} {...props}>
            {children}
          </code>
        </pre>
      );
    },
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-3 space-y-1.5 text-body-md text-on-surface-variant">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-3 space-y-1.5 text-body-md text-on-surface-variant">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="ml-2">{children}</li>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-on-surface">{children}</strong>
    ),
    em: ({ children }) => (
      <em className="italic">{children}</em>
    ),
  };

  // Error boundary fallback
  if (hasError) {
    return (
      <div className="text-body-md text-on-surface-variant leading-relaxed">
        <pre className="whitespace-pre-wrap font-sans">{content}</pre>
      </div>
    );
  }

  try {
    return (
      <div className="markdown-description">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={components}
        >
          {displayContent}
        </ReactMarkdown>
        
        {shouldCollapse && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            aria-expanded={isExpanded}
            aria-label={isExpanded ? 'Show less' : 'Show more'}
            className="flex items-center gap-1 text-primary hover:text-primary-dim transition-colors mt-2"
          >
            <span className="text-label-md font-medium">
              {isExpanded ? 'Show less' : 'Show more'}
            </span>
            <span className="material-symbols-outlined text-sm">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
          </button>
        )}
      </div>
    );
  } catch (error) {
    // Catch rendering errors and fall back to plain text
    console.error('Markdown parsing failed:', error);
    setHasError(true);
    
    return (
      <div className="text-body-md text-on-surface-variant leading-relaxed">
        <pre className="whitespace-pre-wrap font-sans">{content}</pre>
      </div>
    );
  }
};
