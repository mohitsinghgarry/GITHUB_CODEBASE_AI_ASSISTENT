# RepoMind Assistant - Design Reference Document

**Project:** RepoMind Assistant  
**Stitch Project ID:** projects/607025827578097506  
**Device Type:** Desktop (Dark Mode)  
**Last Updated:** April 16, 2026  
**Status:** Private

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Elevation & Depth](#elevation--depth)
6. [Components](#components)
7. [Screen Inventory](#screen-inventory)
8. [Animation Guidelines](#animation-guidelines)
9. [Implementation Notes](#implementation-notes)

---

## Design Philosophy

### Creative North Star: "The Monolithic Curator"

This design system is engineered to feel less like a "website" and more like a **high-performance terminal housed within a premium editorial shell**. It rejects the "busy" aesthetics of traditional SaaS dashboards in favor of an approach characterized by:

- **Vast, intentional negative space**
- **Razor-sharp typography**
- **"Physical" depth achieved through light physics rather than structural lines**
- **Intentional asymmetry** - Primary content is anchored with heavy typographic weights, while utility elements are tucked into "nested" glass containers

The result is a system that feels **authoritative, silent, and incredibly fast**.

---

## Color System

### Base Palette

The palette is built on "Deep Charcoal" foundations, using violet and indigo pulses to highlight intelligence and movement.

#### Primary Colors
- **Primary:** `#a3a6ff` (Electric Indigo)
- **Primary Container:** `#9396ff`
- **Primary Dim:** `#6063ee`
- **Primary Fixed:** `#9396ff`
- **Primary Fixed Dim:** `#8387ff`

#### Secondary Colors
- **Secondary:** `#ac8aff` (Violet)
- **Secondary Container:** `#5516be`
- **Secondary Dim:** `#8455ef`
- **Secondary Fixed:** `#dac9ff`
- **Secondary Fixed Dim:** `#ceb9ff`

#### Tertiary Colors (Success/Emerald)
- **Tertiary:** `#9bffce`
- **Tertiary Container:** `#69f6b8`
- **Tertiary Dim:** `#58e7ab`
- **Tertiary Fixed:** `#69f6b8`
- **Tertiary Fixed Dim:** `#58e7ab`

#### Error Colors
- **Error:** `#ff6e84`
- **Error Container:** `#a70138`
- **Error Dim:** `#d73357`

### Surface Hierarchy (The "No-Line" Rule)

**CRITICAL:** Traditional 1px borders are **prohibited for sectioning**. Define boundaries through background color shifts only.

Think of the UI as a series of stacked, milled obsidian sheets:

- **Base Layer:** `surface` (#0e0e10) — The absolute foundation
- **Sectioning:** `surface-container-low` (#131315) — Used for secondary navigation or side panels
- **Interactive Cards:** `surface-container` (#19191c) — The standard interactive surface
- **Elevated Cards:** `surface-container-high` (#1f1f22)
- **Highest Elevation:** `surface-container-highest` (#262528) — Floating elements requiring immediate focus
- **Lowest (True Black):** `surface-container-lowest` (#000000) — Code blocks and recessed elements
- **Bright Surfaces:** `surface-bright` (#2c2c2f) — Elements that "pop" toward the user
- **Dim Surfaces:** `surface-dim` (#0e0e10)

### Text Colors

- **On Surface:** `#f9f5f8` (Primary text - NOT pure white)
- **On Surface Variant:** `#adaaad` (Secondary text)
- **On Background:** `#f9f5f8`
- **On Primary:** `#0f00a4` (Text on primary buttons - Black/Deep Navy)
- **Outline:** `#767577` (Placeholder text)
- **Outline Variant:** `#48474a` (Ghost borders at 15% opacity)

### The Glass & Gradient Rule

For floating elements (Modals, Command Palettes, Tooltips):
- **Background:** `surface-container` at 70% opacity
- **Effect:** `backdrop-filter: blur(12px)`
- **Signature Pulse:** Use `primary` to `secondary` gradient (Electric Indigo to Violet) exclusively for high-intent CTAs and data-vis highlights

---

## Typography

### Font Families

- **UI Typeface:** Inter (Precision and clarity)
- **Code Typeface:** JetBrains Mono (Technical authority)

### Typographic Hierarchy

#### Display (Hero/Empty States)
- **Display LG:** 3.5rem (56px) / Letter-spacing: -0.02em / Weight: 600
- **Display MD:** 2.8rem (45px) / Letter-spacing: -0.02em / Weight: 600
- **Display SM:** 2.25rem (36px) / Letter-spacing: -0.02em / Weight: 600

#### Headlines (Page Titles)
- **Headline LG:** 2rem (32px) / Weight: 600
- **Headline MD:** 1.75rem (28px) / Weight: 600
- **Headline SM:** 1.5rem (24px) / Weight: 600 / Color: `on-surface` with high contrast

#### Titles (Section Headers)
- **Title LG:** 1.375rem (22px) / Weight: 500
- **Title MD:** 1.125rem (18px) / Weight: 500
- **Title SM:** 1rem (16px) / Weight: 600

#### Body (Content)
- **Body LG:** 1rem (16px) / Weight: 400 / Line-height: 1.6
- **Body MD:** 0.875rem (14px) / Weight: 400 / Line-height: 1.5 (The workhorse)
- **Body SM:** 0.8125rem (13px) / Weight: 400

#### Labels (Metadata/Tags)
- **Label LG:** 0.875rem (14px) / Weight: 500
- **Label MD:** 0.75rem (12px) / Weight: 500
- **Label SM:** 0.6875rem (11px) / Weight: 500 / All-caps / Letter-spacing: +0.05em

### Typography Rules

- Use `on-surface-variant` (#adaaad) for secondary info to reduce cognitive load
- **Never use pure white (#FFFFFF)** - always use `on-surface` (#f9f5f8) to prevent eye strain
- Code blocks always use JetBrains Mono

---

## Spacing & Layout

### The 4px Grid System

**CRITICAL:** Treat the 4px grid as a law, not a suggestion. Every margin must be a multiple of 4.

### Spacing Scale (spacingScale: 3)

Based on 4px base unit with scale factor 3:

- **xs:** 4px (0.25rem)
- **sm:** 8px (0.5rem)
- **md:** 16px (1rem)
- **lg:** 24px (1.5rem)
- **xl:** 32px (2rem)
- **2xl:** 48px (3rem)
- **3xl:** 64px (4rem)
- **4xl:** 96px (6rem)

### Layout Guidelines

- Use **extreme whitespace (64px+)** between major sections to emphasize the "Editorial" feel
- Use 24px or 32px of vertical "Dead Space" between list items
- For dense layouts, use alternating `surface` and `surface-container-low` backgrounds (Zebra-striping without the stripes)

---

## Elevation & Depth

### The Layering Principle

**Depth is not an effect; it is information.**

Instead of drop shadows, use **Tonal Layering**:
- Place a `surface-container-lowest` (#000000) area behind a code block to "recess" it into the page
- Use `surface-bright` (#2c2c2f) to make a button "pop" out toward the user

### Ambient Shadows

Shadows are reserved for elements that physically "float" (Modals, Popovers):

- **Spec:** `box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);`
- **Tinting:** The shadow must never be neutral grey. It should feel like a deep, desaturated violet to match our `on-surface` tones

### The "Ghost Border" Fallback

If contrast testing (WCAG) requires a container boundary:
- **Token:** `outline-variant` (#48474a) at **15% opacity**
- **Rule:** It should be barely visible—a suggestion of an edge, not a cage

---

## Components

### Buttons

#### Primary Button
- **Background:** Gradient fill (`primary` to `secondary`)
- **Text:** `on-primary` (#0f00a4) - Black/Deep Navy
- **Border Radius:** `md` (0.375rem / 6px)
- **Hover:** Shift gradient slightly
- **No borders**

#### Secondary Button
- **Background:** `surface-bright` (#2c2c2f)
- **Border:** Ghost Border (`outline-variant` at 15% opacity)
- **Text:** `on-surface`
- **Hover:** Transition to `surface-container-high`

#### Tertiary Button
- **Background:** Transparent
- **Text:** `on-surface-variant`
- **Hover:** Shift text to `on-surface`

### Input Fields

#### Base State
- **Background:** `surface-container-low` (#131315)
- **Border:** None
- **Placeholder:** `outline` (#767577)
- **Text:** `on-surface`

#### Active/Focus State
- **Border:** 1px `primary-dim` Ghost Border
- **Glow:** Subtle `primary` outer glow (4px blur, 10% opacity)
- **No thick borders**

### Cards & Lists

#### Card Design
- **Background:** `surface-container` or `surface-container-low`
- **Border Radius:** `lg` (0.5rem / 8px) or `md` (0.375rem / 6px)
- **Border:** **PROHIBITED** - Use background color shifts
- **Padding:** 24px or 32px

#### List Separation
- **Prohibition:** **No divider lines**
- **Separation:** Use 24px or 32px of vertical spacing
- **Hover State:** `surface-container-high` background
- **Active State:** Subtle left accent bar in `primary` (2-4px wide)

### Code Blocks

- **Container:** `surface-container-lowest` (#000000 - True black)
- **Border Radius:** `md` (0.375rem / 6px)
- **Font:** JetBrains Mono
- **Syntax Highlighting:**
  - Strings: `tertiary` (Emerald #9bffce)
  - Keywords: `error_dim` (Rose #d73357)
  - Functions: `primary` (Indigo #a3a6ff)

### Icons

- **Library:** Lucide Icons
- **Size:** 16px for UI actions, 20px for section headers
- **Stroke Width:** 1.5px for refined look
- **Color:** Inherit from parent or `on-surface-variant`

---

## Screen Inventory

### 1. Landing Page (Desktop)
- **Screen ID:** `b21ed91cbff04978b7f4b347e891575b`
- **Dimensions:** 2560 x 7220px
- **Purpose:** Marketing/hero page with product introduction
- **Key Elements:**
  - Hero section with large display typography
  - Feature showcase
  - CTA buttons with gradient
  - Footer

### 2. Landing Page (Mobile)
- **Screen ID:** `21562c93d1534fd9a284e37436b2c647`
- **Dimensions:** 390 x 884px
- **Purpose:** Mobile-optimized landing page

### 3. Repository Load
- **Screen ID:** `981d91c77c384bad9c18331384b971e2`
- **Dimensions:** 2560 x 2158px
- **Purpose:** Interface for adding/loading GitHub repositories
- **Key Components:**
  - Repository URL input field
  - Validation feedback
  - Loading states
  - Progress indicators

### 4. Dashboard
- **Screen ID:** `26df9b81380b4c68822acb3520127d80`
- **Dimensions:** 2560 x 2048px
- **Purpose:** Main repository overview and statistics
- **Key Components:**
  - Repository stats cards
  - File count, chunk count, language breakdown
  - Recent activity
  - Quick actions

### 5. Chat with Repo
- **Screen ID:** `140a4c0f72484aca891c44949bc04209`
- **Dimensions:** 2560 x 2048px
- **Purpose:** RAG-powered chat interface
- **Key Components:**
  - Message list (user + assistant bubbles)
  - Code snippet cards with syntax highlighting
  - Source citations
  - Chat input with mode selector
  - Suggested questions for empty state

### 6. File Explorer
- **Screen ID:** `247da9c94a344b6eb026ef3a4c48d5c2`
- **Dimensions:** 2560 x 2048px
- **Purpose:** Browse repository file structure
- **Key Components:**
  - Hierarchical file tree
  - File/folder icons
  - Expand/collapse animations
  - File metadata
  - Language filters

### 7. Smart Search
- **Screen ID:** `b477b428ebe4447b8803228355ac6ff8`
- **Dimensions:** 2560 x 2048px
- **Purpose:** Semantic, keyword, and hybrid search
- **Key Components:**
  - Search bar with mode toggle
  - Search result cards
  - Relevance scores
  - File path breadcrumbs
  - Code preview with highlighting

### 8. Code Review
- **Screen ID:** `a043677f09534f5b8c09e5e93b9eb3d5`
- **Dimensions:** 2560 x 2048px
- **Purpose:** AI-powered code review interface
- **Key Components:**
  - Code viewer with line numbers
  - Review feedback cards
  - Severity indicators
  - Issue descriptions
  - Line-specific annotations

### 9. Code Refactor
- **Screen ID:** `78fd60e682a542e5b7375d593db39a51`
- **Dimensions:** 2560 x 2592px
- **Purpose:** Code improvement suggestions
- **Key Components:**
  - Before/after code comparison
  - Diff viewer
  - Improvement explanations
  - Apply/reject actions

### 10. Settings
- **Screen ID:** `597dc5caf9ad41409ece70c8d7c912b2`
- **Dimensions:** 2560 x 2048px
- **Purpose:** Application configuration
- **Key Components:**
  - Theme toggle (light/dark)
  - Model selection
  - API configuration
  - Preferences

### 11. Mobile Prototype
- **Screen ID:** `7e584bcebcee48ddb9bd966dac681014`
- **Dimensions:** 390 x 884px
- **Purpose:** Mobile interface exploration

---

## Animation Guidelines

### Easing Function

**CRITICAL:** All transitions should use **Quart easing** for a high-end, responsive "snap":

```css
transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
```

### Animation Types

#### 1. Fade In
- **Duration:** 200-300ms
- **Use:** Page loads, modal appearances
- **Opacity:** 0 → 1

#### 2. Slide In
- **Duration:** 300-400ms
- **Use:** Sidebar, drawer, panel animations
- **Transform:** translateX(-20px) → translateX(0)

#### 3. Scale In
- **Duration:** 200ms
- **Use:** Button presses, card interactions
- **Transform:** scale(0.95) → scale(1)

#### 4. Stagger Container
- **Duration:** 50ms delay between children
- **Use:** List items, search results
- **Pattern:** Sequential fade + slide

#### 5. Hover States
- **Duration:** 150ms
- **Use:** All interactive elements
- **Properties:** background-color, transform, opacity

### Framer Motion Presets

```typescript
// lib/animation-presets.ts
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] }
};

export const slideIn = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
  transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.05
    }
  }
};
```

---

## Implementation Notes

### Component States

#### Hover States
- Background color shift (e.g., `surface-container` → `surface-container-high`)
- Subtle scale transform (scale: 1.02)
- Cursor: pointer

#### Active States
- Slightly darker background
- Scale transform (scale: 0.98)
- Accent indicator (left border or glow)

#### Disabled States
- Opacity: 0.5
- Cursor: not-allowed
- No hover effects

#### Loading States
- Skeleton loaders with pulse animation
- Spinner with `primary` color
- Progress bars with gradient

### Glassmorphism Implementation

```css
.glass-panel {
  background: rgba(25, 25, 28, 0.7); /* surface-container at 70% */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(72, 71, 74, 0.15); /* outline-variant at 15% */
}
```

### Gradient Implementation

```css
.primary-gradient {
  background: linear-gradient(135deg, #6063ee 0%, #a3a6ff 100%);
}

.secondary-gradient {
  background: linear-gradient(135deg, #8455ef 0%, #ac8aff 100%);
}

.signature-pulse {
  background: linear-gradient(135deg, #a3a6ff 0%, #ac8aff 100%);
}
```

### Code Syntax Highlighting

```typescript
// Syntax theme for code blocks
export const syntaxTheme = {
  string: '#9bffce',      // tertiary
  keyword: '#d73357',     // error_dim
  function: '#a3a6ff',    // primary
  comment: '#767577',     // outline
  variable: '#f9f5f8',    // on-surface
  number: '#8387ff',      // primary_fixed_dim
  operator: '#adaaad',    // on-surface-variant
};
```

### Responsive Breakpoints

```typescript
export const breakpoints = {
  mobile: '390px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1280px',
  ultrawide: '1920px',
};
```

---

## Design System Assets

### Stitch Project Links

- **Project URL:** https://stitch.google.com/project/607025827578097506
- **Design System Instance:** `assets-cc51171feff040289e1b9f7265cc5680-1776257483775`

### Screen Screenshots

All screen screenshots are available via the Stitch API with download URLs. Reference the screen inventory section for specific screen IDs and dimensions.

### HTML Code Exports

Each screen has an associated HTML export available for reference during implementation. These can be downloaded via the Stitch API.

---

## Do's and Don'ts

### ✅ Do

- Use extreme whitespace (64px+) between major sections
- Use Lucide icons at 16px for UI actions and 20px for section headers
- Treat the 4px grid as a law - every margin must be a multiple of 4
- Use `on-surface` (#f9f5f8) instead of pure white for text
- Use background color shifts to define boundaries
- Use Quart easing for all transitions
- Use glassmorphism for floating elements
- Use the signature gradient sparingly for high-intent CTAs

### ❌ Don't

- Don't use pure white (#FFFFFF) for text
- Don't use 1px borders for sectioning
- Don't use "Card in Card" layouts with borders
- Don't use standard easing functions
- Don't use neutral grey shadows
- Don't clutter the interface with unnecessary elements
- Don't use generic drop shadows

---

## Next Steps for Implementation

1. **Extract Design Tokens:** Create `lib/design-tokens.ts` with all color, spacing, and typography values
2. **Configure Tailwind:** Update `tailwind.config.ts` with custom theme
3. **Create Animation Presets:** Implement `lib/animation-presets.ts` with framer-motion variants
4. **Build Component Library:** Start with atomic components (buttons, inputs, badges)
5. **Implement Layouts:** Create AppShell, Sidebar, Header components
6. **Build Feature Components:** Implement screen-specific components
7. **Add Interactions:** Implement hover states, animations, and transitions
8. **Test Responsiveness:** Ensure all components work across breakpoints
9. **Accessibility:** Ensure WCAG compliance with proper contrast and focus states
10. **Performance:** Optimize animations for 60fps

---

**Document Version:** 1.0  
**Last Updated:** April 16, 2026  
**Maintained By:** Development Team
