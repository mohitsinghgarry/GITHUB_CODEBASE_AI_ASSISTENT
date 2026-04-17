# Code Improvement Page

## Overview

The Code Improvement page allows users to submit code for AI-powered refactoring and receive improved code with detailed explanations of the changes.

## Features

### Code Input
- **Code Editor**: Multi-line code editor with syntax highlighting
- **Language Selection**: Support for 20+ programming languages
- **File Path**: Optional file path for context
- **Line Numbers**: Visual line number display

### Improvement
- **AI-Powered Refactoring**: Uses Ollama LLM for code improvement
- **Best Practices**: Applies language-specific best practices
- **Performance Optimization**: Suggests performance improvements
- **Readability Enhancement**: Improves code clarity and structure
- **Detailed Explanations**: Explains each improvement made

### Results Display
- **View Mode Toggle**: Switch between split and unified diff views
- **Diff Viewer**: Side-by-side or unified comparison of before/after
- **Improvement Panel**: Improved code with collapsible explanation
- **Copy Buttons**: Easy copying of improved code
- **Syntax Highlighting**: Language-aware code display

### States
- **Empty State**: Helpful prompt when no code is entered
- **Loading State**: Spinner and "Improving..." message during processing
- **Error State**: Clear error messages with retry option
- **Results State**: Diff view and improvement panel

## Components Used

- `CodeEditor`: Code input with language selection
- `DiffViewer`: Before/after code comparison
- `ImprovementPanel`: Improved code with explanation
- `Button`: Action buttons (Improve, Clear, View Mode)
- `AlertCircle`: Error state icon
- `Sparkles`: Improvement action icon
- `GitCompare`: Diff view icon

## API Integration

### Endpoint
```typescript
POST /api/v1/improve
```

### Request
```typescript
{
  code: string;
  language?: string;
  filePath?: string;
}
```

### Response
```typescript
{
  improved: string;
  explanation: string;
}
```

## User Flow

1. User pastes code into the editor
2. User optionally selects language and file path
3. User clicks "Improve Code"
4. System sends code to backend for improvement
5. Backend uses Ollama LLM to refactor code
6. Results displayed with diff view and explanation
7. User can toggle between split and unified views
8. User can copy improved code
9. User can read detailed explanation
10. User can clear and improve new code

## View Modes

### Split View
- Side-by-side comparison
- Before code on left (red tint)
- After code on right (green tint)
- Independent scrolling
- Copy buttons for each version

### Unified View
- Stacked comparison
- Before code on top (red background)
- After code on bottom (green background)
- Single scroll area
- Clear visual separation

## Animations

- **Fade In**: Results section fades in
- **Fade In Up**: Diff viewer and improvement panel slide up
- **Expand**: Explanation section expands/collapses
- **Error Animation**: Error banner slides down

## Styling

- Uses Material Design 3 color system
- Diff color coding:
  - Before/Removed: Error red tint
  - After/Added: Tertiary green tint
- Responsive layout with max-width container
- Consistent spacing and typography
- Monospace font for code display

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus states on buttons
- Color contrast compliance
- Screen reader friendly explanations

## Improvement Categories

The AI analyzes and improves code in several areas:

1. **Code Structure**
   - Function decomposition
   - Class organization
   - Module separation

2. **Performance**
   - Algorithm optimization
   - Memory efficiency
   - Caching strategies

3. **Readability**
   - Variable naming
   - Comment clarity
   - Code formatting

4. **Best Practices**
   - Design patterns
   - Error handling
   - Type safety

5. **Security**
   - Input validation
   - SQL injection prevention
   - XSS protection

## Future Enhancements

- [ ] Multiple improvement suggestions to choose from
- [ ] Incremental improvement (step-by-step)
- [ ] Improvement history and comparison
- [ ] Export improved code with explanation
- [ ] Custom improvement rules
- [ ] Batch file improvement
- [ ] Integration with version control
- [ ] Performance metrics comparison
