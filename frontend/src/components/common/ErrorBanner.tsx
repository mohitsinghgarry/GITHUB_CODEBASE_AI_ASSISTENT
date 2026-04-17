/**
 * ErrorBanner Component
 * 
 * A reusable error banner with retry functionality and dismiss option.
 * Uses fadeInUp animation for smooth appearance.
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { AlertCircle, X, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorBannerProps {
  /**
   * Error title
   */
  title?: string;
  
  /**
   * Error message
   */
  message: string;
  
  /**
   * Retry button handler
   */
  onRetry?: () => void;
  
  /**
   * Dismiss button handler
   */
  onDismiss?: () => void;
  
  /**
   * Retry button label
   * @default 'Try Again'
   */
  retryLabel?: string;
  
  /**
   * Show dismiss button
   * @default true
   */
  dismissible?: boolean;
  
  /**
   * Variant style
   * @default 'error'
   */
  variant?: 'error' | 'warning' | 'info';
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

const variantConfig = {
  error: {
    container: 'bg-error-container/10 border-error',
    icon: 'text-error',
    title: 'text-error',
    message: 'text-on-error-container',
  },
  warning: {
    container: 'bg-secondary-container/10 border-secondary',
    icon: 'text-secondary',
    title: 'text-secondary',
    message: 'text-on-secondary-container',
  },
  info: {
    container: 'bg-primary-container/10 border-primary',
    icon: 'text-primary',
    title: 'text-primary',
    message: 'text-on-primary-container',
  },
};

export function ErrorBanner({
  title,
  message,
  onRetry,
  onDismiss,
  retryLabel = 'Try Again',
  dismissible = true,
  variant = 'error',
  className,
}: ErrorBannerProps) {
  const config = variantConfig[variant];

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={cn(
        'relative flex items-start gap-3 p-4 rounded-lg border',
        config.container,
        className
      )}
      role="alert"
      aria-live="assertive"
    >
      {/* Icon */}
      <div className={cn('flex-shrink-0 mt-0.5', config.icon)}>
        <AlertCircle className="w-5 h-5" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className={cn('font-medium text-label-lg mb-1', config.title)}>
            {title}
          </h4>
        )}
        <p className={cn('text-body-sm', config.message)}>
          {message}
        </p>

        {/* Actions */}
        {onRetry && (
          <div className="mt-3">
            <Button
              onClick={onRetry}
              variant="outline"
              size="sm"
              className="h-8"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              {retryLabel}
            </Button>
          </div>
        )}
      </div>

      {/* Dismiss Button */}
      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          className={cn(
            'flex-shrink-0 p-1 rounded-md transition-colors',
            'hover:bg-surface-container-high',
            'focus:outline-none focus:ring-2 focus:ring-primary/20',
            config.icon
          )}
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </motion.div>
  );
}

/**
 * Preset error banner variants for common use cases
 */

export function NetworkErrorBanner({
  onRetry,
  onDismiss,
}: {
  onRetry?: () => void;
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title="Connection Error"
      message="Unable to connect to the server. Please check your internet connection and try again."
      onRetry={onRetry}
      onDismiss={onDismiss}
      variant="error"
    />
  );
}

export function AuthErrorBanner({
  onRetry,
  onDismiss,
}: {
  onRetry?: () => void;
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title="Authentication Error"
      message="Your session has expired. Please sign in again to continue."
      onRetry={onRetry}
      onDismiss={onDismiss}
      variant="warning"
    />
  );
}

export function ValidationErrorBanner({
  message,
  onDismiss,
}: {
  message: string;
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title="Validation Error"
      message={message}
      onDismiss={onDismiss}
      variant="warning"
      dismissible={true}
    />
  );
}

export function ServerErrorBanner({
  onRetry,
  onDismiss,
}: {
  onRetry?: () => void;
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title="Server Error"
      message="An unexpected error occurred on the server. Our team has been notified."
      onRetry={onRetry}
      onDismiss={onDismiss}
      variant="error"
    />
  );
}

export function RateLimitErrorBanner({
  onDismiss,
}: {
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title="Rate Limit Exceeded"
      message="You've made too many requests. Please wait a moment before trying again."
      onDismiss={onDismiss}
      variant="warning"
    />
  );
}

export function InfoBanner({
  title,
  message,
  onDismiss,
}: {
  title?: string;
  message: string;
  onDismiss?: () => void;
}) {
  return (
    <ErrorBanner
      title={title}
      message={message}
      onDismiss={onDismiss}
      variant="info"
      dismissible={true}
    />
  );
}
