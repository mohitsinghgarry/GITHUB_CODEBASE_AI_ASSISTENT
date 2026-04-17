'use client';

import { AppShell } from '@/components/layout/AppShell';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { api, type ChatMessage, type Citation } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { rust } from '@codemirror/lang-rust';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { php } from '@codemirror/lang-php';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView } from '@codemirror/view';
import { ContextPanel } from '@/components/chat/ContextPanel';
import { useResize } from '@/hooks/useResize';

const GROQ_MODEL_LABELS: Record<string, string> = {
  'openai/gpt-oss-120b': 'GPT-OSS 120B',
  'openai/gpt-oss-20b': 'GPT-OSS 20B',
  'llama-3.3-70b-versatile': 'Llama 3.3 70B',
  'llama-3.1-8b-instant': 'Llama 3.1 8B (Fast)',
  'mixtral-8x7b-32768': 'Mixtral 8x7B',
  'llama-3.1-70b-versatile': 'Llama 3.1 70B',
  'gemma2-9b-it': 'Gemma 2 9B',
};

// Custom hook for media query
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);

  return matches;
}

// Get CodeMirror language extension based on language string
const getLanguageExtension = (language: string) => {
  switch (language.toLowerCase()) {
    case 'javascript':
    case 'js':
    case 'jsx':
      return javascript({ jsx: true });
    case 'typescript':
    case 'ts':
    case 'tsx':
      return javascript({ jsx: true, typescript: true });
    case 'python':
    case 'py':
      return python();
    case 'rust':
    case 'rs':
      return rust();
    case 'java':
      return java();
    case 'cpp':
    case 'c++':
    case 'c':
      return cpp();
    case 'php':
      return php();
    default:
      return javascript();
  }
};

export default function ChatPage() {
  const router = useRouter();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [repositories, setRepositories] = useState<Array<{ id: string; name: string }>>([]);
  const [selectedRepos, setSelectedRepos] = useState<string[]>([]);
  const [models, setModels] = useState<Array<{ id: string; name: string; description: string }>>([]);
  const [selectedModel, setSelectedModel] = useState<string>('openai/gpt-oss-120b');
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Context panel state management
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const [currentCitationIndex, setCurrentCitationIndex] = useState<number>(0);
  const contextPanel = useResize(500, 300, 800, 'left');
  
  // Responsive state - check if viewport is below 1200px
  const isNarrowViewport = useMediaQuery('(max-width: 1199px)');
  const [isPanelVisible, setIsPanelVisible] = useState(true);

  // Citation click handler
  const handleCitationClick = (citation: Citation, allCitations: Citation[], index: number) => {
    setSelectedCitation(citation);
    setActiveCitations(allCitations);
    setCurrentCitationIndex(index);
    // Show panel when citation is clicked (important for overlay mode)
    if (isNarrowViewport) {
      setIsPanelVisible(true);
    }
  };

  // Citation navigation handler
  const handleNavigate = (direction: 'next' | 'prev') => {
    const newIndex = direction === 'next' 
      ? Math.min(currentCitationIndex + 1, activeCitations.length - 1)
      : Math.max(currentCitationIndex - 1, 0);
    
    // Only update if index actually changed
    if (newIndex !== currentCitationIndex) {
      setCurrentCitationIndex(newIndex);
      setSelectedCitation(activeCitations[newIndex]);
    }
  };

  // Open in viewer handler
  const handleOpenInViewer = (filePath: string) => {
    router.push(`/viewer?file=${encodeURIComponent(filePath)}`);
  };
  
  // Dismiss handler for overlay mode
  const handleDismissPanel = () => {
    setIsPanelVisible(false);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch repositories
        const { repositories: repos } = await api.listRepositories();
        const completedRepos = repos.filter(r => r.status === 'completed');
        setRepositories(completedRepos.map(r => ({ id: r.id, name: `${r.owner}/${r.name}` })));
        if (completedRepos.length > 0) {
          setSelectedRepos([completedRepos[0].id]);
        }
      } catch (err) {
        console.error('Failed to fetch repositories:', err);
      }

      try {
        // Fetch available models
        const { models: availableModels } = await api.getChatModels();
        setModels(availableModels);
        if (availableModels.length > 0) {
          setSelectedModel(availableModels[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch models:', err);
        // Fallback to default models
        setModels([
          { id: 'openai/gpt-oss-120b', name: 'GPT-OSS 120B', description: 'Flagship open model with reasoning' },
          { id: 'openai/gpt-oss-20b', name: 'GPT-OSS 20B', description: 'Ultra fast, cost-effective' },
          { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B', description: 'Best balance of speed and quality' },
          { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B (Fast)', description: 'Ultra fast responses' },
          { id: 'mixtral-8x7b-32768', name: 'Mixtral 8x7B', description: 'Great for code, 32K context' },
          { id: 'gemma2-9b-it', name: 'Gemma 2 9B', description: 'Efficient and capable' },
        ]);
      }

      // Load the most recent chat session if available
      try {
        const { sessions } = await api.listChatSessions();
        if (sessions.length > 0) {
          const mostRecentSession = sessions[0]; // Already sorted by updated_at desc
          const sessionData = await api.getChatSession(mostRecentSession.id);
          
          // Restore session state
          setSessionId(sessionData.session_id);
          setMessages(sessionData.messages);
          setSelectedRepos(sessionData.repository_ids);
          
          // Auto-select first citation from last assistant message if available
          const lastAssistantMsg = sessionData.messages.filter(m => m.role === 'assistant').pop();
          if (lastAssistantMsg?.citations && lastAssistantMsg.citations.length > 0) {
            setSelectedCitation(lastAssistantMsg.citations[0]);
            setActiveCitations(lastAssistantMsg.citations);
            setCurrentCitationIndex(0);
          }
          
          console.log(`Restored session ${sessionData.session_id} with ${sessionData.messages.length} messages`);
        }
      } catch (err) {
        console.error('Failed to load previous session:', err);
        // Not a critical error, just start with a fresh session
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  const handleSendMessage = async () => {
    if (!message.trim() || isStreaming) return;
    if (selectedRepos.length === 0) {
      setError('Please select at least one repository');
      return;
    }

    const userMessage = message;
    setMessage('');
    setError('');

    const newUserMessage: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, newUserMessage]);

    setIsStreaming(true);
    setStreamingMessage('');
    let fullResponse = '';
    let citations: Citation[] = [];

    try {
      for await (const chunk of api.chatStream({
        message: userMessage,
        repository_ids: selectedRepos,
        session_id: sessionId || undefined,
        model: selectedModel,
        explanation_mode: 'technical',
      })) {
        if (chunk.done) break;
        fullResponse += chunk.chunk;
        setStreamingMessage(fullResponse);
        if (chunk.citations) citations = chunk.citations;
        if (chunk.session_id) setSessionId(chunk.session_id);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: fullResponse,
        timestamp: new Date().toISOString(),
        citations,
      }]);
      setStreamingMessage('');

      // Auto-select first citation when new assistant message with citations arrives
      if (citations && citations.length > 0) {
        setSelectedCitation(citations[0]);
        setActiveCitations(citations);
        setCurrentCitationIndex(0);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    if (msg.role === 'user') {
      return (
        <div key={index} className="flex gap-6 justify-end">
          <div className="flex-1 max-w-xl bg-surface-container-low p-4 rounded-xl border border-outline-variant/10 text-on-surface leading-relaxed">
            {msg.content}
          </div>
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex-shrink-0 flex items-center justify-center border border-primary/20">
            <span className="material-symbols-outlined text-primary text-xl">person</span>
          </div>
        </div>
      );
    }

    return (
      <div key={index} className="flex gap-6 group">
        <div className="w-8 h-8 rounded-lg bg-surface-container-high flex-shrink-0 flex items-center justify-center border border-outline-variant/10">
          <span className="material-symbols-outlined text-primary text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            smart_toy
          </span>
        </div>
        <div className="flex-1 space-y-4">
          <div className="text-on-surface leading-relaxed prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code: ({ node, inline, className, children, ...props }: any) => {
                  const match = /language-(\w+)/.exec(className || '');
                  const language = match ? match[1] : '';
                  const codeString = String(children).replace(/\n$/, '');
                  
                  return !inline && language ? (
                    <div className="my-4">
                      <CodeMirror
                        value={codeString}
                        extensions={[getLanguageExtension(language), EditorView.lineWrapping]}
                        theme={oneDark}
                        editable={false}
                        readOnly={true}
                        basicSetup={{
                          lineNumbers: true,
                          highlightActiveLineGutter: false,
                          highlightSpecialChars: true,
                          foldGutter: false,
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
                          foldKeymap: false,
                          completionKeymap: false,
                          lintKeymap: false,
                        }}
                        style={{
                          fontSize: '14px',
                          backgroundColor: '#000000',
                        }}
                        className="rounded-lg overflow-hidden border border-white/10 [&_.cm-editor]:!bg-[#000000] [&_.cm-gutters]:!bg-[#000000] [&_.cm-scroller]:!bg-[#000000] [&_.cm-content]:!bg-[#000000]"
                      />
                    </div>
                  ) : !inline ? (
                    <code className="block bg-[#000000] text-sm font-mono p-3 rounded-lg my-4 whitespace-pre-wrap border border-white/10" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className="bg-surface-container/50 px-1.5 py-0.5 rounded text-[13px] font-mono text-primary/90" {...props}>
                      {children}
                    </code>
                  );
                },
                pre: ({ children }: any) => <>{children}</>,
                p: ({ children }: any) => <p className="mb-4 last:mb-0">{children}</p>,
                ul: ({ children }: any) => <ul className="list-disc list-inside mb-4 space-y-1.5 ml-2">{children}</ul>,
                ol: ({ children }: any) => <ol className="list-decimal list-inside mb-4 space-y-1.5 ml-2">{children}</ol>,
                li: ({ children }: any) => <li className="text-on-surface leading-relaxed">{children}</li>,
                h1: ({ children }: any) => <h1 className="text-xl font-bold mb-3 mt-6 first:mt-0">{children}</h1>,
                h2: ({ children }: any) => <h2 className="text-lg font-bold mb-2 mt-5 first:mt-0">{children}</h2>,
                h3: ({ children }: any) => <h3 className="text-base font-bold mb-2 mt-4 first:mt-0">{children}</h3>,
                blockquote: ({ children }: any) => (
                  <blockquote className="border-l-4 border-primary/30 pl-4 italic text-on-surface-variant my-4">
                    {children}
                  </blockquote>
                ),
                a: ({ children, href }: any) => (
                  <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
                table: ({ children }: any) => (
                  <div className="overflow-x-auto my-4">
                    <table className="min-w-full border border-outline-variant/20 rounded-lg">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }: any) => (
                  <thead className="bg-surface-container-high">{children}</thead>
                ),
                tbody: ({ children }: any) => <tbody>{children}</tbody>,
                tr: ({ children }: any) => (
                  <tr className="border-b border-outline-variant/10">{children}</tr>
                ),
                th: ({ children }: any) => (
                  <th className="px-4 py-2 text-left text-sm font-semibold">{children}</th>
                ),
                td: ({ children }: any) => (
                  <td className="px-4 py-2 text-sm">{children}</td>
                ),
              }}
            >
              {msg.content}
            </ReactMarkdown>
          </div>
          {msg.citations && msg.citations.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              <span className="text-[10px] text-on-surface-variant uppercase tracking-widest block w-full mb-1">Sources</span>
              {msg.citations.map((citation, idx) => (
                <div
                  key={idx}
                  onClick={() => handleCitationClick(citation, msg.citations!, idx)}
                  className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] border cursor-pointer transition-colors ${
                    selectedCitation?.chunk_id === citation.chunk_id
                      ? 'bg-primary/20 border-primary/50 text-primary'
                      : 'bg-surface-container text-on-surface-variant border-outline-variant/10 hover:border-primary/30'
                  }`}
                  title={citation.content}
                >
                  <span className="material-symbols-outlined text-xs">description</span>
                  {citation.file_path}:{citation.start_line}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  const selectedModelLabel = GROQ_MODEL_LABELS[selectedModel] || selectedModel;

  return (
    <AppShell>
      <div className="flex h-full">
        {/* Message Area - flex-1 with min-width of 600px */}
        <div className="flex-1 flex flex-col min-w-[600px]">

          {/* Top Bar */}
          <div className="h-14 border-b border-outline-variant/10 flex items-center justify-between px-6 bg-surface gap-4">
            {/* Repository Selector */}
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold uppercase tracking-widest text-outline">Repo:</span>
              <select
                value={selectedRepos[0] || ''}
                onChange={(e) => setSelectedRepos(e.target.value ? [e.target.value] : [])}
                className="bg-surface-container border border-outline-variant/20 rounded-lg px-3 py-1.5 text-sm text-on-surface focus:outline-none focus:border-primary/50"
              >
                <option value="">Select repository...</option>
                {repositories.map(repo => (
                  <option key={repo.id} value={repo.id}>{repo.name}</option>
                ))}
              </select>
            </div>

            {/* Model Selector */}
            <div className="flex items-center gap-3">
              {/* Groq Badge */}
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#f55036]/10 border border-[#f55036]/20">
                <span className="text-[10px] font-bold text-[#f55036] uppercase tracking-wider">⚡ Groq</span>
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-outline">Model:</span>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-surface-container border border-outline-variant/20 rounded-lg px-3 py-1.5 text-sm text-on-surface focus:outline-none focus:border-primary/50 min-w-[200px]"
              >
                {models.length > 0 ? models.map(model => (
                  <option key={model.id} value={model.id}>
                    {GROQ_MODEL_LABELS[model.id] || model.name}
                  </option>
                )) : (
                  <>
                    <option value="openai/gpt-oss-120b">GPT-OSS 120B</option>
                    <option value="openai/gpt-oss-20b">GPT-OSS 20B</option>
                    <option value="llama-3.3-70b-versatile">Llama 3.3 70B</option>
                    <option value="llama-3.1-8b-instant">Llama 3.1 8B (Fast)</option>
                    <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
                    <option value="gemma2-9b-it">Gemma 2 9B</option>
                  </>
                )}
              </select>
            </div>

            {/* New Chat Button */}
            {sessionId && (
              <button
                onClick={() => { setMessages([]); setSessionId(null); }}
                className="text-xs text-on-surface-variant hover:text-on-surface flex items-center gap-1 ml-auto"
              >
                <span className="material-symbols-outlined text-sm">refresh</span>
                New Chat
              </button>
            )}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-12 py-8 flex flex-col gap-12 max-w-4xl mx-auto w-full">
            {error && (
              <div className="bg-error/10 border border-error/30 rounded-lg p-4 flex items-start gap-3">
                <span className="material-symbols-outlined text-error text-lg">error</span>
                <p className="text-sm font-medium text-error">{error}</p>
              </div>
            )}

            {messages.length === 0 && !isStreaming && (
              <div className="mt-8 space-y-6 opacity-80">
                <div className="text-center space-y-1">
                  <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-outline">Ask anything about your codebase</h3>
                  <p className="text-[11px] text-outline">Powered by <span className="text-[#f55036] font-semibold">Groq</span> · {selectedModelLabel}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setMessage('Explain the overall architecture of this codebase')}
                    className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10 hover:border-primary/40 hover:bg-surface-container transition-all text-left group"
                  >
                    <span className="material-symbols-outlined text-primary mb-3 block">architecture</span>
                    <p className="text-sm font-medium text-on-surface mb-1">Explain Architecture</p>
                    <p className="text-xs text-on-surface-variant">Summarize the core design patterns used in this repo.</p>
                  </button>
                  <button
                    onClick={() => setMessage('Check for security vulnerabilities in the authentication flow')}
                    className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10 hover:border-primary/40 hover:bg-surface-container transition-all text-left group"
                  >
                    <span className="material-symbols-outlined text-secondary mb-3 block">security</span>
                    <p className="text-sm font-medium text-on-surface mb-1">Security Audit</p>
                    <p className="text-xs text-on-surface-variant">Check for common vulnerabilities in the auth flow.</p>
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => renderMessage(msg, idx))}

            {/* Streaming Message */}
            {isStreaming && streamingMessage && (
              <div className="flex gap-6 group">
                <div className="w-8 h-8 rounded-lg bg-surface-container-high flex-shrink-0 flex items-center justify-center border border-outline-variant/10">
                  <span className="material-symbols-outlined text-primary text-xl animate-pulse" style={{ fontVariationSettings: "'FILL' 1" }}>
                    smart_toy
                  </span>
                </div>
                <div className="flex-1 space-y-4">
                  <div className="text-on-surface leading-relaxed prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code: ({ node, inline, className, children, ...props }: any) => {
                          const match = /language-(\w+)/.exec(className || '');
                          const language = match ? match[1] : '';
                          const codeString = String(children).replace(/\n$/, '');
                          
                          return !inline && language ? (
                            <div className="my-4">
                              <CodeMirror
                                value={codeString}
                                extensions={[getLanguageExtension(language), EditorView.lineWrapping]}
                                theme={oneDark}
                                editable={false}
                                readOnly={true}
                                basicSetup={{
                                  lineNumbers: true,
                                  highlightActiveLineGutter: false,
                                  highlightSpecialChars: true,
                                  foldGutter: false,
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
                                  foldKeymap: false,
                                  completionKeymap: false,
                                  lintKeymap: false,
                                }}
                                style={{
                                  fontSize: '14px',
                                  backgroundColor: '#000000',
                                }}
                                className="rounded-lg overflow-hidden border border-white/10 [&_.cm-editor]:!bg-[#000000] [&_.cm-gutters]:!bg-[#000000] [&_.cm-scroller]:!bg-[#000000] [&_.cm-content]:!bg-[#000000]"
                              />
                            </div>
                          ) : !inline ? (
                            <code className="block bg-[#000000] text-sm font-mono p-3 rounded-lg my-4 whitespace-pre-wrap border border-white/10" {...props}>
                              {children}
                            </code>
                          ) : (
                            <code className="bg-surface-container/50 px-1.5 py-0.5 rounded text-[13px] font-mono text-primary/90 whitespace-nowrap" {...props}>
                              {children}
                            </code>
                          );
                        },
                        pre: ({ children }: any) => <>{children}</>,
                        p: ({ children }: any) => <p className="mb-4 last:mb-0">{children}</p>,
                        ul: ({ children }: any) => <ul className="list-disc list-inside mb-4 space-y-1.5 ml-2">{children}</ul>,
                        ol: ({ children }: any) => <ol className="list-decimal list-inside mb-4 space-y-1.5 ml-2">{children}</ol>,
                        li: ({ children }: any) => <li className="text-on-surface leading-relaxed">{children}</li>,
                        h1: ({ children }: any) => <h1 className="text-xl font-bold mb-3 mt-6 first:mt-0">{children}</h1>,
                        h2: ({ children }: any) => <h2 className="text-lg font-bold mb-2 mt-5 first:mt-0">{children}</h2>,
                        h3: ({ children }: any) => <h3 className="text-base font-bold mb-2 mt-4 first:mt-0">{children}</h3>,
                        blockquote: ({ children }: any) => (
                          <blockquote className="border-l-4 border-primary/30 pl-4 italic text-on-surface-variant my-4">
                            {children}
                          </blockquote>
                        ),
                        a: ({ children, href }: any) => (
                          <a href={href} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                            {children}
                          </a>
                        ),
                        table: ({ children }: any) => (
                          <div className="overflow-x-auto my-4">
                            <table className="min-w-full border border-outline-variant/20 rounded-lg">
                              {children}
                            </table>
                          </div>
                        ),
                        thead: ({ children }: any) => (
                          <thead className="bg-surface-container-high">{children}</thead>
                        ),
                        tbody: ({ children }: any) => <tbody>{children}</tbody>,
                        tr: ({ children }: any) => (
                          <tr className="border-b border-outline-variant/10">{children}</tr>
                        ),
                        th: ({ children }: any) => (
                          <th className="px-4 py-2 text-left text-sm font-semibold">{children}</th>
                        ),
                        td: ({ children }: any) => (
                          <td className="px-4 py-2 text-sm">{children}</td>
                        ),
                      }}
                    >
                      {streamingMessage}
                    </ReactMarkdown>
                    <span className="inline-block w-2 h-4 bg-primary ml-1 animate-pulse"></span>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator before first chunk */}
            {isStreaming && !streamingMessage && (
              <div className="flex gap-6">
                <div className="w-8 h-8 rounded-lg bg-surface-container-high flex-shrink-0 flex items-center justify-center border border-outline-variant/10">
                  <span className="material-symbols-outlined text-primary text-xl animate-pulse" style={{ fontVariationSettings: "'FILL' 1" }}>
                    smart_toy
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                  <span className="flex gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </span>
                  <span className="text-xs text-outline">Thinking with {selectedModelLabel}...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div className="p-6 bg-surface border-t border-outline-variant/10">
            <div className="max-w-4xl mx-auto relative group">
              <div className="bg-surface-container-low rounded-xl border border-outline-variant/20 focus-within:border-primary/50 transition-all p-3">
                <textarea
                  className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-on-surface placeholder:text-outline text-sm resize-none min-h-[80px]"
                  placeholder="Ask anything about the codebase..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={isStreaming}
                />
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-outline-variant/5">
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] text-outline">
                      {selectedRepos.length > 0
                        ? `Searching in ${repositories.find(r => r.id === selectedRepos[0])?.name}`
                        : 'No repository selected'}
                    </span>
                    <span className="text-[10px] text-[#f55036]/70">⚡ {selectedModelLabel}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-[10px] text-outline uppercase tracking-widest">⌘ + Enter to send</span>
                    <button
                      onClick={handleSendMessage}
                      disabled={!message.trim() || isStreaming || selectedRepos.length === 0}
                      className="px-4 py-1.5 rounded bg-gradient-to-r from-primary to-secondary text-on-primary font-bold text-xs flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isStreaming ? 'SENDING...' : 'SEND'}
                      <span className="material-symbols-outlined text-sm">send</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Context Panel - responsive behavior */}
        {/* Desktop mode (>= 1200px): Side-by-side with resizable width */}
        {/* Mobile mode (< 1200px): Overlay with fixed position */}
        {(!isNarrowViewport || isPanelVisible) && (
          <>
            {/* Backdrop for overlay mode */}
            {isNarrowViewport && isPanelVisible && (
              <div 
                className="fixed inset-0 bg-black/50 z-40"
                onClick={handleDismissPanel}
                aria-hidden="true"
              />
            )}
            
            {/* Context Panel */}
            {isNarrowViewport ? (
              // Overlay mode - fixed position
              <ContextPanel
                citation={selectedCitation}
                citations={activeCitations}
                currentIndex={currentCitationIndex}
                onNavigate={handleNavigate}
                onOpenInViewer={handleOpenInViewer}
                isOverlay={true}
                onDismiss={handleDismissPanel}
                className="w-[90vw] max-w-[500px]"
              />
            ) : (
              // Desktop mode - side-by-side with resize handle
              <div 
                className="relative flex"
                style={{ width: `${contextPanel.size}px` }}
              >
                {/* Resize Handle */}
                <div
                  onMouseDown={contextPanel.onMouseDown}
                  className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary/50 transition-colors z-10 group"
                >
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-outline-variant/10 group-hover:bg-primary/30 transition-colors" />
                </div>
                
                <ContextPanel
                  citation={selectedCitation}
                  citations={activeCitations}
                  currentIndex={currentCitationIndex}
                  onNavigate={handleNavigate}
                  onOpenInViewer={handleOpenInViewer}
                  className="flex-1 border-l border-outline-variant/10"
                />
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
