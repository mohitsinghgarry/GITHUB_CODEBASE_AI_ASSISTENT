# Repository Components

This directory contains all components related to repository management in the RepoMind Assistant application.

## Components

### RepoInputCard

Input card for adding a new GitHub repository with URL validation and loading states.

**Features:**
- URL validation for GitHub repositories (HTTPS and SSH formats)
- Loading state with progress indicator
- Error handling with descriptive messages
- Success feedback
- Smooth animations with framer-motion

**Usage:**
```tsx
import { RepoInputCard } from '@/components/repo';

<RepoInputCard
  onSubmit={async (url) => {
    // Handle repository submission
    await addRepository(url);
  }}
  isLoading={isLoading}
  error={error}
  success="Repository added successfully!"
/>
```

**Props:**
- `onSubmit: (url: string) => Promise<void>` - Callback when repository URL is submitted
- `isLoading?: boolean` - Loading state
- `error?: string | null` - Error message
- `success?: string | null` - Success message
- `className?: string` - Additional CSS classes

---

### IndexingProgress

5-stage progress indicator for repository ingestion pipeline.

**Stages:**
1. Clone - Cloning repository
2. Read - Reading source files
3. Chunk - Chunking code
4. Embed - Generating embeddings
5. Store - Storing vectors

**Features:**
- Visual progress bar with percentage
- Stage-by-stage status indicators
- Animated transitions between stages
- Error state handling
- Success state display

**Usage:**
```tsx
import { IndexingProgress } from '@/components/repo';

<IndexingProgress
  stage="embed"
  status="running"
  progressPercent={65}
  repositoryName="owner/repo"
/>
```

**Props:**
- `stage?: IngestionStage` - Current stage ('clone' | 'read' | 'chunk' | 'embed' | 'store')
- `status: JobStatus` - Overall job status ('pending' | 'running' | 'completed' | 'failed')
- `progressPercent: number` - Progress percentage (0-100)
- `errorMessage?: string` - Error message (if failed)
- `repositoryName?: string` - Repository name
- `className?: string` - Additional CSS classes

---

### RepoStats

Display repository statistics in card format.

**Features:**
- Animated stat cards with icons
- Hover effects
- Responsive grid layout
- Shows files count, chunks count, languages count
- Displays branch and last updated time

**Usage:**
```tsx
import { RepoStats } from '@/components/repo';

<RepoStats
  fileCount={1523}
  chunkCount={8456}
  languageCount={5}
  lastUpdated="2026-04-15T10:30:00Z"
  defaultBranch="main"
/>
```

**Props:**
- `fileCount: number` - Number of files indexed
- `chunkCount: number` - Number of code chunks
- `languageCount: number` - Number of programming languages detected
- `lastUpdated?: string` - Last updated timestamp
- `defaultBranch?: string` - Default branch name
- `className?: string` - Additional CSS classes

---

### RepoCard

Card component for displaying repository information in a list.

**Features:**
- Repository metadata display
- Status indicator
- Hover and tap animations
- Click to navigate
- Action buttons (delete, reindex, open in GitHub)
- Error message display

**Usage:**
```tsx
import { RepoCard } from '@/components/repo';

<RepoCard
  repository={repository}
  onClick={() => router.push(`/repos/${repository.id}`)}
  onDelete={() => handleDelete(repository.id)}
  onReindex={() => handleReindex(repository.id)}
/>
```

**Props:**
- `repository: Repository` - Repository data
- `onClick?: () => void` - Click handler for card
- `onDelete?: () => void` - Delete handler
- `onReindex?: () => void` - Reindex handler
- `showActions?: boolean` - Show actions menu (default: true)
- `className?: string` - Additional CSS classes

---

### LanguageChart

Visual breakdown of programming languages in a repository.

**Features:**
- Horizontal bar chart with language percentages
- Color-coded language indicators (GitHub language colors)
- Animated bars with stagger effect
- Hover interactions
- File count display
- "Other" category for languages beyond max display

**Usage:**
```tsx
import { LanguageChart } from '@/components/repo';

<LanguageChart
  languages={[
    { name: 'TypeScript', percentage: 45.2, fileCount: 123 },
    { name: 'Python', percentage: 30.5, fileCount: 87 },
    { name: 'JavaScript', percentage: 15.3, fileCount: 45 },
    { name: 'CSS', percentage: 9.0, fileCount: 28 },
  ]}
  maxLanguages={10}
  showFileCounts={true}
/>
```

**Props:**
- `languages: LanguageData[]` - Language data array
  - `name: string` - Language name
  - `percentage: number` - Percentage (0-100)
  - `fileCount: number` - Number of files
  - `color?: string` - Custom color (optional)
- `maxLanguages?: number` - Maximum number of languages to display (default: 10)
- `showFileCounts?: boolean` - Show file counts (default: true)
- `className?: string` - Additional CSS classes

---

## Design System

All components follow the RepoMind Assistant "Obsidian Intelligence" design framework:

- **Colors**: Deep charcoal foundations with violet and indigo pulses
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: 4px grid system
- **Animations**: Quart easing for high-end, responsive "snap"
- **Surfaces**: Tonal layering without borders (No-Line Rule)

## Animation Presets

Components use the following animation presets from `@/lib/animation-presets`:

- `fadeInUp` - Cards and modals
- `staggerContainer` - Lists and grids
- `staggerItem` - Individual list items
- `hoverScale` - Interactive elements
- `scaleIn` - Buttons and badges

## Dependencies

- `framer-motion` - Animations
- `lucide-react` - Icons
- `@/components/ui/button` - Button component
- `@/components/common/StatusBadge` - Status badge component
- `@/lib/utils` - Utility functions (cn, formatRelativeTime)
- `@/lib/animation-presets` - Animation variants
- `@/types` - TypeScript types

## Related Components

- `StatusBadge` - Used for status indicators
- `Button` - Used for action buttons
- `LoadingSkeleton` - Can be used for loading states
- `ErrorBanner` - Can be used for error states
- `EmptyState` - Can be used for empty states

## Example: Repository List Page

```tsx
import { RepoInputCard, RepoCard } from '@/components/repo';
import { useRepositoryStore } from '@/store/repositoryStore';

export default function RepositoriesPage() {
  const { repositories, addRepository, removeRepository } = useRepositoryStore();

  return (
    <div className="space-y-8">
      {/* Add Repository */}
      <RepoInputCard
        onSubmit={addRepository}
        isLoading={isLoading}
        error={error}
      />

      {/* Repository List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {repositories.map((repo) => (
          <RepoCard
            key={repo.id}
            repository={repo}
            onClick={() => router.push(`/repos/${repo.id}`)}
            onDelete={() => removeRepository(repo.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

## Example: Repository Dashboard

```tsx
import { RepoStats, IndexingProgress, LanguageChart } from '@/components/repo';

export default function RepositoryDashboard({ repository, job, languages }) {
  return (
    <div className="space-y-8">
      {/* Indexing Progress (if in progress) */}
      {job && job.status !== 'completed' && (
        <IndexingProgress
          stage={job.stage}
          status={job.status}
          progressPercent={job.progressPercent}
          errorMessage={job.errorMessage}
          repositoryName={`${repository.owner}/${repository.name}`}
        />
      )}

      {/* Statistics */}
      <RepoStats
        fileCount={repository.fileCount}
        chunkCount={repository.chunkCount}
        languageCount={languages.length}
        lastUpdated={repository.updatedAt}
        defaultBranch={repository.defaultBranch}
      />

      {/* Language Breakdown */}
      <LanguageChart languages={languages} />
    </div>
  );
}
```
