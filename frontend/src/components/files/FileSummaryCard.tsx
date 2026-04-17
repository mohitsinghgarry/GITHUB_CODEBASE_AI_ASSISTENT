/**
 * FileSummaryCard Component
 * 
 * Displays AI-generated summary of a file's purpose and key functionality.
 * Includes loading states and error handling.
 */

'use client';

import { motion } from 'framer-motion';
import { fadeInUp, shimmer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  Sparkles,
  AlertCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useState } from 'react';

interface FileSummaryCardProps {
  /**
   * AI-generated summary text
   */
  summary?: string;
  
  /**
   * Key functions or classes identified
   */
  keyElements?: {
    name: string;
    type: 'function' | 'class' | 'interface' | 'type' | 'constant';
    description?: string;
  }[];
  
  /**
   * Loading state
   */
  isLoading?: boolean;
  
  /**
   * Error state
   */
  error?: string;
  
  /**
   * Callback to regenerate summary
   */
  onRegenerate?: () => void;
  
  /**
   * Collapsible
   * @default false
   */
  collapsible?: boolean;
  
  /**
   * Initially collapsed (only if collapsible)
   * @default false
   */
  initiallyCollapsed?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get badge color for element type
 */
function getElementTypeBadge(type: string): string {
  const badges: Record<string, string> = {
    function: 'bg-primary/20 text-primary',
    class: 'bg-secondary/20 text-secondary',
    interface: 'bg-tertiary/20 text-tertiary',
    type: 'bg-tertiary/20 text-tertiary',
    constant: 'bg-surface-container-high text-text-secondary',
  };
  
  return badges[type] || 'bg-surface-container-high text-text-secondary';
}

export function FileSummaryCard({
  summary,
  keyElements,
  isLoading = false,
  error,
  onRegenerate,
  collapsible = false,
  initiallyCollapsed = false,
  className,
}: FileSummaryCardProps) {
  const [isCollapsed, setIsCollapsed] = useState(initiallyCollapsed);
  
  const hasContent = summary || (keyElements && keyElements.length > 0);
  
  // Loading State
  if (isLoading) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className={cn(
          'p-6 bg-surface-container rounded-lg border border-outline/15',
          className
        )}
      >
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-5 h-5 text-primary animate-pulse" />
          <h3 className="text-title-md text-text-primary font-semibold">
            AI Summary
          </h3>
        </div>
        
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              variants={shimmer}
              initial="initial"
              animate="animate"
              className="h-4 bg-surface-container-high rounded"
              style={{
                width: `${70 + Math.random() * 30}%`,
                backgroundImage:
                  'linear-gradient(90deg, transparent, rgba(163, 166, 255, 0.1), transparent)',
                backgroundSize: '200% 100%',
              }}
            />
          ))}
        </div>
      </motion.div>
    );
  }
  
  // Error State
  if (error) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className={cn(
          'p-6 bg-error/5 rounded-lg border border-error/20',
          className
        )}
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <h3 className="text-title-md text-error font-semibold mb-2">
              Failed to generate summary
            </h3>
            <p className="text-body-md text-text-secondary mb-4">
              {error}
            </p>
            {onRegenerate && (
              <motion.button
                onClick={onRegenerate}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-md',
                  'bg-error/10 text-error hover:bg-error/20',
                  'transition-colors',
                  'focus:outline-none focus-visible:ring-2 focus-visible:ring-error/20'
                )}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <RefreshCw className="w-4 h-4" />
                <span className="text-label-lg">Try Again</span>
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>
    );
  }
  
  // Empty State
  if (!hasContent) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className={cn(
          'p-6 bg-surface-container rounded-lg border border-outline/15',
          className
        )}
      >
        <div className="flex items-center gap-3 mb-3">
          <Sparkles className="w-5 h-5 text-text-tertiary" />
          <h3 className="text-title-md text-text-secondary font-semibold">
            AI Summary
          </h3>
        </div>
        <p className="text-body-md text-text-tertiary">
          No summary available for this file.
        </p>
      </motion.div>
    );
  }
  
  // Content State
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn(
        'p-6 bg-surface-container rounded-lg border border-outline/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-primary" />
          <h3 className="text-title-md text-text-primary font-semibold">
            AI Summary
          </h3>
        </div>
        
        <div className="flex items-center gap-2">
          {onRegenerate && (
            <motion.button
              onClick={onRegenerate}
              className={cn(
                'p-2 rounded-md transition-colors',
                'hover:bg-surface-container-high',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Regenerate summary"
            >
              <RefreshCw className="w-4 h-4 text-text-secondary" />
            </motion.button>
          )}
          
          {collapsible && (
            <motion.button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className={cn(
                'p-2 rounded-md transition-colors',
                'hover:bg-surface-container-high',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title={isCollapsed ? 'Expand' : 'Collapse'}
            >
              {isCollapsed ? (
                <ChevronDown className="w-4 h-4 text-text-secondary" />
              ) : (
                <ChevronUp className="w-4 h-4 text-text-secondary" />
              )}
            </motion.button>
          )}
        </div>
      </div>
      
      {/* Content */}
      {!isCollapsed && (
        <motion.div
          initial={collapsible ? { opacity: 0, height: 0 } : false}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.25 }}
          className="space-y-4"
        >
          {/* Summary Text */}
          {summary && (
            <p className="text-body-md text-text-primary leading-relaxed">
              {summary}
            </p>
          )}
          
          {/* Key Elements */}
          {keyElements && keyElements.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-label-lg text-text-secondary uppercase tracking-wider">
                Key Elements
              </h4>
              <div className="space-y-2">
                {keyElements.map((element, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-start gap-3 p-3 bg-surface-container-low rounded-md"
                  >
                    <span
                      className={cn(
                        'px-2 py-0.5 rounded-full text-label-sm uppercase tracking-wider flex-shrink-0',
                        getElementTypeBadge(element.type)
                      )}
                    >
                      {element.type}
                    </span>
                    <div className="flex-1 min-w-0">
                      <code className="text-body-md text-text-primary font-mono">
                        {element.name}
                      </code>
                      {element.description && (
                        <p className="text-body-sm text-text-secondary mt-1">
                          {element.description}
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
