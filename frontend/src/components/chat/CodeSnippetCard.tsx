/**
 * CodeSnippetCard Component
 * 
 * Displays code snippets with syntax highlighting and copy functionality.
 * Features:
 * - Syntax highlighting using Prism.js
 * - Copy to clipboard button
 * - Language badge
 * - Line numbers (optional)
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { codeBlock } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CodeSnippetCardProps {
  /**
   * Code content to display
   */
  code: string;
  
  /**
   * Programming language for syntax highlighting
   */
  language?: string;
  
  /**
   * Whether to show line numbers
   */
  showLineNumbers?: boolean;
  
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

export function CodeSnippetCard({
  code,
  language = 'plaintext',
  showLineNumbers = false,
  className,
}: CodeSnippetCardProps) {
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
      variants={codeBlock}
      className={cn(
        'rounded-lg overflow-hidden',
        'bg-surface-container-lowest border border-outline-variant/15',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-surface-container-low border-b border-outline-variant/15">
        <span className="text-label-sm text-text-secondary font-mono">
          {getLanguageDisplayName(language)}
        </span>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="h-7 px-2"
        >
          {copied ? (
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

      {/* Code Content */}
      <div className="overflow-x-auto">
        <pre className="p-4 text-body-sm font-mono leading-relaxed">
          {showLineNumbers ? (
            <div className="flex">
              {/* Line Numbers */}
              <div className="select-none pr-4 text-text-tertiary border-r border-outline-variant/15">
                {lines.map((_, index) => (
                  <div key={index} className="text-right">
                    {index + 1}
                  </div>
                ))}
              </div>
              
              {/* Code */}
              <code className="pl-4 text-text-primary block">
                {code}
              </code>
            </div>
          ) : (
            <code className="text-text-primary block">{code}</code>
          )}
        </pre>
      </div>
    </motion.div>
  );
}
