/**
 * Design Tokens: RepoMind Assistant - "Obsidian Intelligence" Framework
 * 
 * Extracted from Stitch Design System
 * Project: RepoMind Assistant (projects/607025827578097506)
 * Creative North Star: The Monolithic Curator
 * 
 * Philosophy:
 * - High-performance terminal housed within a premium editorial shell
 * - Vast, intentional negative space with razor-sharp typography
 * - Physical depth through light physics, not structural lines
 * - Intentional asymmetry with nested glass containers
 */

export const designTokens = {
  /**
   * Color System
   * Built on "Deep Charcoal" foundations with violet and indigo pulses
   */
  colors: {
    // Background & Surface Hierarchy (Obsidian Sheets)
    background: '#0e0e10',           // Base layer - the absolute foundation
    
    surface: {
      DEFAULT: '#0e0e10',            // Surface base
      dim: '#0e0e10',                // Dimmed surface
      bright: '#2c2c2f',             // Brightened surface (for "pop" effect)
      container: {
        DEFAULT: '#19191c',          // Interactive cards - standard surface
        low: '#131315',              // Secondary navigation, side panels
        high: '#1f1f22',             // Elevated surfaces
        highest: '#262528',          // Floating elements (modals, popovers)
        lowest: '#000000',           // True black - for code blocks, recessed areas
      },
      variant: '#262528',            // Surface variant
      tint: '#a3a6ff',               // Surface tint (primary color)
    },

    // Primary Colors (Electric Indigo)
    primary: {
      DEFAULT: '#a3a6ff',            // Primary accent
      container: '#9396ff',          // Primary container
      dim: '#6063ee',                // Dimmed primary (for subtle states)
      fixed: '#9396ff',              // Fixed primary
      'fixed-dim': '#8387ff',        // Fixed dimmed primary
    },

    // Secondary Colors (Violet)
    secondary: {
      DEFAULT: '#ac8aff',            // Secondary accent
      container: '#5516be',          // Secondary container
      dim: '#8455ef',                // Dimmed secondary
      fixed: '#dac9ff',              // Fixed secondary
      'fixed-dim': '#ceb9ff',        // Fixed dimmed secondary
    },

    // Tertiary Colors (Emerald/Success)
    tertiary: {
      DEFAULT: '#9bffce',            // Tertiary accent (emerald)
      container: '#69f6b8',          // Tertiary container
      dim: '#58e7ab',                // Dimmed tertiary
      fixed: '#69f6b8',              // Fixed tertiary
      'fixed-dim': '#58e7ab',        // Fixed dimmed tertiary
    },

    // Semantic Colors
    error: {
      DEFAULT: '#ff6e84',            // Error state
      container: '#a70138',          // Error container
      dim: '#d73357',                // Dimmed error
    },

    // Text Colors (On-Surface)
    text: {
      primary: '#f9f5f8',            // Primary text (on-surface) - NOT pure white
      secondary: '#adaaad',          // Secondary text (on-surface-variant)
      tertiary: '#767577',           // Tertiary text (outline)
      disabled: '#48474a',           // Disabled text (outline-variant)
    },

    // Border & Outline Colors
    outline: {
      DEFAULT: '#767577',            // Standard outline
      variant: '#48474a',            // Outline variant (for ghost borders at 15% opacity)
    },

    // Inverse Colors (for light-on-dark scenarios)
    inverse: {
      surface: '#fcf8fb',
      'on-surface': '#565557',
      primary: '#494bd7',
    },

    // On-Color Text (text that appears on colored backgrounds)
    on: {
      background: '#f9f5f8',
      surface: '#f9f5f8',
      'surface-variant': '#adaaad',
      primary: '#0f00a4',            // Text on primary (dark navy/black)
      'primary-container': '#0a0081',
      'primary-fixed': '#000000',
      'primary-fixed-variant': '#0e009d',
      secondary: '#280067',
      'secondary-container': '#d9c8ff',
      'secondary-fixed': '#40009b',
      'secondary-fixed-variant': '#5f28c8',
      tertiary: '#006443',
      'tertiary-container': '#005a3c',
      'tertiary-fixed': '#00452d',
      'tertiary-fixed-variant': '#006544',
      error: '#490013',
      'error-container': '#ffb2b9',
    },
  },

  /**
   * Spacing System
   * Based on 4px grid (spacingScale: 3 from Stitch)
   * Every margin must be a multiple of 4
   */
  spacing: {
    0: '0',
    1: '0.25rem',      // 4px
    2: '0.5rem',       // 8px
    3: '0.75rem',      // 12px
    4: '1rem',         // 16px
    5: '1.25rem',      // 20px
    6: '1.5rem',       // 24px - minimum separation between items
    8: '2rem',         // 32px - standard separation
    10: '2.5rem',      // 40px
    12: '3rem',        // 48px
    16: '4rem',        // 64px - extreme whitespace for editorial feel
    20: '5rem',        // 80px
    24: '6rem',        // 96px
    32: '8rem',        // 128px
  },

  /**
   * Typography System
   * UI: Inter (precision and clarity)
   * Code: JetBrains Mono (technical authority)
   */
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', 'monospace'],
    },
    
    fontSize: {
      // Display (for empty states and hero headings)
      'display-lg': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '600' }],  // 56px
      'display-md': ['2.875rem', { lineHeight: '1.15', letterSpacing: '-0.02em', fontWeight: '600' }], // 46px
      'display-sm': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '600' }],   // 36px
      
      // Headline (primary page titles)
      'headline-lg': ['2rem', { lineHeight: '1.25', letterSpacing: '0', fontWeight: '600' }],      // 32px
      'headline-md': ['1.75rem', { lineHeight: '1.3', letterSpacing: '0', fontWeight: '600' }],    // 28px
      'headline-sm': ['1.5rem', { lineHeight: '1.35', letterSpacing: '0', fontWeight: '600' }],    // 24px
      
      // Title (section headers)
      'title-lg': ['1.375rem', { lineHeight: '1.4', letterSpacing: '0', fontWeight: '500' }],      // 22px
      'title-md': ['1.125rem', { lineHeight: '1.45', letterSpacing: '0', fontWeight: '500' }],     // 18px
      'title-sm': ['1rem', { lineHeight: '1.5', letterSpacing: '0', fontWeight: '500' }],          // 16px
      
      // Body (workhorse text)
      'body-lg': ['1rem', { lineHeight: '1.6', letterSpacing: '0', fontWeight: '400' }],           // 16px
      'body-md': ['0.875rem', { lineHeight: '1.6', letterSpacing: '0', fontWeight: '400' }],       // 14px
      'body-sm': ['0.75rem', { lineHeight: '1.65', letterSpacing: '0', fontWeight: '400' }],       // 12px
      
      // Label (metadata and tags)
      'label-lg': ['0.875rem', { lineHeight: '1.4', letterSpacing: '0.01em', fontWeight: '500' }], // 14px
      'label-md': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.05em', fontWeight: '500' }],  // 12px
      'label-sm': ['0.6875rem', { lineHeight: '1.4', letterSpacing: '0.1em', fontWeight: '500' }], // 11px - all-caps
    },

    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },

    letterSpacing: {
      tighter: '-0.02em',
      tight: '-0.01em',
      normal: '0',
      wide: '0.01em',
      wider: '0.05em',
      widest: '0.1em',
    },

    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.6',
      loose: '1.75',
    },
  },

  /**
   * Border Radius
   * Roundness: ROUND_FOUR from Stitch (0.375rem base)
   */
  borderRadius: {
    none: '0',
    sm: '0.25rem',       // 4px
    md: '0.375rem',      // 6px - standard button roundness
    lg: '0.5rem',        // 8px
    xl: '0.75rem',       // 12px
    '2xl': '1rem',       // 16px
    '3xl': '1.5rem',     // 24px
    full: '9999px',      // Fully rounded
  },

  /**
   * Shadows
   * Ambient shadows with violet tinting for floating elements
   */
  shadows: {
    // No shadows for standard elements - use tonal layering instead
    none: 'none',
    
    // Ambient shadows for floating elements (modals, popovers)
    float: '0 20px 40px rgba(0, 0, 0, 0.4)',
    'float-lg': '0 24px 48px rgba(0, 0, 0, 0.5)',
    
    // Ghost border (for accessibility fallback)
    ghost: '0 0 0 1px rgba(72, 71, 74, 0.15)', // outline-variant at 15% opacity
    
    // Focus glow (for input fields)
    'focus-glow': '0 0 0 4px rgba(163, 166, 255, 0.1)', // primary at 10% opacity
  },

  /**
   * Backdrop Blur (for glassmorphism)
   */
  backdropBlur: {
    glass: '12px',       // Standard glass effect
    'glass-lg': '20px',  // Enhanced glass effect
  },

  /**
   * Transitions & Animations
   * Use Quart easing for high-end, responsive "snap"
   */
  transitions: {
    easing: {
      quart: 'cubic-bezier(0.16, 1, 0.3, 1)',      // High-end snap
      standard: 'cubic-bezier(0.4, 0, 0.2, 1)',    // Material standard
      decelerate: 'cubic-bezier(0, 0, 0.2, 1)',    // Deceleration
      accelerate: 'cubic-bezier(0.4, 0, 1, 1)',    // Acceleration
    },
    duration: {
      fast: '150ms',
      normal: '250ms',
      slow: '350ms',
    },
  },

  /**
   * Z-Index Scale
   */
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    'modal-backdrop': 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
  },

  /**
   * Icon Sizes
   * Lucide icons at 16px for UI actions, 20px for section headers
   */
  iconSize: {
    sm: '16px',          // UI actions
    md: '20px',          // Section headers
    lg: '24px',          // Large icons
    xl: '32px',          // Extra large icons
  },

  /**
   * Glassmorphism Presets
   */
  glass: {
    // Navigation bars and floating panels
    navigation: {
      background: 'rgba(25, 25, 28, 0.7)',  // surface-container at 70%
      backdropFilter: 'blur(12px)',
    },
    // Modals and overlays
    modal: {
      background: 'rgba(38, 37, 40, 0.8)',  // surface-container-highest at 80%
      backdropFilter: 'blur(20px)',
    },
  },

  /**
   * Gradient Presets
   * Signature gradient: primary to secondary (Electric Indigo to Violet)
   * Use sparingly for high-intent CTAs and data-vis highlights
   */
  gradients: {
    primary: 'linear-gradient(135deg, #a3a6ff 0%, #ac8aff 100%)',
    'primary-subtle': 'linear-gradient(135deg, #6063ee 0%, #8455ef 100%)',
  },
} as const;

export type DesignTokens = typeof designTokens;
