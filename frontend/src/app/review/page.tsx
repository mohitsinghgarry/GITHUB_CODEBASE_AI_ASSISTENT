'use client';

import { useState, useRef, useCallback } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { api, CodeIssue } from '@/lib/api';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { rust } from '@codemirror/lang-rust';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { php } from '@codemirror/lang-php';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap, EditorView } from '@codemirror/view';
import { EditorSelection } from '@codemirror/state';

export default function ReviewPage() {
  const [code, setCode] = useState(`async function fetchUserData(userId: string) {
  // Potential vulnerability here
  const query = \`SELECT * FROM users WHERE id = '\${userId}'\`;
  
  try {
    const result = await db.execute(query);
    if (!result) {
      throw new Error('User not found');
    }
    return result;
  } catch (e) {
    console.log(e); // Security risk: exposing errors
  }
}

export const handler = async (event) => {
  const { id } = event.pathParameters;
  return await fetchUserData(id);
};`);
  const [language, setLanguage] = useState('typescript');
  const [issues, setIssues] = useState<CodeIssue[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expandedIssues, setExpandedIssues] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  
  // Review criteria checkboxes
  const [checkBugs, setCheckBugs] = useState(true);
  const [checkSecurity, setCheckSecurity] = useState(true);
  const [checkStyle, setCheckStyle] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Get CodeMirror language extension
  const getLanguageExtension = () => {
    switch (language) {
      case 'javascript':
      case 'typescript':
        return javascript({ jsx: true, typescript: language === 'typescript' });
      case 'python':
        return python();
      case 'rust':
        return rust();
      case 'java':
        return java();
      case 'cpp':
      case 'c':
        return cpp();
      case 'php':
        return php();
      default:
        return javascript();
    }
  };

  // Show toast notification
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Handle file upload
  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file size (max 1MB)
    if (file.size > 1024 * 1024) {
      showToast('File too large. Maximum size is 1MB.', 'error');
      return;
    }

    // Detect language from file extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    const langMap: Record<string, string> = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'rs': 'rust',
      'go': 'go',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'cs': 'csharp',
      'rb': 'ruby',
      'php': 'php',
    };

    if (ext && langMap[ext]) {
      setLanguage(langMap[ext]);
    }

    // Read file content
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setCode(content);
      showToast(`Loaded ${file.name}`, 'success');
    };
    reader.onerror = () => {
      showToast('Failed to read file', 'error');
    };
    reader.readAsText(file);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Handle code analysis
  const handleAnalyze = async () => {
    if (!code.trim()) {
      showToast('Please enter some code to analyze', 'error');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Build criteria based on checkboxes
      const criteria: string[] = [];
      if (checkBugs || checkSecurity || checkStyle) {
        criteria.push('production_ready');
      }
      if (checkSecurity) {
        criteria.push('security_focused');
      }
      if (checkStyle) {
        criteria.push('style_strict');
      }

      const result = await api.reviewCode({
        code,
        language,
        criteria: criteria.length > 0 ? criteria : undefined,
      });

      setIssues(result.issues);
      setSummary(result.summary);
      
      if (result.issues.length === 0) {
        showToast('No issues found! Code looks good.', 'success');
      } else {
        showToast(`Found ${result.issues.length} issue(s)`, 'info');
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to analyze code. Please try again.';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error('Review failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Toggle issue expansion
  const toggleIssue = (index: number) => {
    const newExpanded = new Set(expandedIssues);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIssues(newExpanded);
  };

  // Copy results to clipboard
  const handleCopyResults = async () => {
    if (!summary || issues.length === 0) {
      showToast('No results to copy', 'error');
      return;
    }

    const text = `Code Review Results
===================
Total Issues: ${summary.total_issues}
Critical: ${summary.critical_count + summary.high_count}
Warnings: ${summary.medium_count}
Suggestions: ${summary.low_count + summary.info_count}

Issues:
${issues.map((issue, i) => `
${i + 1}. [${issue.severity.toUpperCase()}] ${issue.title}
   ${issue.description}
   ${issue.suggestion ? `   Suggestion: ${issue.suggestion}` : ''}
`).join('\n')}`;

    try {
      await navigator.clipboard.writeText(text);
      showToast('Copied to clipboard!', 'success');
    } catch (err) {
      showToast('Failed to copy to clipboard', 'error');
    }
  };

  // Download results as JSON
  const handleDownloadJSON = () => {
    if (!summary || issues.length === 0) {
      showToast('No results to download', 'error');
      return;
    }

    const data = {
      timestamp: new Date().toISOString(),
      language,
      code_lines: code.split('\n').length,
      summary,
      issues,
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code-review-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Downloaded review results', 'success');
  };

  // Apply fix to code
  const handleApplyFix = (issue: CodeIssue) => {
    if (!issue.suggestion) return;

    // For now, just copy the suggestion to clipboard
    // In a real implementation, you'd parse the suggestion and apply it to the code
    navigator.clipboard.writeText(issue.suggestion);
    showToast('Fix copied to clipboard. Apply manually to your code.', 'info');
  };

  // Clear code
  const handleClearCode = () => {
    if (confirm('Are you sure you want to clear all code?')) {
      setCode('');
      setIssues([]);
      setSummary(null);
      setError(null);
      showToast('Code cleared', 'info');
    }
  };

  // Get severity color scheme
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return { badge: 'bg-[#ff6b8a]', text: 'text-[#ff6b8a]', icon: 'security', border: 'border-[#ff6b8a]/20', bg: 'bg-[#ff6b8a]/10' };
      case 'medium':
        return { badge: 'bg-[#a78bfa]', text: 'text-[#a78bfa]', icon: 'warning', border: 'border-[#a78bfa]/20', bg: 'bg-[#a78bfa]/10' };
      case 'low':
      case 'info':
        return { badge: 'bg-[#34d399]', text: 'text-[#34d399]', icon: 'bolt', border: 'border-[#34d399]/20', bg: 'bg-[#34d399]/10' };
      default:
        return { badge: 'bg-gray-500', text: 'text-gray-500', icon: 'info', border: 'border-gray-500/20', bg: 'bg-gray-500/10' };
    }
  };

  // Get severity label
  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'CRITICAL';
      case 'medium':
        return 'WARNING';
      case 'low':
      case 'info':
        return 'SUGGESTION';
      default:
        return severity.toUpperCase();
    }
  };

  // Filter issues by search query
  const filteredIssues = searchQuery
    ? issues.filter(issue =>
        issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : issues;

  return (
    <AppShell>
      <div className="h-full flex overflow-hidden bg-[#0e0e10]">
        {/* Toast Notification */}
        {toast && (
          <div className="fixed top-20 right-6 z-50 animate-in slide-in-from-top-2 duration-300">
            <div className={`px-4 py-3 rounded-lg shadow-2xl border flex items-center gap-3 ${
              toast.type === 'success' ? 'bg-[#19191c] border-[#34d399]/30 text-[#34d399]' :
              toast.type === 'error' ? 'bg-[#19191c] border-[#ff6b8a]/30 text-[#ff6b8a]' :
              'bg-[#19191c] border-[#a3a6ff]/30 text-[#a3a6ff]'
            }`}>
              <span className="material-symbols-outlined text-[20px]">
                {toast.type === 'success' ? 'check_circle' : toast.type === 'error' ? 'error' : 'info'}
              </span>
              <span className="text-sm font-medium">{toast.message}</span>
            </div>
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".js,.ts,.jsx,.tsx,.py,.rs,.go,.java,.cpp,.c,.cs,.rb,.php"
          onChange={handleFileUpload}
          className="hidden"
        />

        {/* Left: Code Input Panel - 50% */}
        <section className="w-1/2 flex flex-col border-r border-[#48474a]/15 bg-[#0e0e10]">
          {/* Top Bar */}
          <div className="p-4 flex items-center justify-between bg-[#131315] shrink-0">
            <div className="flex items-center gap-4">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-transparent border-none text-xs font-semibold text-[#adaaad] focus:ring-0 cursor-pointer hover:text-[#f9f5f8] transition-colors outline-none"
              >
                <option value="typescript">TypeScript</option>
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="rust">Rust</option>
                <option value="go">Go</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="c">C</option>
                <option value="csharp">C#</option>
                <option value="ruby">Ruby</option>
                <option value="php">PHP</option>
              </select>
              <div className="h-4 w-px bg-[#48474a]/30"></div>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={checkBugs}
                    onChange={(e) => setCheckBugs(e.target.checked)}
                    className="hidden peer"
                  />
                  <div className="w-3 h-3 rounded-sm border border-[#767577] peer-checked:bg-[#a3a6ff] peer-checked:border-[#a3a6ff] transition-all duration-300"></div>
                  <span className="text-[10px] uppercase tracking-widest text-[#adaaad] group-hover:text-[#f9f5f8] transition-colors">Bugs</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={checkSecurity}
                    onChange={(e) => setCheckSecurity(e.target.checked)}
                    className="hidden peer"
                  />
                  <div className="w-3 h-3 rounded-sm border border-[#767577] peer-checked:bg-[#8455ef] peer-checked:border-[#8455ef] transition-all duration-300"></div>
                  <span className="text-[10px] uppercase tracking-widest text-[#adaaad] group-hover:text-[#f9f5f8] transition-colors">Security</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={checkStyle}
                    onChange={(e) => setCheckStyle(e.target.checked)}
                    className="hidden peer"
                  />
                  <div className="w-3 h-3 rounded-sm border border-[#767577] peer-checked:bg-[#9bffce] peer-checked:border-[#9bffce] transition-all duration-300"></div>
                  <span className="text-[10px] uppercase tracking-widest text-[#adaaad] group-hover:text-[#f9f5f8] transition-colors">Style</span>
                </label>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleClearCode}
                className="text-xs text-[#767577] font-medium hover:text-[#adaaad] transition-colors flex items-center gap-1.5"
                title="Clear code"
              >
                <span className="material-symbols-outlined text-sm">delete</span>
                Clear
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-xs text-[#a3a6ff] font-medium hover:text-[#9396ff] transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-sm">upload_file</span>
                Upload File
              </button>
            </div>
          </div>

          {/* Code Editor */}
          <div className="flex-1 relative bg-[#000000] overflow-hidden">
            <div className="absolute inset-0 overflow-hidden">
              <CodeMirror
                value={code}
                height="100%"
                theme={oneDark}
                extensions={[
                  getLanguageExtension(),
                  EditorView.lineWrapping,
                  keymap.of([
                    {
                      key: 'Tab',
                      run: (view) => {
                        // Get current selection
                        const selection = view.state.selection.main;
                        
                        // Insert 2 spaces at the exact cursor position
                        view.dispatch({
                          changes: {
                            from: selection.from,
                            to: selection.to,
                            insert: '  '
                          },
                          selection: {
                            anchor: selection.from + 2
                          }
                        });
                        
                        return true;
                      },
                    }
                  ])
                ]}
                onChange={(value) => setCode(value)}
                basicSetup={{
                  lineNumbers: true,
                  highlightActiveLineGutter: true,
                  highlightSpecialChars: true,
                  foldGutter: true,
                  drawSelection: true,
                  dropCursor: true,
                  allowMultipleSelections: true,
                  indentOnInput: false,
                  syntaxHighlighting: true,
                  bracketMatching: true,
                  closeBrackets: true,
                  autocompletion: true,
                  rectangularSelection: true,
                  crosshairCursor: true,
                  highlightActiveLine: true,
                  highlightSelectionMatches: true,
                  closeBracketsKeymap: true,
                  searchKeymap: true,
                  foldKeymap: true,
                  completionKeymap: true,
                  lintKeymap: true,
                }}
                style={{
                  fontSize: '14px',
                  height: '100%',
                  backgroundColor: '#000000',
                }}
                className="h-full [&_.cm-editor]:!bg-[#000000] [&_.cm-gutters]:!bg-[#000000] [&_.cm-activeLineGutter]:!bg-[#000000] [&_.cm-scroller]:!bg-[#000000] [&_.cm-content]:!bg-[#000000]"
              />
            </div>
            <div className="absolute bottom-6 right-6">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !code.trim()}
                className="bg-gradient-to-r from-[#a3a6ff] to-[#ac8aff] text-[#0f00a4] font-bold px-6 py-3 rounded-md shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="material-symbols-outlined">{isAnalyzing ? 'hourglass_empty' : 'auto_awesome'}</span>
                {isAnalyzing ? 'Analyzing...' : 'Analyze Code'}
              </button>
            </div>
          </div>
        </section>

        {/* Right: Review Results Panel - 50% */}
        <section className="w-1/2 flex flex-col bg-[#131315]">
          {summary ? (
            <>
              {/* Summary Bar */}
              <div className="p-6 bg-[#19191c] shrink-0">
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-extrabold tracking-tight mb-1 text-[#f9f5f8]">Analysis Complete</h2>
                    <p className="text-xs text-[#adaaad]">
                      {summary.total_issues} issue{summary.total_issues !== 1 ? 's' : ''} identified in {code.split('\n').length} lines of code
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyResults}
                      className="p-2 bg-[#2c2c2f] rounded text-[#adaaad] hover:text-[#f9f5f8] border border-[#48474a]/15 transition-all"
                      title="Copy results to clipboard"
                    >
                      <span className="material-symbols-outlined">content_copy</span>
                    </button>
                    <button
                      onClick={handleDownloadJSON}
                      className="p-2 bg-[#2c2c2f] rounded text-[#adaaad] hover:text-[#f9f5f8] border border-[#48474a]/15 transition-all"
                      title="Download as JSON"
                    >
                      <span className="material-symbols-outlined">download</span>
                    </button>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-[#0e0e10] p-3 rounded border-l-4 border-[#d73357]">
                    <div className="text-[10px] uppercase tracking-widest text-[#adaaad] mb-1">Critical</div>
                    <div className="text-2xl font-bold text-[#d73357]">{summary.critical_count + summary.high_count}</div>
                  </div>
                  <div className="bg-[#0e0e10] p-3 rounded border-l-4 border-[#8455ef]">
                    <div className="text-[10px] uppercase tracking-widest text-[#adaaad] mb-1">Warning</div>
                    <div className="text-2xl font-bold text-[#8455ef]">{summary.medium_count}</div>
                  </div>
                  <div className="bg-[#0e0e10] p-3 rounded border-l-4 border-[#9bffce]">
                    <div className="text-[10px] uppercase tracking-widest text-[#adaaad] mb-1">Suggestion</div>
                    <div className="text-2xl font-bold text-[#9bffce]">{summary.low_count + summary.info_count}</div>
                  </div>
                </div>

                {/* Search Bar */}
                {issues.length > 0 && (
                  <div className="mt-4 relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-[#767577] text-sm">search</span>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search issues..."
                      className="w-full bg-[#0e0e10] border border-[#48474a]/30 rounded-md pl-9 pr-4 py-2 text-xs text-[#f9f5f8] placeholder:text-[#767577] outline-none focus:border-[#a3a6ff]/50 transition-colors"
                    />
                  </div>
                )}
              </div>

              {/* Issue List */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                {filteredIssues.length === 0 ? (
                  <div className="text-center py-12">
                    <span className="material-symbols-outlined text-4xl text-[#48474a] mb-2 block">search_off</span>
                    <p className="text-[#adaaad] text-sm">No issues match your search</p>
                  </div>
                ) : (
                  filteredIssues.map((issue, index) => {
                    const colors = getSeverityColor(issue.severity);
                    const isExpanded = expandedIssues.has(index);
                    
                    return (
                      <div
                        key={index}
                        className={`bg-[#19191c] rounded-lg border ${colors.border} overflow-hidden transition-all duration-300 hover:border-opacity-50`}
                      >
                        <div className="p-4 flex items-start gap-4">
                          <div className={`w-8 h-8 rounded ${colors.bg} flex items-center justify-center shrink-0`}>
                            <span className={`material-symbols-outlined ${colors.text}`}>{colors.icon}</span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`px-2 py-0.5 rounded-full ${colors.badge} text-[10px] font-bold text-[#0e0e10] uppercase tracking-wider`}>
                                {getSeverityLabel(issue.severity)}
                              </span>
                              <h3 className="text-sm font-bold text-[#f9f5f8]">{issue.title}</h3>
                              {issue.line_number && (
                                <span className="text-[10px] text-[#767577] font-mono">Line {issue.line_number}</span>
                              )}
                            </div>
                            <p className="text-xs text-[#adaaad] leading-relaxed">
                              {issue.description}
                            </p>
                            {issue.suggestion && (
                              <>
                                {isExpanded && (
                                  <div className="mt-4 border border-[#48474a]/20 rounded-md bg-[#000000]">
                                    <div className="px-3 py-2 border-b border-[#48474a]/10 flex items-center justify-between">
                                      <span className="text-[10px] font-mono text-[#767577] uppercase tracking-wider">Suggested Fix</span>
                                      <button
                                        onClick={() => handleApplyFix(issue)}
                                        className="text-[10px] font-bold text-[#a3a6ff] hover:underline"
                                      >
                                        COPY FIX
                                      </button>
                                    </div>
                                    <div className="p-3 font-mono text-[11px] leading-tight text-[#adaaad] whitespace-pre-wrap">
                                      {issue.suggestion}
                                    </div>
                                  </div>
                                )}
                                <button
                                  onClick={() => toggleIssue(index)}
                                  className="mt-3 flex items-center gap-2 text-[10px] font-bold text-[#767577] uppercase tracking-widest hover:text-[#adaaad] transition-colors"
                                >
                                  {isExpanded ? 'Hide' : 'Show'} suggested fix
                                  <span className={`material-symbols-outlined text-[14px] transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                                    expand_more
                                  </span>
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Footer Export */}
              <div className="p-6 border-t border-[#48474a]/15 bg-[#0e0e10] flex justify-between items-center shrink-0">
                <div className="flex items-center gap-2 text-xs text-[#767577]">
                  <span className="w-2 h-2 rounded-full bg-[#9bffce] animate-pulse"></span>
                  Scanning complete
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setIssues([]);
                      setSummary(null);
                      setSearchQuery('');
                      setExpandedIssues(new Set());
                    }}
                    className="px-4 py-2 text-xs font-bold text-[#adaaad] hover:text-[#f9f5f8] transition-colors"
                  >
                    Dismiss All
                  </button>
                  <button
                    onClick={handleDownloadJSON}
                    className="px-4 py-2 bg-[#2c2c2f] border border-[#48474a]/30 rounded text-xs font-bold text-[#f9f5f8] hover:bg-[#262528] transition-all flex items-center gap-2"
                  >
                    <span className="material-symbols-outlined text-[16px]">file_download</span>
                    Download JSON
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <span className="material-symbols-outlined text-6xl text-[#48474a] mb-4 block">code</span>
                <p className="text-[#adaaad] text-sm mb-2">Paste your code and click "Analyze Code" to begin</p>
                <p className="text-[#767577] text-xs">Or drag and drop a file</p>
                {error && (
                  <div className="mt-4 px-4 py-2 bg-[#ff6b8a]/10 border border-[#ff6b8a]/30 rounded text-[#ff6b8a] text-xs">
                    {error}
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}
