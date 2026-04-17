# RepoMind Assistant Design System

## "Obsidian Intelligence" Framework

This design system is engineered to feel less like a "website" and more like a high-performance terminal housed within a premium editorial shell. It rejects the "busy" aesthetics of traditional SaaS dashboards in favor of **The Monolithic Curator**—an approach characterized by vast, intentional negative space, razor-sharp typography, and "physical" depth achieved through light physics rather than structural lines.

---

## Core Principles

### 1. The "No-Line" Rule

**Traditional 1px borders are prohibited for sectioning.**

To define boundaries, you must use **background color shifts**. A sidebar doesn't get a line; it sits on `surface-container-low` while the main stage sits on `surface`. This creates a cleaner, more sophisticated interface that lets the content breathe.

```tsx
// ❌ DON'T: Use borders for sectioning
<div className="border-r border-outline">
  <Sidebar />
</div>

// ✅ DO: Use background color shifts
<div className="bg-surface-container-low">
  <Sidebar />
</div>
<div className="bg-surface">
  <MainContent />
</div>
```

### 2. Tonal Layering (Surface Hierarchy)

Think of the UI as a series of stacked, milled obsidian sheets:

- **Base Layer:** `surface` (#0e0e10) — The absolute foundation
- **Sectioning:** `surface-container-low` (#131315) — Secondary navigation or side panels
- **Interactive Cards:** `surface-container` (#19191c) — Standard interactive surface
- **Elevated Surfaces:** `surface-container-high` (#1f1f22) — Elevated elements
- **Floating Elements:** `surface-container-highest` (#262528) — Modals, popovers

```tsx
// Example: Card on background
<div className="bg-surface p-8">
  <div className="bg-surface-container rounded-md p-6">
    <h3>Card Title</h3>
    <p>Card content</p>
  </div>
</div>
```

### 3. Glassmorphism

All navigation bars and floating panels must use **Glassmorphism**:

- **Background:** `surface-container` at 70% opacity
- **Effect:** `backdrop-filter: blur(12px)`

```tsx
// Navigation bar with glass effect
<nav className="glass fixed top-0 w-full">
  <NavigationContent />
</nav>

// Modal with enhanced glass effect
<div className="glass-modal rounded-lg p-6">
  <ModalContent />
</div>
```

### 4. The Signature Gradient

Use the `primary` to `secondary` gradient (Electric Indigo to Violet) **exclusively** for high-intent CTAs and data-vis highlights. This gradient is the "soul" of the system—use it sparingly to maintain its impact.

```tsx
// Primary CTA button
<button className="gradient-primary text-on-primary px-6 py-3 rounded-md">
  Get Started
</button>

// Subtle gradient for secondary actions
<button className="gradient-primary-subtle text-on-surface px-4 py-2 rounded-md">
  Learn More
</button>
```

### 5. The 4px Grid

Every margin must be a multiple of 4. Use the spacing scale: `1` (4px), `2` (8px), `3` (12px), `4` (16px), `6` (24px), `8` (32px), `16` (64px), etc.

```tsx
// Minimum separation between items: 24px (spacing-6)
<div className="space-y-6">
  <Item />
  <Item />
</div>

// Extreme whitespace for editorial feel: 64px (spacing-16)
<section className="py-16">
  <Content />
</section>
```

---

## Color System

### Background & Surface Colors

```tsx
// Background
bg-background              // #0e0e10 - Base layer

// Surface hierarchy
bg-surface                 // #0e0e10 - Surface base
bg-surface-container-lowest // #000000 - True black (code blocks)
bg-surface-container-low   // #131315 - Side panels
bg-surface-container       // #19191c - Interactive cards
bg-surface-container-high  // #1f1f22 - Elevated surfaces
bg-surface-container-highest // #262528 - Floating elements
bg-surface-bright          // #2c2c2f - Brightened surface
```

### Accent Colors

```tsx
// Primary (Electric Indigo)
bg-primary                 // #a3a6ff
bg-primary-container       // #9396ff
bg-primary-dim             // #6063ee - Subtle states
text-primary

// Secondary (Violet)
bg-secondary               // #ac8aff
bg-secondary-container     // #5516be
bg-secondary-dim           // #8455ef
text-secondary

// Tertiary (Emerald/Success)
bg-tertiary                // #9bffce
bg-tertiary-container      // #69f6b8
bg-tertiary-dim            // #58e7ab
text-tertiary

// Error
bg-error                   // #ff6e84
bg-error-container         // #a70138
bg-error-dim               // #d73357
text-error
```

### Text Colors

```tsx
// Primary text - NOT pure white (#f9f5f8)
text-on-surface            // Primary text
text-on-surface-variant    // Secondary text (#adaaad)
text-outline               // Tertiary text (#767577)
text-outline-variant       // Disabled text (#48474a)
```

---

## Typography

### Font Families

- **UI Elements:** Inter (precision and clarity)
- **Code Elements:** JetBrains Mono (technical authority)

```tsx
// UI text
<p className="font-sans">User interface text</p>

// Code text
<code className="font-mono">const code = 'example';</code>
```

### Type Scale

```tsx
// Display (for empty states and hero headings)
text-display-lg            // 3.5rem, -0.02em tracking
text-display-md            // 2.875rem
text-display-sm            // 2.25rem

// Headline (primary page titles)
text-headline-lg           // 2rem
text-headline-md           // 1.75rem
text-headline-sm           // 1.5rem

// Title (section headers)
text-title-lg              // 1.375rem
text-title-md              // 1.125rem
text-title-sm              // 1rem

// Body (workhorse text)
text-body-lg               // 1rem
text-body-md               // 0.875rem
text-body-sm               // 0.75rem

// Label (metadata and tags)
text-label-lg              // 0.875rem
text-label-md              // 0.75rem, +0.05em tracking
text-label-sm              // 0.6875rem, +0.1em tracking, ALL-CAPS
```

### Usage Examples

```tsx
// Page title
<h1 className="text-headline-lg text-on-surface">
  Repository Dashboard
</h1>

// Section header
<h2 className="text-title-md text-on-surface">
  Recent Activity
</h2>

// Body text
<p className="text-body-md text-on-surface-variant">
  This is the main content text.
</p>

// Metadata label (all-caps)
<span className="text-label-sm uppercase tracking-widest text-on-surface-variant">
  Last Updated
</span>
```

---

## Components

### Buttons

```tsx
// Primary button (gradient)
<button className="btn-primary">
  Primary Action
</button>

// Secondary button (surface-bright with ghost border)
<button className="btn-secondary">
  Secondary Action
</button>

// Tertiary button (text only)
<button className="btn-tertiary">
  Tertiary Action
</button>
```

### Input Fields

```tsx
// Standard input
<input
  type="text"
  className="input"
  placeholder="Enter text..."
/>

// With label
<div className="space-y-2">
  <label className="label">Username</label>
  <input type="text" className="input" />
</div>
```

### Cards

```tsx
// Standard card (no borders)
<div className="card p-6">
  <h3 className="text-title-md">Card Title</h3>
  <p className="text-body-md text-on-surface-variant">Card content</p>
</div>

// Elevated card
<div className="card-elevated p-6">
  <h3 className="text-title-md">Elevated Card</h3>
</div>

// Floating card (with shadow)
<div className="card-floating p-6">
  <h3 className="text-title-md">Floating Card</h3>
</div>
```

### Lists (No Divider Lines)

```tsx
// Use spacing instead of dividers
<div className="space-y-6">
  <div className="hover:bg-surface-container-high p-4 rounded-md transition-quart">
    <ListItem />
  </div>
  <div className="hover:bg-surface-container-high p-4 rounded-md transition-quart">
    <ListItem />
  </div>
</div>

// Zebra-striping without stripes (alternating backgrounds)
<div>
  <div className="bg-surface p-4">
    <ListItem />
  </div>
  <div className="bg-surface-container-low p-4">
    <ListItem />
  </div>
</div>
```

### Code Blocks

```tsx
// Inline code
<code className="bg-surface-container-lowest px-1 py-0.5 rounded-sm font-mono">
  const example = true;
</code>

// Code block
<pre className="bg-surface-container-lowest p-4 rounded-md overflow-x-auto">
  <code className="font-mono text-body-sm">
    {codeContent}
  </code>
</pre>
```

### Badges/Chips

```tsx
// Primary badge
<span className="badge-primary">Active</span>

// Secondary badge
<span className="badge-secondary">Pending</span>

// Tertiary badge
<span className="badge-tertiary">Success</span>

// Error badge
<span className="badge-error">Failed</span>
```

---

## Animations

### Framer Motion Presets

Import animation presets from `lib/animation-presets.ts`:

```tsx
import { fadeIn, fadeInUp, scaleIn, staggerContainer, staggerItem } from '@/lib/animation-presets';
import { motion } from 'framer-motion';

// Fade in animation
<motion.div variants={fadeIn} initial="hidden" animate="visible">
  <Content />
</motion.div>

// Fade in up (for cards)
<motion.div variants={fadeInUp} initial="hidden" animate="visible">
  <Card />
</motion.div>

// Stagger container (for lists)
<motion.div variants={staggerContainer} initial="hidden" animate="visible">
  {items.map((item) => (
    <motion.div key={item.id} variants={staggerItem}>
      <Item data={item} />
    </motion.div>
  ))}
</motion.div>
```

### Transition Easing

All transitions use **Quart easing** for high-end, responsive "snap":

```tsx
// Using Tailwind classes
<div className="transition-quart hover:scale-105">
  <InteractiveElement />
</div>

// Using Framer Motion
<motion.div
  whileHover={{ scale: 1.02 }}
  transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
>
  <Card />
</motion.div>
```

---

## Do's and Don'ts

### ✅ DO

- **Do** use extreme whitespace (64px+) between major sections to emphasize the "Editorial" feel
- **Do** use Lucide icons at 16px for UI actions and 20px for section headers
- **Do** treat the 4px grid as a law, not a suggestion
- **Do** use `text-on-surface` (#f9f5f8) instead of pure white for text
- **Do** use background color shifts to define boundaries
- **Do** use tonal layering for depth instead of shadows

### ❌ DON'T

- **Don't** use pure white (#FFFFFF) for text
- **Don't** use 1px borders for sectioning
- **Don't** use "Card in Card" layouts with borders
- **Don't** use standard easing (use Quart easing: `cubic-bezier(0.16, 1, 0.3, 1)`)
- **Don't** overuse the signature gradient (reserve for high-intent CTAs)
- **Don't** use divider lines between list items (use spacing instead)

---

## Accessibility

### Ghost Borders

If contrast testing (WCAG) requires a container boundary, use a **Ghost Border**:

```tsx
<div className="ghost-border">
  <Content />
</div>
```

This adds a barely visible border using `outline-variant` at 15% opacity.

### Focus States

All interactive elements automatically receive a focus glow:

```tsx
// Automatic focus glow on interactive elements
<button className="btn-primary">
  Button
</button>

// Custom focus state
<div className="focus-visible:shadow-focus-glow">
  <CustomInteractive />
</div>
```

---

## Icon Guidelines

Use **Lucide icons** with consistent sizing:

```tsx
import { Search, Settings } from 'lucide-react';

// UI actions: 16px
<Search size={16} className="text-on-surface-variant" />

// Section headers: 20px
<Settings size={20} className="text-on-surface" />

// Large icons: 24px
<Icon size={24} />
```

Icon stroke width should be **1.5px** for a refined look.

---

## Responsive Design

The design system is built mobile-first with breakpoints:

```tsx
// Mobile-first approach
<div className="p-4 md:p-6 lg:p-8">
  <Content />
</div>

// Responsive typography
<h1 className="text-headline-sm md:text-headline-md lg:text-headline-lg">
  Responsive Heading
</h1>

// Responsive spacing
<section className="py-8 md:py-12 lg:py-16">
  <Content />
</section>
```

---

## Resources

- **Design Tokens:** `frontend/src/lib/design-tokens.ts`
- **Animation Presets:** `frontend/src/lib/animation-presets.ts`
- **Tailwind Config:** `frontend/tailwind.config.ts`
- **Global Styles:** `frontend/src/app/globals.css`
- **Stitch Project:** RepoMind Assistant (projects/607025827578097506)

---

## Questions?

For design system questions or clarifications, refer to the design specification in the Stitch project or consult the design tokens file.
