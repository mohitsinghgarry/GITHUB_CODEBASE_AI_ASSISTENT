'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { api, CodeIssue } from '@/lib/api';
import { IssueCard } from '@/components/diff-review/IssueCard';

export default function DiffReviewPage() {
  const [diff, setDiff] = useState('');
  const [files, setFiles] = useState<any[]>([]);
  const [issues, setIssues] = useState<CodeIssue[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [assessment, setAssessment] = useState('');
  const [recommendation, setRecommendation] = useState<'approve' | 'request_changes' | 'comment' | null>(null);
  const [isReviewing, setIsReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [focusOnChanges, setFocusOnChanges] = useState(true);

  const handleReview = async () => {
    if (!diff.trim()) return;

    setIsReviewing(true);
    setError(null);

    try {
      const result = await api.reviewDiff({
        diff,
        focus_on_changes: focusOnChanges,
      });

      setFiles(result.files);
      setIssues(result.issues);
      setSummary(result.summary);
      setAssessment(result.overall_assessment);
      setRecommendation(result.approval_recommendation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Diff review failed');
    } finally {
      setIsReviewing(false);
    }
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'approve':
        return 'tertiary';
      case 'request_changes':
        return 'error';
      case 'comment':
        return 'primary';
      default:
        return 'outline';
    }
  };

  const getRecommendationIcon = (rec: string) => {
    switch (rec) {
      case 'approve':
        return 'check_circle';
      case 'request_changes':
        return 'cancel';
      case 'comment':
        return 'chat_bubble';
      default:
        return 'help';
    }
  };

  const getRecommendationText = (rec: string) => {
    switch (rec) {
      case 'approve':
        return 'Approve';
      case 'request_changes':
        return 'Request Changes';
      case 'comment':
        return 'Comment';
      default:
        return 'Unknown';
    }
  };

  const exampleDiff = `diff --git a/src/utils/validation.py b/src/utils/validation.py
index 1234567..abcdefg 100644
--- a/src/utils/validation.py
+++ b/src/utils/validation.py
@@ -10,7 +10,10 @@ def validate_email(email):
     """
     Validate email address format.
     """
-    return '@' in email
+    import re
+    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
+    return re.match(pattern, email) is not None
+
 
 def validate_password(password):
     """`;

  return (
    <AppShell>
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-on-surface mb-2">Diff Review</h1>
          <p className="text-on-surface-variant">AI-powered code diff and pull request review</p>
        </div>

        {/* Diff Input */}
        <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6 mb-6">
          <div className="mb-4 flex items-center justify-between">
            <label className="text-sm font-semibold text-on-surface">Git Diff to Review</label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm text-on-surface cursor-pointer">
                <input
                  type="checkbox"
                  checked={focusOnChanges}
                  onChange={(e) => setFocusOnChanges(e.target.checked)}
                  className="w-4 h-4 rounded border-outline-variant/30 text-primary focus:ring-primary"
                />
                Focus on changes only
              </label>
              <button
                onClick={() => setDiff(exampleDiff)}
                className="px-3 py-1.5 bg-surface-container-low border border-outline-variant/15 rounded-md text-xs text-on-surface hover:bg-surface-container-high transition-colors"
              >
                Load Example
              </button>
            </div>
          </div>
          <textarea
            value={diff}
            onChange={(e) => setDiff(e.target.value)}
            placeholder="Paste your git diff here (unified diff format)...&#10;&#10;Example:&#10;diff --git a/file.py b/file.py&#10;index 1234567..abcdefg 100644&#10;--- a/file.py&#10;+++ b/file.py&#10;@@ -10,7 +10,10 @@ def function():&#10;-    old line&#10;+    new line"
            className="w-full h-80 p-4 bg-surface-container-lowest border border-outline-variant/10 rounded-lg text-on-surface font-mono text-xs resize-none focus:ring-1 focus:ring-primary focus:border-primary/50"
          />
          <div className="mt-4 flex gap-3">
            <button
              onClick={handleReview}
              disabled={isReviewing || !diff.trim()}
              className="px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-on-primary font-bold rounded-md hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isReviewing ? 'Reviewing...' : 'Review Diff'}
            </button>
            <button
              onClick={() => {
                setDiff('');
                setFiles([]);
                setIssues([]);
                setSummary(null);
                setAssessment('');
                setRecommendation(null);
                setError(null);
              }}
              className="px-6 py-2.5 bg-surface-bright text-on-surface font-semibold rounded-md hover:bg-surface-container-high transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-error/10 border border-error/20 rounded-xl flex items-start gap-3">
            <span className="material-symbols-outlined text-error">error</span>
            <div className="flex-1">
              <p className="text-error font-medium">Review failed</p>
              <p className="text-error/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Recommendation Badge */}
        {recommendation && (
          <div className="mb-6 bg-surface-container rounded-xl border border-outline-variant/10 p-6">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full bg-${getRecommendationColor(recommendation)}/10 flex items-center justify-center flex-shrink-0`}>
                <span className={`material-symbols-outlined text-${getRecommendationColor(recommendation)} text-2xl`}>
                  {getRecommendationIcon(recommendation)}
                </span>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-on-surface mb-1">
                  Recommendation: {getRecommendationText(recommendation)}
                </h3>
                {assessment && (
                  <p className="text-sm text-on-surface-variant">{assessment}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6 mb-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-outline mb-4">Issue Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-error">{summary.critical_count}</p>
                <p className="text-xs text-on-surface-variant">Critical</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-error">{summary.high_count}</p>
                <p className="text-xs text-on-surface-variant">High</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{summary.medium_count}</p>
                <p className="text-xs text-on-surface-variant">Medium</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-tertiary">{summary.low_count}</p>
                <p className="text-xs text-on-surface-variant">Low</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-outline">{summary.info_count}</p>
                <p className="text-xs text-on-surface-variant">Info</p>
              </div>
            </div>
          </div>
        )}

        {/* Files Changed */}
        {files.length > 0 && (
          <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6 mb-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-outline mb-4">
              Files Changed ({files.length})
            </h3>
            <div className="space-y-3">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="bg-surface-container-low rounded-lg p-4 border border-outline-variant/10"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="material-symbols-outlined text-primary text-lg">description</span>
                    <span className="font-mono text-sm text-on-surface font-medium">
                      {file.file_path}
                    </span>
                  </div>
                  {file.hunks && file.hunks.length > 0 && (
                    <div className="space-y-2">
                      {file.hunks.map((hunk: any, hunkIndex: number) => (
                        <div
                          key={hunkIndex}
                          className="bg-surface-container-lowest rounded p-3 font-mono text-xs"
                        >
                          <div className="text-outline mb-2">
                            @@ -{hunk.old_start},{hunk.old_count} +{hunk.new_start},{hunk.new_count} @@
                          </div>
                          <div className="space-y-0.5">
                            {hunk.lines.slice(0, 10).map((line: any, lineIndex: number) => (
                              <div
                                key={lineIndex}
                                className={`${
                                  line.type === 'addition'
                                    ? 'bg-tertiary/10 text-tertiary'
                                    : line.type === 'deletion'
                                    ? 'bg-error/10 text-error'
                                    : 'text-on-surface-variant'
                                }`}
                              >
                                <span className="select-none mr-2">
                                  {line.type === 'addition' ? '+' : line.type === 'deletion' ? '-' : ' '}
                                </span>
                                {line.content}
                              </div>
                            ))}
                            {hunk.lines.length > 10 && (
                              <div className="text-outline italic">
                                ... {hunk.lines.length - 10} more lines
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Issues */}
        {issues.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-on-surface">Issues Found</h3>
            {issues.map((issue, index) => (
              <IssueCard key={index} issue={issue} index={index} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isReviewing && issues.length === 0 && !error && diff.trim() === '' && (
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-outline text-5xl mb-4">difference</span>
            <p className="text-on-surface-variant mb-2">Paste your git diff above to get AI-powered review</p>
            <p className="text-sm text-outline">Supports unified diff format from git diff, GitHub PRs, and GitLab MRs</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
