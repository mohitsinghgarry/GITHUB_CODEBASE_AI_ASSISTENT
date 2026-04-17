# Stitch Design Implementation Plan

## ✅ Downloaded Screens

All 9 HTML screens have been successfully downloaded from Stitch project **607025827578097506**:

1. ✅ **Dashboard** (21KB) - Main overview with stats and activity feed
2. ✅ **Landing Page** (22KB) - Marketing/welcome page
3. ✅ **Repository Load** (11KB) - Repository selection/loading interface
4. ✅ **Chat with Repo** (20KB) - AI chat interface
5. ✅ **Smart Search** (20KB) - Advanced search functionality
6. ✅ **File Explorer** (20KB) - File browsing interface
7. ✅ **Code Review** (21KB) - Code review interface
8. ✅ **Code Refactor** (20KB) - Refactoring tools
9. ✅ **Settings** (19KB) - Application settings

## 🎨 Design System Analysis

### Color Palette (Dark Mode - "Obsidian Intelligence")
The design uses a sophisticated dark theme with the following key colors:

**Surfaces:**
- `background`: #0e0e10 (Deep charcoal base)
- `surface-container-lowest`: #000000 (True black for recessed elements)
- `surface-container-low`: #131315 (Sidebar/secondary panels)
- `surface-container`: #19191c (Interactive cards)
- `surface-container-high`: #1f1f22 (Elevated elements)
- `surface-container-highest`: #262528 (Modals/floating)
- `surface-bright`: #2c2c2f (Buttons that "pop")

**Primary Colors (Indigo/Violet):**
- `primary`: #a3a6ff (Electric indigo)
- `primary-dim`: #6063ee
- `primary-container`: #9396ff
- `secondary`: #ac8aff (Violet)
- `secondary-dim`: #8455ef

**Accent Colors:**
- `tertiary`: #9bffce (Emerald green for success)
- `tertiary-container`: #69f6b8
- `error`: #ff6e84 (Rose for errors)

**Text Colors:**
- `on-surface`: #f9f5f8 (Primary text - NOT pure white)
- `on-surface-variant`: #adaaad (Secondary text)
- `outline`: #767577 (Tertiary/metadata)

### Typography
- **Primary Font**: Inter (400, 500, 600, 700, 800)
- **Monospace Font**: JetBrains Mono (400, 700)
- **Icons**: Material Symbols Outlined

### Border Radius
- `DEFAULT`: 0.125rem (2px)
- `lg`: 0.25rem (4px)
- `xl`: 0.5rem (8px)
- `full`: 0.75rem (12px)

### Key Design Principles

1. **No-Line Rule**: Borders are prohibited for sectioning. Use background color shifts instead.
2. **Glassmorphism**: Navigation bars use `backdrop-filter: blur(12px)` with 70% opacity
3. **Gradient Pulse**: Primary CTAs use `linear-gradient(135deg, #a3a6ff 0%, #ac8aff 100%)`
4. **Quart Easing**: All transitions use `cubic-bezier(0.16, 1, 0.3, 1)`
5. **4px Grid System**: All spacing must be multiples of 4px
6. **Extreme Whitespace**: 64px+ between major sections

## 📁 Current Frontend Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx (Landing/Home)
│   │   ├── load/page.tsx (Repository Load)
│   │   ├── dashboard/page.tsx (needs creation)
│   │   ├── chat/page.tsx (needs creation)
│   │   ├── search/page.tsx (needs creation)
│   │   ├── files/page.tsx (needs creation)
│   │   ├── review/page.tsx (needs creation)
│   │   ├── refactor/page.tsx (needs creation)
│   │   └── settings/page.tsx (needs creation)
│   ├── components/
│   │   └── layout/
│   │       ├── AppShell.tsx (Main layout wrapper)
│   │       └── Header.tsx (Top navigation)
│   └── styles/
│       └── globals.css
```

## 🎯 Implementation Strategy

### Phase 1: Design System Setup ✅ (Already exists)
- [x] Tailwind config with Stitch colors
- [x] Custom CSS utilities
- [x] Font imports (Inter, JetBrains Mono)
- [x] Material Icons setup

### Phase 2: Core Layout Components (Priority 1)
1. **Sidebar Navigation** (`components/layout/Sidebar.tsx`)
   - Fixed left sidebar (w-64)
   - Logo + branding
   - Navigation items with active states
   - Bottom actions (Select Repository, Health Status)
   
2. **Top Navigation Bar** (`components/layout/TopNav.tsx`)
   - Breadcrumb navigation
   - Global search
   - Notifications
   - User profile

3. **Main Layout Shell** (`components/layout/MainLayout.tsx`)
   - Combines Sidebar + TopNav + Content area
   - Handles responsive behavior

### Phase 3: Page Implementations (Priority 2)

#### 3.1 Dashboard (`app/dashboard/page.tsx`)
Components needed:
- Repository identity bar
- Stats cards (4-column grid)
- Quick actions panel
- Language breakdown chart
- Recent activity table

#### 3.2 Repository Load (`app/load/page.tsx`)
- Already exists, needs Stitch styling update
- Repository URL input
- Loading states
- Success/error feedback

#### 3.3 Chat Interface (`app/chat/page.tsx`)
Components needed:
- Message list with AI/user bubbles
- Code block rendering
- Input area with send button
- Context panel (files referenced)

#### 3.4 Smart Search (`app/search/page.tsx`)
Components needed:
- Search input with filters
- Results list
- File preview panel
- Syntax highlighting

#### 3.5 File Explorer (`app/files/page.tsx`)
Components needed:
- Tree view navigation
- File content viewer
- Breadcrumb path
- File actions toolbar

#### 3.6 Code Review (`app/review/page.tsx`)
Components needed:
- Diff viewer
- Comment threads
- Suggestion cards
- Approval actions

#### 3.7 Code Refactor (`app/refactor/page.tsx`)
Components needed:
- Before/after code comparison
- Refactoring suggestions
- Apply changes button
- Rollback functionality

#### 3.8 Settings (`app/settings/page.tsx`)
Components needed:
- Settings sections
- Form inputs
- Toggle switches
- Save/reset actions

### Phase 4: Reusable Components (Priority 3)
- `Button` (primary, secondary, tertiary variants)
- `Card` (with proper surface elevation)
- `Input` (with ghost border on focus)
- `Badge` (status indicators)
- `Table` (with hover states)
- `CodeBlock` (syntax highlighted)
- `ProgressBar` (for language breakdown)
- `Avatar` (user profile)
- `IconButton` (for actions)

## 🚀 Next Steps

1. **Extract Components**: Parse each HTML file and extract reusable components
2. **Create Component Library**: Build React/Next.js versions of each component
3. **Implement Pages**: Build each page using the component library
4. **Add Interactivity**: Wire up state management and API calls
5. **Test Responsiveness**: Ensure mobile/tablet compatibility
6. **Performance Optimization**: Code splitting, lazy loading

## 📝 Notes

- All designs use Tailwind CSS with custom config
- Material Symbols Outlined icons are used throughout
- Glassmorphism effects require backdrop-filter support
- Custom scrollbar styling is applied globally
- All animations use the custom quart easing function
