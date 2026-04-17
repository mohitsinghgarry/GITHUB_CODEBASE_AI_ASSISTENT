/**
 * Code Review Page
 * 
 * Allows users to submit code for review and displays structured feedback.
 * Features:
 * - Code editor for input
 * - Language and file path configuration
 * - Review summary with severity counts
 * - Detailed issue cards with suggestions
 * - Loading and error states
 * - Stagger animation for results
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { staggerContainer } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { CodeEditor } from '@/components/code/CodeEditor';
import { ReviewSummaryBar } from '@/components/code/ReviewSummaryBar';
import { ReviewResultCard } from '@/components/code/ReviewResultCard';
import { Button } from '@/components/ui/button';
import { AlertCircle, Sparkles } from 'lucide-react';
import { apiClient } from '@/lib/api';
import type { ReviewFeedback, ReviewIssue } from '@/types';

export default function ReviewPage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [filePath, setFilePath] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState<ReviewFeedback | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to review');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setFeedback(null);

    try {
      const result = await apiClient.review.analyze({
        code,
        language,
        filePath: filePath || undefined,
      });

      setFeedback(result);
    } catch (err) {
      console.error('Failed to analyze code:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to analyze code. Please try again.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setCode('');
    setFilePath('');
    setFeedback(null);
    setError(null);
  };

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-display-sm text-on-surface font-semibold">
          Code Review
        </h1>
        <p className="text-body-lg text-on-surface-variant">
          Get AI-powered code review with issue detection and suggestions
        </p>
      </div>

      {/* Code Editor Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-title-lg text-on-surface">
            Enter Code
          </h2>
          <div className="flex items-center gap-3">
            {feedback && (
              <Button
                variant="outline"
                onClick={handleClear}
                disabled={isAnalyzing}
              >
                Clear
              </Button>
            )}
            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !code.trim()}
              className="min-w-[140px]"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 mr-2 border-2 border-on-primary/30 border-t-on-primary rounded-full animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  <span>Analyze Code</span>
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
          placeholder="Paste your code here for review..."
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
              Analysis Failed
            </p>
            <p className="text-body-sm text-error/80 mt-1">
              {error}
            </p>
          </div>
        </motion.div>
      )}

      {/* Results Section */}
      {feedback && (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Summary */}
          <ReviewSummaryBar issues={feedback.issues} />

          {/* Summary Text */}
          {feedback.summary && (
            <div className="rounded-lg p-6 bg-surface-container border border-outline-variant/15">
              <h3 className="text-title-md text-on-surface mb-3">
                Summary
              </h3>
              <p className="text-body-md text-on-surface-variant whitespace-pre-wrap">
                {feedback.summary}
              </p>
            </div>
          )}

          {/* Issues List */}
          {feedback.issues.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-title-lg text-on-surface">
                Issues Found
              </h3>
              <div className="space-y-3">
                {feedback.issues.map((issue, index) => (
                  <ReviewResultCard key={index} issue={issue} />
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Empty State */}
      {!feedback && !error && !isAnalyzing && (
        <div className="rounded-lg border-2 border-dashed border-outline-variant/30 p-12">
          <div className="text-center space-y-3">
            <div className="inline-flex p-4 rounded-full bg-surface-container">
              <Sparkles className="w-8 h-8 text-on-surface-variant" />
            </div>
            <h3 className="text-title-lg text-on-surface">
              Ready to Review
            </h3>
            <p className="text-body-md text-on-surface-variant max-w-md mx-auto">
              Paste your code above and click "Analyze Code" to get AI-powered
              review feedback with issue detection and improvement suggestions.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
