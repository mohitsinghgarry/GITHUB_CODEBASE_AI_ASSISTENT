# Performance Testing Guide

This guide provides instructions for testing the performance of animations and interactions in the RepoMind Assistant frontend.

## Target Metrics

- **Frame Rate**: 60fps (16.67ms per frame)
- **Interaction to Next Paint (INP)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s

## Tools

### 1. Chrome DevTools Performance Panel

**How to use**:
1. Open Chrome DevTools (F12 or Cmd+Option+I)
2. Go to the Performance tab
3. Click the record button (or Cmd+E)
4. Interact with the application
5. Stop recording
6. Analyze the flame chart

**What to look for**:
- Green bars in the FPS chart (60fps)
- No red bars (dropped frames)
- Scripting time < 50ms
- Rendering time < 16ms
- Layout shifts (should be minimal)

### 2. Chrome DevTools Rendering Panel

**How to use**:
1. Open Chrome DevTools
2. Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)
3. Type "Show Rendering"
4. Enable "Frame Rendering Stats"
5. Enable "Paint flashing"

**What to look for**:
- FPS counter stays at 60
- Minimal paint flashing during animations
- No layout thrashing

### 3. Lighthouse

**How to use**:
```bash
# Build production version
npm run build
npm run start

# Open Chrome DevTools > Lighthouse
# Select "Performance" and "Accessibility"
# Click "Analyze page load"
```

**Target scores**:
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90

### 4. React DevTools Profiler

**How to use**:
1. Install React DevTools extension
2. Open DevTools > Profiler tab
3. Click record
4. Interact with the application
5. Stop recording
6. Analyze component render times

**What to look for**:
- Component render times < 16ms
- No unnecessary re-renders
- Efficient memoization

## Test Scenarios

### Scenario 1: Button Interactions

**Test**:
1. Hover over buttons
2. Click buttons
3. Tab through buttons with keyboard

**Expected**:
- Hover state appears within 150ms
- Active state appears immediately
- Focus ring appears on keyboard focus
- No layout shifts
- 60fps throughout

**How to verify**:
```javascript
// In Chrome DevTools Console
performance.mark('hover-start');
// Hover over button
performance.mark('hover-end');
performance.measure('hover-duration', 'hover-start', 'hover-end');
console.log(performance.getEntriesByName('hover-duration')[0].duration);
// Should be < 150ms
```

### Scenario 2: Page Transitions

**Test**:
1. Navigate between pages
2. Observe fade-in/fade-out animations

**Expected**:
- Smooth 250ms transition
- No layout shifts
- 60fps throughout
- Content appears progressively

**How to verify**:
1. Record with Performance panel
2. Check FPS chart for green bars
3. Check for layout shifts in the timeline

### Scenario 3: Toast Notifications

**Test**:
1. Trigger multiple toast notifications
2. Dismiss toasts manually
3. Wait for auto-dismiss

**Expected**:
- Toast appears within 250ms
- Smooth slide-in animation
- No jank when multiple toasts appear
- Smooth exit animation

**How to verify**:
```javascript
// In Chrome DevTools Console
const startTime = performance.now();
// Trigger toast
setTimeout(() => {
  const endTime = performance.now();
  console.log(`Toast appeared in ${endTime - startTime}ms`);
  // Should be < 250ms
}, 0);
```

### Scenario 4: Loading Skeletons

**Test**:
1. Navigate to a page with loading state
2. Observe skeleton loaders
3. Wait for content to load

**Expected**:
- Skeleton appears immediately
- Smooth pulse animation
- No layout shift when content loads
- 60fps throughout

**How to verify**:
1. Enable "Paint flashing" in Rendering panel
2. Observe minimal flashing during skeleton animation
3. Check for layout shifts when content loads

### Scenario 5: Interactive Cards

**Test**:
1. Hover over cards
2. Click cards
3. Tab through cards with keyboard

**Expected**:
- Lift animation within 150ms
- Smooth scale animation on press
- Focus ring appears on keyboard focus
- 60fps throughout

**How to verify**:
1. Record with Performance panel
2. Check for GPU-accelerated transforms
3. Verify no layout recalculations

### Scenario 6: List Animations

**Test**:
1. Navigate to a page with a list
2. Observe stagger animation
3. Scroll through the list

**Expected**:
- Items appear with 50ms stagger
- Smooth fade-in and slide-up
- No jank during animation
- 60fps throughout

**How to verify**:
1. Record with Performance panel
2. Check for consistent frame times
3. Verify stagger timing in timeline

## Automated Performance Tests

### Using Playwright

```typescript
// tests/performance.spec.ts
import { test, expect } from '@playwright/test';

test('button hover performance', async ({ page }) => {
  await page.goto('/');
  
  // Start performance measurement
  await page.evaluate(() => performance.mark('hover-start'));
  
  // Hover over button
  await page.hover('button');
  
  // End performance measurement
  const duration = await page.evaluate(() => {
    performance.mark('hover-end');
    performance.measure('hover-duration', 'hover-start', 'hover-end');
    return performance.getEntriesByName('hover-duration')[0].duration;
  });
  
  // Assert duration is less than 150ms
  expect(duration).toBeLessThan(150);
});

test('page transition performance', async ({ page }) => {
  await page.goto('/');
  
  // Start performance measurement
  const startTime = Date.now();
  
  // Navigate to another page
  await page.click('a[href="/repos"]');
  await page.waitForLoadState('networkidle');
  
  const endTime = Date.now();
  const duration = endTime - startTime;
  
  // Assert transition completes within 1 second
  expect(duration).toBeLessThan(1000);
});

test('toast notification performance', async ({ page }) => {
  await page.goto('/');
  
  // Trigger toast
  const startTime = Date.now();
  await page.click('button[data-testid="trigger-toast"]');
  
  // Wait for toast to appear
  await page.waitForSelector('[role="status"]');
  const endTime = Date.now();
  
  const duration = endTime - startTime;
  
  // Assert toast appears within 250ms
  expect(duration).toBeLessThan(250);
});
```

### Using Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - run: npm install -g @lhci/cli
      - run: lhci autorun
```

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run start',
      url: ['http://localhost:3000'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'interactive': ['error', { maxNumericValue: 3000 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

## Performance Optimization Checklist

### Animations
- [ ] All animations use GPU-accelerated properties (transform, opacity)
- [ ] No animations on layout-triggering properties (width, height, top, left)
- [ ] `will-change` used sparingly and removed after animation
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Frame rate stays at 60fps during animations

### Components
- [ ] Components are memoized where appropriate (React.memo)
- [ ] Expensive calculations are memoized (useMemo)
- [ ] Event handlers are memoized (useCallback)
- [ ] Large lists use virtualization (react-window or similar)
- [ ] Images are lazy-loaded and optimized

### State Management
- [ ] State updates are batched
- [ ] Unnecessary re-renders are avoided
- [ ] Context is split to avoid over-rendering
- [ ] Zustand stores are optimized with selectors

### Network
- [ ] API calls are debounced/throttled
- [ ] Data is cached appropriately
- [ ] Optimistic updates are used where appropriate
- [ ] Loading states are shown immediately

### Bundle Size
- [ ] Code splitting is implemented
- [ ] Dynamic imports are used for large components
- [ ] Tree shaking is enabled
- [ ] Bundle size is monitored

## Common Performance Issues

### Issue 1: Janky Animations

**Symptoms**:
- Dropped frames during animations
- Stuttering or lag

**Causes**:
- Animating layout-triggering properties
- Too many elements animating at once
- Heavy JavaScript execution during animation

**Solutions**:
- Use transform and opacity only
- Reduce number of animated elements
- Use `requestAnimationFrame` for JS animations
- Add `will-change` temporarily

### Issue 2: Slow Hover States

**Symptoms**:
- Delay before hover state appears
- Laggy hover effects

**Causes**:
- Heavy re-renders on hover
- Complex CSS selectors
- JavaScript hover handlers

**Solutions**:
- Use CSS-only hover states
- Simplify selectors
- Debounce hover handlers
- Use `pointer-events: none` on children

### Issue 3: Layout Shifts

**Symptoms**:
- Content jumps during load
- Elements move unexpectedly

**Causes**:
- Images without dimensions
- Dynamic content insertion
- Font loading

**Solutions**:
- Set explicit dimensions on images
- Reserve space for dynamic content
- Use `font-display: swap` or preload fonts
- Use skeleton loaders

### Issue 4: Slow Page Transitions

**Symptoms**:
- Delay between navigation and content
- Blank screen during transition

**Causes**:
- Large bundle size
- Synchronous data fetching
- Heavy component mounting

**Solutions**:
- Implement code splitting
- Use streaming SSR
- Show loading states immediately
- Prefetch data on hover

## Monitoring in Production

### Setup Performance Monitoring

```typescript
// lib/performance-monitoring.ts
export function reportWebVitals(metric: any) {
  // Send to analytics service
  if (metric.label === 'web-vital') {
    console.log(metric);
    
    // Example: Send to Google Analytics
    if (window.gtag) {
      window.gtag('event', metric.name, {
        value: Math.round(metric.value),
        event_label: metric.id,
        non_interaction: true,
      });
    }
  }
}
```

```typescript
// app/layout.tsx
import { reportWebVitals } from '@/lib/performance-monitoring';

export function reportWebVitals(metric: any) {
  reportWebVitals(metric);
}
```

### Key Metrics to Monitor

1. **Core Web Vitals**:
   - LCP (Largest Contentful Paint)
   - FID (First Input Delay) / INP (Interaction to Next Paint)
   - CLS (Cumulative Layout Shift)

2. **Custom Metrics**:
   - Time to Interactive
   - Time to First Byte
   - Bundle Size
   - API Response Times

3. **User Experience Metrics**:
   - Page Load Time
   - Navigation Time
   - Error Rate
   - Bounce Rate

## Resources

- [Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Framer Motion Performance](https://www.framer.com/motion/guide-reduce-bundle-size/)
