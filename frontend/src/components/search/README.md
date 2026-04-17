# Search Components

This directory contains all search-related UI components for the RepoMind Assistant application.

## Components

### SearchBar

A search input component with autocomplete suggestions from search history.

**Features:**
- Auto-expanding input field
- Search history autocomplete dropdown
- Keyboard shortcuts (Enter to search, Escape to clear)
- Clear button
- Loading state indicator
- Recent searches with result counts

**Usage:**
```tsx
import { SearchBar } from '@/components/search';

<SearchBar
  value={query}
  onChange={setQuery}
  onSearch={handleSearch}
  searchHistory={searchHistory}
  isSearching={isSearching}
  placeholder="Search code..."
/>
```

**Props:**
- `value`: Current search query
- `onChange`: Callback when query changes
- `onSearch`: Callback when user submits search
- `searchHistory`: Array of previous searches for autocomplete
- `isSearching`: Loading state
- `placeholder`: Placeholder text
- `disabled`: Whether input is disabled

---

### SearchModeToggle

A three-way toggle for switching between search modes: Semantic, Keyword, and Hybrid.

**Features:**
- Smooth sliding animation between modes
- Icon indicators for each mode
- Optional mode descriptions
- Keyboard navigation support
- Disabled state

**Usage:**
```tsx
import { SearchModeToggle } from '@/components/search';

<SearchModeToggle
  value={searchMode}
  onChange={setSearchMode}
  showDescriptions={true}
/>
```

**Props:**
- `value`: Current search mode ('semantic' | 'keyword' | 'hybrid')
- `onChange`: Callback when mode changes
- `disabled`: Whether toggle is disabled
- `showDescriptions`: Show mode descriptions below toggle

**Search Modes:**
- **Semantic**: AI-powered meaning-based search using embeddings
- **Keyword**: Exact text matching with BM25 algorithm
- **Hybrid**: Combines both semantic and keyword search with score fusion

---

### SearchResultCard

A card component displaying a single search result with file info and code preview.

**Features:**
- File metadata (path, language, line numbers)
- Syntax-highlighted code preview
- Relevance score indicator
- Expandable code preview
- Highlighted matched terms
- Copy code button
- View in context button

**Usage:**
```tsx
import { SearchResultCard } from '@/components/search';

<SearchResultCard
  result={searchResult}
  onViewInContext={() => navigateToFile(result.chunk.filePath)}
  showScore={true}
  maxPreviewLines={10}
/>
```

**Props:**
- `result`: Search result object containing chunk, score, and highlights
- `onViewInContext`: Callback to view file in context
- `showScore`: Show relevance score (default: true)
- `maxPreviewLines`: Maximum lines to show before truncation (default: 10)

**Result Structure:**
```typescript
interface SearchResult {
  chunk: CodeChunk;
  score: number;
  highlights?: string[];
}
```

---

### SearchFilters

A collapsible filter panel for refining search results.

**Features:**
- Multi-select language filter
- Multi-select file extension filter
- Directory path text filter
- Collapsible sections with animations
- Active filter count badge
- Clear all filters button
- Disabled state

**Usage:**
```tsx
import { SearchFilters } from '@/components/search';

<SearchFilters
  filters={filters}
  onChange={setFilters}
  availableLanguages={['Python', 'JavaScript', 'TypeScript']}
  availableExtensions={['.py', '.js', '.ts']}
/>
```

**Props:**
- `filters`: Current filter values
- `onChange`: Callback when filters change
- `availableLanguages`: List of available languages (default: common languages)
- `availableExtensions`: List of available extensions (default: common extensions)
- `disabled`: Whether filters are disabled

**Filter Structure:**
```typescript
interface SearchFilters {
  fileExtension?: string[];
  directoryPath?: string;
  language?: string[];
}
```

---

## Design System Integration

All search components follow the **Obsidian Intelligence** design framework:

### Color System
- **Background**: `surface-container` and `surface-container-low` for layering
- **Borders**: Ghost borders using `outline-variant` at 15% opacity
- **Text**: `text-primary`, `text-secondary`, `text-tertiary` hierarchy
- **Accents**: `primary` for active states and highlights

### Typography
- **Titles**: `text-title-sm` and `text-title-md` for headers
- **Body**: `text-body-md` and `text-body-sm` for content
- **Labels**: `text-label-sm` and `text-label-md` for metadata
- **Code**: `font-mono` for file paths and code snippets

### Animations
All components use Framer Motion with predefined animation presets:
- `staggerItem`: For list items appearing in sequence
- `fadeInDown`: For dropdown menus
- `hoverScale`: For interactive cards
- `expand`: For collapsible sections

### Spacing
- **4px Grid**: All spacing follows multiples of 4px
- **Minimum Separation**: 24px (spacing-6) between items
- **Card Padding**: 20px (p-5) for standard cards

---

## Integration with Search Store

The search components integrate with the Zustand search store:

```tsx
import { useSearchStore } from '@/store/searchStore';

function SearchPage() {
  const {
    query,
    mode,
    results,
    filters,
    searchHistory,
    isSearching,
    setQuery,
    setMode,
    setFilters,
  } = useSearchStore();

  return (
    <div>
      <SearchBar
        value={query}
        onChange={setQuery}
        onSearch={handleSearch}
        searchHistory={searchHistory}
        isSearching={isSearching}
      />
      
      <SearchModeToggle
        value={mode}
        onChange={setMode}
      />
      
      <div className="flex gap-6">
        <SearchFilters
          filters={filters}
          onChange={setFilters}
        />
        
        <div className="flex-1 space-y-4">
          {results.map((result) => (
            <SearchResultCard
              key={result.chunk.id}
              result={result}
              onViewInContext={() => navigateToFile(result.chunk)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Accessibility

All components follow WCAG 2.1 Level AA guidelines:

- **Keyboard Navigation**: Full keyboard support with visible focus states
- **ARIA Labels**: Proper labeling for screen readers
- **Color Contrast**: Minimum 4.5:1 contrast ratio for text
- **Focus Management**: Logical tab order and focus trapping where appropriate
- **Semantic HTML**: Proper use of semantic elements

---

## Performance Considerations

- **Virtualization**: For large result sets, consider using `react-window` or `react-virtual`
- **Debouncing**: Search input should be debounced (300ms recommended)
- **Lazy Loading**: Code previews can be lazy-loaded for better initial render
- **Memoization**: Use `React.memo` for result cards to prevent unnecessary re-renders

---

## Testing

Each component should have:
- Unit tests for logic and interactions
- Integration tests with the search store
- Accessibility tests with `@testing-library/react`
- Visual regression tests with Storybook

---

## Future Enhancements

Potential improvements for search components:

1. **Advanced Filters**
   - Date range filter (last modified)
   - File size filter
   - Author filter (for git blame integration)

2. **Search Suggestions**
   - Auto-complete based on indexed code
   - Suggested queries based on repository content
   - Popular searches across users

3. **Result Enhancements**
   - Syntax highlighting with Prism or Shiki
   - Inline file preview on hover
   - Jump to definition links
   - Related results section

4. **Export Options**
   - Export results to JSON/CSV
   - Share search results via URL
   - Save search queries as bookmarks

5. **Performance**
   - Virtual scrolling for large result sets
   - Progressive loading of results
   - Search result caching

---

## Related Components

- **ChatInput**: Similar input pattern for chat interface
- **FileTree**: For navigating to search results in file explorer
- **CodeViewer**: For viewing full file context
- **StatusBadge**: Used in result cards for status indicators

---

## Resources

- [Design System Documentation](../../DESIGN_SYSTEM.md)
- [Animation Presets](../../lib/animation-presets.ts)
- [Design Tokens](../../lib/design-tokens.ts)
- [Search Store](../../store/searchStore.ts)
- [API Types](../../types/index.ts)
