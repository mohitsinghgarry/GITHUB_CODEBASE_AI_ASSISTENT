# Code Review Page

## Overview

The Code Review page allows users to submit code for AI-powered analysis and receive structured feedback with issue detection and improvement suggestions.

## Features

### Code Input
- **Code Editor**: Multi-line code editor with syntax highlighting
- **Language Selection**: Support for 20+ programming languages
- **File Path**: Optional file path for context
- **Line Numbers**: Visual line number display

### Analysis
- **AI-Powered Review**: Uses Ollama LLM for code analysis
- **Issue Detection**: Identifies bugs, security vulnerabilities, and style violations
- **Severity Levels**: Critical, High, Medium, Low
- **Line References**: Issues linked to specific line numbers
- **Suggestions**: Actionable improvement suggestions for each issue

### Results Display
- **Summary Bar**: Overview with issue counts by severity
- **Summary Text**: High-level analysis summary
- **Issue Cards**: Detailed cards for each issue with:
  - Severity badge with color coding
  - Issue description
  - Line number reference
  - Improvement suggestion
- **Stagger Animation**: Smooth appearance of results

### States
- **Empty State**: Helpful prompt when no code is entered
- **Loading State**: Spinner and "Analyzing..." message during analysis
- **Error State**: Clear error messages with retry option
- **Results State**: Structured feedback display

## Components Used

- `CodeEditor`: Code input with language selection
- `ReviewSummaryBar`: Issue count summary with severity breakdown
- `ReviewResultCard`: Individual issue display
- `Button`: Action buttons (Analyze, Clear)
- `AlertCircle`: Error state icon
- `Sparkles`: Analysis action icon

## API Integration

### Endpoint
```typescript
POST /api/v1/review
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
  issues: ReviewIssue[];
  summary: string;
}
```

### ReviewIssue Type
```typescript
{
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  lineNumber?: number;
  suggestion?: string;
}
```

## User Flow

1. User pastes code into the editor
2. User optionally selects language and file path
3. User clicks "Analyze Code"
4. System sends code to backend for analysis
5. Backend uses Ollama LLM to analyze code
6. Results displayed with summary and issue cards
7. User can review issues and apply suggestions
8. User can clear and analyze new code

## Animations

- **Stagger Container**: Results appear with staggered timing
- **Fade In Up**: Issue cards slide up and fade in
- **Fade In**: Summary bar fades in
- **Error Animation**: Error banner slides down

## Styling

- Uses Material Design 3 color system
- Severity-based color coding:
  - Critical/High: Error red
  - Medium: Secondary yellow
  - Low: Primary blue
- Responsive layout with max-width container
- Consistent spacing and typography

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus states on buttons
- Color contrast compliance
- Screen reader friendly error messages

## Future Enhancements

- [ ] Code diff view showing suggested fixes
- [ ] One-click fix application
- [ ] Export review results as PDF/JSON
- [ ] Review history and comparison
- [ ] Custom review rules configuration
- [ ] Batch file review
- [ ] Integration with version control
