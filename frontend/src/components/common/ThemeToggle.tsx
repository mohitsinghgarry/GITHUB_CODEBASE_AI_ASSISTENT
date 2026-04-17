'use client';

/**
 * Theme Toggle Component
 * 
 * A button component that cycles through light, dark, and system themes.
 * Features smooth icon transitions with framer-motion and tooltips.
 */

import { Sun, Moon, Monitor } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSettingsStore } from '@/store/settingsStore';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const themeIcons = {
  light: Sun,
  dark: Moon,
  system: Monitor,
};

const themeLabels = {
  light: 'Light Mode',
  dark: 'Dark Mode',
  system: 'System Theme',
};

export function ThemeToggle() {
  const { theme, toggleTheme } = useSettingsStore();
  const Icon = themeIcons[theme];

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={toggleTheme}
            className="relative flex items-center justify-center w-10 h-10 rounded-md bg-surface-container-low hover:bg-surface-container-high transition-colors duration-fast ease-quart focus-visible:outline-none focus-visible:shadow-focus-glow"
            aria-label={`Current theme: ${themeLabels[theme]}. Click to change.`}
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={theme}
                initial={{ scale: 0.5, opacity: 0, rotate: -90 }}
                animate={{ scale: 1, opacity: 1, rotate: 0 }}
                exit={{ scale: 0.5, opacity: 0, rotate: 90 }}
                transition={{
                  duration: 0.25,
                  ease: [0.16, 1, 0.3, 1], // Quart easing
                }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <Icon size={16} className="text-on-surface" strokeWidth={1.5} />
              </motion.div>
            </AnimatePresence>
          </button>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="text-body-sm">
          <p>{themeLabels[theme]}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
