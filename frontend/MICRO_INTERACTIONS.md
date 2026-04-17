# Micro-Interactions and Polish

This document describes the micro-interactions, animations, and polish features implemented in the RepoMind Assistant frontend.

## Overview

All micro-interactions follow the "Obsidian Intelligence" design philosophy with:
- **Quart easing** (`cubic-bezier(0.16, 1, 0.3, 1)`) for high-end, responsive "snap"
- **Fast transitions** (150ms) for immediate feedback
- **Subtle animations** that enhance without distracting
- **60fps performance** target for all animations

## Components

### 1. Toast Notifications

**Location**: `src/components/ui/toast.tsx`

**Features**:
- Success, error, warning, and info variants
- Auto-dismissal with configurable duration
- Manual dismiss button
- Smooth slide-in/fade-out animations
- Stacks multiple toasts vertically
- Accessible with ARIA live regions

**Usage**:
```tsx
import { useToast } from '@/hooks/useToast';

function MyComponent() {
  const { success, error, warning, info } = useToast();

  const handleSuccess = () => {
    success({
      title: 'Repository indexed',
      description: 'Your repository has been successfully indexed.',
      duration: 5000,
    });
  };

  const handleError = () => {
    error({
      title: 'Indexing failed',
      description: 'Failed to index repository. Please try again.',
    });
  };

  return (
    <button onClick={handleSuccess}>Show Success</button>
  );
}
```

**Integration**: Add `<ToastProvider />` to your root layout:
```tsx
// app/layout.tsx
import { ToastProvider } from '@/components/providers/ToastProvider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <ToastProvider />
      </body>
    </html>
  );
}
```

### 2. Enhanced Button Component

**Location**: `src/components/ui/button.tsx`

**Enhancements**:
- ✅ Hover states with subtle shadow glow
- ✅ Active/press scale effect (0.98x)
- ✅ Focus ring with offset for accessibility
- ✅ Smooth transitions (150ms)
- ✅ Disabled state with reduced opacity

**Variants**:
- `default`: Primary action with glow on hover
- `outline`: Ghost button with border
- `secondary`: Secondary action with violet glow
- `ghost`: Minimal button with background on hover
- `link`: Text link with underline
- `destructive`: Danger action with red glow

### 3. Enhanced Input Component

**Location**: `src/components/ui/input.tsx`

**Enhancements**:
- ✅ Hover state with border color change
- ✅ Focus ring with offset
- ✅ Smooth transitions (150ms)
- ✅ Accessible focus indicators

### 4. Page Transitions

**Location**: `src/components/common/PageTransition.tsx`

**Features**:
- Fade-in with subtle upward motion on page load
- Fade-out with downward motion on page exit
- 250ms duration with quart easing

**Usage**:
```tsx
import { PageTransition } from '@/components/common/PageTransition';

export default function MyPage() {
  return (
    <PageTransition>
      <div>Page content here</div>
    </PageTransition>
  );
}
```

### 5. Interactive Card Component

**Location**: `src/components/common/InteractiveCard.tsx`

**Features**:
- Hover lift effect (-4px translation)
- Press scale effect (0.98x)
- Focus ring for keyboard navigation
- Border color change on hover
- Configurable hover/press effects

**Usage**:
```tsx
import { InteractiveCard } from '@/components/common/InteractiveCard';

<InteractiveCard onClick={() => console.log('clicked')}>
  <div className="p-6">
    <h3>Card Title</h3>
    <p>Card content</p>
  </div>
</InteractiveCard>
```

### 6. Loading Skeletons

**Location**: `src/components/common/LoadingSkeleton.tsx`

**Features**:
- Pulse animation (opacity 0.5 → 0.8 → 0.5)
- Multiple preset variants (text, card, avatar, button, code block)
- Configurable dimensions and border radius
- Multiple skeleton lines with gap control

**Presets**:
- `TextSkeleton`: Multiple lines of text
- `CardSkeleton`: Full card with title and content
- `AvatarSkeleton`: Circular avatar
- `ButtonSkeleton`: Button-shaped skeleton
- `CodeBlockSkeleton`: Code block with multiple lines

### 7. Spinner Component

**Location**: `src/components/common/Spinner.tsx`

**Features**:
- Smooth rotation animation (360° in 1s)
- Multiple sizes (sm, md, lg, xl)
- Color variants (primary, secondary, tertiary, muted)
- Accessible with ARIA labels
- Full-page overlay variant
- Inline variant with text

**Usage**:
```tsx
import { Spinner, SpinnerOverlay, SpinnerWithText } from '@/components/common/Spinner';

// Basic spinner
<Spinner size="md" variant="primary" />

// Full-page overlay
<SpinnerOverlay label="Loading repository..." />

// Inline with text
<SpinnerWithText text="Indexing files..." />
```

## Focus Management

**Location**: `src/lib/focus-utils.ts`

**Features**:
- Standard focus ring utilities
- Focus trapping for modals/dialogs
- Focus restoration after modal close
- Keyboard navigation helpers
- Screen reader announcements

**Utilities**:
- `focusRing`: Standard focus ring classes
- `focusRingOnColor`: Focus ring for colored backgrounds
- `focusRingInDark`: Focus ring for dark containers
- `trapFocus()`: Trap focus within a container
- `createFocusRestore()`: Restore focus after modal
- `announce()`: Announce to screen readers

**Usage**:
```tsx
import { focusRing, trapFocus, announce } from '@/lib/focus-utils';

// Apply focus ring to custom component
<div className={cn('custom-component', focusRing)} tabIndex={0}>
  Content
</div>

// Trap focus in modal
useEffect(() => {
  const cleanup = trapFocus(modalRef.current);
  return cleanup;
}, []);

// Announce dynamic content
announce('Repository indexed successfully', 'polite');
```

## Animation Presets

**Location**: `src/lib/animation-presets.ts`

All animations use framer-motion variants with consistent easing and timing.

**Available Presets**:
- `fadeIn`: Simple fade in/out
- `fadeInUp`: Fade in with upward motion
- `fadeInDown`: Fade in with downward motion
- `slideInLeft`: Slide from left
- `slideInRight`: Slide from right
- `scaleIn`: Scale up from 0.9
- `staggerContainer`: Container for staggered children
- `staggerItem`: Item in staggered list
- `expand`: Accordion expand/collapse
- `pulse`: Continuous pulse animation
- `shimmer`: Shimmer effect for loaders
- `rotate`: Continuous rotation
- `bounce`: Bounce effect
- `pageTransition`: Page-level transitions
- `hoverScale`: Scale on hover
- `hoverLift`: Lift on hover
- `messageBubble`: Chat message animation
- `toast`: Toast notification animation

## Keyboard Navigation

All interactive elements support keyboard navigation:

### Focus Indicators
- ✅ Visible focus rings on all interactive elements
- ✅ 2px ring with 2px offset for clarity
- ✅ Primary color at 20% opacity
- ✅ Smooth transitions (150ms)

### Tab Order
- ✅ Logical tab order following visual layout
- ✅ Skip links for main content
- ✅ Focus trapping in modals
- ✅ Focus restoration after modal close

### Keyboard Shortcuts
- `Tab`: Move to next focusable element
- `Shift + Tab`: Move to previous focusable element
- `Enter` / `Space`: Activate buttons and links
- `Escape`: Close modals and dropdowns
- `⌘K` / `Ctrl+K`: Open command palette (if implemented)

## Performance Optimization

### Animation Performance
- ✅ All animations use GPU-accelerated properties (transform, opacity)
- ✅ No layout-triggering animations (width, height, top, left)
- ✅ `will-change` applied sparingly for complex animations
- ✅ Reduced motion support via `prefers-reduced-motion`

### Testing
To test animation performance:
1. Open Chrome DevTools
2. Go to Performance tab
3. Record interaction
4. Check for 60fps (16.67ms per frame)
5. Look for dropped frames or jank

### Reduced Motion
All animations respect the `prefers-reduced-motion` media query:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Accessibility Checklist

- ✅ All interactive elements have visible focus indicators
- ✅ Focus rings have sufficient contrast (WCAG 2.1 Level AA)
- ✅ Keyboard navigation works for all interactions
- ✅ Screen reader announcements for dynamic content
- ✅ ARIA labels on icon-only buttons
- ✅ ARIA live regions for toast notifications
- ✅ Semantic HTML elements (button, a, input)
- ✅ Minimum touch target size (44x44px)
- ✅ Color is not the only indicator of state

## Integration Checklist

To integrate micro-interactions into your pages:

1. **Add ToastProvider to root layout**:
   ```tsx
   // app/layout.tsx
   import { ToastProvider } from '@/components/providers/ToastProvider';
   
   export default function RootLayout({ children }) {
     return (
       <html>
         <body>
           {children}
           <ToastProvider />
         </body>
       </html>
     );
   }
   ```

2. **Wrap pages with PageTransition**:
   ```tsx
   import { PageTransition } from '@/components/common/PageTransition';
   
   export default function MyPage() {
     return (
       <PageTransition>
         {/* page content */}
       </PageTransition>
     );
   }
   ```

3. **Use InteractiveCard for clickable cards**:
   ```tsx
   import { InteractiveCard } from '@/components/common/InteractiveCard';
   
   <InteractiveCard onClick={handleClick}>
     {/* card content */}
   </InteractiveCard>
   ```

4. **Add loading states with Spinner or LoadingSkeleton**:
   ```tsx
   import { Spinner, LoadingSkeleton } from '@/components/common';
   
   {isLoading ? <Spinner /> : <Content />}
   {isLoading ? <LoadingSkeleton count={3} /> : <List />}
   ```

5. **Show feedback with toast notifications**:
   ```tsx
   import { useToast } from '@/hooks/useToast';
   
   const { success, error } = useToast();
   
   try {
     await action();
     success({ title: 'Success!' });
   } catch (err) {
     error({ title: 'Failed', description: err.message });
   }
   ```

## Examples

### Repository Card with Hover Effect
```tsx
import { InteractiveCard } from '@/components/common/InteractiveCard';
import { motion } from 'framer-motion';
import { staggerItem } from '@/lib/animation-presets';

<motion.div variants={staggerItem}>
  <InteractiveCard onClick={() => router.push(`/repos/${repo.id}`)}>
    <div className="p-6">
      <h3 className="text-title-md text-text-primary">{repo.name}</h3>
      <p className="text-body-sm text-text-secondary">{repo.description}</p>
    </div>
  </InteractiveCard>
</motion.div>
```

### Form with Loading State
```tsx
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/common/Spinner';
import { useToast } from '@/hooks/useToast';

function MyForm() {
  const [isLoading, setIsLoading] = useState(false);
  const { success, error } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await submitForm();
      success({ title: 'Form submitted successfully' });
    } catch (err) {
      error({ title: 'Submission failed', description: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <Button type="submit" disabled={isLoading}>
        {isLoading ? (
          <>
            <Spinner size="sm" className="mr-2" />
            Submitting...
          </>
        ) : (
          'Submit'
        )}
      </Button>
    </form>
  );
}
```

### List with Stagger Animation
```tsx
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';

<motion.div
  variants={staggerContainer}
  initial="hidden"
  animate="visible"
  className="space-y-4"
>
  {items.map((item) => (
    <motion.div key={item.id} variants={staggerItem}>
      <ItemCard item={item} />
    </motion.div>
  ))}
</motion.div>
```

## Testing

### Manual Testing Checklist
- [ ] All buttons have hover states
- [ ] All buttons have active/press states
- [ ] All buttons have focus rings
- [ ] All inputs have focus rings
- [ ] All cards have hover effects (if interactive)
- [ ] Toast notifications appear and dismiss correctly
- [ ] Page transitions are smooth
- [ ] Loading skeletons appear during data fetching
- [ ] Spinners appear during async operations
- [ ] Keyboard navigation works throughout the app
- [ ] Tab order is logical
- [ ] Focus is trapped in modals
- [ ] Focus is restored after modal close
- [ ] Animations run at 60fps (no jank)
- [ ] Reduced motion is respected

### Performance Testing
```bash
# Run Lighthouse audit
npm run build
npm run start
# Open Chrome DevTools > Lighthouse > Run audit

# Check for:
# - Performance score > 90
# - Accessibility score > 95
# - No layout shifts (CLS < 0.1)
# - Fast interaction times (INP < 200ms)
```

## Future Enhancements

Potential improvements for future iterations:
- [ ] Haptic feedback for mobile devices
- [ ] Sound effects for key interactions (optional)
- [ ] Advanced gesture support (swipe, pinch)
- [ ] Skeleton screens with actual content shapes
- [ ] Optimistic UI updates
- [ ] Undo/redo with toast actions
- [ ] Keyboard shortcut overlay (⌘K menu)
- [ ] Custom cursor states for drag operations
