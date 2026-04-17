/**
 * SearchModeToggle Component
 * 
 * Toggle between search modes: Semantic, Keyword, and Hybrid.
 * 
 * Features:
 * - Three-way toggle with visual feedback
 * - Smooth animations
 * - Keyboard navigation
 * - Descriptions for each mode
 */

'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Sparkles, Search, Zap } from 'lucide-react';
import type { SearchMode } from '@/types';

interface SearchModeToggleProps {
  /**
   * Current search mode
   */
  value: SearchMode;
  
  /**
   * Callback when mode changes
   */
  onChange: (mode: SearchMode) => void;
  
  /**
   * Whether the toggle is disabled
   */
  disabled?: boolean;
  
  /**
   * Show mode descriptions
   * @default false
   */
  showDescriptions?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

const searchModes: Array<{
  value: SearchMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}> = [
  {
    value: 'semantic',
    label: 'Semantic',
    icon: Sparkles,
    description: 'AI-powered meaning-based search',
  },
  {
    value: 'keyword',
    label: 'Keyword',
    icon: Search,
    description: 'Exact text matching with BM25',
  },
  {
    value: 'hybrid',
    label: 'Hybrid',
    icon: Zap,
    description: 'Best of both worlds',
  },
];

export function SearchModeToggle({
  value,
  onChange,
  disabled = false,
  showDescriptions = false,
  className,
}: SearchModeToggleProps) {
  const selectedIndex = searchModes.findIndex((mode) => mode.value === value);

  return (
    <div className={cn('space-y-3', className)}>
      {/* Toggle Buttons */}
      <div
        className={cn(
          'relative inline-flex items-center gap-1 p-1 rounded-xl',
          'bg-surface-container-low border border-outline-variant/15',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Sliding Background */}
        <motion.div
          layoutId="search-mode-bg"
          className="absolute inset-y-1 rounded-lg bg-surface-container-high"
          initial={false}
          animate={{
            x: selectedIndex * 100 + '%',
            width: `calc(${100 / searchModes.length}% - 8px)`,
          }}
          transition={{
            type: 'spring',
            stiffness: 300,
            damping: 30,
          }}
          style={{
            left: '4px',
          }}
        />

        {/* Mode Buttons */}
        {searchModes.map((mode) => {
          const Icon = mode.icon;
          const isSelected = mode.value === value;

          return (
            <button
              key={mode.value}
              onClick={() => !disabled && onChange(mode.value)}
              disabled={disabled}
              className={cn(
                'relative z-10 flex items-center gap-2 px-4 py-2.5 rounded-lg',
                'text-body-md font-medium transition-colors duration-150',
                'disabled:cursor-not-allowed',
                isSelected
                  ? 'text-text-primary'
                  : 'text-text-secondary hover:text-text-primary'
              )}
            >
              <Icon
                className={cn(
                  'w-4 h-4 transition-colors duration-150',
                  isSelected ? 'text-primary' : 'text-text-tertiary'
                )}
              />
              <span>{mode.label}</span>
            </button>
          );
        })}
      </div>

      {/* Mode Description */}
      {showDescriptions && (
        <motion.div
          key={value}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15 }}
          className="px-1"
        >
          <p className="text-body-sm text-text-secondary">
            {searchModes.find((mode) => mode.value === value)?.description}
          </p>
        </motion.div>
      )}
    </div>
  );
}
