/**
 * Spinner Component
 * 
 * A loading spinner with smooth rotation animation.
 * Available in multiple sizes and variants.
 */

'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { rotate } from '@/lib/animation-presets';

interface SpinnerProps {
  /**
   * Size of the spinner
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /**
   * Color variant
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'tertiary' | 'muted';
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Accessible label
   * @default 'Loading...'
   */
  label?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
};

const variantClasses = {
  primary: 'text-primary',
  secondary: 'text-secondary',
  tertiary: 'text-tertiary',
  muted: 'text-text-secondary',
};

export function Spinner({
  size = 'md',
  variant = 'primary',
  className,
  label = 'Loading...',
}: SpinnerProps) {
  return (
    <motion.div
      variants={rotate}
      initial="initial"
      animate="animate"
      className={cn(sizeClasses[size], variantClasses[variant], className)}
      role="status"
      aria-label={label}
    >
      <Loader2 className="h-full w-full" />
      <span className="sr-only">{label}</span>
    </motion.div>
  );
}

/**
 * Full-page spinner overlay
 */
export function SpinnerOverlay({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="fixed inset-0 z-[1500] flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="xl" label={label} />
        <p className="text-body-md text-text-secondary">{label}</p>
      </div>
    </div>
  );
}

/**
 * Inline spinner with text
 */
export function SpinnerWithText({
  text,
  size = 'sm',
}: {
  text: string;
  size?: 'sm' | 'md';
}) {
  return (
    <div className="flex items-center gap-2">
      <Spinner size={size} variant="muted" label={text} />
      <span className="text-body-md text-text-secondary">{text}</span>
    </div>
  );
}
