/**
 * Interactive Card Component
 * 
 * A card component with hover and focus states for interactive elements.
 * Includes lift animation and focus ring for accessibility.
 */

'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { focusRing } from '@/lib/focus-utils';

interface InteractiveCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  href?: string;
  disabled?: boolean;
  /**
   * Enable hover lift effect
   * @default true
   */
  enableHover?: boolean;
  /**
   * Enable press scale effect
   * @default true
   */
  enablePress?: boolean;
}

export function InteractiveCard({
  children,
  className,
  onClick,
  href,
  disabled = false,
  enableHover = true,
  enablePress = true,
}: InteractiveCardProps) {
  const Component = href ? motion.a : motion.div;
  const isInteractive = !disabled && (onClick || href);

  const hoverAnimation = enableHover
    ? {
        y: -4,
        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.3)',
        transition: { duration: 0.15, ease: [0.16, 1, 0.3, 1] },
      }
    : {};

  const tapAnimation = enablePress
    ? {
        scale: 0.98,
        transition: { duration: 0.1, ease: [0.16, 1, 0.3, 1] },
      }
    : {};

  return (
    <Component
      href={href}
      onClick={disabled ? undefined : onClick}
      whileHover={isInteractive ? hoverAnimation : undefined}
      whileTap={isInteractive ? tapAnimation : undefined}
      className={cn(
        'rounded-lg bg-surface-container border border-outline/15',
        'transition-all duration-150',
        isInteractive && [
          'cursor-pointer',
          'hover:border-outline/30',
          focusRing,
        ],
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      tabIndex={isInteractive ? 0 : undefined}
      role={onClick && !href ? 'button' : undefined}
      aria-disabled={disabled}
    >
      {children}
    </Component>
  );
}
