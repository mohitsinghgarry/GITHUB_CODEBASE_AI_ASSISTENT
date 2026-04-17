/**
 * ChatInput Component
 * 
 * Text input with send button and keyboard shortcuts.
 * Features:
 * - Auto-expanding textarea
 * - Send button with loading state
 * - Keyboard shortcuts (Enter to send, Shift+Enter for new line)
 * - Character limit indicator
 * - Disabled state
 */

'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  /**
   * Callback when user sends a message
   */
  onSend: (message: string) => Promise<void>;
  
  /**
   * Whether the input is disabled
   */
  disabled?: boolean;
  
  /**
   * Loading state
   */
  isLoading?: boolean;
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Maximum character limit
   */
  maxLength?: number;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = 'Ask a question about your codebase...',
  maxLength = 2000,
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set height to scrollHeight (with max height limit)
    const maxHeight = 200; // Max height in pixels
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
  }, [message]);

  const handleSend = async () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending || disabled) return;

    setIsSending(true);
    try {
      await onSend(trimmedMessage);
      setMessage('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isDisabled = disabled || isSending || isLoading;
  const canSend = message.trim().length > 0 && !isDisabled;
  const characterCount = message.length;
  const isNearLimit = characterCount > maxLength * 0.9;
  const isOverLimit = characterCount > maxLength;

  return (
    <div className={cn('space-y-2', className)}>
      {/* Input Container - responsive padding and sizing */}
      <div
        className={cn(
          'flex items-end gap-2 p-3 rounded-xl sm:gap-3 sm:p-4',
          'bg-surface-container-low border border-outline-variant/15',
          'focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20',
          'transition-all duration-150',
          isDisabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Textarea - responsive font size */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isDisabled}
          maxLength={maxLength}
          rows={1}
          className={cn(
            'flex-1 resize-none bg-transparent',
            'text-body-md text-text-primary placeholder:text-text-tertiary sm:text-body-lg',
            'focus:outline-none',
            'disabled:cursor-not-allowed',
            'min-h-[24px] max-h-[200px]'
          )}
        />

        {/* Send Button - touch-friendly size */}
        <Button
          onClick={handleSend}
          disabled={!canSend}
          size="icon"
          className={cn(
            'flex-shrink-0 h-11 w-11 min-h-[44px] min-w-[44px]',
            'transition-all duration-150'
          )}
        >
          {isSending || isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </Button>
      </div>

      {/* Footer - responsive visibility */}
      <div className="flex flex-col items-start gap-2 px-1 sm:flex-row sm:items-center sm:justify-between">
        {/* Keyboard Hint - hide on mobile */}
        <span className="hidden text-label-sm text-text-tertiary sm:inline">
          <kbd className="px-1.5 py-0.5 rounded bg-surface-container-low border border-outline-variant/15 font-mono text-label-sm">
            Enter
          </kbd>{' '}
          to send,{' '}
          <kbd className="px-1.5 py-0.5 rounded bg-surface-container-low border border-outline-variant/15 font-mono text-label-sm">
            Shift + Enter
          </kbd>{' '}
          for new line
        </span>

        {/* Character Count */}
        {(isNearLimit || isOverLimit) && (
          <motion.span
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={cn(
              'text-label-sm sm:text-label-md',
              isOverLimit ? 'text-error' : 'text-text-tertiary'
            )}
          >
            {characterCount} / {maxLength}
          </motion.span>
        )}
      </div>
    </div>
  );
}
