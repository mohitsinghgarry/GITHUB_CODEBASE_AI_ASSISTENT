/**
 * Chat Page
 * 
 * Chat interface for interacting with the repository codebase.
 * Features:
 * - Session management (create, load, delete)
 * - Streaming response display with real-time updates
 * - Explanation mode persistence
 * - Message history
 * - Code syntax highlighting in responses
 * 
 * Requirements: 11.3
 * - THE Frontend_App SHALL provide a chat interface with message history and code syntax highlighting
 * - WHEN code is referenced in responses, THE Frontend_App SHALL display it with proper formatting and line numbers
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorBanner } from '@/components/common/ErrorBanner';
import { useChatStore } from '@/store/chatStore';
import { apiClient } from '@/lib/api-client';
import type { ExplanationMode, ChatMessage } from '@/types';

interface ChatPageProps {
  params: {
    repoId: string;
  };
}

export default function ChatPage({ params }: ChatPageProps) {
  const router = useRouter();
  const {
    sessions,
    activeSessionId,
    isStreaming,
    streamingMessage,
    isLoading,
    error,
    activeSession,
    addSession,
    setActiveSession,
    addMessage,
    startStreaming,
    appendToStream,
    stopStreaming,
    setExplanationMode,
    setLoading,
    setError,
  } = useChatStore();

  const [isInitializing, setIsInitializing] = useState(true);

  // Initialize session on mount
  useEffect(() => {
    const initializeSession = async () => {
      try {
        setIsInitializing(true);
        setError(null);

        // Check if there's an active session for this repository
        const existingSessions = Object.values(sessions).filter((session) =>
          session.repositoryIds.includes(params.repoId)
        );

        if (existingSessions.length > 0) {
          // Use the most recent session
          const mostRecentSession = existingSessions.sort(
            (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
          )[0];
          setActiveSession(mostRecentSession.id);
        } else {
          // Create a new session
          const newSession = {
            id: crypto.randomUUID(),
            repositoryIds: [params.repoId],
            messages: [],
            explanationMode: 'technical' as ExplanationMode,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          addSession(newSession);
          setActiveSession(newSession.id);
        }
      } catch (err: any) {
        console.error('Failed to initialize session:', err);
        setError(err.message || 'Failed to initialize chat session');
      } finally {
        setIsInitializing(false);
      }
    };

    initializeSession();
  }, [params.repoId]);

  // Handle sending a message
  const handleSendMessage = useCallback(
    async (message: string) => {
      if (!activeSessionId) {
        setError('No active session');
        return;
      }

      const session = activeSession();
      if (!session) {
        setError('Session not found');
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Add user message to the session
        const userMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'user',
          content: message,
          timestamp: new Date().toISOString(),
        };
        addMessage(activeSessionId, userMessage);

        // Start streaming
        startStreaming();

        // Send message to API with streaming
        const stream = await apiClient.chat.sendStreaming(
          message,
          activeSessionId,
          session.repositoryIds,
          session.explanationMode
        );

        // Process the stream
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true });
          
          // Parse SSE format (data: {...}\n\n)
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'content') {
                  // Append content to stream
                  accumulatedContent += data.content;
                  appendToStream(data.content);
                } else if (data.type === 'done') {
                  // Stream complete - add assistant message
                  const assistantMessage: ChatMessage = {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: accumulatedContent,
                    citations: data.citations,
                    timestamp: new Date().toISOString(),
                  };
                  addMessage(activeSessionId, assistantMessage);
                  stopStreaming();
                } else if (data.type === 'error') {
                  // Handle error
                  setError(data.message || 'An error occurred');
                  stopStreaming();
                }
              } catch (parseError) {
                console.error('Failed to parse SSE data:', parseError);
              }
            }
          }
        }
      } catch (err: any) {
        console.error('Failed to send message:', err);
        setError(err.message || 'Failed to send message');
        stopStreaming();
      } finally {
        setLoading(false);
      }
    },
    [activeSessionId, activeSession, addMessage, startStreaming, appendToStream, stopStreaming, setLoading, setError]
  );

  // Handle mode change
  const handleModeChange = useCallback(
    (mode: ExplanationMode) => {
      if (!activeSessionId) return;
      setExplanationMode(activeSessionId, mode);
    },
    [activeSessionId, setExplanationMode]
  );

  // Handle suggested question click
  const handleSuggestedQuestionClick = useCallback(
    (question: string) => {
      handleSendMessage(question);
    },
    [handleSendMessage]
  );

  if (isInitializing) {
    return (
      <div className="container mx-auto px-6 py-8">
        <LoadingSkeleton />
      </div>
    );
  }

  if (error && !activeSession()) {
    return (
      <div className="container mx-auto px-6 py-8">
        <ErrorBanner
          message={error}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  const session = activeSession();

  return (
    <div className="h-screen flex flex-col">
      <motion.div
        variants={fadeIn}
        initial="hidden"
        animate="visible"
        className="flex-1 container mx-auto px-6 py-8"
      >
        {/* Error Banner */}
        {error && (
          <div className="mb-4">
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {/* Chat Panel */}
        <ChatPanel
          session={session}
          isStreaming={isStreaming}
          streamingMessage={streamingMessage}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onModeChange={handleModeChange}
          onSuggestedQuestionClick={handleSuggestedQuestionClick}
          className="h-full"
        />
      </motion.div>
    </div>
  );
}
