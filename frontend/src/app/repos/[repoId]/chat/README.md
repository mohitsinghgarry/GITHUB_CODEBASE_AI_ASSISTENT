# Chat Page Implementation

## Overview

This directory contains the chat page implementation for the GitHub Codebase RAG Assistant. The chat page provides an interactive interface for users to ask questions about their codebase using natural language.

## Files

- `page.tsx` - Main chat page component
- `page.test.tsx` - Unit tests for the chat page

## Features

### 1. Session Management

The chat page automatically manages chat sessions:

- **Auto-initialization**: Creates a new session if none exists for the repository
- **Session persistence**: Loads existing sessions from the chat store
- **Session selection**: Uses the most recent session if multiple exist

### 2. Streaming Response Display

Real-time message streaming with:

- **SSE (Server-Sent Events)**: Processes streaming responses from the backend
- **Progressive rendering**: Updates the UI as content streams in
- **Smooth animations**: Uses framer-motion for smooth transitions

### 3. Explanation Mode Persistence

Users can select their preferred explanation mode:

- **Beginner**: Clear explanations with examples
- **Technical**: Detailed technical explanations
- **Interview**: Interactive Q&A style

Mode changes are persisted to the session and used for all subsequent messages.

### 4. Message History

- **Persistent storage**: Messages are stored in Zustand store with localStorage persistence
- **Auto-scroll**: Automatically scrolls to the latest message
- **Message formatting**: Supports code syntax highlighting and citations

## Implementation Details

### State Management

The page uses Zustand store (`useChatStore`) for state management:

```typescript
const {
  sessions,              // All chat sessions
  activeSessionId,       // Currently active session ID
  isStreaming,          // Whether a message is streaming
  streamingMessage,     // Current streaming content
  isLoading,            // Loading state
  error,                // Error message
  activeSession,        // Get active session
  addSession,           // Add new session
  setActiveSession,     // Set active session
  addMessage,           // Add message to session
  startStreaming,       // Start streaming
  appendToStream,       // Append to streaming message
  stopStreaming,        // Stop streaming
  setExplanationMode,   // Set explanation mode
  setLoading,           // Set loading state
  setError,             // Set error state
} = useChatStore();
```

### API Integration

The page integrates with the backend API using `apiClient.chat.sendStreaming()`:

```typescript
const stream = await apiClient.chat.sendStreaming(
  message,
  activeSessionId,
  session.repositoryIds,
  session.explanationMode
);
```

### Streaming Response Processing

The page processes SSE (Server-Sent Events) format:

```typescript
// Parse SSE format (data: {...}\n\n)
const lines = chunk.split('\n');
for (const line of lines) {
  if (line.startsWith('data: ')) {
    const data = JSON.parse(line.slice(6));
    
    if (data.type === 'content') {
      // Append content to stream
      appendToStream(data.content);
    } else if (data.type === 'done') {
      // Stream complete - add assistant message
      addMessage(activeSessionId, assistantMessage);
      stopStreaming();
    } else if (data.type === 'error') {
      // Handle error
      setError(data.message);
      stopStreaming();
    }
  }
}
```

## Component Integration

The chat page uses the following components:

- **ChatPanel**: Main chat interface with message list, input, and mode selector
- **MessageList**: Displays chat messages with auto-scroll
- **ChatInput**: Text input with send button
- **ModeSelector**: Explanation mode selector
- **UserMessage**: User message bubble
- **AssistantMessage**: Assistant message bubble with code highlighting
- **CodeSnippetCard**: Code display with syntax highlighting
- **SourceCitations**: Clickable file chips for citations
- **SuggestedQuestions**: Suggested questions for empty state

## Requirements Validation

### Requirement 11.3

✅ **THE Frontend_App SHALL provide a chat interface with message history and code syntax highlighting**

- Chat interface implemented with ChatPanel component
- Message history stored in Zustand store with persistence
- Code syntax highlighting via AssistantMessage and CodeSnippetCard components

✅ **WHEN code is referenced in responses, THE Frontend_App SHALL display it with proper formatting and line numbers**

- CodeSnippetCard component displays code with syntax highlighting
- Line numbers shown for code snippets
- Citations link to source files

## Usage

### Basic Usage

1. Navigate to `/repos/[repoId]/chat`
2. The page automatically initializes a session
3. Type a question in the input field
4. Press Enter or click Send
5. Watch the response stream in real-time

### Changing Explanation Mode

1. Click on the mode selector in the header
2. Select Beginner, Technical, or Interview
3. The mode is persisted for all subsequent messages

### Suggested Questions

When the chat is empty, suggested questions are displayed:

- Understanding Code
- Finding Code
- Code Quality
- Best Practices

Click any suggested question to send it as a message.

## Error Handling

The page handles various error scenarios:

- **Session initialization failure**: Shows error banner with retry option
- **Message send failure**: Shows error banner with dismiss option
- **Streaming error**: Stops streaming and shows error message
- **Network errors**: Handled by API client with retry logic

## Testing

Unit tests are provided in `page.test.tsx`:

- Session initialization
- Message sending
- Streaming responses
- Mode changes
- Error handling

Run tests with:

```bash
npm test src/app/repos/[repoId]/chat/page.test.tsx
```

## Future Enhancements

Potential improvements for future iterations:

1. **Session management UI**: Add ability to create, rename, and delete sessions
2. **Message editing**: Allow users to edit and resend messages
3. **Message regeneration**: Regenerate assistant responses
4. **Export chat**: Export chat history as markdown or PDF
5. **Voice input**: Add speech-to-text for voice queries
6. **Keyboard shortcuts**: Add keyboard shortcuts for common actions
7. **Message search**: Search within chat history
8. **Message bookmarks**: Bookmark important messages

## Performance Considerations

- **Lazy loading**: Messages are rendered on-demand
- **Virtualization**: Consider implementing virtual scrolling for long conversations
- **Debouncing**: Input debouncing to prevent excessive API calls
- **Caching**: Session data cached in localStorage for fast loading

## Accessibility

- **Keyboard navigation**: Full keyboard support
- **Screen reader support**: ARIA labels and roles
- **Focus management**: Proper focus handling for modals and inputs
- **Color contrast**: WCAG AA compliant color contrast ratios

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- React 18+
- Next.js 14+
- Zustand 4+
- Framer Motion 10+
- TailwindCSS 3+

## License

MIT
