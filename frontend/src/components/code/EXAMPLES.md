# Code Review Components - Examples

## Example 1: Simple Code Viewer

```tsx
import { CodeViewer } from '@/components/code';

export function SimpleCodeViewerExample() {
  const code = `function calculateSum(a: number, b: number): number {
  return a + b;
}

const result = calculateSum(5, 10);
console.log(result); // 15`;

  return (
    <CodeViewer
      code={code}
      language="typescript"
      filePath="src/utils/math.ts"
      showLineNumbers={true}
    />
  );
}
```

## Example 2: Code Editor with State

```tsx
import { useState } from 'react';
import { CodeEditor } from '@/components/code';
import { Button } from '@/components/ui/button';

export function CodeEditorExample() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('typescript');
  const [filePath, setFilePath] = useState('');

  const handleSubmit = () => {
    console.log('Submitting code:', { code, language, filePath });
    // Send to API for review
  };

  return (
    <div className="space-y-4">
      <CodeEditor
        value={code}
        onChange={setCode}
        language={language}
        onLanguageChange={setLanguage}
        filePath={filePath}
        onFilePathChange={setFilePath}
        placeholder="Paste your code here for review..."
        minHeight="400px"
      />
      
      <Button onClick={handleSubmit} disabled={!code}>
        Review Code
      </Button>
    </div>
  );
}
```

## Example 3: Review Results Display

```tsx
import { ReviewSummaryBar, ReviewResultCard } from '@/components/code';
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';

export function ReviewResultsExample() {
  const issues = [
    {
      description: "Variable 'unusedVar' is declared but never used",
      severity: 'medium' as const,
      lineNumber: 15,
      suggestion: "Remove the unused variable or use it in your code"
    },
    {
      description: "Potential null pointer exception",
      severity: 'high' as const,
      lineNumber: 42,
      suggestion: "Add null check before accessing property"
    },
    {
      description: "Consider using const instead of let for immutable variables",
      severity: 'low' as const,
      lineNumber: 8,
      suggestion: "Replace 'let' with 'const' for variables that are not reassigned"
    }
  ];

  return (
    <div className="space-y-6">
      <ReviewSummaryBar issues={issues} />
      
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {issues.map((issue, index) => (
          <motion.div key={index} variants={staggerItem}>
            <ReviewResultCard issue={issue} />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
```

## Example 4: Diff Viewer (Split Mode)

```tsx
import { DiffViewer } from '@/components/code';

export function DiffViewerSplitExample() {
  const before = `function getUserData(userId) {
  const user = database.query('SELECT * FROM users WHERE id = ' + userId);
  return user;
}`;

  const after = `function getUserData(userId: string): User | null {
  const user = database.query('SELECT * FROM users WHERE id = ?', [userId]);
  return user ?? null;
}`;

  return (
    <DiffViewer
      before={before}
      after={after}
      language="typescript"
      filePath="src/api/users.ts"
      mode="split"
    />
  );
}
```

## Example 5: Diff Viewer (Unified Mode)

```tsx
import { DiffViewer } from '@/components/code';

export function DiffViewerUnifiedExample() {
  const before = `const data = fetchData();
processData(data);`;

  const after = `const data = await fetchData();
await processData(data);`;

  return (
    <DiffViewer
      before={before}
      after={after}
      language="typescript"
      filePath="src/services/processor.ts"
      mode="unified"
    />
  );
}
```

## Example 6: Improvement Panel

```tsx
import { ImprovementPanel } from '@/components/code';

export function ImprovementPanelExample() {
  const improvedCode = `async function fetchUserData(userId: string): Promise<User> {
  try {
    const response = await fetch(\`/api/users/\${userId}\`);
    
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`);
    }
    
    const user = await response.json();
    return user;
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw error;
  }
}`;

  const explanation = `Key improvements made:

1. **Type Safety**: Added TypeScript types for parameters and return value
2. **Error Handling**: Wrapped in try-catch block for better error handling
3. **HTTP Status Check**: Added response.ok check before parsing JSON
4. **Async/Await**: Used modern async/await syntax instead of callbacks
5. **Template Literals**: Used template literals for cleaner string interpolation
6. **Logging**: Added error logging for debugging purposes`;

  return (
    <ImprovementPanel
      code={improvedCode}
      explanation={explanation}
      language="typescript"
      filePath="src/api/users.ts"
      defaultExpanded={true}
    />
  );
}
```

## Example 7: Complete Review Flow

```tsx
import { useState } from 'react';
import {
  CodeEditor,
  ReviewSummaryBar,
  ReviewResultCard,
  DiffViewer,
  ImprovementPanel
} from '@/components/code';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import type { ReviewFeedback } from '@/types';

export function CompleteReviewFlowExample() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('typescript');
  const [filePath, setFilePath] = useState('');
  const [isReviewing, setIsReviewing] = useState(false);
  const [reviewResults, setReviewResults] = useState<ReviewFeedback | null>(null);
  const [improvedCode, setImprovedCode] = useState<string | null>(null);
  const [improvementExplanation, setImprovementExplanation] = useState<string | null>(null);

  const handleReview = async () => {
    setIsReviewing(true);
    try {
      // Call API to review code
      const response = await fetch('/api/v1/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, filePath })
      });
      
      const results = await response.json();
      setReviewResults(results);
    } catch (error) {
      console.error('Review failed:', error);
    } finally {
      setIsReviewing(false);
    }
  };

  const handleImprove = async () => {
    setIsReviewing(true);
    try {
      // Call API to improve code
      const response = await fetch('/api/v1/improve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, filePath })
      });
      
      const results = await response.json();
      setImprovedCode(results.improvedCode);
      setImprovementExplanation(results.explanation);
    } catch (error) {
      console.error('Improvement failed:', error);
    } finally {
      setIsReviewing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Code Input */}
      <section>
        <h2 className="text-headline-sm text-on-surface mb-4">
          Submit Code for Review
        </h2>
        <CodeEditor
          value={code}
          onChange={setCode}
          language={language}
          onLanguageChange={setLanguage}
          filePath={filePath}
          onFilePathChange={setFilePath}
          placeholder="Paste your code here..."
          minHeight="400px"
        />
        
        <div className="flex gap-3 mt-4">
          <Button
            onClick={handleReview}
            disabled={!code || isReviewing}
          >
            {isReviewing ? 'Reviewing...' : 'Review Code'}
          </Button>
          
          <Button
            variant="secondary"
            onClick={handleImprove}
            disabled={!code || isReviewing}
          >
            {isReviewing ? 'Improving...' : 'Improve Code'}
          </Button>
        </div>
      </section>

      {/* Review Results */}
      {reviewResults && (
        <section>
          <h2 className="text-headline-sm text-on-surface mb-4">
            Review Results
          </h2>
          
          <div className="space-y-6">
            <ReviewSummaryBar issues={reviewResults.issues} />
            
            {reviewResults.issues.length > 0 && (
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="space-y-4"
              >
                {reviewResults.issues.map((issue, index) => (
                  <motion.div key={index} variants={staggerItem}>
                    <ReviewResultCard issue={issue} />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </div>
        </section>
      )}

      {/* Improved Code */}
      {improvedCode && improvementExplanation && (
        <section>
          <h2 className="text-headline-sm text-on-surface mb-4">
            Improved Code
          </h2>
          
          <div className="space-y-6">
            <DiffViewer
              before={code}
              after={improvedCode}
              language={language}
              filePath={filePath}
              mode="split"
            />
            
            <ImprovementPanel
              code={improvedCode}
              explanation={improvementExplanation}
              language={language}
              filePath={filePath}
              defaultExpanded={true}
            />
          </div>
        </section>
      )}
    </div>
  );
}
```

## Example 8: No Issues State

```tsx
import { ReviewSummaryBar } from '@/components/code';

export function NoIssuesExample() {
  return (
    <ReviewSummaryBar issues={[]} />
  );
}
```

## Example 9: Critical Issues Only

```tsx
import { ReviewSummaryBar, ReviewResultCard } from '@/components/code';
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';

export function CriticalIssuesExample() {
  const criticalIssues = [
    {
      description: "SQL Injection vulnerability detected",
      severity: 'critical' as const,
      lineNumber: 23,
      suggestion: "Use parameterized queries instead of string concatenation"
    },
    {
      description: "Hardcoded credentials found in source code",
      severity: 'critical' as const,
      lineNumber: 8,
      suggestion: "Move credentials to environment variables"
    }
  ];

  return (
    <div className="space-y-6">
      <ReviewSummaryBar issues={criticalIssues} />
      
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {criticalIssues.map((issue, index) => (
          <motion.div key={index} variants={staggerItem}>
            <ReviewResultCard issue={issue} />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
```

## Styling Notes

All examples follow the RepoMind Assistant design system:

- **Spacing**: Uses 4px grid (space-y-4, space-y-6, space-y-8)
- **Typography**: text-headline-sm for section headers, text-on-surface for primary text
- **Animations**: Uses framer-motion with staggerContainer and staggerItem for lists
- **Colors**: Follows surface hierarchy and semantic colors (error, tertiary, primary)
