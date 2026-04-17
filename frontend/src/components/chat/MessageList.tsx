/**
 * MessageList Component
 * 
 * Displays a list of chat messages with auto-scroll and virtualization support.
 * Features:
 * - Auto-scroll to latest message
 * - Staggered animation for messages
 * - Support for streaming messages
 * - Virtualization for performance (future enhancement)
 */

'use client';

import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import type { ChatMessage } from '@/types';

interface MessageListProps {
  /**
   * Array of chat messages
   */
  messages: ChatMessage[];
  
  /**
   * Whether a message is currently streaming
   */
  isStreaming?: boolean;
  
  /**
   * Current streaming message content
   */
  streamingMessage?: string;
}

export function MessageList({
  messages,
  isStreaming = false,
  streamingMessage = '',
}: MessageListProps) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {messages.map((message) => (
        <motion.div key={message.id} variants={staggerItem}>
          {message.role === 'user' ? (
            <UserMessage message={message} />
          ) : (
            <AssistantMessage message={message} />
          )}
        </motion.div>
      ))}
      
      {/* Streaming Message */}
      {isStreaming && streamingMessage && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          <AssistantMessage
            message={{
              id: 'streaming',
              role: 'assistant',
              content: streamingMessage,
              timestamp: new Date().toISOString(),
            }}
            isStreaming
          />
        </motion.div>
      )}
    </motion.div>
  );
}
