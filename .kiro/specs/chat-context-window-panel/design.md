# Design Document: Chat Context Window Panel

## Overview

The Chat Context Window Panel feature adds a dedicated side panel to the chat interface that displays referenced code files with syntax highlighting, line numbers, and highlighted line ranges. This panel provides immediate visual context for code citations mentioned in assistant responses, improving code comprehension without requiring navigation away from the conversation.

The feature integrates seamlessly with the existing chat page by:
- Adding a new `ContextPanel` component positioned on the right side of the chat interface
- Managing state for the currently selected citation and navigation between multiple citations
- Responding to citation badge clicks to update the displayed content
- Providing responsive behavior that adapts to different viewport sizes
- Leveraging the existing `react-syntax-highlighter` library for code rendering

The implementation follows the existing component architecture patterns in the frontend codebase, using React hooks for state management and Tailwind CSS for styling consistent with the Material Design 3 theme.

## Architecture

### Component Structure

```
ChatPage (frontend/src/app/chat/page.tsx)
├── AppShell (layout wrapper)
├── TopBar (repository/model selectors)
├── MessageArea (existing chat messages)
│   ├── UserMessage
│   ├── AssistantMessage
│   │   └── CitationBadges (clickable)
│   └── ChatInput
└── ContextPanel (NEW)
    ├── ContextPanelHeader
    │   ├── FilePath display
    │   └── OpenInViewerButton
    ├── CitationNavigator (when multiple citations)
    └── CodeDisplay
        ├── SyntaxHighlighter (react-syntax-highlighter)
        └── LineNumbers with highlighting
```

### State Management

The chat page will manage the following new state:

```typescript
// Currently selected citation to display in context panel
const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

// Index of current citation when navigating multiple citations in a message
const [currentCitationIndex, setCurrentCitationIndex] = useState<number>(0);

// Citations from the currently active assistant message
const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
```

### Data Flow

1. **Citation Display Trigger**:
   - Assistant message arrives with citations array
   - First citation automatically selected and displayed in ContextPanel
   - `selectedCitation` state updated
   - `activeCitations` state updated with all citations from message

2. **Citation Badge Click**:
   - User clicks citation badge in message
   - Click handler updates `selectedCitation` state
   - ContextPanel re-renders with new citation content
   - Clicked badge receives active styling

3. **Citation Navigation**:
   - User clicks next/previous navigation controls
   - `currentCitationIndex` incremented/decremented
   - `selectedCitation` updated to `activeCitations[currentCitationIndex]`
   - ContextPanel re-renders with new citation

4. **Open in Viewer**:
   - User clicks "Open in Viewer" button
   - Navigation to `/viewer?file=${citation.file_path}` (or appropriate viewer route)

### Integration Points

1. **Chat Message Rendering**:
   - Modify citation badge rendering to include click handlers
   - Add active state styling to currently selected citation badge
   - Pass `onCitationClick` callback to citation badge components

2. **Layout Adjustment**:
   - Modify chat page layout to accommodate side panel
   - Use CSS Grid or Flexbox to create two-column layout
   - Message area: flexible width with minimum 600px
   - Context panel: fixed width 400-600px

3. **Responsive Behavior**:
   - Media query at 1200px breakpoint
   - Below 1200px: Context panel overlays message area
   - Add dismiss button for overlay mode
   - Use CSS `position: fixed` for overlay positioning

## Components and Interfaces

### ContextPanel Component

**File**: `frontend/src/components/chat/ContextPanel.tsx`

```typescript
interface ContextPanelProps {
  citation: Citation | null;
  citations: Citation[];
  currentIndex: number;
  onNavigate: (direction: 'next' | 'prev') => void;
  onOpenInViewer: (filePath: string) => void;
  className?: string;
}

export function ContextPanel({
  citation,
  citations,
  currentIndex,
  onNavigate,
  onOpenInViewer,
  className
}: ContextPanelProps): JSX.Element
```

**Responsibilities**:
- Render empty state when no citation provided
- Display header with file path and "Open in Viewer" button
- Render navigation controls when multiple citations exist
- Display code content with syntax highlighting and line numbers
- Auto-scroll to highlighted line range on content change

### ContextPanelHeader Component

**File**: `frontend/src/components/chat/ContextPanelHeader.tsx`

```typescript
interface ContextPanelHeaderProps {
  filePath: string;
  onOpenInViewer: () => void;
}

export function ContextPanelHeader({
  filePath,
  onOpenInViewer
}: ContextPanelHeaderProps): JSX.Element
```

**Responsibilities**:
- Display "CONTEXT:" label with file path
- Truncate long file paths with ellipsis
- Render "Open in Viewer" button with external link icon
- Apply distinct background styling

### CitationNavigator Component

**File**: `frontend/src/components/chat/CitationNavigator.tsx`

```typescript
interface CitationNavigatorProps {
  currentIndex: number;
  totalCount: number;
  onNext: () => void;
  onPrevious: () => void;
}

export function CitationNavigator({
  currentIndex,
  totalCount,
  onNext,
  onPrevious
}: CitationNavigatorProps): JSX.Element
```

**Responsibilities**:
- Display current index and total count (e.g., "1 / 3")
- Render previous/next navigation buttons
- Disable previous button when at first citation
- Disable next button when at last citation
- Apply hover and disabled states

### CodeDisplay Component

**File**: `frontend/src/components/chat/CodeDisplay.tsx`

```typescript
interface CodeDisplayProps {
  content: string;
  language: string | null;
  startLine: number;
  endLine: number;
}

export function CodeDisplay({
  content,
  language,
  startLine,
  endLine
}: CodeDisplayProps): JSX.Element
```

**Responsibilities**:
- Render code with syntax highlighting using `react-syntax-highlighter`
- Display line numbers starting from `startLine`
- Apply background highlighting to lines in range `[startLine, endLine]`
- Handle null language by displaying as plain text
- Use `vscDarkPlus` theme for consistency

### Modified ChatPage Layout

**File**: `frontend/src/app/chat/page.tsx`

```typescript
// Add state management
const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
const [currentCitationIndex, setCurrentCitationIndex] = useState<number>(0);

// Add citation click handler
const handleCitationClick = (citation: Citation, allCitations: Citation[], index: number) => {
  setSelectedCitation(citation);
  setActiveCitations(allCitations);
  setCurrentCitationIndex(index);
};

// Add navigation handler
const handleNavigate = (direction: 'next' | 'prev') => {
  const newIndex = direction === 'next' 
    ? Math.min(currentCitationIndex + 1, activeCitations.length - 1)
    : Math.max(currentCitationIndex - 1, 0);
  setCurrentCitationIndex(newIndex);
  setSelectedCitation(activeCitations[newIndex]);
};

// Add open in viewer handler
const handleOpenInViewer = (filePath: string) => {
  // Navigate to viewer page with file path
  router.push(`/viewer?file=${encodeURIComponent(filePath)}`);
};

// Update layout to include ContextPanel
return (
  <AppShell>
    <div className="flex h-full">
      <div className="flex-1 flex flex-col min-w-[600px]">
        {/* Existing chat interface */}
      </div>
      <ContextPanel
        citation={selectedCitation}
        citations={activeCitations}
        currentIndex={currentCitationIndex}
        onNavigate={handleNavigate}
        onOpenInViewer={handleOpenInViewer}
        className="w-[500px] border-l border-outline-variant/10"
      />
    </div>
  </AppShell>
);
```

### Citation Badge Modifications

Update citation badge rendering to include click handlers and active state:

```typescript
// In renderMessage function for assistant messages
{msg.citations && msg.citations.length > 0 && (
  <div className="flex flex-wrap gap-2 pt-2">
    <span className="text-[10px] text-on-surface-variant uppercase tracking-widest block w-full mb-1">
      Sources
    </span>
    {msg.citations.map((citation, idx) => (
      <div
        key={idx}
        onClick={() => handleCitationClick(citation, msg.citations!, idx)}
        className={cn(
          "flex items-center gap-1.5 px-2 py-1 rounded text-[11px] border cursor-pointer transition-colors",
          selectedCitation?.chunk_id === citation.chunk_id
            ? "bg-primary/20 border-primary/50 text-primary"
            : "bg-surface-container text-on-surface-variant border-outline-variant/10 hover:border-primary/30"
        )}
        title={citation.content}
      >
        <span className="material-symbols-outlined text-xs">description</span>
        {citation.file_path}:{citation.start_line}
      </div>
    ))}
  </div>
)}
```

## Data Models

### Citation Interface (Existing)

```typescript
interface Citation {
  chunk_id: string;
  repository_id: string;
  file_path: string;
  start_line: number;
  end_line: number;
  language: string | null;
  content: string;
  score?: number;
}
```

This interface is already defined in the backend schema and frontend API client. No modifications needed.

### Component State Types

```typescript
// Context panel state
type ContextPanelState = {
  selectedCitation: Citation | null;
  activeCitations: Citation[];
  currentCitationIndex: number;
};

// Navigation direction
type NavigationDirection = 'next' | 'prev';

// Empty state configuration
type EmptyStateConfig = {
  icon: string;
  message: string;
};
```

## Error Handling

### Missing or Invalid Citation Data

**Scenario**: Citation object missing required fields or contains invalid data

**Handling**:
- Validate citation object before rendering
- Display error state in ContextPanel with message: "Unable to display code reference"
- Log error to console for debugging
- Prevent navigation to invalid citations

```typescript
function isValidCitation(citation: Citation | null): citation is Citation {
  return (
    citation !== null &&
    typeof citation.file_path === 'string' &&
    typeof citation.start_line === 'number' &&
    typeof citation.end_line === 'number' &&
    typeof citation.content === 'string' &&
    citation.start_line > 0 &&
    citation.end_line >= citation.start_line
  );
}
```

### Syntax Highlighter Errors

**Scenario**: react-syntax-highlighter fails to render code (invalid language, parsing error)

**Handling**:
- Wrap SyntaxHighlighter in error boundary
- Fall back to plain text rendering with monospace font
- Display warning message: "Syntax highlighting unavailable"
- Preserve line numbers and highlighting functionality

```typescript
try {
  return (
    <SyntaxHighlighter
      language={language || 'text'}
      style={vscDarkPlus}
      showLineNumbers={true}
      startingLineNumber={startLine}
      wrapLines={true}
      lineProps={(lineNumber) => ({
        style: {
          backgroundColor: lineNumber >= startLine && lineNumber <= endLine
            ? 'rgba(255, 255, 255, 0.1)'
            : 'transparent'
        }
      })}
    >
      {content}
    </SyntaxHighlighter>
  );
} catch (error) {
  console.error('Syntax highlighting failed:', error);
  return (
    <pre className="font-mono text-sm p-4 bg-surface-container-lowest">
      <code>{content}</code>
    </pre>
  );
}
```

### Navigation Errors

**Scenario**: User attempts to navigate beyond citation bounds

**Handling**:
- Disable navigation buttons at boundaries
- Clamp index values to valid range [0, citations.length - 1]
- Prevent state updates for invalid navigation attempts

```typescript
const handleNavigate = (direction: 'next' | 'prev') => {
  const newIndex = direction === 'next' 
    ? Math.min(currentCitationIndex + 1, activeCitations.length - 1)
    : Math.max(currentCitationIndex - 1, 0);
  
  // Only update if index actually changed
  if (newIndex !== currentCitationIndex) {
    setCurrentCitationIndex(newIndex);
    setSelectedCitation(activeCitations[newIndex]);
  }
};
```

### Empty State Handling

**Scenario**: No citations available in conversation

**Handling**:
- Display empty state component with helpful message
- Show icon indicating panel purpose
- Center content vertically and horizontally
- Provide clear call-to-action

```typescript
if (!citation) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center">
      <span className="material-symbols-outlined text-6xl text-outline mb-4">
        code
      </span>
      <p className="text-sm text-on-surface-variant max-w-xs">
        No code references yet. Ask a question about the codebase to see relevant code here.
      </p>
    </div>
  );
}
```

## Testing Strategy

### Unit Tests

**Component Rendering Tests**:
- ContextPanel renders empty state when citation is null
- ContextPanel renders code content when citation provided
- ContextPanelHeader displays correct file path
- ContextPanelHeader truncates long file paths
- CitationNavigator displays correct index and total count
- CitationNavigator disables buttons at boundaries
- CodeDisplay renders line numbers starting from startLine
- CodeDisplay applies highlighting to correct line range

**Interaction Tests**:
- Citation badge click updates selectedCitation state
- Navigation buttons update currentCitationIndex correctly
- Open in Viewer button triggers navigation with correct file path
- Citation badge shows active state when selected
- Clicking same citation badge does not cause re-render

**Edge Case Tests**:
- Single citation: navigation controls not displayed
- Empty citations array: empty state displayed
- Invalid citation data: error state displayed
- Null language: plain text rendering used
- start_line equals end_line: single line highlighted

**Responsive Behavior Tests**:
- Context panel positioned correctly at different viewport widths
- Overlay mode activated below 1200px breakpoint
- Dismiss button appears in overlay mode
- Message area maintains minimum width

### Integration Tests

**End-to-End Citation Flow**:
1. Send chat message
2. Receive assistant response with citations
3. Verify first citation displayed in context panel
4. Click different citation badge
5. Verify context panel updates with new citation
6. Navigate through multiple citations
7. Verify each citation displays correctly

**Layout Integration**:
1. Verify chat interface layout with context panel
2. Verify message area width adjustment
3. Verify responsive behavior at different breakpoints
4. Verify scrolling behavior (independent scroll areas)

**Syntax Highlighting Integration**:
1. Test various programming languages (Python, TypeScript, JavaScript, etc.)
2. Verify vscDarkPlus theme applied correctly
3. Verify line numbers align with code lines
4. Verify highlighted lines have distinct background

### Manual Testing Checklist

- [ ] Context panel displays on right side of chat interface
- [ ] First citation automatically displayed when assistant message arrives
- [ ] Citation badges are clickable and show hover state
- [ ] Active citation badge has distinct visual style
- [ ] Context panel updates when different citation clicked
- [ ] Navigation controls appear for multiple citations
- [ ] Previous button disabled on first citation
- [ ] Next button disabled on last citation
- [ ] File path displayed correctly in header
- [ ] Long file paths truncated with ellipsis
- [ ] "Open in Viewer" button navigates correctly
- [ ] Syntax highlighting applied based on language
- [ ] Line numbers start at correct value
- [ ] Highlighted lines have distinct background
- [ ] Code content scrollable independently
- [ ] Header remains fixed during scroll
- [ ] Empty state displayed when no citations
- [ ] Responsive behavior works at different viewport sizes
- [ ] Overlay mode activates below 1200px
- [ ] Dismiss button works in overlay mode

## Implementation Notes

### Styling Considerations

1. **Color Scheme**: Use existing Material Design 3 theme tokens
   - Background: `bg-surface-container-low`
   - Border: `border-outline-variant/10`
   - Text: `text-on-surface`
   - Highlighted lines: `bg-primary/10`
   - Active badge: `bg-primary/20 border-primary/50`

2. **Typography**: Use existing font classes
   - Header label: `text-[10px] uppercase tracking-widest`
   - File path: `text-sm font-mono`
   - Code: `font-mono text-sm`
   - Line numbers: `text-xs text-outline-variant`

3. **Spacing**: Follow existing patterns
   - Panel padding: `p-4`
   - Header padding: `px-4 py-3`
   - Gap between elements: `gap-2` or `gap-4`

### Performance Considerations

1. **Syntax Highlighting**: 
   - react-syntax-highlighter can be slow for large code blocks
   - Consider virtualization for very long files (>1000 lines)
   - Use `showLineNumbers` prop instead of custom line number rendering

2. **State Updates**:
   - Memoize citation click handlers to prevent unnecessary re-renders
   - Use `useCallback` for navigation handlers
   - Consider `useMemo` for computed values (e.g., isFirstCitation, isLastCitation)

3. **Scroll Performance**:
   - Use `scrollIntoView` with `behavior: 'smooth'` for auto-scroll
   - Debounce scroll events if adding scroll-based features
   - Use CSS `overflow-y: auto` instead of custom scroll implementation

### Accessibility Considerations

1. **Keyboard Navigation**:
   - Citation badges should be keyboard accessible (use button elements)
   - Navigation controls should support keyboard (arrow keys)
   - "Open in Viewer" button should be keyboard accessible

2. **Screen Readers**:
   - Add aria-label to navigation buttons ("Previous citation", "Next citation")
   - Add aria-label to citation badges with file path and line range
   - Add aria-live region for context panel updates
   - Add role="region" and aria-label to context panel

3. **Focus Management**:
   - Maintain focus on clicked citation badge
   - Trap focus in overlay mode
   - Restore focus when dismissing overlay

### Browser Compatibility

- Target modern browsers (Chrome, Firefox, Safari, Edge)
- Use CSS Grid/Flexbox (widely supported)
- react-syntax-highlighter supports all modern browsers
- Test responsive behavior on mobile devices (though primarily desktop feature)

### Future Enhancements

1. **Code Actions**:
   - Copy code button in context panel
   - Download file button
   - Share citation link

2. **Enhanced Navigation**:
   - Keyboard shortcuts for citation navigation (Ctrl+[ and Ctrl+])
   - Jump to specific citation by number
   - Search within displayed code

3. **Customization**:
   - Adjustable panel width (drag to resize)
   - Theme selection for syntax highlighting
   - Toggle line numbers on/off

4. **Performance**:
   - Virtual scrolling for very large files
   - Lazy loading of citation content
   - Caching of syntax-highlighted content

5. **Collaboration**:
   - Share specific citation with team members
   - Annotate citations with comments
   - Bookmark frequently referenced citations
