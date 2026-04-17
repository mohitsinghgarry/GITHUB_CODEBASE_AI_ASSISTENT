/**
 * AssistantMessage Component
 * 
 * Left-aligned message bubble for assistant messages with code snippets and citations.
 * Features:
 * - Left-aligned layout
 * - Code snippet rendering with syntax highlighting
 * - Source citations display
 * - Streaming indicator
 * - Markdown-like formatting
 */

'use client';

import { motion } from 'framer-motion';
import { messageBubble } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Bot, Loader2 } from 'lucide-react';
import { CodeSnippetCard } from './CodeSnippetCard';
import { SourceCitations } from './SourceCitations';
import type { ChatMessage } from '@/types';

interface AssistantMessageProps {
  /**
   * The assistant message to display
   */
  message: ChatMessage;
  
  /**
   * Whether this message is currently streaming
   */
  isStreaming?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Format timestamp to readable format
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

/**
 * Parse message content to extract code blocks
 */
function parseMessageContent(content: string): Array<{ type: 'text' | 'code'; content: string; language?: string }> {
  const parts: Array<{ type: 'text' | 'code'; content: string; language?: string }> = [];
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  
  let lastIndex = 0;
  let match;
  
  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      const textContent = content.slice(lastIndex, match.index).trim();
      if (textContent) {
        parts.push({ type: 'text', content: textContent });
      }
    }
    
    // Add code block
    parts.push({
      type: 'code',
      content: match[2].trim(),
      language: match[1] || 'plaintext',
    });
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text
  if (lastIndex < content.length) {
    const textContent = content.slice(lastIndex).trim();
    if (textContent) {
      parts.push({ type: 'text', content: textContent });
    }
  }
  
  // If no code blocks found, return entire content as text
  if (parts.length === 0) {
    parts.push({ type: 'text', content });
  }
  
  return parts;
}

export function AssistantMessage({
  message,
  isStreaming = false,
  className,
}: AssistantMessageProps) {
  const contentParts = parseMessageContent(message.content);
  const hasCitations = message.citations && message.citations.length > 0;

  return (
    <motion.div
      variants={messageBubble}
      className={cn('flex justify-start gap-3', className)}
    >
      {/* Assistant Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center">
        {isStreaming ? (
          <Loader2 className="w-4 h-4 text-secondary animate-spin" />
        ) : (
          <Bot className="w-4 h-4 text-secondary" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex flex-col items-start max-w-[80%]">
        {/* Timestamp */}
        <span className="text-label-sm text-text-tertiary mb-1.5">
          {isStreaming ? 'Thinking...' : formatTimestamp(message.timestamp)}
        </span>
        
        {/* Message Bubble */}
        <div
          className={cn(
            'px-4 py-3 rounded-xl',
            'bg-surface-container-high',
            'text-body-md text-text-primary',
            'border border-outline-variant/15',
            'w-full'
          )}
        >
          <div className="space-y-3">
            {contentParts.map((part, index) => (
              <div key={index}>
                {part.type === 'text' ? (
                  <p className="whitespace-pre-wrap break-words leading-relaxed">
                    {part.content}
                  </p>
                ) : (
                  <CodeSnippetCard
                    code={part.content}
                    language={part.language || 'plaintext'}
                  />
                )}
              </div>
            ))}
          </div>
          
          {/* Streaming Cursor */}
          {isStreaming && (
            <motion.span
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="inline-block w-2 h-4 ml-1 bg-secondary"
            />
          )}
        </div>

        {/* Source Citations */}
        {hasCitations && (
          <div className="mt-3 w-full">
            <SourceCitations citations={message.citations!} />
          </div>
        )}
      </div>
    </motion.div>
  );
}
