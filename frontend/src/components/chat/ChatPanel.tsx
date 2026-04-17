/**
 * ChatPanel Component
 * 
 * Full-height chat interface with message list, input, and mode selector.
 * Features:
 * - Full-height layout with flex container
 * - Message list with auto-scroll
 * - Chat input with send button
 * - Explanation mode selector
 * - Suggested questions for empty state
 */

'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ModeSelector } from './ModeSelector';
import { SuggestedQuestions } from './SuggestedQuestions';
import type { ChatSession, ExplanationMode } from '@/types';

interface ChatPanelProps {
  /**
   * Current chat session
   */
  session: ChatSession | null;
  
  /**
   * Whether a message is currently streaming
   */
  isStreaming?: boolean;
  
  /**
   * Current streaming message content
   */
  streamingMessage?: string;
  
  /**
   * Loading state
   */
  isLoading?: boolean;
  
  /**
   * Callback when user sends a message
   */
  onSendMessage: (message: string) => Promise<void>;
  
  /**
   * Callback when explanation mode changes
   */
  onModeChange: (mode: ExplanationMode) => void;
  
  /**
   * Callback when a suggested question is clicked
   */
  onSuggestedQuestionClick?: (question: string) => void;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

export function ChatPanel({
  session,
  isStreaming = false,
  streamingMessage = '',
  isLoading = false,
  onSendMessage,
  onModeChange,
  onSuggestedQuestionClick,
  className,
}: ChatPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasMessages = session && session.messages.length > 0;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [session?.messages, streamingMessage]);

  const handleSuggestedQuestionClick = (question: string) => {
    if (onSuggestedQuestionClick) {
      onSuggestedQuestionClick(question);
    } else {
      onSendMessage(question);
    }
  };

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className={cn(
        'flex flex-col h-full bg-surface-container rounded-xl border border-outline-variant/15',
        className
      )}
    >
      {/* Header with Mode Selector */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/15">
        <div>
          <h2 className="text-title-md text-text-primary font-medium">
            Chat with Codebase
          </h2>
          <p className="text-body-sm text-text-secondary mt-0.5">
            Ask questions about your code
          </p>
        </div>
        
        {session && (
          <ModeSelector
            mode={session.explanationMode}
            onChange={onModeChange}
          />
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {hasMessages ? (
          <>
            <MessageList
              messages={session.messages}
              isStreaming={isStreaming}
              streamingMessage={streamingMessage}
            />
            <div ref={messagesEndRef} />
          </>
        ) : (
          <SuggestedQuestions
            onQuestionClick={handleSuggestedQuestionClick}
          />
        )}
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-outline-variant/15">
        <ChatInput
          onSend={onSendMessage}
          disabled={isLoading || isStreaming}
          isLoading={isLoading}
        />
      </div>
    </motion.div>
  );
}
