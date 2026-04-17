# Zustand Stores

This directory contains all Zustand stores for state management in the application.

## Stores

### 1. Repository Store (`repositoryStore.ts`)

Manages repository state including list of repositories, selected repository, ingestion jobs, and repository statistics.

**Usage:**

```typescript
import { useRepositoryStore } from '@/store';

function RepositoryList() {
  const repositories = useRepositoryStore((state) => state.repositories);
  const addRepository = useRepositoryStore((state) => state.addRepository);
  const selectedRepository = useRepositoryStore((state) => state.selectedRepository());
  
  // Add a repository
  const handleAdd = (repo: Repository) => {
    addRepository(repo);
  };
  
  return (
    <div>
      {repositories.map((repo) => (
        <div key={repo.id}>{repo.name}</div>
      ))}
    </div>
  );
}
```

**Key Features:**
- Repository CRUD operations
- Ingestion job tracking
- Selected repository management
- Computed getters for derived state

### 2. Chat Store (`chatStore.ts`)

Manages chat session state including active sessions, messages, streaming state, and explanation modes.

**Usage:**

```typescript
import { useChatStore } from '@/store';

function ChatInterface() {
  const activeSession = useChatStore((state) => state.activeSession());
  const addMessage = useChatStore((state) => state.addMessage);
  const isStreaming = useChatStore((state) => state.isStreaming);
  
  // Add a message to the active session
  const handleSendMessage = (content: string) => {
    if (activeSession) {
      addMessage(activeSession.id, {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      });
    }
  };
  
  return (
    <div>
      {activeSession?.messages.map((msg) => (
        <div key={msg.id}>{msg.content}</div>
      ))}
    </div>
  );
}
```

**Key Features:**
- Session management
- Message CRUD operations
- Streaming support
- Explanation mode configuration

### 3. Search Store (`searchStore.ts`)

Manages search state including queries, results, search modes, filters, and search history.

**Usage:**

```typescript
import { useSearchStore } from '@/store';

function SearchInterface() {
  const query = useSearchStore((state) => state.query);
  const mode = useSearchStore((state) => state.mode);
  const results = useSearchStore((state) => state.results);
  const setQuery = useSearchStore((state) => state.setQuery);
  const setMode = useSearchStore((state) => state.setMode);
  
  // Perform a search
  const handleSearch = () => {
    // API call would go here
    // Then update results with setResults
  };
  
  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <select value={mode} onChange={(e) => setMode(e.target.value as SearchMode)}>
        <option value="semantic">Semantic</option>
        <option value="keyword">Keyword</option>
        <option value="hybrid">Hybrid</option>
      </select>
    </div>
  );
}
```

**Key Features:**
- Search query management
- Multiple search modes (semantic, keyword, hybrid)
- Filter management
- Search history
- Pagination support

### 4. Settings Store (`settingsStore.ts`)

Manages application settings and user preferences including theme, UI preferences, and feature flags.

**Usage:**

```typescript
import { useSettingsStore } from '@/store';

function ThemeToggle() {
  const theme = useSettingsStore((state) => state.theme);
  const toggleTheme = useSettingsStore((state) => state.toggleTheme);
  
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  );
}

function SettingsPanel() {
  const fontSize = useSettingsStore((state) => state.fontSize);
  const setFontSize = useSettingsStore((state) => state.setFontSize);
  const streamingEnabled = useSettingsStore((state) => state.streamingEnabled);
  const setStreamingEnabled = useSettingsStore((state) => state.setStreamingEnabled);
  
  return (
    <div>
      <select value={fontSize} onChange={(e) => setFontSize(e.target.value as FontSize)}>
        <option value="xs">Extra Small</option>
        <option value="sm">Small</option>
        <option value="base">Base</option>
        <option value="lg">Large</option>
        <option value="xl">Extra Large</option>
      </select>
      
      <label>
        <input
          type="checkbox"
          checked={streamingEnabled}
          onChange={(e) => setStreamingEnabled(e.target.checked)}
        />
        Enable streaming responses
      </label>
    </div>
  );
}
```

**Key Features:**
- Theme management (light/dark/system)
- UI preferences (font size, line numbers, word wrap)
- Chat preferences (streaming, citations, auto-scroll)
- Search preferences (default mode, top-K, highlighting)
- Code review preferences
- Notification preferences
- Feature flags

## Store Architecture

All stores follow these patterns:

1. **TypeScript Types**: Fully typed with TypeScript for type safety
2. **Devtools Integration**: Redux DevTools support for debugging
3. **Persistence**: Automatic persistence to localStorage (selective)
4. **Computed Getters**: Derived state through getter functions
5. **Action Naming**: Clear action names for DevTools tracking
6. **Immutable Updates**: All state updates are immutable

## Persistence Strategy

Each store selectively persists state:

- **Repository Store**: Persists repositories and selected repository ID
- **Chat Store**: Persists sessions and active session ID
- **Search Store**: Persists mode, filters, history, and preferences
- **Settings Store**: Persists all settings

Transient state (loading, errors, streaming) is NOT persisted.

## Best Practices

1. **Selector Pattern**: Use selectors to subscribe to specific state slices
   ```typescript
   // Good - only re-renders when repositories change
   const repositories = useRepositoryStore((state) => state.repositories);
   
   // Bad - re-renders on any state change
   const store = useRepositoryStore();
   ```

2. **Computed Getters**: Use computed getters for derived state
   ```typescript
   const selectedRepo = useRepositoryStore((state) => state.selectedRepository());
   ```

3. **Action Batching**: Multiple actions in a single function don't cause multiple re-renders
   ```typescript
   const handleSubmit = () => {
     setQuery(newQuery);
     setMode('hybrid');
     setFilters({ language: ['python'] });
   };
   ```

4. **Reset Functions**: Use reset functions to clear state when needed
   ```typescript
   const reset = useRepositoryStore((state) => state.reset);
   ```

## Testing

To test components using these stores, you can:

1. **Mock the store**:
   ```typescript
   import { useRepositoryStore } from '@/store';
   
   jest.mock('@/store', () => ({
     useRepositoryStore: jest.fn(),
   }));
   ```

2. **Create a test store**:
   ```typescript
   import { create } from 'zustand';
   
   const testStore = create<RepositoryState>()((set) => ({
     // ... test state
   }));
   ```

## Migration from Other State Management

If migrating from Redux or Context API:

- **Redux**: Zustand actions are similar to Redux actions but don't require reducers
- **Context**: Zustand provides better performance by avoiding unnecessary re-renders
- **useState**: Zustand is better for global state that needs to be shared across components

## Performance Considerations

1. **Selector Optimization**: Only subscribe to the state you need
2. **Shallow Equality**: Zustand uses shallow equality by default
3. **Computed Values**: Use computed getters instead of deriving in components
4. **Persistence**: Only persist necessary state to avoid localStorage bloat
