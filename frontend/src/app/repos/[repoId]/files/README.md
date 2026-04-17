# File Explorer Pages

This directory contains the file explorer pages for browsing repository files.

## Pages

### `/repos/[repoId]/files` - File Explorer Page

Main file explorer page that displays the repository file tree.

**Features:**
- Hierarchical file tree with expand/collapse
- Language filtering
- File search
- File count statistics
- Click to navigate to file details

**Components Used:**
- `FileTree` - Hierarchical file tree component
- `LanguageFilter` - Multi-select language filter
- `Input` - Search input field

**API Calls:**
- `apiClient.repositories.get()` - Fetch repository metadata
- `apiClient.search.semantic()` - Fetch all chunks to build file tree

### `/repos/[repoId]/files/[...filePath]` - File Detail Page

Individual file detail page with syntax-highlighted code viewer.

**Features:**
- File metadata display (path, language, size, lines)
- Syntax-highlighted code viewer with line numbers
- Copy code functionality
- AI-generated file summary
- Breadcrumb navigation
- "Ask About This File" quick action
- External link to GitHub

**Components Used:**
- `FileHeader` - File metadata display
- `FileSummaryCard` - AI-generated summary
- `CodeViewer` - Syntax-highlighted code viewer
- `Button` - Action buttons

**API Calls:**
- `apiClient.repositories.get()` - Fetch repository metadata
- `apiClient.search.keyword()` - Fetch file chunks by path
- `apiClient.chat.send()` - Generate file summary

## File Tree Structure

The file tree is built from code chunks by:

1. Grouping chunks by file path
2. Splitting paths into directory hierarchy
3. Creating tree nodes for directories and files
4. Sorting directories first, then alphabetically
5. Attaching metadata (language, line count) to file nodes

## Code Reconstruction

File content is reconstructed from chunks by:

1. Sorting chunks by start line number
2. Filling gaps with empty lines
3. Merging overlapping or adjacent chunks
4. Joining lines into complete file content

## Syntax Highlighting

Syntax highlighting is provided by `react-syntax-highlighter` with:

- **Theme:** VS Code Dark Plus (matching design system)
- **Font:** JetBrains Mono (monospace)
- **Features:** Line numbers, copy button, line highlighting
- **Languages:** JavaScript, TypeScript, Python, Java, Go, Rust, C++, and more

## Navigation Flow

```
Repository Dashboard
  ↓
File Explorer (tree view)
  ↓
File Detail (code viewer)
  ↓
Chat (ask about file)
```

## Design System Compliance

All pages follow the "Obsidian Intelligence" design system:

- **No-Line Rule:** Uses background color shifts instead of borders
- **Tonal Layering:** Surface hierarchy for depth
- **Typography:** Inter for UI, JetBrains Mono for code
- **Spacing:** 4px grid system
- **Animations:** Framer Motion with Quart easing

## Future Enhancements

- [ ] Dedicated API endpoint for file tree (instead of using search)
- [ ] Pagination for large repositories
- [ ] File content caching
- [ ] Diff viewer for file changes
- [ ] Inline file editing
- [ ] File download functionality
- [ ] Syntax highlighting theme selector
- [ ] Code folding/unfolding
- [ ] Jump to definition/references
