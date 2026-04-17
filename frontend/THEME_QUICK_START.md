# Theme Support - Quick Start Guide

## Testing the Implementation

### 1. Start the Development Server
```bash
cd frontend
npm run dev
```

### 2. Navigate to Test Page
Open your browser and go to: `http://localhost:3000/theme-test`

### 3. Test Theme Toggle
- Click the theme toggle button (sun/moon/monitor icon) in the top-right
- Theme should cycle: Light → Dark → System
- All colors should transition smoothly (250ms)
- Preference should persist after page reload

### 4. Visual Verification Checklist
On the test page, verify:
- [ ] Typography is readable in both themes
- [ ] Color palette displays correctly
- [ ] Buttons have proper contrast
- [ ] Form inputs are readable
- [ ] Cards have appropriate backgrounds
- [ ] Badges are visible
- [ ] Code blocks have correct background
- [ ] Surface hierarchy is distinguishable
- [ ] No flash of unstyled content (FOUC)
- [ ] Smooth transitions between themes

## Using Theme in Your Components

### Method 1: Tailwind Dark Variant (Recommended)
```tsx
<div className="bg-white dark:bg-surface-container">
  <p className="text-gray-900 dark:text-on-surface">
    This text adapts to theme
  </p>
</div>
```

### Method 2: CSS Variables (Automatic)
```tsx
<div className="bg-background text-foreground">
  <p className="text-muted-foreground">
    Uses CSS variables that change with theme
  </p>
</div>
```

### Method 3: Programmatic Access
```tsx
import { useSettingsStore } from '@/store/settingsStore';

function MyComponent() {
  const { theme, setTheme, toggleTheme } = useSettingsStore();
  
  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={() => setTheme('light')}>Light</button>
      <button onClick={() => setTheme('dark')}>Dark</button>
      <button onClick={() => setTheme('system')}>System</button>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
}
```

## Design System Colors

### Dark Mode (Default)
- Background: `#0e0e10` (Deep charcoal)
- Primary: `#a3a6ff` (Electric Indigo)
- Secondary: `#ac8aff` (Violet)
- Tertiary: `#9bffce` (Emerald)
- Text: `#f9f5f8` (Soft white)

### Light Mode
- Background: `#f9f5f8` (Soft white)
- Primary: `#494bd7` (Deeper indigo)
- Secondary: `#5516be` (Deeper violet)
- Tertiary: `#00a86b` (Deeper emerald)
- Text: `#0e0e10` (Deep charcoal)

## Common Patterns

### Card with Theme Support
```tsx
<div className="bg-surface-container dark:bg-surface-container rounded-lg p-6 border border-outline-variant/15">
  <h3 className="text-on-surface dark:text-on-surface">Card Title</h3>
  <p className="text-on-surface-variant dark:text-on-surface-variant">
    Card content
  </p>
</div>
```

### Button with Theme Support
```tsx
<button className="bg-primary hover:bg-primary-dim text-on-primary dark:bg-primary dark:hover:bg-primary-dim dark:text-on-primary">
  Click Me
</button>
```

### Input with Theme Support
```tsx
<input 
  className="bg-surface-container-low dark:bg-surface-container-low text-on-surface dark:text-on-surface border border-outline-variant dark:border-outline-variant"
  placeholder="Enter text..."
/>
```

## Troubleshooting

### Theme doesn't persist
- Check that zustand persist middleware is working
- Clear localStorage and try again: `localStorage.clear()`

### Colors look wrong
- Verify you're using the correct Tailwind classes
- Check that globals.css has both `:root` and `.dark` CSS variables
- Ensure ThemeProvider is wrapping your app in layout.tsx

### Transitions are janky
- Check that `.theme-transitioning` class is being applied
- Verify transition duration is 250ms
- Ensure Quart easing is used: `cubic-bezier(0.16, 1, 0.3, 1)`

### FOUC (Flash of Unstyled Content)
- Verify `suppressHydrationWarning` is on `<html>` element
- Check that ThemeProvider has mounted state check
- Ensure theme is applied before first render

## Files to Reference

- **ThemeProvider**: `src/components/providers/ThemeProvider.tsx`
- **ThemeToggle**: `src/components/common/ThemeToggle.tsx`
- **Global Styles**: `src/app/globals.css`
- **Tailwind Config**: `tailwind.config.ts`
- **Settings Store**: `src/store/settingsStore.ts`
- **Test Page**: `src/app/theme-test/page.tsx`

## Next Steps

1. Test theme toggle on all pages
2. Verify all existing components work in light mode
3. Add light mode variants to any custom components
4. Test with real users for accessibility
5. Consider adding theme preview feature
6. Add theme customization options (accent colors, etc.)
