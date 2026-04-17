# Layout Components

This directory contains the core layout components for the RepoMind Assistant application.

## Components

### AppShell

The main layout wrapper that provides the overall structure for the application.

**Features:**
- Responsive layout with sidebar and header
- Mobile-friendly with collapsible sidebar
- Command palette integration (⌘K)
- Smooth animations with framer-motion

**Usage:**
```tsx
import { AppShell } from '@/components/layout';

export default function RootLayout({ children }) {
  return (
    <AppShell>
      {children}
    </AppShell>
  );
}
```

### Sidebar

Navigation sidebar with repository selector and main navigation links.

**Features:**
- Persistent on desktop, overlay on mobile
- Active route highlighting with smooth animation
- Repository selector with quick add button
- Badge support for navigation items
- Glassmorphism effect with backdrop blur

**Navigation Items:**
- Home
- Repositories (with count badge)
- Search
- Chat
- Code Review
- Settings

### Header

Top navigation bar with breadcrumbs and utility actions.

**Features:**
- Dynamic breadcrumb navigation based on current route
- Search trigger (opens command palette)
- Notifications with badge indicator
- Theme toggle (dark/light mode)
- User menu
- Mobile menu toggle

**Responsive Behavior:**
- Desktop: Full breadcrumbs + all actions
- Mobile: Hamburger menu + essential actions only

### CommandPalette

Quick action palette triggered by ⌘K (or Ctrl+K on Windows/Linux).

**Features:**
- Fuzzy search across all commands
- Keyboard navigation (↑↓ to navigate, Enter to select, Esc to close)
- Grouped commands by category (Navigation, Actions, Recent)
- Visual feedback for selected command
- Glassmorphism modal with backdrop blur

**Command Categories:**
- **Navigation**: Quick navigation to main pages
- **Actions**: Quick actions like adding repositories
- **Recent**: Recently accessed items (future enhancement)

**Keyboard Shortcuts:**
- `⌘K` / `Ctrl+K`: Open command palette
- `↑` / `↓`: Navigate commands
- `Enter`: Execute selected command
- `Esc`: Close palette

## Design System Integration

All layout components follow the RepoMind Assistant design system:

### Colors
- Background: Deep charcoal (`#0e0e10`)
- Surface containers: Layered obsidian sheets
- Primary accent: Electric indigo (`#a3a6ff`)
- Secondary accent: Violet (`#ac8aff`)

### Typography
- UI: Inter font family
- Code: JetBrains Mono font family
- Consistent sizing scale from design tokens

### Animations
- Easing: Quart easing for high-end snap feel
- Duration: Fast (150ms), Normal (250ms), Slow (350ms)
- Variants: fadeIn, slideInLeft, scaleInCenter, staggerContainer

### Spacing
- 4px grid system
- Generous whitespace for editorial feel
- Consistent padding and margins

## Responsive Breakpoints

- **Mobile**: < 768px
  - Sidebar: Overlay with backdrop
  - Header: Hamburger menu + essential actions
  - Command palette: Full screen

- **Tablet**: 768px - 1024px
  - Sidebar: Overlay with backdrop
  - Header: Full breadcrumbs + all actions
  - Command palette: Centered modal

- **Desktop**: > 1024px
  - Sidebar: Persistent
  - Header: Full breadcrumbs + all actions
  - Command palette: Centered modal

## State Management

Layout components integrate with Zustand stores:

- **repositoryStore**: Repository list and selection
- **settingsStore**: Theme preferences

## Accessibility

All layout components follow accessibility best practices:

- Semantic HTML elements
- ARIA labels for icon-only buttons
- Keyboard navigation support
- Focus management
- Screen reader friendly

## Future Enhancements

- [ ] User profile dropdown menu
- [ ] Notification panel
- [ ] Recent items in command palette
- [ ] Customizable sidebar width
- [ ] Pinned repositories in sidebar
- [ ] Keyboard shortcut customization
