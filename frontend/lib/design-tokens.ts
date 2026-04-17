/**
 * Design Tokens for RepoMind Assistant
 * Extracted from Stitch Design System: "The Obsidian Intelligence" Framework
 * 
 * Creative North Star: The Monolithic Curator
 * 
 * @see frontend/DESIGN_REFERENCE.md for complete design documentation
 */

export const repoMindTokens = {
  /**
   * Color System
   * Built on "Deep Charcoal" foundations with violet and indigo pulses
   */
  colors: {
    // Primary Colors (Electric Indigo)
    primary: {
      DEFAULT: '#a3a6ff',
      container: '#9396ff',
      dim: '#6063ee',
      fixed: '#9396ff',
      fixedDim: '#8387ff',
      onPrimary: '#0f00a4',
      onContainer: '#0a0081',
      onFixed: '#000000',
      onFixedVariant: '#0e009d',
    },

    // Secondary Colors (Violet)
    secondary: {
      DEFAULT: '#ac8aff',
      container: '#5516be',
      dim: '#8455ef',
      fixed: '#dac9ff',
      fixedDim: '#ceb9ff',
      onSecondary: '#280067',
      onContainer: '#d9c8ff',
      onFixed: '#40009b',
      onFixedVariant: '#5f28c8',
    },

    // Tertiary Colors (Emerald/Success)
    tertiary: {
      DEFAULT: '#9bffce',
      container: '#69f6b8',
      dim: '#58e7ab',
      fixed: '#69f6b8',
      fixedDim: '#58e7ab',
      onTertiary: '#006443',
      onContainer: '#005a3c',
      onFixed: '#00452d',
      onFixedVariant: '#006544',
    },

    // Error Colors
    error: {
      DEFAULT: '#ff6e84',
      container: '#a70138',
      dim: '#d73357',
      onError: '#490013',
      onContainer: '#ffb2b9',
    },

    // Surface Hierarchy (The "No-Line" Rule)
    // Use background color shifts instead of borders
    surface: {
      DEFAULT: '#0e0e10',              // Base layer - absolute foundation
      bright: '#2c2c2f',               // Elements that "pop" toward user
      dim: '#0e0e10',                  // Dim surfaces
      container: '#19191c',            // Standard interactive surface
      containerHigh: '#1f1f22',        // Elevated cards
      containerHighest: '#262528',     // Floating elements (modals, popovers)
      containerLow: '#131315',         // Secondary navigation, side panels
      containerLowest: '#000000',      // Code blocks, recessed elements (true black)
      variant: '#262528',              // Surface variant
      tint: '#a3a6ff',                 // Surface tint
    },

    // Background
    background: {
      DEFAULT: '#0e0e10',
      onBackground: '#f9f5f8',
    },

    // Text Colors
    // CRITICAL: Never use pure white (#FFFFFF)
    text: {
      primary: '#f9f5f8',              // on-surface - primary text
      secondary: '#adaaad',            // on-surface-variant - secondary text
      tertiary: '#767577',             // outline - placeholder text
      inverse: '#565557',              // inverse-on-surface
    },

    // Outline/Borders
    // Use sparingly - prefer background color shifts
    outline: {
      DEFAULT: '#767577',
      variant: '#48474a',              // Ghost borders at 15% opacity
    },

    // Inverse Colors
    inverse: {
      surface: '#fcf8fb',
      onSurface: '#565557',
      primary: '#494bd7',
    },
  },

  /**
   * Typography System
   * UI: Inter (Precision and clarity)
   * Code: JetBrains Mono (Technical authority)
   */
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
    },

    // Display (Hero/Empty States)
    display: {
      lg: {
        fontSize: '3.5rem',            // 56px
        lineHeight: '1.1',
        fontWeight: '600',
        letterSpacing: '-0.02em',
      },
      md: {
        fontSize: '2.8rem',            // 45px
        lineHeight: '1.15',
        fontWeight: '600',
        letterSpacing: '-0.02em',
      },
      sm: {
        fontSize: '2.25rem',           // 36px
        lineHeight: '1.2',
        fontWeight: '600',
        letterSpacing: '-0.02em',
      },
    },

    // Headlines (Page Titles)
    headline: {
      lg: {
        fontSize: '2rem',              // 32px
        lineHeight: '1.25',
        fontWeight: '600',
      },
      md: {
        fontSize: '1.75rem',           // 28px
        lineHeight: '1.3',
        fontWeight: '600',
      },
      sm: {
        fontSize: '1.5rem',            // 24px
        lineHeight: '1.35',
        fontWeight: '600',
      },
    },

    // Titles (Section Headers)
    title: {
      lg: {
        fontSize: '1.375rem',          // 22px
        lineHeight: '1.4',
        fontWeight: '500',
      },
      md: {
        fontSize: '1.125rem',          // 18px
        lineHeight: '1.45',
        fontWeight: '500',
      },
      sm: {
        fontSize: '1rem',              // 16px
        lineHeight: '1.5',
        fontWeight: '600',
      },
    },

    // Body (Content)
    body: {
      lg: {
        fontSize: '1rem',              // 16px
        lineHeight: '1.6',
        fontWeight: '400',
      },
      md: {
        fontSize: '0.875rem',          // 14px - The workhorse
        lineHeight: '1.5',
        fontWeight: '400',
      },
      sm: {
        fontSize: '0.8125rem',         // 13px
        lineHeight: '1.45',
        fontWeight: '400',
      },
    },

    // Labels (Metadata/Tags)
    label: {
      lg: {
        fontSize: '0.875rem',          // 14px
        lineHeight: '1.4',
        fontWeight: '500',
      },
      md: {
        fontSize: '0.75rem',           // 12px
        lineHeight: '1.35',
        fontWeight: '500',
      },
      sm: {
        fontSize: '0.6875rem',         // 11px
        lineHeight: '1.3',
        fontWeight: '500',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.05em',
      },
    },
  },

  /**
   * Spacing System
   * Based on 4px grid (spacingScale: 3)
   * CRITICAL: Every margin must be a multiple of 4
   */
  spacing: {
    0: '0',
    xs: '0.25rem',                     // 4px
    sm: '0.5rem',                      // 8px
    md: '1rem',                        // 16px
    lg: '1.5rem',                      // 24px
    xl: '2rem',                        // 32px
    '2xl': '3rem',                     // 48px
    '3xl': '4rem',                     // 64px
    '4xl': '6rem',                     // 96px
    '5xl': '8rem',                     // 128px
    '6xl': '12rem',                    // 192px
  },

  /**
   * Border Radius
   * Roundness: ROUND_FOUR (0.375rem / 6px)
   */
  borderRadius: {
    none: '0',
    sm: '0.25rem',                     // 4px
    md: '0.375rem',                    // 6px - Primary roundness
    lg: '0.5rem',                      // 8px
    xl: '0.75rem',                     // 12px
    '2xl': '1rem',                     // 16px
    '3xl': '1.5rem',                   // 24px
    full: '9999px',
  },

  /**
   * Shadows
   * Use sparingly - prefer tonal layering
   */
  shadows: {
    // Ambient shadows for floating elements
    float: '0 20px 40px rgba(0, 0, 0, 0.4)',
    floatViolet: '0 20px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(163, 166, 255, 0.05)',
    
    // Subtle shadows
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    
    // Glow effects
    primaryGlow: '0 0 0 4px rgba(163, 166, 255, 0.1)',
    secondaryGlow: '0 0 0 4px rgba(172, 138, 255, 0.1)',
  },

  /**
   * Gradients
   * Use sparingly for high-intent CTAs
   */
  gradients: {
    // Signature Pulse (Primary to Secondary)
    signaturePulse: 'linear-gradient(135deg, #a3a6ff 0%, #ac8aff 100%)',
    
    // Primary gradient
    primary: 'linear-gradient(135deg, #6063ee 0%, #a3a6ff 100%)',
    
    // Secondary gradient
    secondary: 'linear-gradient(135deg, #8455ef 0%, #ac8aff 100%)',
    
    // Tertiary gradient
    tertiary: 'linear-gradient(135deg, #58e7ab 0%, #9bffce 100%)',
  },

  /**
   * Glassmorphism
   * For floating elements (modals, command palettes, tooltips)
   */
  glass: {
    background: 'rgba(25, 25, 28, 0.7)',  // surface-container at 70%
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(72, 71, 74, 0.15)', // outline-variant at 15%
  },

  /**
   * Animation
   * Quart easing for high-end, responsive "snap"
   */
  animation: {
    // Easing function
    easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
    
    // Durations
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
      slower: '400ms',
    },
    
    // Stagger delay
    stagger: '50ms',
  },

  /**
   * Icons
   * Lucide Icons with specific sizing
   */
  icons: {
    size: {
      sm: '16px',                      // UI actions
      md: '20px',                      // Section headers
      lg: '24px',
    },
    strokeWidth: '1.5px',              // Refined look
  },

  /**
   * Code Syntax Highlighting
   * For code blocks and snippets
   */
  syntax: {
    string: '#9bffce',                 // tertiary
    keyword: '#d73357',                // error_dim
    function: '#a3a6ff',               // primary
    comment: '#767577',                // outline
    variable: '#f9f5f8',               // on-surface
    number: '#8387ff',                 // primary_fixed_dim
    operator: '#adaaad',               // on-surface-variant
    background: '#000000',             // surface-container-lowest
  },

  /**
   * Breakpoints
   * Responsive design breakpoints
   */
  breakpoints: {
    mobile: '390px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px',
    ultrawide: '1920px',
  },
} as const;

/**
 * Type exports for TypeScript
 */
export type RepoMindTokens = typeof repoMindTokens;
export type ColorToken = keyof typeof repoMindTokens.colors;
export type SpacingToken = keyof typeof repoMindTokens.spacing;
export type TypographyToken = keyof typeof repoMindTokens.typography;

/**
 * Helper function to get color with opacity
 */
export function withOpacity(color: string, opacity: number): string {
  // Convert hex to rgba
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Helper function to apply glassmorphism
 */
export function applyGlass(opacity: number = 0.7) {
  return {
    background: withOpacity('#19191c', opacity),
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    border: `1px solid ${withOpacity('#48474a', 0.15)}`,
  };
}
