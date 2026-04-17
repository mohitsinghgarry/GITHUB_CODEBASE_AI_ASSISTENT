/**
 * RepoInputCard Component
 * 
 * Input card for adding a new GitHub repository with URL validation and loading states.
 * Features:
 * - URL validation for GitHub repositories
 * - Loading state with progress indicator
 * - Error handling with descriptive messages
 * - Smooth animations with framer-motion
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Github, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

interface RepoInputCardProps {
  /**
   * Callback when repository URL is submitted
   */
  onSubmit: (url: string) => Promise<void>;
  
  /**
   * Loading state
   */
  isLoading?: boolean;
  
  /**
   * Error message
   */
  error?: string | null;
  
  /**
   * Success message
   */
  success?: string | null;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Validate GitHub repository URL
 */
function validateGitHubUrl(url: string): { valid: boolean; error?: string } {
  if (!url.trim()) {
    return { valid: false, error: 'URL is required' };
  }

  // GitHub URL patterns
  const httpsPattern = /^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/;
  const sshPattern = /^git@github\.com:[\w-]+\/[\w.-]+\.git$/;

  if (!httpsPattern.test(url) && !sshPattern.test(url)) {
    return {
      valid: false,
      error: 'Invalid GitHub URL. Use format: https://github.com/owner/repo',
    };
  }

  return { valid: true };
}

export function RepoInputCard({
  onSubmit,
  isLoading = false,
  error = null,
  success = null,
  className,
}: RepoInputCardProps) {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous validation error
    setValidationError(null);

    // Validate URL
    const validation = validateGitHubUrl(url);
    if (!validation.valid) {
      setValidationError(validation.error || 'Invalid URL');
      return;
    }

    // Submit
    try {
      await onSubmit(url);
      // Clear input on success
      if (!error) {
        setUrl('');
      }
    } catch (err) {
      // Error handled by parent component
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    // Clear validation error when user types
    if (validationError) {
      setValidationError(null);
    }
  };

  const displayError = validationError || error;
  const hasError = !!displayError;

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn(
        'bg-surface-container rounded-xl p-6 border border-outline-variant/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
          <Github className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="text-title-md text-text-primary font-medium">
            Add Repository
          </h3>
          <p className="text-body-sm text-text-secondary mt-0.5">
            Enter a GitHub repository URL to index
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Input Field */}
        <div>
          <label htmlFor="repo-url" className="sr-only">
            Repository URL
          </label>
          <input
            id="repo-url"
            type="text"
            value={url}
            onChange={handleInputChange}
            placeholder="https://github.com/owner/repository"
            disabled={isLoading}
            className={cn(
              'w-full px-4 py-3 rounded-lg',
              'bg-surface-container-low border border-outline-variant/15',
              'text-body-md text-text-primary placeholder:text-text-tertiary',
              'focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary',
              'transition-all duration-150',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              hasError && 'border-error focus:ring-error/20 focus:border-error'
            )}
          />
          
          {/* Error Message */}
          {hasError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 mt-2 text-body-sm text-error"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{displayError}</span>
            </motion.div>
          )}

          {/* Success Message */}
          {success && !hasError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 mt-2 text-body-sm text-tertiary"
            >
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{success}</span>
            </motion.div>
          )}
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full"
          size="lg"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Adding Repository...
            </>
          ) : (
            <>
              <Github className="w-4 h-4 mr-2" />
              Add Repository
            </>
          )}
        </Button>
      </form>

      {/* Help Text */}
      <div className="mt-4 pt-4 border-t border-outline-variant/15">
        <p className="text-body-sm text-text-tertiary">
          Supported formats:
        </p>
        <ul className="mt-2 space-y-1 text-body-sm text-text-tertiary">
          <li className="flex items-center gap-2">
            <span className="w-1 h-1 rounded-full bg-text-tertiary" />
            HTTPS: <code className="text-label-sm font-mono text-text-secondary">https://github.com/owner/repo</code>
          </li>
          <li className="flex items-center gap-2">
            <span className="w-1 h-1 rounded-full bg-text-tertiary" />
            SSH: <code className="text-label-sm font-mono text-text-secondary">git@github.com:owner/repo.git</code>
          </li>
        </ul>
      </div>
    </motion.div>
  );
}
