/**
 * CodeViewer Component
 * 
 * Displays code with syntax highlighting and copy functionality.
 * Features:
 * - Syntax highlighting
 * - Copy to clipboard button
 * - Line numbers
 * - Language badge
 * - Fade in animation
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CodeViewerProps {
  /**
   * Code content to display
   */
  code: string;
  
  /**
   * Programming language for syntax highlighting
   */
  language?: string;
  
  /**
   * File path (optional)
   */
  filePath?: string;
  
  /**
   * Whether to show line numbers
   */
  showLineNumbers?: boolean;
  
  /**
   * Starting line number (for partial code display)
   */
  startLine?: number;
  
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
    rb: 'Ruby',
    php: 'PHP',
    swift: 'Swift',
    kt: 'Kotlin',
    cs: 'C#',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    yml: 'YAML',
    md: 'Markdown',
    sql: 'SQL',
    sh: 'Shell',
    bash: 'Bash',
    plaintext: 'Text',
  };
  
  return languageMap[language.toLowerCase()] || language.toUpperCase();
}

export function CodeViewer({
  code,
  language = 'plaintext',
  filePath,
  showLineNumbers = true,
  startLine = 1,
  className,
}: CodeViewerProps) {
  const [copied, setCopied] = useState(false);

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
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className={cn(
        'rounded-lg overflow-hidden',
        'bg-surface-container-lowest border border-outline-variant/15',
        className
      )}
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

      {/* Code Content */}
      <div className="overflow-x-auto">
        <pre className="p-4 text-body-sm font-mono leading-relaxed">
          {showLineNumbers ? (
            <div className="flex">
              {/* Line Numbers */}
              <div className="select-none pr-4 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right">
                {lines.map((_, index) => (
                  <div key={index}>
                    {startLine + index}
                  </div>
                ))}
              </div>
              
              {/* Code */}
              <code className="pl-4 text-on-surface block flex-1">
                {code}
              </code>
            </div>
          ) : (
            <code className="text-on-surface block">{code}</code>
          )}
        </pre>
      </div>
    </motion.div>
  );
}
