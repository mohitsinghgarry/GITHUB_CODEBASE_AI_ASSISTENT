/**
 * Responsive Design Utilities
 * 
 * Helper functions and constants for responsive design implementation.
 */

/**
 * Breakpoint values in pixels
 */
export const BREAKPOINTS = {
  xs: 320,   // Small mobile
  sm: 640,   // Large mobile
  md: 768,   // Tablet
  lg: 1024,  // Desktop
  xl: 1280,  // Large desktop
  '2xl': 1536, // Extra large
} as const;

/**
 * Touch target minimum sizes (in pixels)
 */
export const TOUCH_TARGETS = {
  minimum: 44,      // Minimum touch target size
  comfortable: 48,  // Comfortable touch target size
  large: 56,        // Large touch target size
} as const;

/**
 * Responsive spacing scale
 */
export const RESPONSIVE_SPACING = {
  mobile: {
    xs: '0.25rem',  // 4px
    sm: '0.5rem',   // 8px
    md: '1rem',     // 16px
    lg: '1.5rem',   // 24px
    xl: '2rem',     // 32px
  },
  tablet: {
    xs: '0.25rem',  // 4px
    sm: '0.5rem',   // 8px
    md: '1.5rem',   // 24px
    lg: '2rem',     // 32px
    xl: '3rem',     // 48px
  },
  desktop: {
    xs: '0.5rem',   // 8px
    sm: '1rem',     // 16px
    md: '2rem',     // 32px
    lg: '3rem',     // 48px
    xl: '4rem',     // 64px
  },
} as const;

/**
 * Check if current viewport matches a breakpoint
 */
export function isBreakpoint(breakpoint: keyof typeof BREAKPOINTS): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth >= BREAKPOINTS[breakpoint];
}

/**
 * Get current breakpoint
 */
export function getCurrentBreakpoint(): keyof typeof BREAKPOINTS {
  if (typeof window === 'undefined') return 'lg';
  
  const width = window.innerWidth;
  
  if (width >= BREAKPOINTS['2xl']) return '2xl';
  if (width >= BREAKPOINTS.xl) return 'xl';
  if (width >= BREAKPOINTS.lg) return 'lg';
  if (width >= BREAKPOINTS.md) return 'md';
  if (width >= BREAKPOINTS.sm) return 'sm';
  return 'xs';
}

/**
 * Check if device is mobile (< 768px)
 */
export function isMobile(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth < BREAKPOINTS.md;
}

/**
 * Check if device is tablet (768px - 1024px)
 */
export function isTablet(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth >= BREAKPOINTS.md && window.innerWidth < BREAKPOINTS.lg;
}

/**
 * Check if device is desktop (>= 1024px)
 */
export function isDesktop(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth >= BREAKPOINTS.lg;
}

/**
 * Check if device supports touch
 */
export function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false;
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

/**
 * Get responsive value based on current breakpoint
 */
export function getResponsiveValue<T>(values: {
  mobile?: T;
  tablet?: T;
  desktop?: T;
  default: T;
}): T {
  if (typeof window === 'undefined') return values.default;
  
  if (isDesktop() && values.desktop !== undefined) {
    return values.desktop;
  }
  
  if (isTablet() && values.tablet !== undefined) {
    return values.tablet;
  }
  
  if (isMobile() && values.mobile !== undefined) {
    return values.mobile;
  }
  
  return values.default;
}

/**
 * Hook to track window size changes
 */
export function useWindowSize() {
  const [windowSize, setWindowSize] = React.useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  React.useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

/**
 * Hook to track current breakpoint
 */
export function useBreakpoint() {
  const [breakpoint, setBreakpoint] = React.useState<keyof typeof BREAKPOINTS>(
    typeof window !== 'undefined' ? getCurrentBreakpoint() : 'lg'
  );

  React.useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    function handleResize() {
      setBreakpoint(getCurrentBreakpoint());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return breakpoint;
}

/**
 * Hook to check if device is mobile
 */
export function useIsMobile() {
  const [mobile, setMobile] = React.useState(
    typeof window !== 'undefined' ? isMobile() : false
  );

  React.useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    function handleResize() {
      setMobile(isMobile());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return mobile;
}

/**
 * Hook to check if device is tablet
 */
export function useIsTablet() {
  const [tablet, setTablet] = React.useState(
    typeof window !== 'undefined' ? isTablet() : false
  );

  React.useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    function handleResize() {
      setTablet(isTablet());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return tablet;
}

/**
 * Hook to check if device is desktop
 */
export function useIsDesktop() {
  const [desktop, setDesktop] = React.useState(
    typeof window !== 'undefined' ? isDesktop() : true
  );

  React.useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    function handleResize() {
      setDesktop(isDesktop());
    }

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return desktop;
}

/**
 * Responsive class name generator
 * 
 * @example
 * responsiveClass({
 *   mobile: 'text-sm',
 *   tablet: 'text-base',
 *   desktop: 'text-lg'
 * })
 */
export function responsiveClass(classes: {
  mobile?: string;
  tablet?: string;
  desktop?: string;
  base?: string;
}): string {
  const classNames: string[] = [];
  
  if (classes.base) {
    classNames.push(classes.base);
  }
  
  if (classes.mobile) {
    classNames.push(classes.mobile);
  }
  
  if (classes.tablet) {
    classNames.push(`md:${classes.tablet}`);
  }
  
  if (classes.desktop) {
    classNames.push(`lg:${classes.desktop}`);
  }
  
  return classNames.join(' ');
}

/**
 * Generate responsive padding classes
 */
export function responsivePadding(size: 'sm' | 'md' | 'lg' = 'md'): string {
  const paddingMap = {
    sm: 'p-3 md:p-4 lg:p-6',
    md: 'p-4 md:p-6 lg:p-8',
    lg: 'p-6 md:p-8 lg:p-12',
  };
  
  return paddingMap[size];
}

/**
 * Generate responsive gap classes
 */
export function responsiveGap(size: 'sm' | 'md' | 'lg' = 'md'): string {
  const gapMap = {
    sm: 'gap-2 md:gap-3 lg:gap-4',
    md: 'gap-4 md:gap-6 lg:gap-8',
    lg: 'gap-6 md:gap-8 lg:gap-12',
  };
  
  return gapMap[size];
}

/**
 * Generate responsive grid columns
 */
export function responsiveGrid(columns: {
  mobile?: number;
  tablet?: number;
  desktop?: number;
}): string {
  const classes: string[] = [];
  
  if (columns.mobile) {
    classes.push(`grid-cols-${columns.mobile}`);
  }
  
  if (columns.tablet) {
    classes.push(`md:grid-cols-${columns.tablet}`);
  }
  
  if (columns.desktop) {
    classes.push(`lg:grid-cols-${columns.desktop}`);
  }
  
  return classes.join(' ');
}

/**
 * Generate responsive text size classes
 */
export function responsiveText(size: 'sm' | 'md' | 'lg' = 'md'): string {
  const textMap = {
    sm: 'text-body-sm md:text-body-md',
    md: 'text-body-md md:text-body-lg',
    lg: 'text-body-lg md:text-title-md lg:text-title-lg',
  };
  
  return textMap[size];
}

// Import React for hooks
import * as React from 'react';
