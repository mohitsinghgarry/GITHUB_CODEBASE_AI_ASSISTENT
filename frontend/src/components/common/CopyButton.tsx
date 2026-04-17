/**
 * CopyButton Component
 * 
 * A reusable copy-to-clipboard button with success feedback.
 * Uses scaleIn animation and provides visual feedback on copy.
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { scaleIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CopyButtonProps {
  /**
   * Text to copy to clipboard
   */
  text: string;
  
  /**
   * Success message to display
   * @default 'Copied!'
   */
  successMessage?: string;
  
  /**
   * Duration to show success state (ms)
   * @default 2000
   */
  successDuration?: number;
  
  /**
   * Button size
   * @default 'sm'
   */
  size?: 'sm' | 'default' | 'lg' | 'icon';
  
  /**
   * Button variant
   * @default 'ghost'
   */
  variant?: 'default' | 'outline' | 'ghost' | 'secondary';
  
  /**
   * Show label text
   * @default false
   */
  showLabel?: boolean;
  
  /**
   * Custom label text
   * @default 'Copy'
   */
  label?: string;
  
  /**
   * Additional CSS classes
   */
  className?: string;
  
  /**
   * Callback after successful copy
   */
  onCopy?: () => void;
  
  /**
   * Callback on copy error
   */
  onError?: (error: Error) => void;
}

export function CopyButton({
  text,
  successMessage = 'Copied!',
  successDuration = 2000,
  size = 'sm',
  variant = 'ghost',
  showLabel = false,
  label = 'Copy',
  className,
  onCopy,
  onError,
}: CopyButtonProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      onCopy?.();

      // Reset after duration
      setTimeout(() => {
        setIsCopied(false);
      }, successDuration);
    } catch (error) {
      console.error('Failed to copy text:', error);
      onError?.(error as Error);
    }
  };

  return (
    <Button
      onClick={handleCopy}
      size={size}
      variant={variant}
      className={cn(
        'relative transition-colors',
        isCopied && 'text-tertiary',
        className
      )}
      aria-label={isCopied ? successMessage : label}
    >
      {/* Icon with animation */}
      <motion.div
        key={isCopied ? 'check' : 'copy'}
        variants={scaleIn}
        initial="hidden"
        animate="visible"
        className="flex items-center gap-2"
      >
        {isCopied ? (
          <Check className="w-4 h-4" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
        
        {showLabel && (
          <span className="text-label-md">
            {isCopied ? successMessage : label}
          </span>
        )}
      </motion.div>
    </Button>
  );
}

/**
 * CopyButtonWithTooltip
 * 
 * Copy button with tooltip for better UX
 */

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface CopyButtonWithTooltipProps extends CopyButtonProps {
  /**
   * Tooltip text
   * @default 'Copy to clipboard'
   */
  tooltip?: string;
  
  /**
   * Success tooltip text
   * @default 'Copied!'
   */
  successTooltip?: string;
}

export function CopyButtonWithTooltip({
  tooltip = 'Copy to clipboard',
  successTooltip = 'Copied!',
  ...props
}: CopyButtonWithTooltipProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(props.text);
      setIsCopied(true);
      props.onCopy?.();

      setTimeout(() => {
        setIsCopied(false);
      }, props.successDuration || 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
      props.onError?.(error as Error);
    }
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            onClick={handleCopy}
            size={props.size || 'sm'}
            variant={props.variant || 'ghost'}
            className={cn(
              'relative transition-colors',
              isCopied && 'text-tertiary',
              props.className
            )}
            aria-label={isCopied ? successTooltip : tooltip}
          >
            <motion.div
              key={isCopied ? 'check' : 'copy'}
              variants={scaleIn}
              initial="hidden"
              animate="visible"
            >
              {isCopied ? (
                <Check className="w-4 h-4" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </motion.div>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{isCopied ? successTooltip : tooltip}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

/**
 * CodeCopyButton
 * 
 * Specialized copy button for code blocks
 */

export function CodeCopyButton({
  code,
  className,
}: {
  code: string;
  className?: string;
}) {
  return (
    <CopyButtonWithTooltip
      text={code}
      size="icon"
      variant="ghost"
      className={cn(
        'absolute top-2 right-2 h-8 w-8',
        'bg-surface-container-high/50 hover:bg-surface-container-high',
        'backdrop-blur-sm',
        className
      )}
      tooltip="Copy code"
      successTooltip="Copied!"
    />
  );
}

/**
 * InlineCopyButton
 * 
 * Inline copy button for text snippets
 */

export function InlineCopyButton({
  text,
  className,
}: {
  text: string;
  className?: string;
}) {
  return (
    <CopyButton
      text={text}
      size="icon"
      variant="ghost"
      className={cn('h-6 w-6 ml-1', className)}
      successDuration={1500}
    />
  );
}

/**
 * CopyTextButton
 * 
 * Copy button with visible label
 */

export function CopyTextButton({
  text,
  label = 'Copy',
  className,
}: {
  text: string;
  label?: string;
  className?: string;
}) {
  return (
    <CopyButton
      text={text}
      label={label}
      showLabel={true}
      size="sm"
      variant="outline"
      className={className}
    />
  );
}

/**
 * useCopyToClipboard Hook
 * 
 * Custom hook for copy-to-clipboard functionality
 */

export function useCopyToClipboard() {
  const [isCopied, setIsCopied] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const copy = async (text: string, duration = 2000) => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setError(null);

      setTimeout(() => {
        setIsCopied(false);
      }, duration);

      return true;
    } catch (err) {
      const error = err as Error;
      setError(error);
      console.error('Failed to copy text:', error);
      return false;
    }
  };

  return { isCopied, error, copy };
}
