/**
 * Code Improvement Page
 * 
 * Allows users to submit code for improvement and displays refactored code with explanations.
 * Features:
 * - Code editor for input
 * - Language and file path configuration
 * - Before/after diff view
 * - Improvement panel with explanations
 * - Loading and error states
 * - Fade in animations
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { CodeEditor } from '@/components/code/CodeEditor';
import { DiffViewer } from '@/components/code/DiffViewer';
import { ImprovementPanel } from '@/components/code/ImprovementPanel';
import { Button } from '@/components/ui/button';
import { AlertCircle, Sparkles, GitCompare } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ImprovePage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [filePath, setFilePath] = useState('');
  const [isImproving, setIsImproving] = useState(false);
  const [improvedCode, setImprovedCode] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'split' | 'unified'>('split');

  const handleImprove = async () => {
    if (!code.trim()) {
      setError('Please enter some code to improve');
      return;
    }

    setIsImproving(true);
    setError(null);
    setImprovedCode(null);
    setExplanation(null);

    try {
      const result = await apiClient.review.improve({
        code,
        language,
        filePath: filePath || undefined,
      });

      setImprovedCode(result.improved);
      setExplanation(result.explanation);
    } catch (err) {
      console.error('Failed to improve code:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to improve code. Please try again.'
      );
    } finally {
      setIsImproving(false);
    }
  };

  const handleClear = () => {
    setCode('');
    setFilePath('');
    setImprovedCode(null);
    setExplanation(null);
    setError(null);
  };

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-display-sm text-on-surface font-semibold">
          Code Improvement
        </h1>
        <p className="text-body-lg text-on-surface-variant">
          Get AI-powered code improvements with refactoring suggestions and explanations
        </p>
      </div>

      {/* Code Editor Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-title-lg text-on-surface">
            Enter Code
          </h2>
          <div className="flex items-center gap-3">
            {improvedCode && (
              <Button
                variant="outline"
                onClick={handleClear}
                disabled={isImproving}
              >
                Clear
              </Button>
            )}
            <Button
              onClick={handleImprove}
              disabled={isImproving || !code.trim()}
              className="min-w-[140px]"
            >
              {isImproving ? (
                <>
                  <div className="w-4 h-4 mr-2 border-2 border-on-primary/30 border-t-on-primary rounded-full animate-spin" />
                  <span>Improving...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  <span>Improve Code</span>
                </>
              )}
            </Button>
          </div>
        </div>

        <CodeEditor
          value={code}
          onChange={setCode}
          language={language}
          onLanguageChange={setLanguage}
          filePath={filePath}
          onFilePathChange={setFilePath}
          placeholder="Paste your code here for improvement suggestions..."
          minHeight="400px"
        />
      </div>

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            'rounded-lg p-4',
            'bg-error/10 border border-error/20',
            'flex items-start gap-3'
          )}
        >
          <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-body-md text-error font-medium">
              Improvement Failed
            </p>
            <p className="text-body-sm text-error/80 mt-1">
              {error}
            </p>
          </div>
        </motion.div>
      )}

      {/* Results Section */}
      {improvedCode && explanation && (
        <motion.div
          variants={fadeIn}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* View Mode Toggle */}
          <div className="flex items-center justify-between">
            <h2 className="text-title-lg text-on-surface">
              Comparison
            </h2>
            <div className="flex items-center gap-2 p-1 rounded-lg bg-surface-container">
              <Button
                variant={viewMode === 'split' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('split')}
                className="h-8"
              >
                <GitCompare className="w-4 h-4 mr-2" />
                Split View
              </Button>
              <Button
                variant={viewMode === 'unified' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setViewMode('unified')}
                className="h-8"
              >
                Unified View
              </Button>
            </div>
          </div>

          {/* Diff Viewer */}
          <DiffViewer
            before={code}
            after={improvedCode}
            language={language}
            filePath={filePath || undefined}
            mode={viewMode}
          />

          {/* Improvement Panel */}
          <div className="space-y-4">
            <h2 className="text-title-lg text-on-surface">
              Improved Version
            </h2>
            <ImprovementPanel
              code={improvedCode}
              explanation={explanation}
              language={language}
              filePath={filePath || undefined}
              defaultExpanded={true}
            />
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!improvedCode && !error && !isImproving && (
        <div className="rounded-lg border-2 border-dashed border-outline-variant/30 p-12">
          <div className="text-center space-y-3">
            <div className="inline-flex p-4 rounded-full bg-surface-container">
              <Sparkles className="w-8 h-8 text-on-surface-variant" />
            </div>
            <h3 className="text-title-lg text-on-surface">
              Ready to Improve
            </h3>
            <p className="text-body-md text-on-surface-variant max-w-md mx-auto">
              Paste your code above and click "Improve Code" to get AI-powered
              refactoring suggestions with detailed explanations of the changes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
