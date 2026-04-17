# Design Document: Diff Review UI Enhancement

## Overview

This design enhances the diff review interface by transforming plain-text issue displays into rich, structured presentations with markdown rendering, collapsible sections, and improved visual hierarchy. The enhancement focuses on readability and scannability while maintaining the existing "Obsidian Intelligence" design system.

### Goals

- Render markdown-formatted issue descriptions with proper typography and code highlighting
- Implement collapsible sections for long descriptions to improve scanning efficiency
- Enhance code block formatting with distinct visual treatment
- Establish clear visual hierarchy between issue components
- Maintain accessibility standards (WCAG 2.1 AA)
- Preserve performance with large numbers of issues

### Non-Goals

- Modifying the backend API response structure
- Adding interactive code editing capabilities
- Implementing syntax highlighting for code blocks (use existing libraries)
- Changing the overall page layout or navigation

## Architecture

### Component Structure

```
DiffReviewPage (existing)
├── IssueCard (new)
│   ├── IssueHeader
│   │   ├── SeverityBadge
│   │   └── IssueTitle
│   ├── MarkdownDescription (new)
│   │   └── CollapsibleContent (new)
│   ├── LineNumberBadge
│   └── SuggestionSection (new)
```

### Technology Stack

- **Markdown Rendering**: `react-markdown` (already installed)
- **Markdown Extensions**: `remark-gfm` for GitHub Flavored Markdown (already installed)
- **Syntax Highlighting**: `react-syntax-highlighter` (already installed)
- **Styling**: Tailwind CSS with existing design tokens
- **State Management**: React hooks (useState for collapse state)

### Design Principles

1. **No-Line Rule**: Use background color shifts instead of borders for visual separation
2. **Tonal Layering**: Leverage surface hierarchy (container-lowest through container-highest)
3. **Typography Scale**: Use established font sizes (body-md, body-lg, label-md)
4. **Quart Easing**: Apply cubic-bezier(0.16, 1, 0.3, 1) for animations
5. **4px Grid**: All spacing must be multiples of 4px

## Components and Interfaces

### IssueCard Component

**Purpose**: Encapsulates all issue display logic with enhanced formatting

**Props**:
```typescript
interface IssueCardProps {
  issue: CodeIssue;
  index: number;
}

interface CodeIssue {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;  // Markdown-formatted
  line_number?: number;
  suggestion?: string;
}
```

**Responsibilities**:
- Render severity badge with appropriate color and icon
- Display issue title with proper typography
- Render markdown description with collapsible behavior
- Show line number badge when present
- Display suggestion section with distinct styling

### MarkdownDescription Component

**Purpose**: Renders markdown content with custom styling

**Props**:
```typescript
interface MarkdownDescriptionProps {
  content: string;
  maxLength?: number;  // Character threshold for collapsing (default: 200)
}
```

**Implementation Details**:
- Uses `react-markdown` with `remark-gfm` plugin
- Custom component overrides for code blocks, headings, lists
- Applies Tailwind classes matching design system
- Handles parsing errors gracefully with fallback to plain text

**Custom Renderers**:
```typescript
const components = {
  code: CodeBlock,        // Inline and block code
  h1: Heading1,           // Markdown headings
  h2: Heading2,
  h3: Heading3,
  p: Paragraph,           // Paragraphs with proper spacing
  ul: UnorderedList,      // Lists with spacing
  ol: OrderedList,
  li: ListItem,
  strong: Strong,         // Bold text
  em: Emphasis,           // Italic text
}
```

### CollapsibleContent Component

**Purpose**: Provides expand/collapse functionality for long content

**Props**:
```typescript
interface CollapsibleContentProps {
  content: string;
  maxLength: number;
  isMarkdown?: boolean;
}
```

**State**:
```typescript
const [isExpanded, setIsExpanded] = useState(false);
```

**Behavior**:
- Initially shows truncated preview (first `maxLength` characters)
- Displays "Show more" button with chevron-down icon
- Expands to full content on click with smooth animation
- Changes to "Show less" button with chevron-up icon when expanded
- Uses `accordion-down` and `accordion-up` animations from Tailwind config

### SuggestionSection Component

**Purpose**: Displays code suggestions with distinct visual treatment

**Props**:
```typescript
interface SuggestionSectionProps {
  suggestion: string;
}
```

**Styling**:
- Background: `surface-container-lowest` (true black for code)
- Border radius: `rounded-lg` (0.5rem)
- Padding: `p-4` (1rem)
- Font: `font-mono text-sm`
- Text color: `text-tertiary` (emerald for positive action)
- Icon: lightbulb or code icon in tertiary color

## Data Models

### Issue Display State

```typescript
interface IssueDisplayState {
  issues: CodeIssue[];
  expandedIssues: Set<number>;  // Track which issues are expanded
}
```

### Markdown Rendering Configuration

```typescript
interface MarkdownConfig {
  remarkPlugins: [remarkGfm];
  components: {
    code: ComponentType<CodeProps>;
    h1: ComponentType<HeadingProps>;
    h2: ComponentType<HeadingProps>;
    h3: ComponentType<HeadingProps>;
    p: ComponentType<ParagraphProps>;
    ul: ComponentType<ListProps>;
    ol: ComponentType<ListProps>;
    li: ComponentType<ListItemProps>;
    strong: ComponentType<TextProps>;
    em: ComponentType<TextProps>;
  };
}
```

### Code Block Props

```typescript
interface CodeBlockProps {
  inline?: boolean;
  className?: string;
  children: ReactNode;
}
```

## Error Handling

### Markdown Parsing Errors

**Scenario**: Malformed markdown or unsupported syntax
**Handling**: 
- Wrap `ReactMarkdown` in error boundary
- Fallback to plain text rendering with preserved line breaks
- Log error to console for debugging
- Display subtle warning icon (optional)

```typescript
try {
  return <ReactMarkdown>{content}</ReactMarkdown>;
} catch (error) {
  console.error('Markdown parsing failed:', error);
  return <pre className="whitespace-pre-wrap">{content}</pre>;
}
```

### Missing or Invalid Issue Data

**Scenario**: Issue object missing required fields
**Handling**:
- Provide default values for optional fields
- Display "Unknown" for missing severity
- Show empty state for missing description
- Skip rendering suggestion section if not present

```typescript
const {
  severity = 'info',
  title = 'Untitled Issue',
  description = '',
  line_number,
  suggestion
} = issue;
```

### Performance with Large Issue Lists

**Scenario**: Rendering 50+ issues with markdown
**Handling**:
- Use React.memo for IssueCard to prevent unnecessary re-renders
- Implement virtualization if issue count exceeds 100 (future enhancement)
- Lazy load markdown rendering for collapsed issues
- Debounce expand/collapse animations

## Testing Strategy

### Unit Tests

**Component Tests** (using React Testing Library):

1. **IssueCard Rendering**
   - Renders all issue fields correctly
   - Applies correct severity colors and icons
   - Shows/hides line number based on presence
   - Shows/hides suggestion section based on presence

2. **MarkdownDescription**
   - Renders headings with correct hierarchy
   - Renders code blocks with monospace font
   - Renders inline code with background
   - Renders lists with proper spacing
   - Handles bold and italic text
   - Falls back to plain text on parsing error

3. **CollapsibleContent**
   - Shows truncated content initially when length exceeds threshold
   - Shows full content when length is below threshold
   - Expands content on "Show more" click
   - Collapses content on "Show less" click
   - Updates button text and icon correctly
   - Applies smooth animation during transitions

4. **SuggestionSection**
   - Renders suggestion text with monospace font
   - Applies correct background color
   - Shows suggestion icon
   - Maintains consistent padding and spacing

**Example Test Cases**:

```typescript
describe('IssueCard', () => {
  it('renders markdown in description', () => {
    const issue = {
      severity: 'high',
      title: 'Test Issue',
      description: '# Heading\n\nThis is **bold** text with `code`',
    };
    render(<IssueCard issue={issue} index={0} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Heading');
    expect(screen.getByText('bold')).toHaveClass('font-bold');
  });

  it('collapses long descriptions', () => {
    const longDescription = 'a'.repeat(250);
    const issue = {
      severity: 'medium',
      title: 'Long Issue',
      description: longDescription,
    };
    render(<IssueCard issue={issue} index={0} />);
    expect(screen.getByText(/Show more/i)).toBeInTheDocument();
  });
});
```

### Integration Tests

1. **Full Issue List Rendering**
   - Renders multiple issues with varying severities
   - Handles mixed content (some with suggestions, some without)
   - Maintains performance with 20+ issues
   - Preserves scroll position after expand/collapse

2. **Markdown Edge Cases**
   - Handles nested lists
   - Renders code blocks with language hints
   - Processes GFM tables (if present)
   - Handles special characters and HTML entities

### Accessibility Tests

1. **Keyboard Navigation**
   - Tab through all interactive elements (expand/collapse buttons)
   - Activate expand/collapse with Enter and Space keys
   - Focus visible on all interactive elements

2. **Screen Reader Support**
   - Severity badges have aria-label
   - Expand/collapse buttons have descriptive aria-label
   - Code blocks have role="code" or appropriate semantic markup
   - Headings maintain proper hierarchy (h1 → h2 → h3)

3. **Color Contrast**
   - All text meets WCAG AA contrast ratios (4.5:1 for normal text)
   - Severity badges maintain contrast against backgrounds
   - Code blocks have sufficient contrast

### Visual Regression Tests

1. **Snapshot Tests**
   - Capture snapshots of IssueCard in all severity states
   - Capture collapsed and expanded states
   - Capture with and without suggestions
   - Capture markdown rendering variations

### Manual Testing Checklist

- [ ] Markdown headings render with correct sizes
- [ ] Code blocks have distinct background and monospace font
- [ ] Inline code has subtle background
- [ ] Lists have proper spacing and bullets/numbers
- [ ] Long descriptions collapse correctly
- [ ] Expand/collapse animation is smooth
- [ ] Suggestion section is visually distinct
- [ ] All severity colors match design system
- [ ] Typography follows design scale
- [ ] Spacing follows 4px grid
- [ ] No borders used for separation (No-Line Rule)
- [ ] Keyboard navigation works smoothly
- [ ] Focus indicators are visible

## Implementation Notes

### Markdown Styling

Apply Tailwind classes to match design system:

```typescript
const markdownComponents = {
  h1: ({ children }) => (
    <h1 className="text-title-lg font-semibold text-on-surface mb-4">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-title-md font-semibold text-on-surface mb-3">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-title-sm font-medium text-on-surface mb-2">
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p className="text-body-md text-on-surface-variant mb-3 leading-relaxed">
      {children}
    </p>
  ),
  code: ({ inline, children }) => {
    if (inline) {
      return (
        <code className="px-1.5 py-0.5 bg-surface-container-lowest rounded text-primary font-mono text-sm">
          {children}
        </code>
      );
    }
    return (
      <pre className="bg-surface-container-lowest rounded-lg p-4 overflow-x-auto mb-4">
        <code className="font-mono text-sm text-on-surface">
          {children}
        </code>
      </pre>
    );
  },
  ul: ({ children }) => (
    <ul className="list-disc list-inside mb-3 space-y-1.5 text-body-md text-on-surface-variant">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-inside mb-3 space-y-1.5 text-body-md text-on-surface-variant">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="ml-2">{children}</li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-on-surface">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic">{children}</em>
  ),
};
```

### Collapse Animation

Use Tailwind's built-in accordion animations:

```typescript
<div
  className={`overflow-hidden transition-all duration-normal ease-quart ${
    isExpanded ? 'max-h-[2000px]' : 'max-h-24'
  }`}
>
  {content}
</div>
```

### Performance Optimization

```typescript
// Memoize IssueCard to prevent unnecessary re-renders
export const IssueCard = React.memo(({ issue, index }: IssueCardProps) => {
  // Component implementation
});

// Memoize markdown components
const MemoizedMarkdown = React.memo(ReactMarkdown);
```

### Accessibility Enhancements

```typescript
// Expand/collapse button
<button
  onClick={() => setIsExpanded(!isExpanded)}
  aria-expanded={isExpanded}
  aria-label={isExpanded ? 'Show less' : 'Show more'}
  className="flex items-center gap-1 text-primary hover:text-primary-dim transition-colors"
>
  <span className="text-label-md">
    {isExpanded ? 'Show less' : 'Show more'}
  </span>
  <span className="material-symbols-outlined text-sm">
    {isExpanded ? 'expand_less' : 'expand_more'}
  </span>
</button>

// Severity badge
<span
  role="status"
  aria-label={`Severity: ${severity}`}
  className={`px-3 py-1 rounded-full bg-${color}/10 text-${color} text-xs font-bold uppercase`}
>
  {severity}
</span>
```

## Migration Path

### Phase 1: Create New Components
- Implement IssueCard component
- Implement MarkdownDescription component
- Implement CollapsibleContent component
- Implement SuggestionSection component
- Add unit tests for each component

### Phase 2: Integrate into DiffReviewPage
- Replace existing issue rendering with IssueCard
- Test with existing API responses
- Verify no regressions in functionality

### Phase 3: Polish and Optimize
- Add accessibility enhancements
- Optimize performance with memoization
- Add visual regression tests
- Update documentation

## Future Enhancements

- Syntax highlighting for code blocks based on language hints
- Copy-to-clipboard button for code blocks
- Collapsible file sections in addition to issue descriptions
- Keyboard shortcuts for expanding/collapsing all issues
- Virtualized rendering for 100+ issues
- Dark/light mode toggle (design system already supports it)
