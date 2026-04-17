# Code Review Components

This directory contains components for code review and improvement features.

## Components

### CodeViewer

Displays code with syntax highlighting and copy functionality.

**Features:**
- Syntax highlighting
- Copy to clipboard button
- Line numbers
- Language badge
- File path display
- Fade in animation

**Usage:**
```tsx
import { CodeViewer } from '@/components/code';

<CodeViewer
  code={codeString}
  language="typescript"
  filePath="src/components/Button.tsx"
  showLineNumbers={true}
  startLine={1}
/>
```

### CodeEditor

Simple code input editor for code review and improvement requests.

**Features:**
- Textarea with monospace font
- Line numbers
- Language selector
- File path input
- Fade in animation

**Usage:**
```tsx
import { CodeEditor } from '@/components/code';

<CodeEditor
  value={code}
  onChange={setCode}
  language={language}
  onLanguageChange={setLanguage}
  filePath={filePath}
  onFilePathChange={setFilePath}
  placeholder="Paste your code here..."
  minHeight="300px"
/>
```

### ReviewResultCard

Displays a single code review issue with details.

**Features:**
- Severity badge with color coding (critical, high, medium, low)
- Issue description
- Line number reference
- Suggestion (if available)
- Fade in up animation

**Usage:**
```tsx
import { ReviewResultCard } from '@/components/code';

<ReviewResultCard
  issue={{
    description: "Variable 'x' is never used",
    severity: "medium",
    lineNumber: 42,
    suggestion: "Remove unused variable or use it in the code"
  }}
/>
```

### ReviewSummaryBar

Displays a summary of code review results with severity counts.

**Features:**
- Total issue count
- Breakdown by severity (critical, high, medium, low)
- Color-coded badges
- Success state when no issues found
- Fade in animation

**Usage:**
```tsx
import { ReviewSummaryBar } from '@/components/code';

<ReviewSummaryBar
  issues={reviewIssues}
/>
```

### DiffViewer

Displays before/after code comparison with diff highlighting.

**Features:**
- Side-by-side or unified diff view
- Line-by-line comparison
- Addition/deletion highlighting
- Copy buttons for both versions
- Slide up animation

**Usage:**
```tsx
import { DiffViewer } from '@/components/code';

// Split view (side-by-side)
<DiffViewer
  before={originalCode}
  after={improvedCode}
  language="typescript"
  filePath="src/utils/helper.ts"
  mode="split"
/>

// Unified view
<DiffViewer
  before={originalCode}
  after={improvedCode}
  language="typescript"
  filePath="src/utils/helper.ts"
  mode="unified"
/>
```

### ImprovementPanel

Displays improved/refactored code with explanations.

**Features:**
- Improved code display with syntax highlighting
- Explanation of changes
- Copy button
- Collapsible explanation section
- Fade in up animation

**Usage:**
```tsx
import { ImprovementPanel } from '@/components/code';

<ImprovementPanel
  code={improvedCode}
  explanation="Refactored to use async/await instead of callbacks for better readability and error handling."
  language="typescript"
  filePath="src/api/client.ts"
  defaultExpanded={true}
/>
```

## Animation Presets

All components use animation presets from `@/lib/animation-presets`:

- **fadeIn**: General content appearance
- **fadeInUp**: Cards and panels sliding up
- **expand**: Collapsible sections

## Design System

Components follow the RepoMind Assistant design system:

- **Colors**: Surface hierarchy with tonal layering
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: 4px grid system
- **Animations**: Quart easing for smooth transitions
- **No borders**: Uses background color shifts for boundaries

## Type Definitions

All components use types from `@/types`:

```typescript
interface ReviewIssue {
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  lineNumber?: number;
  suggestion?: string;
}

interface ReviewFeedback {
  issues: ReviewIssue[];
  summary: string;
}
```

## Example: Complete Review Flow

```tsx
import {
  CodeEditor,
  ReviewSummaryBar,
  ReviewResultCard,
  DiffViewer,
  ImprovementPanel
} from '@/components/code';

function CodeReviewPage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('typescript');
  const [reviewResults, setReviewResults] = useState<ReviewFeedback | null>(null);

  const handleReview = async () => {
    const results = await apiClient.reviewCode({ code, language });
    setReviewResults(results);
  };

  return (
    <div className="space-y-6">
      {/* Input */}
      <CodeEditor
        value={code}
        onChange={setCode}
        language={language}
        onLanguageChange={setLanguage}
      />

      {/* Results */}
      {reviewResults && (
        <>
          <ReviewSummaryBar issues={reviewResults.issues} />
          
          <div className="space-y-4">
            {reviewResults.issues.map((issue, index) => (
              <ReviewResultCard key={index} issue={issue} />
            ))}
          </div>

          {/* Show improvements if available */}
          {improvedCode && (
            <>
              <DiffViewer
                before={code}
                after={improvedCode}
                language={language}
                mode="split"
              />
              
              <ImprovementPanel
                code={improvedCode}
                explanation={improvementExplanation}
                language={language}
              />
            </>
          )}
        </>
      )}
    </div>
  );
}
```

## Accessibility

All components include:
- Keyboard navigation support
- Focus states with visible indicators
- ARIA labels where appropriate
- Semantic HTML structure
- Screen reader friendly content

## Performance

- Components use React.memo where appropriate
- Animations use GPU-accelerated transforms
- Large code blocks are virtualized when needed
- Copy operations use the Clipboard API with fallbacks
