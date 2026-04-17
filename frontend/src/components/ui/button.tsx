/**
 * Button Component
 * 
 * A versatile button component with multiple variants and sizes.
 * Based on the RepoMind Assistant design system.
 */

import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md font-medium transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]',
  {
    variants: {
      variant: {
        default:
          'bg-primary text-on-primary hover:bg-primary-dim hover:shadow-lg hover:shadow-primary/20 active:bg-primary-dim',
        outline:
          'border border-outline bg-transparent hover:bg-surface-container-high hover:border-outline-variant active:bg-surface-container-highest',
        secondary:
          'bg-secondary text-on-secondary hover:bg-secondary-dim hover:shadow-lg hover:shadow-secondary/20 active:bg-secondary-dim',
        ghost:
          'hover:bg-surface-container-high active:bg-surface-container-highest',
        link:
          'text-primary underline-offset-4 hover:underline hover:text-primary-dim',
        destructive:
          'bg-error text-on-error hover:bg-error/90 hover:shadow-lg hover:shadow-error/20 active:bg-error/80',
      },
      size: {
        default: 'h-11 min-h-[44px] px-4 py-2 text-label-lg',
        sm: 'h-9 min-h-[36px] px-3 text-label-md',
        lg: 'h-12 min-h-[48px] px-6 text-label-lg',
        icon: 'h-11 w-11 min-h-[44px] min-w-[44px]',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
