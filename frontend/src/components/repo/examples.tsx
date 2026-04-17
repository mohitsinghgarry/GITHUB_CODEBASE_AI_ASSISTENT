/**
 * Repository Components - Usage Examples
 * 
 * This file demonstrates how to use the repository management components.
 * These examples can be used as reference when building pages.
 */

import { useState } from 'react';
import {
  RepoInputCard,
  IndexingProgress,
  RepoStats,
  RepoCard,
  LanguageChart,
} from '@/components/repo';
import type { Repository, IngestionJob } from '@/types';

/**
 * Example 1: Repository Input Form
 * 
 * Shows how to use RepoInputCard for adding new repositories
 */
export function RepoInputExample() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Simulate success
      setSuccess('Repository added successfully!');
    } catch (err) {
      setError('Failed to add repository. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <RepoInputCard
      onSubmit={handleSubmit}
      isLoading={isLoading}
      error={error}
      success={success}
    />
  );
}

/**
 * Example 2: Indexing Progress Display
 * 
 * Shows how to display ingestion progress
 */
export function IndexingProgressExample() {
  const job: IngestionJob = {
    id: '123',
    repositoryId: 'repo-123',
    status: 'running',
    stage: 'embed',
    progressPercent: 65,
    startedAt: new Date().toISOString(),
    retryCount: 0,
  };

  return (
    <IndexingProgress
      stage={job.stage}
      status={job.status}
      progressPercent={job.progressPercent}
      repositoryName="facebook/react"
    />
  );
}

/**
 * Example 3: Repository Statistics
 * 
 * Shows how to display repository stats
 */
export function RepoStatsExample() {
  return (
    <RepoStats
      fileCount={1523}
      chunkCount={8456}
      languageCount={5}
      lastUpdated={new Date().toISOString()}
      defaultBranch="main"
    />
  );
}

/**
 * Example 4: Repository Card List
 * 
 * Shows how to display a list of repositories
 */
export function RepoCardListExample() {
  const repositories: Repository[] = [
    {
      id: '1',
      url: 'https://github.com/facebook/react',
      owner: 'facebook',
      name: 'react',
      defaultBranch: 'main',
      lastCommitHash: 'abc123',
      status: 'completed',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      chunkCount: 8456,
      indexPath: '/indices/1.faiss',
    },
    {
      id: '2',
      url: 'https://github.com/vercel/next.js',
      owner: 'vercel',
      name: 'next.js',
      defaultBranch: 'canary',
      lastCommitHash: 'def456',
      status: 'embedding',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      chunkCount: 0,
    },
    {
      id: '3',
      url: 'https://github.com/microsoft/vscode',
      owner: 'microsoft',
      name: 'vscode',
      defaultBranch: 'main',
      lastCommitHash: 'ghi789',
      status: 'failed',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      chunkCount: 0,
      errorMessage: 'Failed to clone repository: Authentication required',
    },
  ];

  const handleCardClick = (repo: Repository) => {
    console.log('Navigate to:', repo.id);
  };

  const handleDelete = (repo: Repository) => {
    console.log('Delete:', repo.id);
  };

  const handleReindex = (repo: Repository) => {
    console.log('Reindex:', repo.id);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {repositories.map((repo) => (
        <RepoCard
          key={repo.id}
          repository={repo}
          onClick={() => handleCardClick(repo)}
          onDelete={() => handleDelete(repo)}
          onReindex={() => handleReindex(repo)}
        />
      ))}
    </div>
  );
}

/**
 * Example 5: Language Chart
 * 
 * Shows how to display language breakdown
 */
export function LanguageChartExample() {
  const languages = [
    { name: 'TypeScript', percentage: 45.2, fileCount: 123 },
    { name: 'Python', percentage: 30.5, fileCount: 87 },
    { name: 'JavaScript', percentage: 15.3, fileCount: 45 },
    { name: 'CSS', percentage: 5.8, fileCount: 28 },
    { name: 'HTML', percentage: 2.1, fileCount: 12 },
    { name: 'Shell', percentage: 1.1, fileCount: 5 },
  ];

  return <LanguageChart languages={languages} maxLanguages={10} />;
}

/**
 * Example 6: Complete Repository Dashboard
 * 
 * Shows how to combine multiple components for a full dashboard
 */
export function RepositoryDashboardExample() {
  const repository: Repository = {
    id: '1',
    url: 'https://github.com/facebook/react',
    owner: 'facebook',
    name: 'react',
    defaultBranch: 'main',
    lastCommitHash: 'abc123',
    status: 'completed',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    chunkCount: 8456,
    indexPath: '/indices/1.faiss',
  };

  const languages = [
    { name: 'JavaScript', percentage: 65.2, fileCount: 523 },
    { name: 'TypeScript', percentage: 25.5, fileCount: 187 },
    { name: 'CSS', percentage: 5.3, fileCount: 45 },
    { name: 'HTML', percentage: 4.0, fileCount: 28 },
  ];

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div>
        <h1 className="text-headline-lg text-text-primary font-semibold">
          {repository.owner}/{repository.name}
        </h1>
        <p className="text-body-md text-text-secondary mt-2">
          Repository dashboard and statistics
        </p>
      </div>

      {/* Statistics */}
      <RepoStats
        fileCount={783}
        chunkCount={repository.chunkCount}
        languageCount={languages.length}
        lastUpdated={repository.updatedAt}
        defaultBranch={repository.defaultBranch}
      />

      {/* Language Breakdown */}
      <LanguageChart languages={languages} />
    </div>
  );
}

/**
 * Example 7: Repository List with Add Form
 * 
 * Shows how to combine RepoInputCard with RepoCard list
 */
export function RepositoryListPageExample() {
  const [repositories, setRepositories] = useState<Repository[]>([
    {
      id: '1',
      url: 'https://github.com/facebook/react',
      owner: 'facebook',
      name: 'react',
      defaultBranch: 'main',
      lastCommitHash: 'abc123',
      status: 'completed',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      chunkCount: 8456,
      indexPath: '/indices/1.faiss',
    },
  ]);

  const handleAddRepository = async (url: string) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Add new repository
    const newRepo: Repository = {
      id: Date.now().toString(),
      url,
      owner: url.split('/')[3],
      name: url.split('/')[4],
      defaultBranch: 'main',
      lastCommitHash: '',
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      chunkCount: 0,
    };

    setRepositories([...repositories, newRepo]);
  };

  return (
    <div className="space-y-8 p-8">
      {/* Add Repository Form */}
      <RepoInputCard onSubmit={handleAddRepository} />

      {/* Repository List */}
      <div>
        <h2 className="text-title-lg text-text-primary font-medium mb-4">
          Your Repositories
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {repositories.map((repo) => (
            <RepoCard
              key={repo.id}
              repository={repo}
              onClick={() => console.log('Navigate to:', repo.id)}
              onDelete={() => {
                setRepositories(repositories.filter((r) => r.id !== repo.id));
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
