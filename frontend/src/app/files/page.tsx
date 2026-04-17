'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';
import { api } from '@/lib/api';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { rust } from '@codemirror/lang-rust';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { php } from '@codemirror/lang-php';
import { oneDark } from '@codemirror/theme-one-dark';
import { useResize } from '@/hooks/useResize';

// ─── Types ────────────────────────────────────────────────────────────────────

interface FileEntry {
  file_path: string;
  language: string | null;
  start_line: number;
  end_line: number;
  chunk_count: number;
}

interface FileContent {
  file_path: string;
  language: string | null;
  content: string;
  start_line: number;
  end_line: number;
}

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'dir';
  language?: string | null;
  children?: TreeNode[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildTree(files: FileEntry[]): TreeNode[] {
  const root: Record<string, any> = {};

  for (const file of files) {
    const parts = file.file_path.split('/');
    let node = root;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (!node[part]) {
        node[part] = i === parts.length - 1
          ? { __file: true, __language: file.language, __path: file.file_path }
          : {};
      }
      node = node[part];
    }
  }

  function toNodes(obj: Record<string, any>, basePath: string): TreeNode[] {
    return Object.entries(obj)
      .filter(([k]) => !k.startsWith('__'))
      .map(([name, val]) => {
        const path = basePath ? `${basePath}/${name}` : name;
        if (val.__file) {
          return { name, path: val.__path, type: 'file' as const, language: val.__language };
        }
        return {
          name,
          path,
          type: 'dir' as const,
          children: toNodes(val, path),
        };
      })
      .sort((a, b) => {
        if (a.type !== b.type) return a.type === 'dir' ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
  }

  return toNodes(root, '');
}

const LANG_COLORS: Record<string, string> = {
  python: 'bg-blue-500',
  javascript: 'bg-yellow-400',
  typescript: 'bg-blue-400',
  rust: 'bg-orange-500',
  go: 'bg-cyan-400',
  java: 'bg-red-500',
  cpp: 'bg-purple-500',
  c: 'bg-gray-400',
  html: 'bg-orange-400',
  css: 'bg-pink-400',
  json: 'bg-green-400',
  markdown: 'bg-gray-300',
};

function langColor(lang: string | null | undefined) {
  return LANG_COLORS[lang?.toLowerCase() ?? ''] ?? 'bg-outline-variant';
}

function fileIcon(lang: string | null | undefined) {
  const l = lang?.toLowerCase();
  if (l === 'python') return 'code';
  if (l === 'javascript' || l === 'typescript') return 'javascript';
  if (l === 'rust') return 'memory';
  if (l === 'json') return 'data_object';
  if (l === 'markdown') return 'article';
  return 'description';
}

// ─── Tree Node Component ──────────────────────────────────────────────────────

function TreeItem({
  node,
  depth,
  selectedPath,
  onSelect,
}: {
  node: TreeNode;
  depth: number;
  selectedPath: string | null;
  onSelect: (node: TreeNode) => void;
}) {
  const [open, setOpen] = useState(depth < 2);

  const handleFolderClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setOpen(prev => !prev);
  };

  if (node.type === 'file') {
    return (
      <button
        onClick={() => onSelect(node)}
        className={`w-full flex items-center gap-1.5 py-1 pr-2 rounded text-left transition-colors text-[13px] ${
          selectedPath === node.path
            ? 'bg-primary/15 text-primary'
            : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        <span className="material-symbols-outlined text-[15px] flex-shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>
          {fileIcon(node.language)}
        </span>
        <span className="truncate">{node.name}</span>
      </button>
    );
  }

  return (
    <div>
      <button
        onClick={handleFolderClick}
        className="w-full flex items-center gap-1.5 py-1 pr-2 rounded text-left text-on-surface-variant hover:bg-surface-container transition-colors text-[13px]"
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        <span className="material-symbols-outlined text-[15px] flex-shrink-0">
          {open ? 'folder_open' : 'folder'}
        </span>
        <span className="truncate font-medium">{node.name}</span>
        <span className="material-symbols-outlined text-[13px] ml-auto flex-shrink-0">
          {open ? 'expand_less' : 'expand_more'}
        </span>
      </button>
      {open && node.children?.map(child => (
        <TreeItem
          key={child.path}
          node={child}
          depth={depth + 1}
          selectedPath={selectedPath}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function FilesPage() {
  const router = useRouter();
  const [repositories, setRepositories] = useState<Array<{ id: string; name: string }>>([]);
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileEntry | null>(null);
  const [fileContent, setFileContent] = useState<FileContent | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [activeLanguages, setActiveLanguages] = useState<Set<string>>(new Set());
  const [copied, setCopied] = useState(false);

  const aiPanel = useResize(288, 200, 480, 'left');

  // Get CodeMirror language extension
  const getLanguageExtension = (lang: string | null) => {
    const language = lang?.toLowerCase() ?? '';
    switch (language) {
      case 'javascript':
        return javascript({ jsx: true });
      case 'typescript':
        return javascript({ jsx: true, typescript: true });
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



  // Load repositories on mount
  useEffect(() => {
    api.listRepositories().then(({ repositories: repos }) => {
      const completed = repos.filter(r => r.status === 'completed');
      setRepositories(completed.map(r => ({ id: r.id, name: `${r.owner}/${r.name}` })));
      if (completed.length > 0) setSelectedRepo(completed[0].id);
    }).catch(console.error);
  }, []);

  // Load files when repo changes
  useEffect(() => {
    if (!selectedRepo) return;
    setIsLoadingFiles(true);
    setFiles([]);
    setSelectedFile(null);
    setFileContent(null);
    api.listRepositoryFiles(selectedRepo)
      .then(({ files: f }) => setFiles(f))
      .catch(console.error)
      .finally(() => setIsLoadingFiles(false));
  }, [selectedRepo]);

  // Load file content when file selected
  useEffect(() => {
    if (!selectedFile || !selectedRepo) return;
    setIsLoadingContent(true);
    setFileContent(null);
    api.getFileContent(selectedRepo, selectedFile.file_path)
      .then(setFileContent)
      .catch(console.error)
      .finally(() => setIsLoadingContent(false));
  }, [selectedFile, selectedRepo]);

  // Unique languages in repo
  const languages = useMemo(() => {
    const langs = new Set(files.map(f => f.language).filter(Boolean) as string[]);
    return Array.from(langs).sort();
  }, [files]);

  // Filtered files
  const filteredFiles = useMemo(() => {
    if (activeLanguages.size === 0) return files;
    return files.filter(f => f.language && activeLanguages.has(f.language));
  }, [files, activeLanguages]);

  const tree = useMemo(() => buildTree(filteredFiles), [filteredFiles]);

  function toggleLanguage(lang: string) {
    setActiveLanguages(prev => {
      const next = new Set(prev);
      next.has(lang) ? next.delete(lang) : next.add(lang);
      return next;
    });
  }

  function handleSelectFile(node: TreeNode) {
    if (node.type !== 'file') return;
    const entry = files.find(f => f.file_path === node.path) ?? null;
    setSelectedFile(entry);
  }

  function handleCopy() {
    if (!fileContent) return;
    navigator.clipboard.writeText(fileContent.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleAskAI() {
    if (!fileContent) return;
    router.push(`/chat?file=${encodeURIComponent(fileContent.file_path)}`);
  }

  // Breadcrumb parts
  const breadcrumbs = selectedFile
    ? selectedFile.file_path.split('/')
    : [];

  const repoName = repositories.find(r => r.id === selectedRepo)?.name ?? '';

  return (
    <AppShell>
      <div className="flex h-full overflow-hidden">

        {/* ── Left: File Tree ─────────────────────────────────────────── */}
        <aside
          className="flex-shrink-0 flex flex-col bg-surface-container-low border-r border-outline-variant/10 overflow-hidden"
          style={{ width: '288px' }}
        >

          {/* Language filters */}
          <div className="px-4 pt-4 pb-2 border-b border-outline-variant/10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase font-bold tracking-[0.2em] text-outline">Language Filters</span>
              {activeLanguages.size > 0 && (
                <button onClick={() => setActiveLanguages(new Set())} className="text-[10px] text-primary hover:underline">
                  Clear
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {languages.map(lang => (
                <button
                  key={lang}
                  onClick={() => toggleLanguage(lang)}
                  className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border transition-colors ${
                    activeLanguages.has(lang)
                      ? 'bg-primary/15 border-primary/40 text-primary'
                      : 'bg-surface-container border-outline-variant/20 text-on-surface-variant hover:border-primary/30'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${langColor(lang)}`} />
                  {lang.charAt(0).toUpperCase() + lang.slice(1)}
                </button>
              ))}
              {languages.length === 0 && !isLoadingFiles && (
                <span className="text-xs text-outline">No files indexed</span>
              )}
            </div>
          </div>

          {/* Tree */}
          <div className="flex-1 overflow-y-auto py-2 px-1">
            {isLoadingFiles ? (
              <div className="flex items-center justify-center h-20 text-xs text-outline">
                <span className="material-symbols-outlined animate-spin text-sm mr-2">progress_activity</span>
                Loading files...
              </div>
            ) : tree.length === 0 ? (
              <div className="text-center text-xs text-outline py-8">
                {selectedRepo ? 'No files found' : 'Select a repository'}
              </div>
            ) : (
              tree.map(node => (
                <TreeItem
                  key={node.path}
                  node={node}
                  depth={0}
                  selectedPath={selectedFile?.file_path ?? null}
                  onSelect={handleSelectFile}
                />
              ))
            )}
          </div>
        </aside>

        {/* ── Center: Code Viewer ──────────────────────────────────────── */}
        <main className="flex-1 flex flex-col overflow-hidden bg-surface-container-lowest">
          {fileContent ? (
            <>
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-3 border-b border-outline-variant/10 bg-surface-container-low/60 backdrop-blur flex-shrink-0">
                <div className="flex flex-col min-w-0">
                  <div className="flex items-center gap-1.5 text-xs text-on-surface-variant mb-0.5">
                    <span className="material-symbols-outlined text-[14px]">account_tree</span>
                    {[repoName.split('/')[1] ?? repoName, ...breadcrumbs.slice(0, -1)].map((part, i) => (
                      <span key={i} className="flex items-center gap-1">
                        {i > 0 && <span className="text-outline">›</span>}
                        {part}
                      </span>
                    ))}
                  </div>
                  <h2 className="text-sm font-bold text-on-surface truncate">{breadcrumbs.at(-1)}</h2>
                  <span className="text-[10px] text-outline font-mono">
                    Lines {fileContent.start_line}–{fileContent.end_line} · {fileContent.language ?? 'text'}
                  </span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-semibold rounded-md transition-all border border-outline-variant/20"
                  >
                    <span className="material-symbols-outlined text-sm">{copied ? 'check' : 'content_copy'}</span>
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button
                    onClick={handleAskAI}
                    className="flex items-center gap-1.5 px-4 py-1.5 bg-gradient-to-r from-primary to-secondary text-on-primary text-xs font-bold rounded-md transition-all"
                  >
                    <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>chat_bubble</span>
                    Ask AI about this file
                  </button>
                </div>
              </div>

              {/* Code */}
              <div className="flex-1 overflow-hidden bg-[#000000]">
                <CodeMirror
                  value={fileContent.content}
                  height="100%"
                  theme={oneDark}
                  extensions={[getLanguageExtension(fileContent.language)]}
                  editable={false}
                  readOnly={true}
                  basicSetup={{
                    lineNumbers: true,
                    highlightActiveLineGutter: false,
                    highlightSpecialChars: true,
                    foldGutter: true,
                    drawSelection: false,
                    dropCursor: false,
                    allowMultipleSelections: false,
                    indentOnInput: false,
                    syntaxHighlighting: true,
                    bracketMatching: true,
                    closeBrackets: false,
                    autocompletion: false,
                    rectangularSelection: false,
                    crosshairCursor: false,
                    highlightActiveLine: false,
                    highlightSelectionMatches: false,
                    closeBracketsKeymap: false,
                    searchKeymap: true,
                    foldKeymap: true,
                    completionKeymap: false,
                    lintKeymap: false,
                  }}
                  style={{
                    fontSize: '13px',
                    height: '100%',
                    backgroundColor: '#000000',
                  }}
                  className="h-full [&_.cm-editor]:!bg-[#000000] [&_.cm-gutters]:!bg-[#000000] [&_.cm-activeLineGutter]:!bg-[#000000] [&_.cm-scroller]:!bg-[#000000] [&_.cm-content]:!bg-[#000000]"
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              {isLoadingContent ? (
                <div className="flex flex-col items-center gap-3 text-outline">
                  <span className="material-symbols-outlined text-4xl animate-spin">progress_activity</span>
                  <span className="text-sm">Loading file...</span>
                </div>
              ) : (
                <div className="text-center">
                  <span className="material-symbols-outlined text-outline text-6xl mb-4 block">description</span>
                  <p className="text-on-surface-variant text-sm">Search and select a file to view its contents</p>
                </div>
              )}
            </div>
          )}
        </main>

        {/* ── Right: AI Analysis Panel ─────────────────────────────────── */}
        {fileContent && (
          <aside
            className="flex-shrink-0 flex flex-col bg-surface-container-low border-l border-outline-variant/10 overflow-y-auto relative"
            style={{ width: aiPanel.size }}
          >
            {/* Left resize handle */}
            <div
              onMouseDown={aiPanel.onMouseDown}
              className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize z-10 group"
            >
              <div className="absolute inset-0 bg-outline-variant/10 group-hover:bg-primary/40 transition-colors" />
            </div>
            <AIAnalysisPanel file={fileContent} />
          </aside>
        )}
      </div>
    </AppShell>
  );
}

// ─── AI Analysis Panel ────────────────────────────────────────────────────────

function AIAnalysisPanel({ file }: { file: FileContent }) {
  const analysis = useMemo(() => analyzeFile(file), [file.file_path]);

  return (
    <div className="p-4 space-y-5">
      {/* Purpose */}
      <section>
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-outlined text-primary text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
          <span className="text-[10px] uppercase font-bold tracking-[0.15em] text-outline">Purpose</span>
        </div>
        <p className="text-xs text-on-surface-variant leading-relaxed">{analysis.purpose}</p>
      </section>

      {/* Main Functions */}
      {analysis.functions.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-secondary text-[16px]">functions</span>
            <span className="text-[10px] uppercase font-bold tracking-[0.15em] text-outline">Main Functions</span>
          </div>
          <div className="space-y-2">
            {analysis.functions.map((fn, i) => (
              <div key={i}>
                <code className="text-[11px] text-primary font-mono">{fn.name}</code>
                <p className="text-[11px] text-on-surface-variant mt-0.5">{fn.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Dependencies */}
      {analysis.dependencies.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-tertiary text-[16px]">hub</span>
            <span className="text-[10px] uppercase font-bold tracking-[0.15em] text-outline">Dependencies</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {analysis.dependencies.map((dep, i) => (
              <span key={i} className="px-2 py-0.5 bg-surface-container rounded text-[11px] text-on-surface-variant border border-outline-variant/15 font-mono">
                {dep}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* AI Insight */}
      <section className="bg-primary/5 border border-primary/15 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-outlined text-primary text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
          <span className="text-[10px] uppercase font-bold tracking-[0.15em] text-primary">AI Insight</span>
        </div>
        <p className="text-[11px] text-on-surface-variant leading-relaxed italic">"{analysis.insight}"</p>
      </section>
    </div>
  );
}

// ─── Static analysis helper ───────────────────────────────────────────────────

function analyzeFile(file: FileContent) {
  const lines = file.content.split('\n');
  const lang = file.language?.toLowerCase() ?? '';
  const fileName = file.file_path.split('/').pop() ?? '';

  // Extract imports/dependencies
  const deps = new Set<string>();
  const fnRegexes: RegExp[] = [];

  if (lang === 'python') {
    lines.forEach(l => {
      const m = l.match(/^(?:import|from)\s+([\w.]+)/);
      if (m) deps.add(m[1].split('.')[0]);
    });
    fnRegexes.push(/^def\s+(\w+)\s*\(/);
  } else if (lang === 'javascript' || lang === 'typescript') {
    lines.forEach(l => {
      const m = l.match(/(?:import|require)\s*(?:\{[^}]*\}|[\w*]+)\s*(?:from\s*)?['"]([^'"]+)['"]/);
      if (m) deps.add(m[1].replace(/^[./]+/, '').split('/')[0]);
    });
    fnRegexes.push(/(?:function|const|async function)\s+(\w+)\s*[=(]/);
  } else if (lang === 'rust') {
    lines.forEach(l => {
      const m = l.match(/^use\s+([\w:]+)/);
      if (m) deps.add(m[1].split('::')[0]);
    });
    fnRegexes.push(/^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)/);
  }

  // Extract functions
  const functions: Array<{ name: string; description: string }> = [];
  for (const line of lines) {
    for (const re of fnRegexes) {
      const m = line.match(re);
      if (m && functions.length < 4) {
        functions.push({ name: `${m[1]}()`, description: `Handles ${m[1].replace(/_/g, ' ')} logic.` });
      }
    }
  }

  // Purpose
  const lineCount = lines.length;
  const purpose = `This ${lang || 'code'} file (${fileName}) contains ${lineCount} lines and defines ${functions.length} function${functions.length !== 1 ? 's' : ''}. It appears to handle ${fileName.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' ')} functionality.`;

  // Insight
  const insights = [
    'Consider adding unit tests to improve code coverage.',
    'Some functions could benefit from more descriptive variable names.',
    'This file has good separation of concerns.',
    'Consider extracting repeated logic into helper functions.',
    'The code structure follows common patterns for this language.',
  ];
  const insight = insights[fileName.length % insights.length];

  return {
    purpose,
    functions,
    dependencies: Array.from(deps).slice(0, 6),
    insight,
  };
}
