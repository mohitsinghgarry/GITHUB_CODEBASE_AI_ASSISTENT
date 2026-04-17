/**
 * CodeEditor Component
 * 
 * Simple code input editor for code review and improvement requests.
 * Features:
 * - Textarea with monospace font
 * - Line numbers
 * - Language selector
 * - File path input
 * - Fade in animation
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface CodeEditorProps {
  /**
   * Code content
   */
  value: string;
  
  /**
   * Change handler
   */
  onChange: (value: string) => void;
  
  /**
   * Programming language
   */
  language?: string;
  
  /**
   * Language change handler
   */
  onLanguageChange?: (language: string) => void;
  
  /**
   * File path
   */
  filePath?: string;
  
  /**
   * File path change handler
   */
  onFilePathChange?: (filePath: string) => void;
  
  /**
   * Placeholder text
   */
  placeholder?: string;
  
  /**
   * Minimum height
   */
  minHeight?: string;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

const SUPPORTED_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'jsx', label: 'React' },
  { value: 'tsx', label: 'React TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
  { value: 'swift', label: 'Swift' },
  { value: 'kotlin', label: 'Kotlin' },
  { value: 'csharp', label: 'C#' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'sql', label: 'SQL' },
  { value: 'bash', label: 'Bash' },
  { value: 'plaintext', label: 'Plain Text' },
];

export function CodeEditor({
  value,
  onChange,
  language = 'plaintext',
  onLanguageChange,
  filePath,
  onFilePathChange,
  placeholder = 'Paste your code here...',
  minHeight = '300px',
  className,
}: CodeEditorProps) {
  const [lineCount, setLineCount] = useState(1);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    // Update line count
    const lines = newValue.split('\n').length;
    setLineCount(lines);
  };

  const lines = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className={cn('space-y-4', className)}
    >
      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* File Path Input */}
        {onFilePathChange && (
          <div className="space-y-2">
            <Label htmlFor="file-path" className="text-label-md text-on-surface-variant">
              File Path (Optional)
            </Label>
            <Input
              id="file-path"
              type="text"
              value={filePath || ''}
              onChange={(e) => onFilePathChange(e.target.value)}
              placeholder="e.g., src/components/Button.tsx"
              className="font-mono text-body-sm"
            />
          </div>
        )}
        
        {/* Language Selector */}
        {onLanguageChange && (
          <div className="space-y-2">
            <Label htmlFor="language" className="text-label-md text-on-surface-variant">
              Language
            </Label>
            <Select value={language} onValueChange={onLanguageChange}>
              <SelectTrigger id="language" className="font-mono">
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Code Editor */}
      <div className="rounded-lg overflow-hidden bg-surface-container-lowest border border-outline-variant/15">
        <div className="flex">
          {/* Line Numbers */}
          <div className="select-none py-4 pl-4 pr-3 text-outline-variant border-r border-outline-variant/15 min-w-[3rem] text-right bg-surface-container-low">
            {lines.map((lineNum) => (
              <div key={lineNum} className="text-body-sm font-mono leading-relaxed">
                {lineNum}
              </div>
            ))}
          </div>
          
          {/* Textarea */}
          <textarea
            value={value}
            onChange={handleChange}
            placeholder={placeholder}
            className={cn(
              'flex-1 p-4 bg-transparent',
              'text-body-sm font-mono leading-relaxed text-on-surface',
              'placeholder:text-outline-variant',
              'focus:outline-none',
              'resize-none'
            )}
            style={{ minHeight }}
            spellCheck={false}
          />
        </div>
      </div>
    </motion.div>
  );
}
