/**
 * Input Component
 * 
 * Text input field following the design system.
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-11 min-h-[44px] w-full rounded-md',
          'bg-surface-container border border-outline/15',
          'px-4 py-2',
          'text-body-md text-on-surface',
          'placeholder:text-on-surface-variant',
          'focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-offset-2 focus:ring-offset-background focus:border-primary',
          'hover:border-outline/30',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'transition-all duration-150',
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';

export { Input };
