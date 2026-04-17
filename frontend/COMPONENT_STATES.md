# Component States Documentation

This document details the various states for all components in the RepoMind Assistant design system, extracted from the Stitch design.

---

## Button States

### Primary Button

#### Default
- Background: Gradient (`primary` to `secondary`)
- Text: `on-primary` (#0f00a4)
- Border: None
- Border Radius: `md` (6px)

#### Hover
- Background: Slightly shifted gradient
- Transform: `scale(1.02)`
- Cursor: pointer
- Transition: 150ms with Quart easing

#### Active/Pressed
- Transform: `scale(0.98)`
- Background: Darker gradient
- Transition: 150ms with Quart easing

#### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px
- Glow: `0 0 0 4px rgba(163, 166, 255, 0.1)`

#### Disabled
- Opacity: 0.5
- Cursor: not-allowed
- No hover effects
- Background: Desaturated gradient

#### Loading
- Spinner icon in `on-primary` color
- Text: "Loading..." or hidden
- Disabled state applied
- Spinner animation: 1s linear infinite

---

## Secondary Button

#### Default
- Background: `surface-bright` (#2c2c2f)
- Text: `on-surface` (#f9f5f8)
- Border: Ghost border (`outline-variant` at 15% opacity)
- Border Radius: `md` (6px)

#### Hover
- Background: `surface-container-high` (#1f1f22)
- Transform: `scale(1.02)`
- Border opacity: 20%

#### Active/Pressed
- Transform: `scale(0.98)`
- Background: `surface-container` (#19191c)

#### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

#### Disabled
- Opacity: 0.5
- Cursor: not-allowed
- No hover effects

---

## Tertiary Button (Text Button)

#### Default
- Background: Transparent
- Text: `on-surface-variant` (#adaaad)
- Border: None

#### Hover
- Text: `on-surface` (#f9f5f8)
- Background: `surface-container-low` (#131315)
- Border Radius: `md` (6px)

#### Active/Pressed
- Transform: `scale(0.98)`
- Background: `surface-container` (#19191c)

#### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

#### Disabled
- Opacity: 0.5
- Cursor: not-allowed

---

## Input Field States

### Text Input

#### Default
- Background: `surface-container-low` (#131315)
- Border: None
- Text: `on-surface` (#f9f5f8)
- Placeholder: `outline` (#767577)
- Padding: 12px 16px
- Border Radius: `md` (6px)

#### Hover
- Background: `surface-container` (#19191c)

#### Focus
- Border: 1px `primary-dim` (#6063ee)
- Glow: `0 0 0 4px rgba(163, 166, 255, 0.1)`
- Background: `surface-container` (#19191c)

#### Filled
- Text: `on-surface` (#f9f5f8)
- Background: `surface-container-low` (#131315)

#### Error
- Border: 1px `error` (#ff6e84)
- Glow: `0 0 0 4px rgba(255, 110, 132, 0.1)`
- Helper text: `error` color

#### Disabled
- Opacity: 0.5
- Cursor: not-allowed
- Background: `surface-dim` (#0e0e10)

---

## Card States

### Interactive Card

#### Default
- Background: `surface-container` (#19191c)
- Border: None (use background color shift)
- Border Radius: `lg` (8px)
- Padding: 24px

#### Hover
- Background: `surface-container-high` (#1f1f22)
- Transform: `translateY(-2px)`
- Shadow: `0 4px 12px rgba(0, 0, 0, 0.2)`
- Cursor: pointer

#### Active/Selected
- Background: `surface-container-high` (#1f1f22)
- Left border: 2px `primary` (#a3a6ff)
- Padding-left: 22px (to compensate for border)

#### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

#### Loading
- Skeleton pulse animation
- Opacity: 0.7

---

## List Item States

### Default
- Background: Transparent
- Padding: 12px 16px
- Border: None

### Hover
- Background: `surface-container-high` (#1f1f22)
- Cursor: pointer

### Active/Selected
- Background: `surface-container-high` (#1f1f22)
- Left accent: 2px `primary` (#a3a6ff)

### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: -2px (inside)

---

## Badge/Chip States

### Default
- Background: `surface-variant` (#262528)
- Text: `on-surface` (#f9f5f8)
- Border Radius: `full` (9999px)
- Padding: 4px 12px
- Font: `label-sm`

### Hover (if interactive)
- Background: `surface-container-highest` (#262528)
- Transform: `scale(1.05)`

### Active/Selected
- Background: `primary-container` (#9396ff)
- Text: `on-primary` (#0f00a4)

### Status Variants

#### Success
- Background: `tertiary-container` (#69f6b8)
- Text: `on-tertiary` (#006443)

#### Warning
- Background: `#f59e0b` at 20% opacity
- Text: `#f59e0b`

#### Error
- Background: `error-container` (#a70138)
- Text: `on-error-container` (#ffb2b9)

#### Info
- Background: `primary-container` (#9396ff)
- Text: `on-primary-container` (#0a0081)

---

## Modal States

### Backdrop
- Background: `rgba(0, 0, 0, 0.6)`
- Backdrop filter: `blur(4px)`

### Modal Container

#### Default
- Background: `surface-container-highest` (#262528)
- Border Radius: `xl` (12px)
- Shadow: `0 20px 40px rgba(0, 0, 0, 0.4)`
- Max-width: 600px
- Padding: 32px

#### Glassmorphism Variant
- Background: `rgba(25, 25, 28, 0.7)`
- Backdrop filter: `blur(12px)`
- Border: `1px solid rgba(72, 71, 74, 0.15)`

---

## Tooltip States

### Default
- Background: `surface-container-highest` (#262528)
- Text: `on-surface` (#f9f5f8)
- Border Radius: `md` (6px)
- Padding: 8px 12px
- Font: `body-sm`
- Shadow: `0 4px 12px rgba(0, 0, 0, 0.3)`
- Max-width: 250px

### Arrow
- Color: `surface-container-highest` (#262528)
- Size: 6px

---

## Dropdown Menu States

### Menu Container
- Background: `surface-container-highest` (#262528)
- Border Radius: `lg` (8px)
- Shadow: `0 8px 24px rgba(0, 0, 0, 0.3)`
- Padding: 8px
- Min-width: 200px

### Menu Item

#### Default
- Background: Transparent
- Text: `on-surface` (#f9f5f8)
- Padding: 10px 12px
- Border Radius: `md` (6px)

#### Hover
- Background: `surface-container-high` (#1f1f22)
- Cursor: pointer

#### Active/Selected
- Background: `surface-container-high` (#1f1f22)
- Text: `primary` (#a3a6ff)
- Icon: `primary` (#a3a6ff)

#### Disabled
- Opacity: 0.5
- Cursor: not-allowed

---

## Toggle/Switch States

### Default (Off)
- Track background: `surface-container-high` (#1f1f22)
- Thumb background: `outline` (#767577)
- Width: 44px
- Height: 24px
- Border Radius: `full`

### On
- Track background: `primary` (#a3a6ff)
- Thumb background: `on-primary` (#0f00a4)

### Hover
- Track opacity: 0.9

### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

### Disabled
- Opacity: 0.5
- Cursor: not-allowed

---

## Checkbox States

### Default (Unchecked)
- Background: `surface-container-low` (#131315)
- Border: 2px `outline-variant` (#48474a)
- Size: 20px
- Border Radius: `sm` (4px)

### Checked
- Background: `primary` (#a3a6ff)
- Border: 2px `primary` (#a3a6ff)
- Checkmark: `on-primary` (#0f00a4)

### Hover
- Border color: `primary-dim` (#6063ee)

### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

### Disabled
- Opacity: 0.5
- Cursor: not-allowed

### Indeterminate
- Background: `primary` (#a3a6ff)
- Icon: Minus sign in `on-primary` (#0f00a4)

---

## Radio Button States

### Default (Unselected)
- Background: `surface-container-low` (#131315)
- Border: 2px `outline-variant` (#48474a)
- Size: 20px
- Border Radius: `full`

### Selected
- Background: `surface-container-low` (#131315)
- Border: 2px `primary` (#a3a6ff)
- Inner dot: 10px `primary` (#a3a6ff)

### Hover
- Border color: `primary-dim` (#6063ee)

### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: 2px

### Disabled
- Opacity: 0.5
- Cursor: not-allowed

---

## Progress Bar States

### Default
- Track background: `surface-container-high` (#1f1f22)
- Fill background: Gradient (`primary` to `secondary`)
- Height: 8px
- Border Radius: `full`

### Indeterminate
- Animated gradient moving left to right
- Animation: 1.5s ease-in-out infinite

---

## Skeleton Loader States

### Default
- Background: `surface-container-low` (#131315)
- Border Radius: Matches target component
- Animation: Pulse (opacity 0.5 → 0.8 → 0.5)
- Duration: 1.5s infinite

---

## Code Block States

### Default
- Background: `surface-container-lowest` (#000000)
- Border Radius: `md` (6px)
- Padding: 16px
- Font: JetBrains Mono
- Font size: `body-md` (14px)

### With Line Numbers
- Line numbers: `outline` (#767577)
- Line number padding: 8px
- Line number width: 40px
- Line number alignment: right

### Highlighted Line
- Background: `primary` at 5% opacity
- Left border: 2px `primary` (#a3a6ff)

### Copy Button

#### Default
- Position: Absolute top-right
- Background: `surface-container-high` (#1f1f22)
- Icon: `on-surface-variant` (#adaaad)
- Padding: 8px
- Border Radius: `md` (6px)
- Opacity: 0 (hidden)

#### Hover (on code block)
- Opacity: 1

#### Clicked
- Icon: Check mark
- Icon color: `tertiary` (#9bffce)
- Duration: 2s then revert

---

## Chat Message States

### User Message

#### Default
- Background: `primary-container` (#9396ff)
- Text: `on-primary` (#0f00a4)
- Border Radius: `lg` (8px) with bottom-right `sm` (4px)
- Padding: 12px 16px
- Max-width: 70%
- Align: Right

### Assistant Message

#### Default
- Background: `surface-container` (#19191c)
- Text: `on-surface` (#f9f5f8)
- Border Radius: `lg` (8px) with bottom-left `sm` (4px)
- Padding: 12px 16px
- Max-width: 80%
- Align: Left

#### Loading
- Typing indicator: 3 dots pulsing
- Dot color: `on-surface-variant` (#adaaad)
- Animation: Sequential pulse

---

## Search Result States

### Default
- Background: `surface-container` (#19191c)
- Border: None
- Border Radius: `lg` (8px)
- Padding: 16px

### Hover
- Background: `surface-container-high` (#1f1f22)
- Transform: `translateY(-2px)`
- Shadow: `0 4px 12px rgba(0, 0, 0, 0.2)`
- Cursor: pointer

### Active/Selected
- Background: `surface-container-high` (#1f1f22)
- Left border: 2px `primary` (#a3a6ff)

---

## File Tree Node States

### Default
- Background: Transparent
- Text: `on-surface` (#f9f5f8)
- Padding: 8px 12px

### Hover
- Background: `surface-container-high` (#1f1f22)
- Cursor: pointer

### Expanded
- Icon: Chevron down
- Children visible

### Collapsed
- Icon: Chevron right
- Children hidden

### Selected
- Background: `surface-container-high` (#1f1f22)
- Text: `primary` (#a3a6ff)
- Icon: `primary` (#a3a6ff)

---

## Tab States

### Default (Inactive)
- Background: Transparent
- Text: `on-surface-variant` (#adaaad)
- Border-bottom: 2px transparent
- Padding: 12px 16px

### Hover
- Text: `on-surface` (#f9f5f8)

### Active
- Text: `primary` (#a3a6ff)
- Border-bottom: 2px `primary` (#a3a6ff)

### Focus
- Outline: 2px `primary` at 50% opacity
- Outline offset: -2px

### Disabled
- Opacity: 0.5
- Cursor: not-allowed

---

## Loading Spinner States

### Default
- Color: `primary` (#a3a6ff)
- Size: 24px
- Stroke width: 2px
- Animation: Spin 1s linear infinite

### Small
- Size: 16px
- Stroke width: 2px

### Large
- Size: 48px
- Stroke width: 3px

---

## Empty State

### Default
- Icon: 64px in `on-surface-variant` (#adaaad)
- Title: `headline-sm` in `on-surface` (#f9f5f8)
- Description: `body-md` in `on-surface-variant` (#adaaad)
- CTA Button: Primary button
- Spacing: 24px between elements

---

## Error State

### Default
- Icon: 48px in `error` (#ff6e84)
- Title: `headline-sm` in `on-surface` (#f9f5f8)
- Description: `body-md` in `on-surface-variant` (#adaaad)
- Error message: `body-sm` in `error` (#ff6e84)
- Retry button: Secondary button
- Spacing: 16px between elements

---

## Success State

### Default
- Icon: 48px in `tertiary` (#9bffce)
- Title: `headline-sm` in `on-surface` (#f9f5f8)
- Description: `body-md` in `on-surface-variant` (#adaaad)
- CTA Button: Primary button
- Spacing: 16px between elements

---

**Document Version:** 1.0  
**Last Updated:** April 16, 2026
