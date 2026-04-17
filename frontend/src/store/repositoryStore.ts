/**
 * Repository Store
 * 
 * Manages repository state including:
 * - List of repositories
 * - Selected repository
 * - Ingestion jobs
 * - Repository statistics
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Repository, IngestionJob } from '@/types';

interface RepositoryState {
  // State
  repositories: Repository[];
  selectedRepositoryId: string | null;
  ingestionJobs: Record<string, IngestionJob>; // jobId -> job
  isLoading: boolean;
  error: string | null;

  // Computed getters
  selectedRepository: () => Repository | null;
  getRepositoryById: (id: string) => Repository | null;
  getJobsByRepositoryId: (repositoryId: string) => IngestionJob[];
  
  // Actions
  setRepositories: (repositories: Repository[]) => void;
  addRepository: (repository: Repository) => void;
  updateRepository: (id: string, updates: Partial<Repository>) => void;
  removeRepository: (id: string) => void;
  selectRepository: (id: string | null) => void;
  
  setIngestionJobs: (jobs: IngestionJob[]) => void;
  addIngestionJob: (job: IngestionJob) => void;
  updateIngestionJob: (jobId: string, updates: Partial<IngestionJob>) => void;
  removeIngestionJob: (jobId: string) => void;
  
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  repositories: [],
  selectedRepositoryId: null,
  ingestionJobs: {},
  isLoading: false,
  error: null,
};

export const useRepositoryStore = create<RepositoryState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Computed getters
        selectedRepository: () => {
          const { selectedRepositoryId, repositories } = get();
          if (!selectedRepositoryId) return null;
          return repositories.find((r) => r.id === selectedRepositoryId) || null;
        },

        getRepositoryById: (id: string) => {
          const { repositories } = get();
          return repositories.find((r) => r.id === id) || null;
        },

        getJobsByRepositoryId: (repositoryId: string) => {
          const { ingestionJobs } = get();
          return Object.values(ingestionJobs).filter(
            (job) => job.repositoryId === repositoryId
          );
        },

        // Repository actions
        setRepositories: (repositories) =>
          set({ repositories }, false, 'setRepositories'),

        addRepository: (repository) =>
          set(
            (state) => ({
              repositories: [...state.repositories, repository],
            }),
            false,
            'addRepository'
          ),

        updateRepository: (id, updates) =>
          set(
            (state) => ({
              repositories: state.repositories.map((repo) =>
                repo.id === id ? { ...repo, ...updates } : repo
              ),
            }),
            false,
            'updateRepository'
          ),

        removeRepository: (id) =>
          set(
            (state) => ({
              repositories: state.repositories.filter((repo) => repo.id !== id),
              selectedRepositoryId:
                state.selectedRepositoryId === id
                  ? null
                  : state.selectedRepositoryId,
              // Remove associated jobs
              ingestionJobs: Object.fromEntries(
                Object.entries(state.ingestionJobs).filter(
                  ([_, job]) => job.repositoryId !== id
                )
              ),
            }),
            false,
            'removeRepository'
          ),

        selectRepository: (id) =>
          set({ selectedRepositoryId: id }, false, 'selectRepository'),

        // Ingestion job actions
        setIngestionJobs: (jobs) =>
          set(
            {
              ingestionJobs: jobs.reduce(
                (acc, job) => {
                  acc[job.id] = job;
                  return acc;
                },
                {} as Record<string, IngestionJob>
              ),
            },
            false,
            'setIngestionJobs'
          ),

        addIngestionJob: (job) =>
          set(
            (state) => ({
              ingestionJobs: {
                ...state.ingestionJobs,
                [job.id]: job,
              },
            }),
            false,
            'addIngestionJob'
          ),

        updateIngestionJob: (jobId, updates) =>
          set(
            (state) => ({
              ingestionJobs: {
                ...state.ingestionJobs,
                [jobId]: {
                  ...state.ingestionJobs[jobId],
                  ...updates,
                },
              },
            }),
            false,
            'updateIngestionJob'
          ),

        removeIngestionJob: (jobId) =>
          set(
            (state) => {
              const { [jobId]: _, ...rest } = state.ingestionJobs;
              return { ingestionJobs: rest };
            },
            false,
            'removeIngestionJob'
          ),

        // Utility actions
        setLoading: (isLoading) => set({ isLoading }, false, 'setLoading'),

        setError: (error) => set({ error }, false, 'setError'),

        reset: () => set(initialState, false, 'reset'),
      }),
      {
        name: 'repository-store',
        partialize: (state) => ({
          repositories: state.repositories,
          selectedRepositoryId: state.selectedRepositoryId,
          // Don't persist loading/error states
        }),
      }
    ),
    { name: 'RepositoryStore' }
  )
);
