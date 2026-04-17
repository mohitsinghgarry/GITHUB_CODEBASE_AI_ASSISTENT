# Search Page

## Overview

The Search Page provides a comprehensive interface for querying repository code using semantic, keyword, or hybrid search modes. It includes advanced filtering, result export, and navigation capabilities.

## Features

### 1. Search Modes

Three search modes are available via a tabbed interface:

- **Semantic Search**: AI-powered meaning-based search using vector embeddings
- **Keyword Search**: Exact text matching with BM25 ranking
- **Hybrid Search**: Combines both semantic and keyword search with score fusion

Users can switch between modes seamlessly, and the search automatically re-executes with the new mode.

### 2. Search Bar

- Auto-expanding input field
- Search history with autocomplete suggestions
- Keyboard shortcuts:
  - `Enter` to search
  - `Esc` to clear
- Loading state indicator
- Clear button

### 3. Search Filters

Collapsible filter panel with:

- **Languages**: Multi-select language filter (Python, JavaScript, TypeScript, etc.)
- **File Extensions**: Multi-select extension filter (.py, .js, .ts, etc.)
- **Directory Path**: Text input for filtering by directory path

Active filter count badge shows the number of applied filters.

### 4. Search Results

Each result card displays:

- File metadata (path, language, line numbers)
- Syntax-highlighted code preview
- Relevance score (as percentage)
- Matched terms (for keyword search)
- Actions:
  - Copy code button
  - "View in context" button (navigates to file viewer)

Results support:
- Expandable code previews (show more/less)
- Pagination (10 results per page)
- Smooth animations

### 5. Export Functionality

Export search results in two formats:

- **JSON**: Structured data with full metadata
  - Query, mode, filters, timestamp
  - All results with scores, file paths, content, highlights
  
- **CSV**: Tabular format for spreadsheet analysis
  - Columns: Score, File Path, Start Line, End Line, Language, Content
  - Properly escaped content for CSV compatibility

### 6. Search History

- Stores recent searches with query, mode, filters, and result count
- Autocomplete suggestions based on search history
- Persisted in Zustand store (localStorage)
- Maximum 20 items

### 7. Empty States

- **No Query**: Prompts user to enter a search query
- **No Results**: Suggests adjusting query or filters
- **Error State**: Displays error banner with dismiss option

## Usage

### Basic Search

1. Enter a search query in the search bar
2. Press `Enter` or click "Search"
3. View results with relevance scores

### Advanced Search

1. Click "Filters" to open the filter panel
2. Select languages, file extensions, or directory path
3. Search automatically updates with filters applied

### Mode Switching

1. Click on a different search mode (Semantic, Keyword, Hybrid)
2. Search automatically re-executes with the new mode
3. Results update with new relevance scores

### Export Results

1. Perform a search to get results
2. Click "JSON" or "CSV" in the top-right corner
3. File downloads automatically with timestamp

### View in Context

1. Click "View" button on any result card
2. Navigates to file viewer with the specific line highlighted
3. Shows full file context around the matched code

## State Management

Uses Zustand store (`useSearchStore`) for:

- Query and search mode
- Results and pagination
- Filters (language, extension, directory)
- Search history
- Loading and error states

State is partially persisted to localStorage:
- Mode, filters, topK, search history, page size
- Query and results are session-only

## API Integration

Calls backend search endpoints via `apiClient`:

```typescript
// Semantic search
apiClient.search.semantic(searchRequest)

// Keyword search
apiClient.search.keyword(searchRequest)

// Hybrid search
apiClient.search.hybrid(searchRequest)
```

Search request includes:
- `query`: Search query string
- `repositoryIds`: Array of repository IDs to search
- `topK`: Maximum number of results (default: 10)
- `filters`: Optional filters (language, extension, directory)

## Design System

Follows the RepoMind Assistant design system:

- **Colors**: Surface hierarchy with tonal layering
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: 4px grid system
- **Animations**: Framer Motion with Quart easing
- **Components**: shadcn/ui base components

### Key Design Elements

- No 1px borders (uses background color shifts)
- Glassmorphism for elevated surfaces
- Extreme whitespace (64px+ between sections)
- Signature gradient for high-intent CTAs
- Ghost borders for accessibility

## Accessibility

- Keyboard navigation support
- Focus states on all interactive elements
- ARIA labels for screen readers
- Semantic HTML structure
- Color contrast meets WCAG AA standards

## Performance

- Debounced search input (prevents excessive API calls)
- Pagination (10 results per page)
- Lazy loading of code previews
- Optimized re-renders with React.memo and useCallback
- Efficient state updates with Zustand

## Error Handling

- Network errors: Retry with exponential backoff (API client)
- Validation errors: Display error banner with message
- Empty results: Show helpful empty state
- Export errors: Log to console and show error banner

## Future Enhancements

- [ ] Saved searches (bookmark queries with filters)
- [ ] Search suggestions (autocomplete from indexed code)
- [ ] Advanced query syntax (boolean operators, regex)
- [ ] Result highlighting (highlight matched terms in code)
- [ ] Search analytics (track popular queries)
- [ ] Bulk actions (export multiple results, compare results)
- [ ] Search within results (filter existing results)
- [ ] Custom result sorting (by score, file path, date)

## Related Components

- `SearchBar` - Search input with autocomplete
- `SearchModeToggle` - Mode switcher (Semantic/Keyword/Hybrid)
- `SearchResultCard` - Individual result display
- `SearchFilters` - Filter panel with language/extension/directory
- `useSearchStore` - Zustand store for search state
- `apiClient.search` - API client for search endpoints

## Requirements Satisfied

- **11.5**: Separate interfaces for semantic search and keyword search
- **11.6**: Display search results with relevance scores and navigation to source files

## Testing

### Manual Testing Checklist

- [ ] Search with semantic mode
- [ ] Search with keyword mode
- [ ] Search with hybrid mode
- [ ] Apply language filter
- [ ] Apply file extension filter
- [ ] Apply directory path filter
- [ ] Export results as JSON
- [ ] Export results as CSV
- [ ] View result in context
- [ ] Navigate between pages
- [ ] Use search history autocomplete
- [ ] Clear search query
- [ ] Handle empty results
- [ ] Handle network errors
- [ ] Test keyboard shortcuts (Enter, Esc)
- [ ] Test responsive design (mobile, tablet, desktop)

### Unit Tests (TODO)

- Search query validation
- Filter application logic
- Export format generation
- Pagination calculations
- Search history management

### Integration Tests (TODO)

- API search endpoint calls
- Navigation to file viewer
- State persistence (localStorage)
- Error handling flows
