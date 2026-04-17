'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';
import { api, Repository } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [languages, setLanguages] = useState<Array<{
    name: string;
    percentage: number;
    color: string;
  }>>([]);

  useEffect(() => {
    fetchRepositories();
    fetchLanguageStats();
  }, []);

  const fetchRepositories = async () => {
    try {
      const { repositories: repos } = await api.listRepositories();
      setRepositories(repos);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch repositories');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLanguageStats = async () => {
    try {
      const { languages: langs } = await api.getLanguageStats();
      
      // Map languages to colors
      const colorMap: Record<string, string> = {
        'Javascript': 'primary',
        'Typescript': 'primary',
        'Python': 'secondary',
        'Css': 'tertiary',
        'Html': 'tertiary',
        'Json': 'outline',
        'Markdown': 'outline',
        'Text': 'outline',
      };
      
      const formattedLanguages = langs.map(lang => ({
        name: lang.name,
        percentage: lang.percentage,
        color: colorMap[lang.name] || 'outline'
      }));
      
      setLanguages(formattedLanguages);
    } catch (err) {
      console.error('Failed to fetch language stats:', err);
      // Don't set error state, just use empty array
    }
  };

  const completedRepos = repositories.filter(r => r.status === 'completed');
  const totalFiles = completedRepos.reduce((sum, r) => sum + (r.total_files || 0), 0);
  const totalChunks = completedRepos.reduce((sum, r) => sum + (r.total_chunks || 0), 0);

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-primary border-t-transparent"></div>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell>
        <div className="p-8 max-w-7xl mx-auto">
          <div className="p-4 bg-error/10 border border-error/20 rounded-xl flex items-start gap-3">
            <span className="material-symbols-outlined text-error">error</span>
            <div className="flex-1">
              <p className="text-error font-medium">Failed to load dashboard</p>
              <p className="text-error/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  if (completedRepos.length === 0) {
    return (
      <AppShell>
        <div className="p-8 max-w-7xl mx-auto">
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-outline text-6xl mb-4">folder_off</span>
            <h2 className="text-2xl font-bold text-on-surface mb-2">No Repositories Indexed</h2>
            <p className="text-on-surface-variant mb-6">Add a repository to get started</p>
            <button
              onClick={() => router.push('/load')}
              className="px-6 py-3 bg-gradient-to-r from-primary to-secondary text-on-primary font-bold rounded-md hover:opacity-90 transition-opacity"
            >
              Add Repository
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  const mainRepo = completedRepos[0];
  return (
    <AppShell>
      <div className="p-8 max-w-7xl mx-auto w-full">
        {/* Repository Identity Bar */}
        <section className="flex items-end justify-between mb-12">
          <div className="flex items-center gap-6">
            <div className="w-16 h-16 bg-surface-container-high rounded-xl flex items-center justify-center border border-outline-variant/15">
              <span 
                className="material-symbols-outlined text-primary text-4xl" 
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                terminal
              </span>
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-3xl font-extrabold tracking-tight text-on-surface">{mainRepo.name}</h2>
                <span className="px-2 py-0.5 rounded bg-tertiary-container/10 border border-tertiary-container/20 text-tertiary text-[10px] font-bold uppercase tracking-widest">
                  Ready
                </span>
              </div>
              <p className="text-on-surface-variant mt-1">
                {mainRepo.owner} • Indexed {mainRepo.indexed_at ? new Date(mainRepo.indexed_at).toLocaleDateString() : 'recently'}
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push(`/repositories`)}
              className="px-4 py-2 bg-surface-bright text-on-surface text-sm font-semibold rounded-md flex items-center gap-2 hover:bg-surface-container-highest transition-colors"
            >
              <span className="material-symbols-outlined text-lg">refresh</span>
              Manage
            </button>
            <button
              onClick={() => router.push('/chat')}
              className="px-6 py-2 bg-gradient-to-r from-primary to-secondary text-on-primary text-sm font-bold rounded-md active:scale-95 transition-transform"
            >
              Chat with Repo
            </button>
          </div>
        </section>

        {/* Bento Stats Row */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10">
            <p className="text-[10px] font-bold text-outline uppercase tracking-widest mb-1">Total Files</p>
            <p className="text-3xl font-bold text-on-surface">{totalFiles.toLocaleString()}</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">description</span>
              <span>Across {completedRepos.length} {completedRepos.length === 1 ? 'repository' : 'repositories'}</span>
            </div>
          </div>
          <div className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10">
            <p className="text-[10px] font-bold text-outline uppercase tracking-widest mb-1">Total Chunks</p>
            <p className="text-3xl font-bold text-on-surface">
              {totalChunks >= 1000 ? `${(totalChunks / 1000).toFixed(1)}k` : totalChunks.toLocaleString()}
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">database</span>
              <span>Vector embeddings</span>
            </div>
          </div>
          <div className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10">
            <p className="text-[10px] font-bold text-outline uppercase tracking-widest mb-1">Repositories</p>
            <p className="text-3xl font-bold text-on-surface">{completedRepos.length}</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">folder</span>
              <span>Fully indexed</span>
            </div>
          </div>
          <div className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/10">
            <p className="text-[10px] font-bold text-outline uppercase tracking-widest mb-1">Index Health</p>
            <p className="text-3xl font-bold text-tertiary">100%</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">bolt</span>
              <span>Ready for queries</span>
            </div>
          </div>
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Left: Quick Actions & Language Breakdown */}
          <div className="lg:col-span-1 space-y-8">
            {/* Quick Actions */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-on-surface uppercase tracking-widest flex items-center gap-2">
                <span className="w-1 h-4 bg-primary rounded-full"></span>
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-2">
                <button
                  onClick={() => router.push('/chat')}
                  className="w-full flex items-center justify-between p-4 bg-surface-container rounded-lg group hover:bg-surface-container-high transition-all"
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-primary">chat_bubble</span>
                    <span className="text-sm font-medium">Ask a question</span>
                  </div>
                  <span className="material-symbols-outlined text-outline group-hover:text-on-surface transition-colors">
                    chevron_right
                  </span>
                </button>
                <button
                  onClick={() => router.push('/search')}
                  className="w-full flex items-center justify-between p-4 bg-surface-container rounded-lg group hover:bg-surface-container-high transition-all"
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-secondary">search</span>
                    <span className="text-sm font-medium">Search code</span>
                  </div>
                  <span className="material-symbols-outlined text-outline group-hover:text-on-surface transition-colors">
                    chevron_right
                  </span>
                </button>
                <button
                  onClick={() => router.push('/files')}
                  className="w-full flex items-center justify-between p-4 bg-surface-container rounded-lg group hover:bg-surface-container-high transition-all"
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-tertiary">folder_zip</span>
                    <span className="text-sm font-medium">Browse files</span>
                  </div>
                  <span className="material-symbols-outlined text-outline group-hover:text-on-surface transition-colors">
                    chevron_right
                  </span>
                </button>
              </div>
            </div>

            {/* Language Breakdown */}
            <div className="p-8 rounded-2xl bg-surface-container border border-outline-variant/10">
              <h3 className="text-sm font-bold text-on-surface uppercase tracking-widest mb-6">Language Breakdown</h3>
              {languages.length > 0 ? (
                <div className="space-y-6">
                  {languages.map((lang) => (
                    <div key={lang.name} className="space-y-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="font-mono text-on-surface">{lang.name}</span>
                        <span className="text-on-surface-variant">{lang.percentage}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                        <div className={`h-full bg-${lang.color} rounded-full`} style={{ width: `${lang.percentage}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-on-surface-variant text-sm">
                  No language data available
                </div>
              )}
            </div>
          </div>

          {/* Right: Repository List */}
          <div className="lg:col-span-2">
            <div className="bg-surface-container border border-outline-variant/10 rounded-2xl overflow-hidden">
              <div className="px-8 py-6 border-b border-outline-variant/10 flex justify-between items-center">
                <h3 className="text-sm font-bold text-on-surface uppercase tracking-widest">Indexed Repositories</h3>
                <button
                  onClick={() => router.push('/repositories')}
                  className="text-xs font-semibold text-primary-dim hover:text-primary transition-colors"
                >
                  View All
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-[10px] uppercase tracking-widest text-outline border-b border-outline-variant/5">
                      <th className="px-8 py-4 font-bold">Repository</th>
                      <th className="px-8 py-4 font-bold">Files</th>
                      <th className="px-8 py-4 font-bold">Chunks</th>
                      <th className="px-8 py-4 font-bold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/5">
                    {completedRepos.slice(0, 5).map((repo) => (
                      <tr key={repo.id} className="hover:bg-surface-container-high transition-colors group">
                        <td className="px-8 py-5">
                          <div>
                            <p className="text-sm font-medium text-on-surface">{repo.name}</p>
                            <p className="text-xs text-on-surface-variant mt-1">{repo.owner}</p>
                          </div>
                        </td>
                        <td className="px-8 py-5">
                          <span className="text-xs font-mono">{repo.total_files?.toLocaleString() || 0}</span>
                        </td>
                        <td className="px-8 py-5">
                          <span className="text-xs font-mono">{repo.total_chunks?.toLocaleString() || 0}</span>
                        </td>
                        <td className="px-8 py-5 text-right">
                          <button
                            onClick={() => router.push('/chat')}
                            className="px-3 py-1.5 rounded bg-surface-bright text-xs font-bold hover:bg-surface-container-highest transition-colors active:scale-95"
                          >
                            Chat
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-6 bg-surface-container-low flex justify-center">
                <p className="text-xs text-outline italic">Showing {Math.min(5, completedRepos.length)} of {completedRepos.length} indexed {completedRepos.length === 1 ? 'repository' : 'repositories'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
