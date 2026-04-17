/**
 * StatusBadge Component
 * 
 * A reusable status badge with status-based colors and optional icon.
 * Uses scaleIn animation for smooth appearance.
 */

'use client';

import { motion } from 'framer-motion';
import { scaleIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Loader2,
  Circle,
  LucideIcon,
} from 'lucide-react';

type StatusType =
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'pending'
  | 'loading'
  | 'idle'
  | 'completed'
  | 'failed'
  | 'running'
  | 'queued';

interface StatusBadgeProps {
  /**
   * Status type
   */
  status: StatusType;
  
  /**
   * Custom label (overrides default status label)
   */
  label?: string;
  
  /**
   * Show icon
   * @default true
   */
  showIcon?: boolean;
  
  /**
   * Custom icon (overrides default status icon)
   */
  icon?: LucideIcon;
  
  /**
   * Size variant
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';
  
  /**
   * Variant style
   * @default 'default'
   */
  variant?: 'default' | 'outline' | 'subtle';
  
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * Animate on mount
   * @default true
   */
  animate?: boolean;
}

const statusConfig: Record<
  StatusType,
  {
    label: string;
    icon: LucideIcon;
    color: {
      default: string;
      outline: string;
      subtle: string;
    };
  }
> = {
  success: {
    label: 'Success',
    icon: CheckCircle2,
    color: {
      default: 'bg-tertiary text-on-tertiary',
      outline: 'border-tertiary text-tertiary',
      subtle: 'bg-tertiary/10 text-tertiary',
    },
  },
  completed: {
    label: 'Completed',
    icon: CheckCircle2,
    color: {
      default: 'bg-tertiary text-on-tertiary',
      outline: 'border-tertiary text-tertiary',
      subtle: 'bg-tertiary/10 text-tertiary',
    },
  },
  error: {
    label: 'Error',
    icon: XCircle,
    color: {
      default: 'bg-error text-on-error',
      outline: 'border-error text-error',
      subtle: 'bg-error/10 text-error',
    },
  },
  failed: {
    label: 'Failed',
    icon: XCircle,
    color: {
      default: 'bg-error text-on-error',
      outline: 'border-error text-error',
      subtle: 'bg-error/10 text-error',
    },
  },
  warning: {
    label: 'Warning',
    icon: AlertCircle,
    color: {
      default: 'bg-secondary text-on-secondary',
      outline: 'border-secondary text-secondary',
      subtle: 'bg-secondary/10 text-secondary',
    },
  },
  info: {
    label: 'Info',
    icon: AlertCircle,
    color: {
      default: 'bg-primary text-on-primary',
      outline: 'border-primary text-primary',
      subtle: 'bg-primary/10 text-primary',
    },
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    color: {
      default: 'bg-surface-container-high text-text-secondary',
      outline: 'border-outline text-text-secondary',
      subtle: 'bg-surface-container text-text-secondary',
    },
  },
  queued: {
    label: 'Queued',
    icon: Clock,
    color: {
      default: 'bg-surface-container-high text-text-secondary',
      outline: 'border-outline text-text-secondary',
      subtle: 'bg-surface-container text-text-secondary',
    },
  },
  loading: {
    label: 'Loading',
    icon: Loader2,
    color: {
      default: 'bg-primary text-on-primary',
      outline: 'border-primary text-primary',
      subtle: 'bg-primary/10 text-primary',
    },
  },
  running: {
    label: 'Running',
    icon: Loader2,
    color: {
      default: 'bg-primary text-on-primary',
      outline: 'border-primary text-primary',
      subtle: 'bg-primary/10 text-primary',
    },
  },
  idle: {
    label: 'Idle',
    icon: Circle,
    color: {
      default: 'bg-surface-container-high text-text-tertiary',
      outline: 'border-outline-variant text-text-tertiary',
      subtle: 'bg-surface-container text-text-tertiary',
    },
  },
};

const sizeConfig = {
  sm: {
    container: 'px-2 py-0.5 text-label-sm gap-1',
    icon: 'w-3 h-3',
  },
  md: {
    container: 'px-2.5 py-1 text-label-md gap-1.5',
    icon: 'w-3.5 h-3.5',
  },
  lg: {
    container: 'px-3 py-1.5 text-label-lg gap-2',
    icon: 'w-4 h-4',
  },
};

export function StatusBadge({
  status,
  label,
  showIcon = true,
  icon: CustomIcon,
  size = 'md',
  variant = 'default',
  className,
  animate = true,
}: StatusBadgeProps) {
  const config = statusConfig[status];
  const sizeStyles = sizeConfig[size];
  const Icon = CustomIcon || config.icon;
  const displayLabel = label || config.label;

  const isAnimatedIcon = status === 'loading' || status === 'running';

  const badge = (
    <div
      className={cn(
        'inline-flex items-center font-medium rounded-full uppercase tracking-wider',
        sizeStyles.container,
        variant === 'outline' && 'border bg-transparent',
        config.color[variant],
        className
      )}
    >
      {showIcon && (
        <Icon
          className={cn(
            sizeStyles.icon,
            isAnimatedIcon && 'animate-spin'
          )}
        />
      )}
      <span>{displayLabel}</span>
    </div>
  );

  if (!animate) {
    return badge;
  }

  return (
    <motion.div
      variants={scaleIn}
      initial="hidden"
      animate="visible"
      className="inline-block"
    >
      {badge}
    </motion.div>
  );
}

/**
 * Preset status badge variants for common use cases
 */

export function SuccessBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="success" label={label} size={size} />;
}

export function ErrorBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="error" label={label} size={size} />;
}

export function WarningBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="warning" label={label} size={size} />;
}

export function InfoBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="info" label={label} size={size} />;
}

export function PendingBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="pending" label={label} size={size} />;
}

export function LoadingBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="loading" label={label} size={size} />;
}

export function CompletedBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="completed" label={label} size={size} />;
}

export function FailedBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="failed" label={label} size={size} />;
}

export function RunningBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="running" label={label} size={size} />;
}

export function QueuedBadge({ label, size }: { label?: string; size?: 'sm' | 'md' | 'lg' }) {
  return <StatusBadge status="queued" label={label} size={size} />;
}
