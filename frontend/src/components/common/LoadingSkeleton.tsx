/**
 * LoadingSkeleton Component
 * 
 * A reusable skeleton loader with pulse animation for loading states.
 * Uses the shimmer animation preset for a smooth loading effect.
 */

'use client';

import { motion } from 'framer-motion';
import { skeleton } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';

interface LoadingSkeletonProps {
  /**
   * Width of the skeleton (CSS value)
   * @default '100%'
   */
  width?: string | number;
  
  /**
   * Height of the skeleton (CSS value)
   * @default '1rem'
   */
  height?: string | number;
  
  /**
   * Border radius variant
   * @default 'md'
   */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | 'full';
  
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * Number of skeleton lines to render
   * @default 1
   */
  count?: number;
  
  /**
   * Gap between skeleton lines (when count > 1)
   * @default '0.5rem'
   */
  gap?: string;
}

const roundedClasses = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
  '3xl': 'rounded-3xl',
  full: 'rounded-full',
};

export function LoadingSkeleton({
  width = '100%',
  height = '1rem',
  rounded = 'md',
  className,
  count = 1,
  gap = '0.5rem',
}: LoadingSkeletonProps) {
  const skeletonStyle = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  if (count === 1) {
    return (
      <motion.div
        variants={skeleton}
        initial="initial"
        animate="animate"
        className={cn(
          'bg-surface-container-high',
          roundedClasses[rounded],
          className
        )}
        style={skeletonStyle}
        aria-label="Loading..."
        role="status"
      />
    );
  }

  return (
    <div
      className="flex flex-col"
      style={{ gap }}
      role="status"
      aria-label="Loading..."
    >
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          variants={skeleton}
          initial="initial"
          animate="animate"
          className={cn(
            'bg-surface-container-high',
            roundedClasses[rounded],
            className
          )}
          style={skeletonStyle}
        />
      ))}
    </div>
  );
}

/**
 * Preset skeleton variants for common use cases
 */

export function TextSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <LoadingSkeleton
          key={index}
          height="1rem"
          width={index === lines - 1 ? '60%' : '100%'}
          rounded="sm"
        />
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="p-6 bg-surface-container rounded-lg space-y-4">
      <LoadingSkeleton height="1.5rem" width="40%" rounded="sm" />
      <TextSkeleton lines={3} />
      <div className="flex gap-2">
        <LoadingSkeleton height="2rem" width="5rem" rounded="md" />
        <LoadingSkeleton height="2rem" width="5rem" rounded="md" />
      </div>
    </div>
  );
}

export function AvatarSkeleton({ size = 40 }: { size?: number }) {
  return (
    <LoadingSkeleton
      width={size}
      height={size}
      rounded="full"
    />
  );
}

export function ButtonSkeleton() {
  return (
    <LoadingSkeleton
      height="2.5rem"
      width="6rem"
      rounded="md"
    />
  );
}

export function CodeBlockSkeleton() {
  return (
    <div className="p-4 bg-surface-container-lowest rounded-lg space-y-2">
      <LoadingSkeleton height="1rem" width="80%" rounded="sm" />
      <LoadingSkeleton height="1rem" width="90%" rounded="sm" />
      <LoadingSkeleton height="1rem" width="70%" rounded="sm" />
      <LoadingSkeleton height="1rem" width="85%" rounded="sm" />
    </div>
  );
}
