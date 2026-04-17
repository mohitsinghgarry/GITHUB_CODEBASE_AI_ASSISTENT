/**
 * Tailwind CSS Configuration
 * RepoMind Assistant - "Obsidian Intelligence" Framework
 * 
 * Design Philosophy:
 * - High-performance terminal housed within a premium editorial shell
 * - Vast, intentional negative space with razor-sharp typography
 * - Physical depth through light physics, not structural lines
 * - No-Line Rule: Borders prohibited for sectioning (use background color shifts)
 * - Quart easing for high-end, responsive "snap"
 */

import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    // Responsive breakpoints
    screens: {
      'xs': '320px',   // Small mobile
      'sm': '640px',   // Large mobile
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px',  // Large desktop
      '2xl': '1536px', // Extra large
    },
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',    // 16px on mobile
        sm: '1.5rem',       // 24px on large mobile
        md: '2rem',         // 32px on tablet
        lg: '2.5rem',       // 40px on desktop
        xl: '3rem',         // 48px on large desktop
        '2xl': '4rem',      // 64px on extra large
      },
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      /**
       * Colors - RepoMind Assistant Design System
       * Based on "Deep Charcoal" foundations with violet and indigo pulses
       * Light mode uses soft whites with muted violet accents
       */
      colors: {
        // Background & Surface Hierarchy (Obsidian Sheets)
        background: '#0e0e10',
        
        // Primary Colors (Electric Indigo)
        primary: {
          DEFAULT: '#a3a6ff',
          container: '#9396ff',
          dim: '#6063ee',
          fixed: '#9396ff',
          'fixed-dim': '#8387ff',
          foreground: '#0f00a4',
          // Light mode variants
          light: '#494bd7',
          'light-container': '#e0e1ff',
          'light-foreground': '#f9f5f8',
        },
        
        // Secondary Colors (Violet)
        secondary: {
          DEFAULT: '#ac8aff',
          container: '#5516be',
          dim: '#8455ef',
          fixed: '#dac9ff',
          'fixed-dim': '#ceb9ff',
          foreground: '#f9f5f8',
          // Light mode variants
          light: '#5516be',
          'light-container': '#e8d9ff',
          'light-foreground': '#f9f5f8',
        },
        
        // Tertiary Colors (Emerald/Success)
        tertiary: {
          DEFAULT: '#9bffce',
          container: '#69f6b8',
          dim: '#58e7ab',
          fixed: '#69f6b8',
          'fixed-dim': '#58e7ab',
          foreground: '#006443',
          // Light mode variants
          light: '#00a86b',
          'light-container': '#c8f5e0',
          'light-foreground': '#f9f5f8',
        },
        
        // Error Colors
        error: {
          DEFAULT: '#ff6e84',
          container: '#a70138',
          dim: '#d73357',
          foreground: '#490013',
          // Light mode variants
          light: '#d73157',
          'light-container': '#ffd9e0',
          'light-foreground': '#f9f5f8',
        },
        
        // Surface Hierarchy (Tonal Layering)
        surface: {
          DEFAULT: '#0e0e10',              // Base layer (dark)
          'container-lowest': '#000000',   // True black - code blocks, recessed areas
          'container-low': '#131315',      // Secondary navigation, side panels
          container: '#19191c',            // Interactive cards - standard surface
          'container-high': '#1f1f22',     // Elevated surfaces
          'container-highest': '#262528',  // Floating elements (modals, popovers)
          bright: '#2c2c2f',               // Brightened surface (for "pop" effect)
          dim: '#0e0e10',                  // Dimmed surface
          variant: '#262528',              // Surface variant
          tint: '#a3a6ff',                 // Surface tint (primary color)
          // Light mode variants
          light: '#f9f5f8',                // Base layer (light)
          'light-container-lowest': '#e8e5e8',  // Lightest - code blocks
          'light-container-low': '#f0f0f2',     // Secondary navigation
          'light-container': '#ffffff',         // Interactive cards
          'light-container-high': '#ffffff',    // Elevated surfaces
          'light-container-highest': '#ffffff', // Floating elements
          'light-bright': '#ffffff',            // Brightened surface
          'light-dim': '#f0f0f2',               // Dimmed surface
          'light-variant': '#ebebee',           // Surface variant
          'light-tint': '#494bd7',              // Surface tint (primary color)
        },
        
        // Text Colors (On-Surface)
        'on-surface': {
          DEFAULT: '#f9f5f8',              // Primary text - NOT pure white (dark mode)
          variant: '#adaaad',              // Secondary text
          // Light mode variants
          light: '#0e0e10',                // Primary text (light mode)
          'light-variant': '#565557',      // Secondary text (light mode)
        },
        'on-background': '#f9f5f8',
        'on-primary': '#0f00a4',
        'on-secondary': '#280067',
        'on-tertiary': '#006443',
        'on-error': '#490013',
        
        // Border & Outline Colors
        outline: {
          DEFAULT: '#767577',              // Standard outline (dark mode)
          variant: '#48474a',              // Ghost borders at 15% opacity
          // Light mode variants
          light: '#adaaad',                // Standard outline (light mode)
          'light-variant': '#c8c7c9',      // Ghost borders (light mode)
        },
        
        // Inverse Colors
        inverse: {
          surface: '#fcf8fb',
          'on-surface': '#565557',
          primary: '#494bd7',
        },
        
        // Shadcn/ui compatibility (CSS variables)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        foreground: 'hsl(var(--foreground))',
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      
      /**
       * Typography
       * UI: Work Sans (modern, clean, professional)
       * Code: JetBrains Mono (technical authority)
       */
      fontFamily: {
        sans: ['"Work Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'Courier New', 'monospace'],
      },
      
      /**
       * Font Sizes with Line Heights and Letter Spacing
       */
      fontSize: {
        // Display (for empty states and hero headings)
        'display-lg': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '600' }],
        'display-md': ['2.875rem', { lineHeight: '1.15', letterSpacing: '-0.02em', fontWeight: '600' }],
        'display-sm': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '600' }],
        
        // Headline (primary page titles)
        'headline-lg': ['2rem', { lineHeight: '1.25', letterSpacing: '0', fontWeight: '600' }],
        'headline-md': ['1.75rem', { lineHeight: '1.3', letterSpacing: '0', fontWeight: '600' }],
        'headline-sm': ['1.5rem', { lineHeight: '1.35', letterSpacing: '0', fontWeight: '600' }],
        
        // Title (section headers)
        'title-lg': ['1.375rem', { lineHeight: '1.4', letterSpacing: '0', fontWeight: '500' }],
        'title-md': ['1.125rem', { lineHeight: '1.45', letterSpacing: '0', fontWeight: '500' }],
        'title-sm': ['1rem', { lineHeight: '1.5', letterSpacing: '0', fontWeight: '500' }],
        
        // Body (workhorse text)
        'body-lg': ['1rem', { lineHeight: '1.6', letterSpacing: '0', fontWeight: '400' }],
        'body-md': ['0.875rem', { lineHeight: '1.6', letterSpacing: '0', fontWeight: '400' }],
        'body-sm': ['0.75rem', { lineHeight: '1.65', letterSpacing: '0', fontWeight: '400' }],
        
        // Label (metadata and tags)
        'label-lg': ['0.875rem', { lineHeight: '1.4', letterSpacing: '0.01em', fontWeight: '500' }],
        'label-md': ['0.75rem', { lineHeight: '1.4', letterSpacing: '0.05em', fontWeight: '500' }],
        'label-sm': ['0.6875rem', { lineHeight: '1.4', letterSpacing: '0.1em', fontWeight: '500' }],
      },
      
      /**
       * Letter Spacing
       */
      letterSpacing: {
        tighter: '-0.02em',
        tight: '-0.01em',
        normal: '0',
        wide: '0.01em',
        wider: '0.05em',
        widest: '0.1em',
      },
      
      /**
       * Spacing System
       * Based on 4px grid - every margin must be a multiple of 4
       */
      spacing: {
        0: '0',
        1: '0.25rem',      // 4px
        2: '0.5rem',       // 8px
        3: '0.75rem',      // 12px
        4: '1rem',         // 16px
        5: '1.25rem',      // 20px
        6: '1.5rem',       // 24px - minimum separation
        8: '2rem',         // 32px - standard separation
        10: '2.5rem',      // 40px
        12: '3rem',        // 48px
        16: '4rem',        // 64px - extreme whitespace
        20: '5rem',        // 80px
        24: '6rem',        // 96px
        32: '8rem',        // 128px
      },
      
      /**
       * Border Radius
       * Roundness: ROUND_FOUR (0.375rem base)
       */
      borderRadius: {
        none: '0',
        sm: '0.25rem',     // 4px
        md: '0.375rem',    // 6px - standard button roundness
        lg: '0.5rem',      // 8px
        xl: '0.75rem',     // 12px
        '2xl': '1rem',     // 16px
        '3xl': '1.5rem',   // 24px
        full: '9999px',    // Fully rounded
      },
      
      /**
       * Box Shadows
       * Ambient shadows with violet tinting for floating elements
       */
      boxShadow: {
        none: 'none',
        // Ambient shadows for floating elements
        float: '0 20px 40px rgba(0, 0, 0, 0.4)',
        'float-lg': '0 24px 48px rgba(0, 0, 0, 0.5)',
        // Ghost border (for accessibility fallback)
        ghost: '0 0 0 1px rgba(72, 71, 74, 0.15)',
        // Focus glow (for input fields)
        'focus-glow': '0 0 0 4px rgba(163, 166, 255, 0.1)',
        // Standard shadows (lighter for dark mode)
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
      },
      
      /**
       * Backdrop Blur (for glassmorphism)
       */
      backdropBlur: {
        glass: '12px',       // Standard glass effect
        'glass-lg': '20px',  // Enhanced glass effect
      },
      
      /**
       * Transition Timing Functions
       * Quart easing for high-end, responsive "snap"
       */
      transitionTimingFunction: {
        quart: 'cubic-bezier(0.16, 1, 0.3, 1)',      // High-end snap (primary)
        standard: 'cubic-bezier(0.4, 0, 0.2, 1)',    // Material standard
        decelerate: 'cubic-bezier(0, 0, 0.2, 1)',    // Deceleration
        accelerate: 'cubic-bezier(0.4, 0, 1, 1)',    // Acceleration
      },
      
      /**
       * Transition Durations
       */
      transitionDuration: {
        fast: '150ms',
        normal: '250ms',
        slow: '350ms',
      },
      
      /**
       * Background Images (for gradients)
       */
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #a3a6ff 0%, #ac8aff 100%)',
        'gradient-primary-subtle': 'linear-gradient(135deg, #6063ee 0%, #8455ef 100%)',
      },
      
      /**
       * Keyframe Animations
       */
      keyframes: {
        // Accordion animations
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        // Shimmer animation (for skeleton loaders)
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        // Pulse animation
        pulse: {
          '0%, 100%': { opacity: '1', scale: '1' },
          '50%': { opacity: '0.8', scale: '1.05' },
        },
        // Fade in animations
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in-down': {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        // Slide animations
        'slide-in-left': {
          '0%': { transform: 'translateX(-100px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        // Scale animations
        'scale-in': {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      
      /**
       * Animations
       */
      animation: {
        'accordion-down': 'accordion-down 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'accordion-up': 'accordion-up 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        shimmer: 'shimmer 1.5s linear infinite',
        pulse: 'pulse 2s cubic-bezier(0.16, 1, 0.3, 1) infinite',
        'fade-in': 'fade-in 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in-up': 'fade-in-up 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in-down': 'fade-in-down 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-left': 'slide-in-left 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-right': 'slide-in-right 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in': 'scale-in 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
