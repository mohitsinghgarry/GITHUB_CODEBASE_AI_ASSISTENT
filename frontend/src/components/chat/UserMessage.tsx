/**
 * UserMessage Component
 * 
 * Right-aligned message bubble for user messages.
 * Features:
 * - Right-aligned layout
 * - Gradient background
 * - Timestamp display
 * - Smooth animations
 */

'use client';

import { motion } from 'framer-motion';
import { messageBubble } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { User } from 'lucide-react';
import type { ChatMessage } from '@/types';

interface UserMessageProps {
  /**
   * The user message to display
   */
  message: ChatMessage;
  
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

export function UserMessage({ message, className }: UserMessageProps) {
  return (
    <motion.div
      variants={messageBubble}
      className={cn('flex justify-end gap-3', className)}
    >
      {/* Message Content */}
      <div className="flex flex-col items-end max-w-[80%]">
        {/* Timestamp */}
        <span className="text-label-sm text-text-tertiary mb-1.5">
          {formatTimestamp(message.timestamp)}
        </span>
        
        {/* Message Bubble */}
        <div
          className={cn(
            'px-4 py-3 rounded-xl',
            'bg-gradient-to-br from-primary to-primary-dim',
            'text-body-md text-on-primary',
            'shadow-sm'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>

      {/* User Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
        <User className="w-4 h-4 text-primary" />
      </div>
    </motion.div>
  );
}
