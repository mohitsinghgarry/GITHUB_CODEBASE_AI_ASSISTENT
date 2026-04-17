# File Explorer Components

A comprehensive set of components for displaying and interacting with repository file structures.

## Components

### FileTree

The main container component that displays a hierarchical file tree structure.

**Features:**
- Hierarchical file/directory display
- Language-based filtering
- File and directory counting
- Staggered animations on mount
- Loading and empty states

**Usage:**
```tsx
import { FileTree, FileTreeNode } from '@/components/files';

const nodes: FileTreeNode[] = [
  {
    id: '1',
    name: 'src',
    path: 'src',
    type: 'directory',
    children: [
      {
        id: '2',
        name: 'index.ts',
        path: 'src/index.ts',
        type: 'file',
        language: 'typescript',
        size: 1024,
        lineCount: 50,
      },
    ],
  },
];

<FileTree
  nodes={nodes}
  onFileSelect={(node) => console.log('Selected:', node)}
  selectedPath="src/index.ts"
  showLanguageFilter={true}
/>
```

**Props:**
- `nodes`: Array of root file tree nodes
- `onFileSelect`: Callback when a file is selected
- `selectedPath`: Currently selected file path
- `showLanguageFilter`: Show language filter (default: true)
- `languages`: Available languages (auto-detected if not provided)
- `isLoading`: Loading state
- `className`: Additional CSS classes

---

### FileNode

Individual file or directory node with expand/collapse functionality.

**Features:**
- Expand/collapse animations for directories
- File type icons
- Language badges
- Metadata display (size, line count)
- Selection states
- Hover effects

**Usage:**
```tsx
import { FileNode, FileTreeNode } from '@/components/files';

const node: FileTreeNode = {
  id: '1',
  name: 'index.ts',
  path: 'src/index.ts',
  type: 'file',
  language: 'typescript',
  size: 1024,
  lineCount: 50,
};

<FileNode
  node={node}
  onSelect={(node) => console.log('Selected:', node)}
  selectedPath="src/index.ts"
  level={0}
/>
```

**Props:**
- `node`: Tree node data
- `onSelect`: Callback when node is selected
- `selectedPath`: Currently selected file path
- `level`: Nesting level (for indentation)
- `className`: Additional CSS classes

---

### FileHeader

Displays file metadata at the top of file viewers.

**Features:**
- File path with directory breadcrumb
- Language badge
- File size and line count
- Last modified date and author
- Copy path button
- External link to GitHub

**Usage:**
```tsx
import { FileHeader } from '@/components/files';

<FileHeader
  path="src/components/FileTree.tsx"
  language="typescript"
  size={5120}
  lineCount={250}
  lastModified={new Date()}
  lastModifiedBy="john.doe"
  repositoryUrl="https://github.com/user/repo"
  showCopyPath={true}
  showExternalLink={true}
/>
```

**Props:**
- `path`: File path
- `language`: Programming language
- `size`: File size in bytes
- `lineCount`: Number of lines
- `lastModified`: Last modified date
- `lastModifiedBy`: Last modified author
- `repositoryUrl`: Repository URL for external link
- `showCopyPath`: Show copy path button (default: true)
- `showExternalLink`: Show external link button (default: true)
- `className`: Additional CSS classes

---

### FileSummaryCard

Displays AI-generated summary of a file's purpose and key functionality.

**Features:**
- AI-generated summary text
- Key elements (functions, classes, interfaces)
- Loading states with shimmer animation
- Error handling with retry
- Collapsible content
- Regenerate button

**Usage:**
```tsx
import { FileSummaryCard } from '@/components/files';

<FileSummaryCard
  summary="This file implements the main application entry point..."
  keyElements={[
    {
      name: 'main',
      type: 'function',
      description: 'Application entry point',
    },
    {
      name: 'App',
      type: 'class',
      description: 'Main application class',
    },
  ]}
  isLoading={false}
  error={undefined}
  onRegenerate={() => console.log('Regenerate')}
  collapsible={true}
  initiallyCollapsed={false}
/>
```

**Props:**
- `summary`: AI-generated summary text
- `keyElements`: Array of key functions/classes
- `isLoading`: Loading state
- `error`: Error message
- `onRegenerate`: Callback to regenerate summary
- `collapsible`: Enable collapse/expand (default: false)
- `initiallyCollapsed`: Initially collapsed state (default: false)
- `className`: Additional CSS classes

---

### LanguageFilter

Multi-select filter for programming languages.

**Features:**
- Language chips with selection states
- Select all / Clear all buttons
- Staggered animations
- Collapsible
- Language-specific colors

**Usage:**
```tsx
import { LanguageFilter } from '@/components/files';

<LanguageFilter
  languages={['typescript', 'javascript', 'python']}
  selectedLanguages={['typescript']}
  onSelectionChange={(languages) => console.log('Selected:', languages)}
  showIcon={true}
  showClearAll={true}
  showSelectAll={true}
  collapsible={false}
/>
```

**Props:**
- `languages`: Available languages
- `selectedLanguages`: Currently selected languages
- `onSelectionChange`: Callback when selection changes
- `showIcon`: Show filter icon (default: true)
- `showClearAll`: Show clear all button (default: true)
- `showSelectAll`: Show select all button (default: true)
- `collapsible`: Enable collapse/expand (default: false)
- `className`: Additional CSS classes

---

## Types

### FileTreeNode

```typescript
interface FileTreeNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  language?: string;
  size?: number;
  children?: FileTreeNode[];
  lineCount?: number;
}
```

---

## Animations

All components use framer-motion animations from `@/lib/animation-presets`:

- **FileTree**: `staggerContainer` and `staggerItem` for sequential appearance
- **FileNode**: `treeNode` for expand/collapse, `fadeIn` for appearance
- **FileHeader**: `fadeInUp` for smooth entrance
- **FileSummaryCard**: `fadeInUp` for entrance, `shimmer` for loading
- **LanguageFilter**: `fadeIn` for container, `staggerContainer` for chips

---

## Styling

All components follow the RepoMind Assistant design system:

- **Colors**: Uses design tokens from `@/lib/design-tokens`
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: 4px grid system
- **Animations**: Quart easing for high-end snap

---

## Examples

### Complete File Explorer

```tsx
import { FileTree, FileHeader, FileSummaryCard } from '@/components/files';

function FileExplorer() {
  const [selectedFile, setSelectedFile] = useState<FileTreeNode | null>(null);
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* File Tree */}
      <div className="lg:col-span-1">
        <FileTree
          nodes={treeNodes}
          onFileSelect={setSelectedFile}
          selectedPath={selectedFile?.path}
        />
      </div>
      
      {/* File Details */}
      {selectedFile && (
        <div className="lg:col-span-2 space-y-6">
          <FileHeader
            path={selectedFile.path}
            language={selectedFile.language}
            size={selectedFile.size}
            lineCount={selectedFile.lineCount}
          />
          
          <FileSummaryCard
            summary="AI-generated summary..."
            keyElements={[...]}
          />
        </div>
      )}
    </div>
  );
}
```

---

## Testing

All components are designed to be testable:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { FileTree } from '@/components/files';

test('renders file tree', () => {
  const nodes = [
    { id: '1', name: 'test.ts', path: 'test.ts', type: 'file' },
  ];
  
  render(<FileTree nodes={nodes} />);
  expect(screen.getByText('test.ts')).toBeInTheDocument();
});

test('calls onFileSelect when file is clicked', () => {
  const handleSelect = jest.fn();
  const nodes = [
    { id: '1', name: 'test.ts', path: 'test.ts', type: 'file' },
  ];
  
  render(<FileTree nodes={nodes} onFileSelect={handleSelect} />);
  fireEvent.click(screen.getByText('test.ts'));
  expect(handleSelect).toHaveBeenCalledWith(nodes[0]);
});
```
