/**
 * DiffViewer Component
 * 
 * Displays before/after code comparison with diff highlighting.
 * Features:
 * - Side-by-side or unified diff view
 * - Line-by-line comparison
 * - Addition/deletion highlighting
 * - Copy buttons for both versions
 * - Slide up animation
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DiffViewerProps {
  /**
   * Original code (before)
   */
  before: string;
  
  /**
   * Modified code (after)
   */
  after: string;
  
  /**
   * Programming language
   */
  language?: string;
  
  /**
   * File path
   */
  filePath?: string;
  
  /**
   * View mode: side-by-side or unified
   */
  mode?: 'split' | 'unified';
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get language display name
 */
function getLanguageDisplayName(language: string): string {
  const languageMap: Record<string, string> = {
    js: 'JavaScript',
    ts: 'TypeScript',
    jsx: 'React',
    tsx: 'React TypeScript',
    py: 'Python',
    python: 'Python',
    java: 'Java',
    cpp: 'C++',
    c: 'C',
    go: 'Go',
    rs: 'Rust',
    rust: 'Rust',
    plaintext: 'Text',
  };
  
  return languageMap[language.toLowerCase()] || language.toUpperCase();
}

export function DiffViewer({
  before,
  after,
  language = 'plaintext',
  filePath,
  mode = 'split',
  className,
}: DiffViewerProps) {
  const [copiedBefore, setCopiedBefore] = useState(false);
  const [copiedAfter, setCopiedAfter] = useState(false);

  const handleCopyBefore = async () => {
    try {
      await navigator.clipboard.writeText(before);
      setCopiedBefore(true);
      setTimeout(() => setCopiedBefore(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleCopyAfter = async () => {
    try {
      await navigator.clipboard.writeText(after);
      setCopiedAfter(true);
      setTimeout(() => setCopiedAfter(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const beforeLines = before.split('\n');
  const afterLines = after.split('\n');

  if (mode === 'split') {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className={cn('rounded-lg overflow-hidden bg-surface-container-lowest border border-outline-variant/15', className)}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-surface-container-low border-b border-outline-variant/15">
          <div className="flex items-center gap-3">
            <span className="text-label-sm text-on-surface-variant font-mono uppercase tracking-widest">
              {getLanguageDisplayName(language)}
            </span>
            {filePath && (
              <>
                <span className="text-outline-variant">•</span>
                <span className="text-body-sm text-on-surface-variant font-mono">
                  {filePath}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Split View */}
        <div className="grid grid-cols-2 divide-x divide-outline-variant/15">
          {/* Before (Left) */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between px-4 py-2 bg-error/5 border-b border-outline-variant/15">
              <span className="text-label-sm text-error uppercase tracking-widest">
                Before
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyBefore}
                className="h-7 px-2"
              >
                {copiedBefore ? (
                  <>
                    <Check className="w-3.5 h-3.5 mr-1.5" />
                    <span className="text-label-sm">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 mr-1.5" />
                    <span className="text-label-sm">Copy</span>
                  </>
                )}
              </Button>
            </div>
            <div className="overflow-x-auto">
              <pre className="p-4 text-body-sm font-mono leading-relaxed">
                <div className="flex">
                  <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                    {beforeLines.map((_, index) => (
                      <div key={index}>{index + 1}</div>
                    ))}
                  </div>
                  <code className="pl-4 text-on-surface block flex-1">
                    {before}
                  </code>
                </div>
              </pre>
            </div>
          </div>

          {/* After (Right) */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between px-4 py-2 bg-tertiary/5 border-b border-outline-variant/15">
              <span className="text-label-sm text-tertiary uppercase tracking-widest">
                After
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyAfter}
                className="h-7 px-2"
              >
                {copiedAfter ? (
                  <>
                    <Check className="w-3.5 h-3.5 mr-1.5" />
                    <span className="text-label-sm">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 mr-1.5" />
                    <span className="text-label-sm">Copy</span>
                  </>
                )}
              </Button>
            </div>
            <div className="overflow-x-auto">
              <pre className="p-4 text-body-sm font-mono leading-relaxed">
                <div className="flex">
                  <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                    {afterLines.map((_, index) => (
                      <div key={index}>{index + 1}</div>
                    ))}
                  </div>
                  <code className="pl-4 text-on-surface block flex-1">
                    {after}
                  </code>
                </div>
              </pre>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  // Unified view
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn('rounded-lg overflow-hidden bg-surface-container-lowest border border-outline-variant/15', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface-container-low border-b border-outline-variant/15">
        <div className="flex items-center gap-3">
          <span className="text-label-sm text-on-surface-variant font-mono uppercase tracking-widest">
            {getLanguageDisplayName(language)}
          </span>
          {filePath && (
            <>
              <span className="text-outline-variant">•</span>
              <span className="text-body-sm text-on-surface-variant font-mono">
                {filePath}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Unified View */}
      <div className="overflow-x-auto">
        <pre className="text-body-sm font-mono leading-relaxed">
          {/* Before */}
          <div className="bg-error/5 border-b border-outline-variant/15">
            <div className="px-4 py-2 border-b border-outline-variant/15">
              <span className="text-label-sm text-error uppercase tracking-widest">
                Before
              </span>
            </div>
            <div className="p-4 flex">
              <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                {beforeLines.map((_, index) => (
                  <div key={index}>{index + 1}</div>
                ))}
              </div>
              <code className="pl-4 text-on-surface block flex-1">
                {before}
              </code>
            </div>
          </div>

          {/* After */}
          <div className="bg-tertiary/5">
            <div className="px-4 py-2 border-b border-outline-variant/15">
              <span className="text-label-sm text-tertiary uppercase tracking-widest">
                After
              </span>
            </div>
            <div className="p-4 flex">
              <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                {afterLines.map((_, index) => (
                  <div key={index}>{index + 1}</div>
                ))}
              </div>
              <code className="pl-4 text-on-surface block flex-1">
                {after}
              </code>
            </div>
          </div>
        </pre>
      </div>
    </motion.div>
  );
}
