/**
 * ModeSelector Component
 * 
 * Selector for explanation modes (Beginner, Technical, Interview).
 * Features:
 * - Three mode options
 * - Active state indication
 * - Smooth transitions
 * - Tooltips for mode descriptions
 */

'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { GraduationCap, Code2, MessageSquare } from 'lucide-react';
import type { ExplanationMode } from '@/types';

interface ModeSelectorProps {
  /**
   * Current explanation mode
   */
  mode: ExplanationMode;
  
  /**
   * Callback when mode changes
   */
  onChange: (mode: ExplanationMode) => void;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface ModeOption {
  value: ExplanationMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const modeOptions: ModeOption[] = [
  {
    value: 'beginner',
    label: 'Beginner',
    icon: GraduationCap,
    description: 'Clear explanations with examples',
  },
  {
    value: 'technical',
    label: 'Technical',
    icon: Code2,
    description: 'Detailed technical explanations',
  },
  {
    value: 'interview',
    label: 'Interview',
    icon: MessageSquare,
    description: 'Interactive Q&A style',
  },
];

export function ModeSelector({ mode, onChange, className }: ModeSelectorProps) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      {/* Label */}
      <span className="text-label-sm text-text-tertiary mr-2">Mode:</span>

      {/* Mode Buttons */}
      <div className="flex items-center gap-1 p-1 rounded-lg bg-surface-container-low border border-outline-variant/15">
        {modeOptions.map((option) => {
          const Icon = option.icon;
          const isActive = mode === option.value;

          return (
            <button
              key={option.value}
              onClick={() => onChange(option.value)}
              title={option.description}
              className={cn(
                'relative flex items-center gap-1.5 px-3 py-1.5 rounded-md',
                'text-label-md font-medium',
                'transition-all duration-150',
                'focus:outline-none focus:ring-2 focus:ring-primary/20',
                isActive
                  ? 'text-on-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-container-high'
              )}
            >
              {/* Active Background */}
              {isActive && (
                <motion.div
                  layoutId="activeMode"
                  className="absolute inset-0 bg-primary rounded-md"
                  transition={{
                    type: 'spring',
                    stiffness: 500,
                    damping: 30,
                  }}
                />
              )}

              {/* Content */}
              <span className="relative z-10 flex items-center gap-1.5">
                <Icon className="w-3.5 h-3.5" />
                <span>{option.label}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
