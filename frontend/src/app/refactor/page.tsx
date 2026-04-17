'use client';

import { useState } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { api, CodeImprovement } from '@/lib/api';

export default function RefactorPage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [improvedCode, setImprovedCode] = useState('');
  const [improvements, setImprovements] = useState<CodeImprovement[]>([]);
  const [summary, setSummary] = useState('');
  const [isImproving, setIsImproving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleImprove = async () => {
    if (!code.trim()) return;

    setIsImproving(true);
    setError(null);

    try {
      const result = await api.improveCode({
        code,
        language,
      });

      setImprovedCode(result.improved_code);
      setImprovements(result.improvements);
      setSummary(result.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Improvement failed');
    } finally {
      setIsImproving(false);
    }
  };
  return (
    <AppShell>
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-on-surface mb-2">Code Refactor</h1>
          <p className="text-on-surface-variant">AI-powered code improvements and modernization</p>
        </div>

        {/* Code Input */}
        <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6 mb-6">
          <div className="mb-4 flex items-center justify-between">
            <label className="text-sm font-semibold text-on-surface">Code to Improve</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="px-3 py-1.5 bg-surface-container-low border border-outline-variant/15 rounded-md text-sm text-on-surface"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
            </select>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            className="w-full h-64 p-4 bg-surface-container-lowest border border-outline-variant/10 rounded-lg text-on-surface font-mono text-sm resize-none focus:ring-1 focus:ring-primary focus:border-primary/50"
          />
          <div className="mt-4 flex gap-3">
            <button
              onClick={handleImprove}
              disabled={isImproving || !code.trim()}
              className="px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-on-primary font-bold rounded-md hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isImproving ? 'Improving...' : 'Improve Code'}
            </button>
            <button
              onClick={() => {
                setCode('');
                setImprovedCode('');
                setImprovements([]);
                setSummary('');
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
              <p className="text-error font-medium">Improvement failed</p>
              <p className="text-error/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Before/After Comparison */}
        {improvedCode && (
          <>
            <div className="grid grid-cols-2 gap-6 mb-8">
              {/* Before */}
              <div className="bg-surface-container rounded-xl border border-outline-variant/10 overflow-hidden">
                <div className="px-4 py-3 bg-surface-container-low border-b border-outline-variant/10 flex items-center justify-between">
                  <span className="text-sm font-semibold text-on-surface">Before</span>
                  <span className="text-xs text-error font-mono">Original</span>
                </div>
                <div className="p-4 bg-surface-container-lowest font-mono text-sm max-h-96 overflow-y-auto">
                  <pre className="text-on-surface-variant whitespace-pre-wrap">{code}</pre>
                </div>
              </div>

              {/* After */}
              <div className="bg-surface-container rounded-xl border border-outline-variant/10 overflow-hidden">
                <div className="px-4 py-3 bg-surface-container-low border-b border-outline-variant/10 flex items-center justify-between">
                  <span className="text-sm font-semibold text-on-surface">After</span>
                  <span className="text-xs text-tertiary font-mono">Improved</span>
                </div>
                <div className="p-4 bg-surface-container-lowest font-mono text-sm max-h-96 overflow-y-auto">
                  <pre className="text-on-surface-variant whitespace-pre-wrap">{improvedCode}</pre>
                </div>
              </div>
            </div>

            {/* Summary */}
            {summary && (
              <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6 mb-6">
                <h3 className="text-sm font-bold uppercase tracking-widest text-outline mb-4">Summary</h3>
                <p className="text-on-surface-variant">{summary}</p>
              </div>
            )}

            {/* Improvements List */}
            {improvements.length > 0 && (
              <div className="bg-surface-container rounded-xl border border-outline-variant/10 p-6">
                <h3 className="text-sm font-bold uppercase tracking-widest text-outline mb-6">Improvements Applied</h3>
                <div className="space-y-4">
                  {improvements.map((improvement, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <span className="material-symbols-outlined text-tertiary text-lg">check_circle</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-on-surface">{improvement.category}</p>
                        <p className="text-xs text-on-surface-variant mt-1">{improvement.description}</p>
                        {improvement.before_snippet && improvement.after_snippet && (
                          <div className="mt-3 grid grid-cols-2 gap-4">
                            <div className="bg-surface-container-lowest rounded-lg p-3 font-mono text-xs">
                              <p className="text-error-dim mb-2">Before:</p>
                              <pre className="text-on-surface-variant whitespace-pre-wrap">{improvement.before_snippet}</pre>
                            </div>
                            <div className="bg-surface-container-lowest rounded-lg p-3 font-mono text-xs">
                              <p className="text-tertiary mb-2">After:</p>
                              <pre className="text-on-surface-variant whitespace-pre-wrap">{improvement.after_snippet}</pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-3 mt-8">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(improvedCode);
                    }}
                    className="px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-on-primary font-bold rounded-md hover:opacity-90 transition-opacity"
                  >
                    Copy Improved Code
                  </button>
                  <button
                    onClick={() => {
                      setCode(improvedCode);
                      setImprovedCode('');
                      setImprovements([]);
                      setSummary('');
                    }}
                    className="px-6 py-2.5 bg-surface-bright text-on-surface font-semibold rounded-md hover:bg-surface-container-high transition-colors"
                  >
                    Use as Input
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!isImproving && !improvedCode && !error && code.trim() === '' && (
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-outline text-5xl mb-4">auto_fix_high</span>
            <p className="text-on-surface-variant">Paste your code above to get AI-powered improvements</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
