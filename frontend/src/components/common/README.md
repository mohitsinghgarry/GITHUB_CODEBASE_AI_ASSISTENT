# Common Components

Reusable UI components used throughout the RepoMind Assistant application. These components follow the "Obsidian Intelligence" design framework and use framer-motion for animations.

## Components

### LoadingSkeleton

A versatile skeleton loader with pulse animation for loading states.

**Features:**
- Configurable width, height, and border radius
- Multiple skeleton lines support
- Preset variants (Text, Card, Avatar, Button, CodeBlock)
- Smooth pulse animation

**Usage:**
```tsx
import { LoadingSkeleton, TextSkeleton, CardSkeleton } from '@/components/common';

// Basic skeleton
<LoadingSkeleton width="100%" height="2rem" rounded="md" />

// Multiple lines
<LoadingSkeleton count={3} gap="0.5rem" />

// Preset variants
<TextSkeleton lines={3} />
<CardSkeleton />
```

**Props:**
- `width`: Width of the skeleton (CSS value, default: '100%')
- `height`: Height of the skeleton (CSS value, default: '1rem')
- `rounded`: Border radius variant (default: 'md')
- `count`: Number of skeleton lines (default: 1)
- `gap`: Gap between lines when count > 1 (default: '0.5rem')
- `className`: Additional CSS classes

### EmptyState

A reusable empty state component with icon, message, and optional action buttons.

**Features:**
- Customizable icon (Lucide icons)
- Primary and secondary action buttons
- Three size variants (sm, md, lg)
- Smooth fadeInUp animation
- Preset variants for common scenarios

**Usage:**
```tsx
import { EmptyState, NoRepositoriesEmpty } from '@/components/common';
import { FolderOpen } from 'lucide-react';

// Custom empty state
<EmptyState
  icon={FolderOpen}
  title="No repositories yet"
  description="Add your first repository to get started."
  actionLabel="Add Repository"
  onAction={() => console.log('Add clicked')}
/>

// Preset variants
<NoRepositoriesEmpty onAction={handleAdd} />
<NoSearchResultsEmpty />
<NoChatHistoryEmpty />
```

**Props:**
- `icon`: Lucide icon component (required)
- `title`: Title text (required)
- `description`: Description text
- `actionLabel`: Primary action button label
- `onAction`: Primary action button handler
- `secondaryActionLabel`: Secondary action button label
- `onSecondaryAction`: Secondary action button handler
- `size`: Size variant ('sm' | 'md' | 'lg', default: 'md')
- `className`: Additional CSS classes

**Preset Variants:**
- `NoRepositoriesEmpty`: For empty repository list
- `NoSearchResultsEmpty`: For empty search results
- `NoChatHistoryEmpty`: For empty chat history
- `NoFilesEmpty`: For empty file list
- `NoDataEmpty`: Generic no data state
- `ErrorEmpty`: For error states with retry

### ErrorBanner

A reusable error banner with retry functionality and dismiss option.

**Features:**
- Three variants (error, warning, info)
- Retry button with loading state
- Dismissible with close button
- Smooth fadeInUp animation
- Preset variants for common errors

**Usage:**
```tsx
import { ErrorBanner, NetworkErrorBanner } from '@/components/common';

// Custom error banner
<ErrorBanner
  title="Connection Error"
  message="Unable to connect to the server."
  onRetry={handleRetry}
  onDismiss={handleDismiss}
  variant="error"
/>

// Preset variants
<NetworkErrorBanner onRetry={handleRetry} onDismiss={handleDismiss} />
<AuthErrorBanner onRetry={handleRetry} onDismiss={handleDismiss} />
<ServerErrorBanner onRetry={handleRetry} onDismiss={handleDismiss} />
```

**Props:**
- `title`: Error title
- `message`: Error message (required)
- `onRetry`: Retry button handler
- `onDismiss`: Dismiss button handler
- `retryLabel`: Retry button label (default: 'Try Again')
- `dismissible`: Show dismiss button (default: true)
- `variant`: Style variant ('error' | 'warning' | 'info', default: 'error')
- `className`: Additional CSS classes

**Preset Variants:**
- `NetworkErrorBanner`: For network/connection errors
- `AuthErrorBanner`: For authentication errors
- `ValidationErrorBanner`: For validation errors
- `ServerErrorBanner`: For server errors
- `RateLimitErrorBanner`: For rate limit errors
- `InfoBanner`: For informational messages

### StatusBadge

A reusable status badge with status-based colors and optional icon.

**Features:**
- 11 predefined status types
- Three variants (default, outline, subtle)
- Three size variants (sm, md, lg)
- Animated icons for loading/running states
- Smooth scaleIn animation
- Preset badge components

**Usage:**
```tsx
import { StatusBadge, SuccessBadge, LoadingBadge } from '@/components/common';

// Custom status badge
<StatusBadge status="success" label="Completed" size="md" variant="default" />

// Preset badges
<SuccessBadge />
<ErrorBadge />
<LoadingBadge />
<RunningBadge />
```

**Props:**
- `status`: Status type (required)
  - 'success' | 'error' | 'warning' | 'info' | 'pending' | 'loading' | 'idle' | 'completed' | 'failed' | 'running' | 'queued'
- `label`: Custom label (overrides default)
- `showIcon`: Show icon (default: true)
- `icon`: Custom icon (overrides default)
- `size`: Size variant ('sm' | 'md' | 'lg', default: 'md')
- `variant`: Style variant ('default' | 'outline' | 'subtle', default: 'default')
- `animate`: Animate on mount (default: true)
- `className`: Additional CSS classes

**Preset Badges:**
- `SuccessBadge` / `CompletedBadge`: Green badge for success states
- `ErrorBadge` / `FailedBadge`: Red badge for error states
- `WarningBadge`: Yellow badge for warning states
- `InfoBadge`: Blue badge for info states
- `PendingBadge` / `QueuedBadge`: Gray badge for pending states
- `LoadingBadge` / `RunningBadge`: Blue badge with spinning icon

### CopyButton

A reusable copy-to-clipboard button with success feedback.

**Features:**
- Automatic clipboard API integration
- Visual success feedback (icon change)
- Configurable success duration
- Multiple variants (with/without tooltip, inline, code)
- Smooth scaleIn animation
- Custom hook for programmatic usage

**Usage:**
```tsx
import {
  CopyButton,
  CopyButtonWithTooltip,
  CodeCopyButton,
  useCopyToClipboard,
} from '@/components/common';

// Basic copy button
<CopyButton text="Hello World" />

// With tooltip
<CopyButtonWithTooltip text="Hello World" tooltip="Copy to clipboard" />

// For code blocks
<CodeCopyButton code={codeString} />

// Using the hook
const { isCopied, copy } = useCopyToClipboard();
<button onClick={() => copy('Hello World')}>
  {isCopied ? 'Copied!' : 'Copy'}
</button>
```

**Props:**
- `text`: Text to copy (required)
- `successMessage`: Success message (default: 'Copied!')
- `successDuration`: Duration to show success state in ms (default: 2000)
- `size`: Button size ('sm' | 'default' | 'lg' | 'icon', default: 'sm')
- `variant`: Button variant (default: 'ghost')
- `showLabel`: Show label text (default: false)
- `label`: Custom label text (default: 'Copy')
- `onCopy`: Callback after successful copy
- `onError`: Callback on copy error
- `className`: Additional CSS classes

**Specialized Variants:**
- `CopyButtonWithTooltip`: Copy button with tooltip
- `CodeCopyButton`: Positioned for code blocks (absolute top-right)
- `InlineCopyButton`: Small inline copy button
- `CopyTextButton`: Copy button with visible label

**Hook:**
- `useCopyToClipboard()`: Returns `{ isCopied, error, copy }`

## Animation Presets

All components use framer-motion animations from `@/lib/animation-presets`:

- **fadeInUp**: Used by EmptyState and ErrorBanner
- **scaleIn**: Used by StatusBadge and CopyButton
- **skeleton**: Used by LoadingSkeleton

## Design Tokens

All components use design tokens from `@/lib/design-tokens`:

- Colors: Surface hierarchy, semantic colors, text colors
- Spacing: 4px grid system
- Typography: Inter font family with predefined scales
- Border Radius: Consistent roundness values
- Shadows: Ambient shadows for floating elements

## Accessibility

All components follow accessibility best practices:

- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Focus states with visible indicators
- Screen reader friendly

## Examples

### Loading State
```tsx
<div className="space-y-4">
  <TextSkeleton lines={3} />
  <CardSkeleton />
</div>
```

### Empty State with Action
```tsx
<EmptyState
  icon={FolderOpen}
  title="No repositories"
  description="Get started by adding your first repository."
  actionLabel="Add Repository"
  onAction={handleAdd}
  secondaryActionLabel="Learn More"
  onSecondaryAction={handleLearnMore}
/>
```

### Error Handling
```tsx
{error && (
  <ErrorBanner
    title="Failed to load data"
    message={error.message}
    onRetry={refetch}
    onDismiss={() => setError(null)}
  />
)}
```

### Status Display
```tsx
<div className="flex gap-2">
  <StatusBadge status={job.status} />
  <StatusBadge status="running" label="Processing" />
</div>
```

### Copy Functionality
```tsx
<div className="relative">
  <pre className="p-4 bg-surface-container-lowest rounded-lg">
    <code>{codeString}</code>
  </pre>
  <CodeCopyButton code={codeString} />
</div>
```

## Best Practices

1. **Use preset variants** when available for consistency
2. **Combine components** for complex UI patterns
3. **Respect animation settings** - don't disable animations unless necessary
4. **Follow size conventions** - use 'sm' for compact UIs, 'md' for standard, 'lg' for emphasis
5. **Provide meaningful labels** for accessibility
6. **Handle errors gracefully** with ErrorBanner and retry functionality
7. **Use loading states** to improve perceived performance

## Dependencies

- `framer-motion`: Animation library
- `lucide-react`: Icon library
- `@radix-ui/react-slot`: Polymorphic component support
- `@radix-ui/react-tooltip`: Tooltip primitives
- `class-variance-authority`: Variant management
- `clsx` + `tailwind-merge`: Class name utilities
