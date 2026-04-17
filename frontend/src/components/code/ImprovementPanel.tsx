/**
 * ImprovementPanel Component
 * 
 * Displays improved/refactored code with explanations.
 * Features:
 * - Improved code display with syntax highlighting
 * - Explanation of changes
 * - Copy button
 * - Collapsible explanation section
 * - Fade in up animation
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeInUp, expand } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Copy, Check, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ImprovementPanelProps {
  /**
   * Improved code
   */
  code: string;
  
  /**
   * Explanation of improvements
   */
  explanation: string;
  
  /**
   * Programming language
   */
  language?: string;
  
  /**
   * File path
   */
  filePath?: string;
  
  /**
   * Whether explanation is expanded by default
   */
  defaultExpanded?: boolean;
  
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

export function ImprovementPanel({
  code,
  explanation,
  language = 'plaintext',
  filePath,
  defaultExpanded = true,
  className,
}: ImprovementPanelProps) {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const lines = code.split('\n');

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className={cn('rounded-lg overflow-hidden bg-surface-container border border-outline-variant/15', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface-container-low border-b border-outline-variant/15">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-md bg-tertiary/10">
            <Sparkles className="w-4 h-4 text-tertiary" />
          </div>
          <div>
            <h3 className="text-title-sm text-on-surface">Improved Code</h3>
            {filePath && (
              <p className="text-label-sm text-on-surface-variant font-mono">
                {filePath}
              </p>
            )}
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="h-8 px-3"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              <span className="text-label-md">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              <span className="text-label-md">Copy</span>
            </>
          )}
        </Button>
      </div>

      {/* Code Display */}
      <div className="bg-surface-container-lowest">
        <div className="flex items-center justify-between px-4 py-2 border-b border-outline-variant/15">
          <span className="text-label-sm text-on-surface-variant font-mono uppercase tracking-widest">
            {getLanguageDisplayName(language)}
          </span>
        </div>
        
        <div className="overflow-x-auto">
          <pre className="p-4 text-body-sm font-mono leading-relaxed">
            <div className="flex">
              <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                {lines.map((_, index) => (
                  <div key={index}>{index + 1}</div>
                ))}
              </div>
              <code className="pl-4 text-on-surface block flex-1">
                {code}
              </code>
            </div>
          </pre>
        </div>
      </div>

      {/* Explanation Section */}
      <div className="border-t border-outline-variant/15">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            'w-full flex items-center justify-between px-4 py-3',
            'hover:bg-surface-container-high transition-quart',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/20'
          )}
        >
          <span className="text-label-md text-on-surface uppercase tracking-widest">
            Explanation
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-on-surface-variant" />
          ) : (
            <ChevronDown className="w-4 h-4 text-on-surface-variant" />
          )}
        </button>

        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              initial="collapsed"
              animate="expanded"
              exit="collapsed"
              variants={expand}
            >
              <div className="px-4 pb-4">
                <div className="p-4 rounded-md bg-surface-container-low">
                  <p className="text-body-md text-on-surface-variant whitespace-pre-wrap">
                    {explanation}
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
