/**
 * Toast Notification Component
 * 
 * A toast notification system with success, error, warning, and info variants.
 * Uses framer-motion for smooth animations and auto-dismissal.
 */

'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast as toastAnimation } from '@/lib/animation-presets';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
  duration?: number;
}

interface ToastProps extends Toast {
  onDismiss: (id: string) => void;
}

const variantStyles = {
  success: {
    container: 'bg-tertiary/10 border-tertiary/20',
    icon: 'text-tertiary',
    IconComponent: CheckCircle2,
  },
  error: {
    container: 'bg-error/10 border-error/20',
    icon: 'text-error',
    IconComponent: AlertCircle,
  },
  warning: {
    container: 'bg-[#f59e0b]/10 border-[#f59e0b]/20',
    icon: 'text-[#f59e0b]',
    IconComponent: AlertTriangle,
  },
  info: {
    container: 'bg-primary/10 border-primary/20',
    icon: 'text-primary',
    IconComponent: Info,
  },
};

export function ToastItem({ id, title, description, variant, duration = 5000, onDismiss }: ToastProps) {
  const { container, icon, IconComponent } = variantStyles[variant];

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onDismiss(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onDismiss]);

  return (
    <motion.div
      layout
      variants={toastAnimation}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={cn(
        'pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border backdrop-blur-glass',
        container
      )}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <IconComponent className={cn('h-5 w-5 flex-shrink-0 mt-0.5', icon)} />
          <div className="flex-1 min-w-0">
            <p className="text-label-lg text-text-primary font-medium">{title}</p>
            {description && (
              <p className="mt-1 text-body-sm text-text-secondary">{description}</p>
            )}
          </div>
          <button
            onClick={() => onDismiss(id)}
            className="flex-shrink-0 rounded-md p-1 hover:bg-surface-container-high transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20"
            aria-label="Dismiss notification"
          >
            <X className="h-4 w-4 text-text-secondary" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: string) => void }) {
  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="pointer-events-none fixed top-0 right-0 z-[1600] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:bottom-0 sm:right-0 sm:flex-col md:max-w-[420px]"
    >
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} {...toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
}
