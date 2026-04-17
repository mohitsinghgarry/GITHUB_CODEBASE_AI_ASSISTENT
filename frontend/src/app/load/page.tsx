/**
 * Load Repository Page
 * 
 * Pixel-perfect implementation of Stitch design
 * Centered card layout with glassmorphism and progress tracking
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, type Repository } from '@/lib/api';

export default function LoadRepositoryPage() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<string>('');
  const [recentRepos, setRecentRepos] = useState<Repository[]>([]);

  // Fetch recent repositories on mount
  useEffect(() => {
    const fetchRecentRepos = async () => {
      try {
        const { repositories } = await api.listRepositories();
        setRecentRepos(repositories.slice(0, 2)); // Get 2 most recent
      } catch (err) {
        console.error('Failed to fetch recent repositories:', err);
      }
    };
    fetchRecentRepos();
  }, []);

  // Poll job status
  useEffect(() => {
    if (!jobId) return;

    console.log('[Polling] Starting to poll job:', jobId);

    // Poll immediately on mount
    const pollOnce = async () => {
      try {
        console.log('[Polling] Fetching job status for:', jobId);
        const { job } = await api.getJobStatus(jobId);
        
        console.log('[Polling] Job status received:', {
          status: job.status,
          stage: job.stage,
          progress: job.progress_percent
        });
        
        setProgress(job.progress_percent);
        setStage(job.stage || 'pending');
        
        if (job.status === 'completed') {
          console.log('[Polling] Job completed! Redirecting to dashboard...');
          setIsLoading(false);
          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
          return true; // Stop polling
        } else if (job.status === 'failed') {
          console.log('[Polling] Job failed:', job.error_message);
          setError(job.error_message || 'Indexing failed');
          setIsLoading(false);
          return true; // Stop polling
        }
        return false; // Continue polling
      } catch (err) {
        console.error('[Polling] Error polling job status:', err);
        return false; // Continue polling despite error
      }
    };

    // Poll immediately
    pollOnce();

    // Then poll every 500ms
    const interval = setInterval(async () => {
      const shouldStop = await pollOnce();
      if (shouldStop) {
        clearInterval(interval);
      }
    }, 500);

    return () => {
      console.log('[Polling] Cleaning up interval for job:', jobId);
      clearInterval(interval);
    };
  }, [jobId, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    console.log('[Submit] Starting repository creation for:', repoUrl);
    setIsLoading(true);
    setError('');
    setJobId(null);
    setProgress(0);
    setStage('');

    try {
      console.log('[Submit] Calling API to create repository...');
      const result = await api.createRepository(repoUrl);
      console.log('[Submit] Repository created successfully:', {
        repository_id: result.repository.id,
        job_id: result.job_id,
        message: result.message
      });
      setJobId(result.job_id);
    } catch (err) {
      console.error('[Submit] Error creating repository:', err);
      setError(err instanceof Error ? err.message : 'Failed to add repository');
      setIsLoading(false);
    }
  };

  const getStageLabel = (stageValue: string) => {
    const labels: Record<string, string> = {
      'clone': 'Cloning repository...',
      'read': 'Reading file structure...',
      'chunk': 'Chunking code...',
      'embed': 'Generating embeddings...',
      'store': 'Storing in database...',
      'pending': 'Preparing...',
    };
    return labels[stageValue] || 'Processing...';
  };

  const getStatusBadge = (status: string) => {
    if (status === 'completed') {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-tertiary/10 text-tertiary uppercase">Indexed</span>;
    } else if (status === 'failed') {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-error/10 text-error uppercase">Failed</span>;
    } else if (status === 'pending' || status === 'cloning' || status === 'reading' || status === 'chunking' || status === 'embedding') {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-primary/10 text-primary uppercase">Indexing</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-primary/10 text-primary uppercase">Stale</span>;
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className="bg-background text-on-surface selection:bg-primary selection:text-on-primary min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background Layer */}
      <div 
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle, #48474a 1px, transparent 1px)',
          backgroundSize: '32px 32px'
        }}
      ></div>
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary opacity-5 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary opacity-5 blur-[120px] rounded-full"></div>

      {/* Main Content Area */}
      <main className="relative z-10 w-full max-w-[640px] px-6 py-12 flex flex-col gap-16">
        {/* Header Branding */}
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-surface-container flex items-center justify-center rounded-xl border border-outline-variant/15">
            <span className="material-symbols-outlined text-primary text-3xl">psychology</span>
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-extrabold tracking-tighter text-on-surface">RepoMind</h1>
            <p className="text-on-surface-variant font-medium tracking-tight mt-1">AI-Powered Dev Intelligence</p>
          </div>
        </div>

        {/* Central Card */}
        <section 
          className="border border-outline-variant/15 rounded-2xl p-8 flex flex-col gap-8"
          style={{
            background: 'rgba(25, 25, 28, 0.7)',
            backdropFilter: 'blur(12px)'
          }}
        >
          <header className="flex flex-col gap-2">
            <h2 className="text-2xl font-semibold tracking-tight text-on-surface">Load a Repository</h2>
            <p className="text-on-surface-variant text-sm">Supports public repositories from GitHub, GitLab, and Bitbucket.</p>
          </header>

          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            {/* Error Message */}
            {error && (
              <div className="bg-error/10 border border-error/30 rounded-lg p-4 flex items-start gap-3">
                <span className="material-symbols-outlined text-error text-lg">error</span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-error">{error}</p>
                </div>
              </div>
            )}

            {/* Input Field */}
            <div className="relative group">
              <label 
                className="absolute -top-2.5 left-4 px-2 bg-surface-container text-[10px] font-bold tracking-widest uppercase text-outline" 
                htmlFor="repo-url"
              >
                Repository URL
              </label>
              <div className="flex items-center gap-3 bg-surface-container-low border border-outline-variant/15 group-focus-within:border-primary/40 rounded-xl px-4 py-4 transition-all duration-300">
                <span className="material-symbols-outlined text-outline">link</span>
                <input 
                  className="bg-transparent border-none focus:ring-0 focus:outline-none text-on-surface w-full font-medium placeholder:text-outline" 
                  id="repo-url" 
                  placeholder="https://github.com/username/repository" 
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                />
                {repoUrl && (
                  <span 
                    className="material-symbols-outlined text-tertiary-dim" 
                    style={{ fontVariationSettings: "'FILL' 1" }}
                  >
                    check_circle
                  </span>
                )}
              </div>
            </div>

            {/* CTA Button */}
            <button 
              type="submit"
              disabled={!repoUrl || isLoading}
              className="w-full h-14 bg-gradient-to-r from-primary to-secondary text-on-primary-container font-bold rounded-xl shadow-lg shadow-primary/10 hover:scale-[1.01] active:scale-95 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="material-symbols-outlined">sync</span>
              Load & Index Repository
            </button>
          </form>

          {/* State Progression */}
          {isLoading && jobId && (
            <div className="flex flex-col gap-6 pt-4">
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-center text-xs font-bold tracking-widest uppercase">
                  <span className="text-on-surface">System Indexing</span>
                  <span className="text-primary">{progress}%</span>
                </div>
                <div className="space-y-4">
                  {/* Progress Item - Current Stage */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-on-surface-variant">
                      <span>{getStageLabel(stage)}</span>
                      <span className="text-primary font-medium">Active</span>
                    </div>
                    <div className="h-1 w-full bg-surface-container-lowest rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary transition-all duration-300" 
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Recent Repositories Row */}
        <section className="flex flex-col gap-6">
          <div className="flex items-center gap-4">
            <h3 className="text-xs font-bold tracking-[0.2em] uppercase text-outline whitespace-nowrap">Recent Repositories</h3>
            <div className="h-[1px] w-full bg-outline-variant/15"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentRepos.length > 0 ? (
              recentRepos.map((repo) => (
                <Link key={repo.id} href="/dashboard">
                  <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/5 flex flex-col gap-3 hover:bg-surface-container transition-colors cursor-pointer group">
                    <div className="flex justify-between items-start">
                      <span className="material-symbols-outlined text-outline group-hover:text-primary transition-colors">folder</span>
                      {getStatusBadge(repo.status)}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-on-surface">{repo.owner}/{repo.name}</p>
                      <p className="text-xs text-on-surface-variant mt-0.5">
                        Last synced {getTimeAgo(repo.updated_at)}
                      </p>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="col-span-2 text-center py-8 text-on-surface-variant text-sm">
                No recent repositories
              </div>
            )}
          </div>
        </section>

        {/* Footer Help */}
        <footer className="flex justify-center items-center gap-8 text-[11px] font-medium text-outline uppercase tracking-widest">
          <a className="hover:text-on-surface transition-colors flex items-center gap-1.5" href="#">
            <span className="material-symbols-outlined text-[14px]">help</span>
            Documentation
          </a>
          <a className="hover:text-on-surface transition-colors flex items-center gap-1.5" href="#">
            <span className="material-symbols-outlined text-[14px]">shield</span>
            Privacy Policy
          </a>
        </footer>
      </main>

      {/* Side Decoration (Implicit AI feel) */}
      <div className="fixed top-0 right-0 h-screen w-32 pointer-events-none opacity-40 md:block hidden">
        <div className="flex flex-col gap-4 py-8 items-center h-full border-l border-outline-variant/10">
          <div className="text-[10px] [writing-mode:vertical-rl] font-bold tracking-[0.5em] text-outline uppercase">Neural Core Alpha-7</div>
          <div className="flex-grow flex flex-col justify-center gap-2">
            <div className="w-1 h-1 bg-primary rounded-full"></div>
            <div className="w-1 h-1 bg-outline-variant rounded-full"></div>
            <div className="w-1 h-8 bg-gradient-to-b from-primary to-transparent rounded-full"></div>
            <div className="w-1 h-1 bg-outline-variant rounded-full"></div>
            <div className="w-1 h-1 bg-outline-variant rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
