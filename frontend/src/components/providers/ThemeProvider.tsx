'use client';

/**
 * Theme Provider
 * 
 * Manages theme application and system preference detection.
 * Applies theme class to document.documentElement and handles smooth transitions.
 */

import { useEffect, useState } from 'react';
import { useSettingsStore } from '@/store/settingsStore';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const theme = useSettingsStore((state) => state.theme);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Determine the effective theme
    const effectiveTheme = theme === 'system' 
      ? (systemPrefersDark ? 'dark' : 'light')
      : theme;

    // Add transition class for smooth theme change
    root.classList.add('theme-transitioning');

    // Apply theme class
    if (effectiveTheme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }

    // Remove transition class after animation completes (250ms)
    const timer = setTimeout(() => {
      root.classList.remove('theme-transitioning');
    }, 250);

    return () => clearTimeout(timer);
  }, [theme, mounted]);

  // Listen for system theme changes when theme is set to 'system'
  useEffect(() => {
    if (!mounted || theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      const root = document.documentElement;
      root.classList.add('theme-transitioning');

      if (e.matches) {
        root.classList.add('dark');
        root.classList.remove('light');
      } else {
        root.classList.add('light');
        root.classList.remove('dark');
      }

      setTimeout(() => {
        root.classList.remove('theme-transitioning');
      }, 250);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, mounted]);

  // Prevent flash of unstyled content
  if (!mounted) {
    return <>{children}</>;
  }

  return <>{children}</>;
}
