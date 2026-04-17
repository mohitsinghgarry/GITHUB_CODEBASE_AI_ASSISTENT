# CodeDisplay Component

## Overview

The `CodeDisplay` component renders code content with syntax highlighting, line numbers, and visual highlighting for specific line ranges. It's designed to display code citations in the chat context panel.

## Features

- ✅ Syntax highlighting using `react-syntax-highlighter` with `vscDarkPlus` theme
- ✅ Line numbers starting from a custom `startLine` value
- ✅ Visual highlighting for lines within `[startLine, endLine]` range
- ✅ Handles `null` language by displaying as plain text
- ✅ Error boundary for graceful fallback on syntax highlighter failures
- ✅ Responsive and scrollable for long code blocks

## Requirements Validation

**Validates: Requirements 1.3, 1.4, 1.5**

- **Requirement 1.3**: Syntax highlighting with vscDarkPlus theme using react-syntax-highlighter, handle null language as plain text ✅
- **Requirement 1.4**: Line numbers starting at startLine value, visually distinct and aligned ✅
- **Requirement 1.5**: Visual highlighting for lines within [startLine, endLine] range with distinct background color ✅

## Usage

```tsx
import { CodeDisplay } from '@/components/chat/CodeDisplay';

function MyComponent() {
  return (
    <CodeDisplay
      content="function hello() {\n  console.log('Hello, World!');\n}"
      language="javascript"
      startLine={1}
      endLine={2}
    />
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `content` | `string` | Yes | The code content to display |
| `language` | `string \| null` | Yes | Programming language for syntax highlighting (e.g., 'typescript', 'python'). Use `null` for plain text |
| `startLine` | `number` | Yes | Starting line number for display and highlighting |
| `endLine` | `number` | Yes | Ending line number for highlighting |

## Examples

### TypeScript with Highlighting

```tsx
<CodeDisplay
  content={`function greet(name: string): string {
  return \`Hello, \${name}!\`;
}

const message = greet("World");`}
  language="typescript"
  startLine={1}
  endLine={3}
/>
```

### Python with Single Line Highlight

```tsx
<CodeDisplay
  content={`def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total`}
  language="python"
  startLine={1}
  endLine={1}
/>
```

### Plain Text (null language)

```tsx
<CodeDisplay
  content="This is plain text.\nNo syntax highlighting."
  language={null}
  startLine={10}
  endLine={11}
/>
```

### Code Starting at Higher Line Number

```tsx
<CodeDisplay
  content={`    if (condition) {
        performAction();
    }
}`}
  language="typescript"
  startLine={45}
  endLine={47}
/>
```

## Styling

The component uses:
- **vscDarkPlus theme**: Dark theme consistent with VS Code
- **Highlighted lines**: `rgba(255, 255, 255, 0.1)` background
- **Line numbers**: Right-aligned, 50% opacity, non-selectable
- **Font**: Monospace, 0.875rem (14px)
- **Padding**: 1rem
- **Border radius**: 0.375rem

## Error Handling

The component includes an error boundary that catches syntax highlighter failures and displays a fallback UI:

```
⚠️ Syntax highlighting unavailable
[Plain text code display]
```

This ensures the component never crashes and always displays the code content, even if syntax highlighting fails.

## Supported Languages

The component supports all languages supported by `react-syntax-highlighter`, including:

- JavaScript / TypeScript
- Python
- Java
- C / C++ / C#
- Go
- Rust
- Ruby
- PHP
- HTML / CSS
- SQL
- Shell / Bash
- And many more...

When `language` is `null`, the content is displayed as plain text without syntax highlighting.

## Performance Considerations

- The component uses `Prism` syntax highlighter for better performance
- Line highlighting is applied via inline styles for optimal rendering
- For very large code blocks (>1000 lines), consider implementing virtualization

## Accessibility

- Line numbers are marked as non-selectable (`userSelect: 'none'`)
- Code content remains fully selectable for copying
- Proper semantic HTML structure with `<pre>` and `<code>` elements

## Testing

See `CodeDisplay.example.tsx` for visual examples demonstrating:
- TypeScript code with multi-line highlighting
- Python code with single-line highlighting
- JavaScript code with range highlighting
- Plain text display (null language)
- Code starting at higher line numbers

## Integration with Context Panel

This component is designed to be used within the `ContextPanel` component:

```tsx
<ContextPanel>
  <CodeDisplay
    content={citation.content}
    language={citation.language}
    startLine={citation.startLine}
    endLine={citation.endLine}
  />
</ContextPanel>
```

## Future Enhancements

Potential improvements for future iterations:
- Copy button for code content
- Line wrapping toggle
- Theme selection (light/dark)
- Virtual scrolling for very large files
- Diff highlighting for code changes
