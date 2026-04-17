/**
 * Chat Store
 * 
 * Manages chat session state including:
 * - Active chat sessions
 * - Messages and conversation history
 * - Streaming state
 * - Explanation mode
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ChatSession, ChatMessage, ExplanationMode } from '@/types';

interface ChatState {
  // State
  sessions: Record<string, ChatSession>; // sessionId -> session
  activeSessionId: string | null;
  isStreaming: boolean;
  streamingMessage: string;
  isLoading: boolean;
  error: string | null;

  // Computed getters
  activeSession: () => ChatSession | null;
  getSessionById: (id: string) => ChatSession | null;
  getSessionsByRepositoryId: (repositoryId: string) => ChatSession[];
  
  // Session actions
  setSessions: (sessions: ChatSession[]) => void;
  addSession: (session: ChatSession) => void;
  updateSession: (sessionId: string, updates: Partial<ChatSession>) => void;
  removeSession: (sessionId: string) => void;
  setActiveSession: (sessionId: string | null) => void;
  
  // Message actions
  addMessage: (sessionId: string, message: ChatMessage) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  removeMessage: (sessionId: string, messageId: string) => void;
  clearMessages: (sessionId: string) => void;
  
  // Streaming actions
  startStreaming: () => void;
  appendToStream: (content: string) => void;
  stopStreaming: () => void;
  
  // Explanation mode actions
  setExplanationMode: (sessionId: string, mode: ExplanationMode) => void;
  
  // Utility actions
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  sessions: {},
  activeSessionId: null,
  isStreaming: false,
  streamingMessage: '',
  isLoading: false,
  error: null,
};

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Computed getters
        activeSession: () => {
          const { activeSessionId, sessions } = get();
          if (!activeSessionId) return null;
          return sessions[activeSessionId] || null;
        },

        getSessionById: (id: string) => {
          const { sessions } = get();
          return sessions[id] || null;
        },

        getSessionsByRepositoryId: (repositoryId: string) => {
          const { sessions } = get();
          return Object.values(sessions).filter((session) =>
            session.repositoryIds.includes(repositoryId)
          );
        },

        // Session actions
        setSessions: (sessionList) =>
          set(
            {
              sessions: sessionList.reduce(
                (acc, session) => {
                  acc[session.id] = session;
                  return acc;
                },
                {} as Record<string, ChatSession>
              ),
            },
            false,
            'setSessions'
          ),

        addSession: (session) =>
          set(
            (state) => ({
              sessions: {
                ...state.sessions,
                [session.id]: session,
              },
            }),
            false,
            'addSession'
          ),

        updateSession: (sessionId, updates) =>
          set(
            (state) => ({
              sessions: {
                ...state.sessions,
                [sessionId]: {
                  ...state.sessions[sessionId],
                  ...updates,
                  updatedAt: new Date().toISOString(),
                },
              },
            }),
            false,
            'updateSession'
          ),

        removeSession: (sessionId) =>
          set(
            (state) => {
              const { [sessionId]: _, ...rest } = state.sessions;
              return {
                sessions: rest,
                activeSessionId:
                  state.activeSessionId === sessionId
                    ? null
                    : state.activeSessionId,
              };
            },
            false,
            'removeSession'
          ),

        setActiveSession: (sessionId) =>
          set({ activeSessionId: sessionId }, false, 'setActiveSession'),

        // Message actions
        addMessage: (sessionId, message) =>
          set(
            (state) => {
              const session = state.sessions[sessionId];
              if (!session) return state;

              return {
                sessions: {
                  ...state.sessions,
                  [sessionId]: {
                    ...session,
                    messages: [...session.messages, message],
                    updatedAt: new Date().toISOString(),
                  },
                },
              };
            },
            false,
            'addMessage'
          ),

        updateMessage: (sessionId, messageId, updates) =>
          set(
            (state) => {
              const session = state.sessions[sessionId];
              if (!session) return state;

              return {
                sessions: {
                  ...state.sessions,
                  [sessionId]: {
                    ...session,
                    messages: session.messages.map((msg) =>
                      msg.id === messageId ? { ...msg, ...updates } : msg
                    ),
                    updatedAt: new Date().toISOString(),
                  },
                },
              };
            },
            false,
            'updateMessage'
          ),

        removeMessage: (sessionId, messageId) =>
          set(
            (state) => {
              const session = state.sessions[sessionId];
              if (!session) return state;

              return {
                sessions: {
                  ...state.sessions,
                  [sessionId]: {
                    ...session,
                    messages: session.messages.filter(
                      (msg) => msg.id !== messageId
                    ),
                    updatedAt: new Date().toISOString(),
                  },
                },
              };
            },
            false,
            'removeMessage'
          ),

        clearMessages: (sessionId) =>
          set(
            (state) => {
              const session = state.sessions[sessionId];
              if (!session) return state;

              return {
                sessions: {
                  ...state.sessions,
                  [sessionId]: {
                    ...session,
                    messages: [],
                    updatedAt: new Date().toISOString(),
                  },
                },
              };
            },
            false,
            'clearMessages'
          ),

        // Streaming actions
        startStreaming: () =>
          set(
            { isStreaming: true, streamingMessage: '' },
            false,
            'startStreaming'
          ),

        appendToStream: (content) =>
          set(
            (state) => ({
              streamingMessage: state.streamingMessage + content,
            }),
            false,
            'appendToStream'
          ),

        stopStreaming: () =>
          set(
            { isStreaming: false, streamingMessage: '' },
            false,
            'stopStreaming'
          ),

        // Explanation mode actions
        setExplanationMode: (sessionId, mode) =>
          set(
            (state) => {
              const session = state.sessions[sessionId];
              if (!session) return state;

              return {
                sessions: {
                  ...state.sessions,
                  [sessionId]: {
                    ...session,
                    explanationMode: mode,
                    updatedAt: new Date().toISOString(),
                  },
                },
              };
            },
            false,
            'setExplanationMode'
          ),

        // Utility actions
        setLoading: (isLoading) => set({ isLoading }, false, 'setLoading'),

        setError: (error) => set({ error }, false, 'setError'),

        reset: () => set(initialState, false, 'reset'),
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessions: state.sessions,
          activeSessionId: state.activeSessionId,
          // Don't persist streaming/loading/error states
        }),
      }
    ),
    { name: 'ChatStore' }
  )
);
