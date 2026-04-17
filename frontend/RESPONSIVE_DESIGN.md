# Responsive Design Implementation

## Breakpoint Strategy

### Tailwind Breakpoints
- **Mobile**: `< 768px` (default, no prefix)
- **Tablet**: `768px - 1024px` (md: prefix)
- **Desktop**: `≥ 1024px` (lg: prefix)
- **Large Desktop**: `≥ 1280px` (xl: prefix)
- **Extra Large**: `≥ 1536px` (2xl: prefix)

### Custom Breakpoints
```typescript
screens: {
  'xs': '320px',   // Small mobile
  'sm': '640px',   // Large mobile
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
}
```

## Touch Target Requirements

### Minimum Sizes (Mobile)
- **Buttons**: 44x44px minimum
- **Interactive elements**: 44x44px minimum
- **Links in text**: 44px height minimum
- **Form inputs**: 44px height minimum

### Implementation
```tsx
// Button classes
className="h-11 min-h-[44px] px-4" // 44px height

// Icon button classes
className="h-11 w-11 min-h-[44px] min-w-[44px]" // 44x44px

// Input classes
className="h-11 min-h-[44px]" // 44px height
```

## Spacing Adjustments by Breakpoint

### Container Padding
- **Mobile**: `px-4` (16px)
- **Tablet**: `md:px-6` (24px)
- **Desktop**: `lg:px-8` (32px)

### Section Spacing
- **Mobile**: `py-6` (24px)
- **Tablet**: `md:py-8` (32px)
- **Desktop**: `lg:py-12` (48px)

### Card Spacing
- **Mobile**: `p-4` (16px)
- **Tablet**: `md:p-6` (24px)
- **Desktop**: `lg:p-8` (32px)

## Typography Adjustments

### Display Text
```tsx
// Mobile → Tablet → Desktop
className="text-display-sm md:text-display-md lg:text-display-lg"
```

### Headline Text
```tsx
className="text-headline-sm md:text-headline-md lg:text-headline-lg"
```

### Body Text
```tsx
// Generally stays consistent, but can adjust for readability
className="text-body-md lg:text-body-lg"
```

## Layout Patterns

### Sidebar
- **Mobile**: Overlay with backdrop (fixed, z-50)
- **Tablet**: Overlay with backdrop (fixed, z-50)
- **Desktop**: Persistent sidebar (relative, no overlay)

```tsx
// Sidebar container
className="fixed lg:relative z-50 lg:z-auto"

// Overlay (mobile/tablet only)
className="fixed inset-0 bg-black/50 lg:hidden"
```

### Header
- **Mobile**: Compact with hamburger menu
- **Tablet**: Compact with hamburger menu
- **Desktop**: Full breadcrumbs and actions

```tsx
// Menu button (mobile/tablet only)
className="lg:hidden"

// Search bar (desktop only)
className="hidden md:flex"
```

### Grid Layouts
```tsx
// 1 column → 2 columns → 3 columns → 4 columns
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
```

### Flex Layouts
```tsx
// Stack on mobile, row on desktop
className="flex flex-col lg:flex-row gap-4"
```

## Component-Specific Guidelines

### AppShell
- Mobile: Full-width content, overlay sidebar
- Tablet: Full-width content, overlay sidebar
- Desktop: Sidebar + content side-by-side

### Chat Interface
- Mobile: Full-screen chat, stacked input
- Tablet: Full-screen chat, inline input
- Desktop: Split view with sidebar

### Search Results
- Mobile: 1 column, compact cards
- Tablet: 2 columns, standard cards
- Desktop: 3 columns, expanded cards

### Code Viewer
- Mobile: Horizontal scroll, smaller font
- Tablet: Horizontal scroll, standard font
- Desktop: Full width, standard font

### File Tree
- Mobile: Compact spacing, smaller icons
- Tablet: Standard spacing, standard icons
- Desktop: Expanded spacing, larger icons

## Testing Checklist

### Mobile (320px - 768px)
- [ ] All touch targets ≥ 44x44px
- [ ] No horizontal overflow
- [ ] Text is readable (not too small)
- [ ] Buttons are easily tappable
- [ ] Forms are usable
- [ ] Navigation is accessible
- [ ] Modals fit on screen
- [ ] Images scale properly

### Tablet (768px - 1024px)
- [ ] Layout uses available space
- [ ] Touch targets remain ≥ 44x44px
- [ ] Multi-column layouts work
- [ ] Sidebar behavior is correct
- [ ] Forms are well-spaced
- [ ] Tables are readable

### Desktop (1024px+)
- [ ] Sidebar is persistent
- [ ] Full navigation visible
- [ ] Multi-column layouts utilized
- [ ] Hover states work
- [ ] Keyboard navigation works
- [ ] Content doesn't stretch too wide

## Common Responsive Patterns

### Hide/Show Elements
```tsx
// Hide on mobile, show on desktop
className="hidden lg:block"

// Show on mobile, hide on desktop
className="block lg:hidden"

// Show on mobile and tablet, hide on desktop
className="block lg:hidden"
```

### Responsive Sizing
```tsx
// Width
className="w-full lg:w-1/2"

// Height
className="h-auto lg:h-screen"

// Max width
className="max-w-full lg:max-w-4xl"
```

### Responsive Spacing
```tsx
// Padding
className="p-4 md:p-6 lg:p-8"

// Margin
className="m-4 md:m-6 lg:m-8"

// Gap
className="gap-4 md:gap-6 lg:gap-8"
```

### Responsive Text
```tsx
// Font size
className="text-sm md:text-base lg:text-lg"

// Text alignment
className="text-center lg:text-left"

// Line clamp
className="line-clamp-2 lg:line-clamp-none"
```

## Performance Considerations

### Image Optimization
- Use Next.js Image component
- Provide responsive sizes
- Use appropriate formats (WebP, AVIF)

### Lazy Loading
- Lazy load below-the-fold content
- Use Intersection Observer
- Defer non-critical resources

### Mobile-First CSS
- Write mobile styles first
- Add desktop styles with breakpoints
- Minimize CSS overrides

## Accessibility

### Focus States
- Visible focus indicators
- Keyboard navigation support
- Skip links for navigation

### Screen Readers
- Proper ARIA labels
- Semantic HTML
- Descriptive alt text

### Color Contrast
- WCAG AA compliance minimum
- Test in both light and dark modes
- Ensure text is readable

## Implementation Status

### Completed
- [x] Tailwind breakpoint configuration
- [x] Touch target size standards
- [x] Spacing system
- [x] Typography scale

### In Progress
- [ ] Component responsive updates
- [ ] Touch target verification
- [ ] Layout testing

### Pending
- [ ] Cross-browser testing
- [ ] Device testing
- [ ] Performance optimization
