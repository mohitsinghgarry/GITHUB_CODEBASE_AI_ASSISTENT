# Responsive Design Testing Checklist

## Testing Methodology

### Browser DevTools Testing
1. Open Chrome/Firefox DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
3. Test at specific breakpoints
4. Test orientation changes (portrait/landscape)
5. Test touch interactions

### Breakpoints to Test
- **320px** - iPhone SE (smallest mobile)
- **375px** - iPhone 12/13 Pro
- **414px** - iPhone 12/13 Pro Max
- **768px** - iPad Mini (tablet start)
- **1024px** - iPad Pro (desktop start)
- **1280px** - Desktop
- **1920px** - Large desktop

## Mobile Testing (320px - 768px)

### Layout
- [ ] No horizontal scrolling
- [ ] Content fits within viewport
- [ ] Sidebar opens as overlay
- [ ] Sidebar closes when clicking backdrop
- [ ] Header is compact with hamburger menu
- [ ] Footer (if present) is accessible

### Touch Targets
- [ ] All buttons are ≥ 44x44px
- [ ] All icon buttons are ≥ 44x44px
- [ ] All form inputs are ≥ 44px height
- [ ] All links in navigation are ≥ 44px height
- [ ] Adequate spacing between interactive elements (≥8px)

### Typography
- [ ] Text is readable (not too small)
- [ ] Headings scale appropriately
- [ ] Line length is comfortable (45-75 characters)
- [ ] Line height provides good readability

### Navigation
- [ ] Hamburger menu is visible and functional
- [ ] Sidebar slides in from left
- [ ] Navigation items are easily tappable
- [ ] Active state is clearly visible
- [ ] Breadcrumbs are truncated appropriately

### Forms
- [ ] Input fields are full width or appropriately sized
- [ ] Labels are visible and associated with inputs
- [ ] Error messages are visible
- [ ] Submit buttons are prominent and tappable
- [ ] Form validation works correctly

### Images & Media
- [ ] Images scale to fit container
- [ ] Images maintain aspect ratio
- [ ] No image overflow
- [ ] Lazy loading works correctly

### Code Blocks
- [ ] Code blocks have horizontal scroll
- [ ] Font size is readable
- [ ] Syntax highlighting is visible
- [ ] Copy button is accessible

### Cards & Lists
- [ ] Cards stack vertically (1 column)
- [ ] Card content is readable
- [ ] List items have adequate spacing
- [ ] Hover states work (if applicable)

### Modals & Overlays
- [ ] Modals fit within viewport
- [ ] Modal content is scrollable if needed
- [ ] Close button is accessible
- [ ] Backdrop dismisses modal

### Performance
- [ ] Page loads quickly
- [ ] Animations are smooth (60fps)
- [ ] No layout shift during load
- [ ] Images load progressively

## Tablet Testing (768px - 1024px)

### Layout
- [ ] Layout uses available space efficiently
- [ ] Sidebar behavior is appropriate (overlay or persistent)
- [ ] Multi-column layouts work (2 columns)
- [ ] Content doesn't stretch too wide

### Touch Targets
- [ ] All interactive elements remain ≥ 44x44px
- [ ] Spacing is comfortable for touch

### Typography
- [ ] Text size is appropriate for viewing distance
- [ ] Headings are prominent

### Navigation
- [ ] Navigation is easily accessible
- [ ] Breadcrumbs are fully visible
- [ ] Search is accessible

### Grid Layouts
- [ ] 2-column grids display correctly
- [ ] Gap spacing is appropriate
- [ ] Cards are well-proportioned

### Forms
- [ ] Forms use available width appropriately
- [ ] Multi-column forms work (if applicable)

### Tables
- [ ] Tables are readable
- [ ] Horizontal scroll if needed
- [ ] Column widths are appropriate

## Desktop Testing (1024px+)

### Layout
- [ ] Sidebar is persistent
- [ ] Full navigation is visible
- [ ] Multi-column layouts utilized (3-4 columns)
- [ ] Content has max-width constraint
- [ ] Whitespace is used effectively

### Navigation
- [ ] Full breadcrumbs visible
- [ ] All navigation items visible
- [ ] Search bar is prominent
- [ ] Hover states work correctly

### Interactions
- [ ] Hover states are visible
- [ ] Keyboard navigation works
- [ ] Focus states are clear
- [ ] Tooltips appear on hover

### Grid Layouts
- [ ] 3-4 column grids display correctly
- [ ] Cards are well-proportioned
- [ ] Gap spacing is appropriate

### Forms
- [ ] Forms are well-spaced
- [ ] Multi-column layouts work
- [ ] Inline validation works

### Tables
- [ ] Tables display fully
- [ ] Sorting works correctly
- [ ] Filtering works correctly

### Code Blocks
- [ ] Code blocks display at full width
- [ ] Line numbers are visible
- [ ] Syntax highlighting is clear

## Cross-Browser Testing

### Chrome
- [ ] Layout renders correctly
- [ ] Animations work smoothly
- [ ] Forms function correctly

### Firefox
- [ ] Layout renders correctly
- [ ] Animations work smoothly
- [ ] Forms function correctly

### Safari (macOS/iOS)
- [ ] Layout renders correctly
- [ ] Animations work smoothly
- [ ] Forms function correctly
- [ ] Touch interactions work

### Edge
- [ ] Layout renders correctly
- [ ] Animations work smoothly
- [ ] Forms function correctly

## Accessibility Testing

### Keyboard Navigation
- [ ] Tab order is logical
- [ ] All interactive elements are reachable
- [ ] Focus indicators are visible
- [ ] Escape key closes modals
- [ ] Enter/Space activates buttons

### Screen Reader
- [ ] Headings are properly structured
- [ ] ARIA labels are present
- [ ] Alt text for images
- [ ] Form labels are associated
- [ ] Error messages are announced

### Color Contrast
- [ ] Text meets WCAG AA (4.5:1)
- [ ] Large text meets WCAG AA (3:1)
- [ ] Interactive elements are distinguishable
- [ ] Focus indicators are visible

### Dark Mode
- [ ] All components work in dark mode
- [ ] Contrast is maintained
- [ ] Images/icons are visible
- [ ] Transitions are smooth

## Performance Testing

### Mobile Performance
- [ ] First Contentful Paint < 1.8s
- [ ] Time to Interactive < 3.8s
- [ ] Cumulative Layout Shift < 0.1
- [ ] Largest Contentful Paint < 2.5s

### Network Conditions
- [ ] Works on 3G connection
- [ ] Works on 4G connection
- [ ] Works offline (if applicable)
- [ ] Progressive enhancement works

## Component-Specific Testing

### AppShell
- [ ] Sidebar toggles correctly on mobile
- [ ] Sidebar is persistent on desktop
- [ ] Overlay appears on mobile/tablet
- [ ] Content area adjusts to sidebar state

### Header
- [ ] Hamburger menu visible on mobile/tablet
- [ ] Breadcrumbs truncate on mobile
- [ ] All actions are accessible
- [ ] Search button works on all sizes

### Sidebar
- [ ] Width adjusts responsively
- [ ] Navigation items are tappable
- [ ] Repository selector works
- [ ] Scrolling works with many items

### Chat Interface
- [ ] Message list scrolls correctly
- [ ] Input area is accessible
- [ ] Code snippets are readable
- [ ] Citations are tappable

### Search Results
- [ ] Grid adjusts to screen size
- [ ] Cards are readable
- [ ] Filters are accessible
- [ ] Pagination works

### File Tree
- [ ] Tree structure is clear
- [ ] Expand/collapse works
- [ ] File names are readable
- [ ] Icons are visible

### Code Viewer
- [ ] Code is readable
- [ ] Horizontal scroll works
- [ ] Line numbers are visible
- [ ] Copy button is accessible

### Forms
- [ ] All inputs are accessible
- [ ] Validation messages are visible
- [ ] Submit button is prominent
- [ ] Error states are clear

## Testing Tools

### Browser DevTools
- Chrome DevTools Device Mode
- Firefox Responsive Design Mode
- Safari Web Inspector

### Online Tools
- BrowserStack (real device testing)
- LambdaTest (cross-browser testing)
- Responsively App (multi-device preview)

### Accessibility Tools
- axe DevTools
- WAVE Browser Extension
- Lighthouse (Chrome DevTools)

### Performance Tools
- Lighthouse (Chrome DevTools)
- WebPageTest
- PageSpeed Insights

## Common Issues to Watch For

### Mobile
- Text too small to read
- Buttons too small to tap
- Horizontal scrolling
- Content overflow
- Slow loading
- Unresponsive interactions

### Tablet
- Inefficient use of space
- Touch targets too small
- Layout breaks between breakpoints
- Navigation issues

### Desktop
- Content stretches too wide
- Hover states not working
- Keyboard navigation issues
- Focus states not visible

## Sign-Off Checklist

- [ ] All mobile breakpoints tested (320px, 375px, 414px, 768px)
- [ ] All tablet breakpoints tested (768px, 1024px)
- [ ] All desktop breakpoints tested (1024px, 1280px, 1920px)
- [ ] Touch targets verified (≥ 44x44px on mobile)
- [ ] Typography scales appropriately
- [ ] Spacing adjusts per breakpoint
- [ ] All layouts tested
- [ ] All components tested
- [ ] Cross-browser testing complete
- [ ] Accessibility testing complete
- [ ] Performance testing complete
- [ ] Dark mode tested
- [ ] Light mode tested

## Notes

### Issues Found
_Document any issues discovered during testing_

### Resolutions
_Document how issues were resolved_

### Future Improvements
_Document potential improvements for future iterations_
