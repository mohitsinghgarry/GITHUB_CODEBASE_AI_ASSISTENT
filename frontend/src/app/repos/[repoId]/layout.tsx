/**
 * Repository Layout
 * 
 * Layout wrapper for repository pages with sidebar navigation.
 * Features:
 * - Sidebar with repository-specific navigation
 * - Repository context
 * - Responsive layout
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { slideInLeft } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  MessageSquare,
  Search,
  FileText,
  ArrowLeft,
  FolderGit2,
} from 'lucide-react';
import { useRepositoryStore } from '@/store/repositoryStore';
import { apiClient } from '@/lib/api';
import type { Repository } from '@/types';

interface RepositoryLayoutProps {
  children: React.ReactNode;
  params: {
    repoId: string;
  };
}

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

export default function RepositoryLayout({
  children,
  params,
}: RepositoryLayoutProps) {
  const pathname = usePathname();
  const { getRepositoryById, updateRepository } = useRepositoryStore();
  const [repository, setRepository] = useState<Repository | null>(null);

  // Fetch repository data
  useEffect(() => {
    const fetchRepository = async () => {
      // Try to get from store first
      const storedRepo = getRepositoryById(params.repoId);
      if (storedRepo) {
        setRepository(storedRepo);
      }

      // Fetch from API to ensure fresh data
      try {
        const repo = await apiClient.repositories.get(params.repoId);
        setRepository(repo);
        updateRepository(repo.id, repo);
      } catch (err) {
        console.error('Failed to fetch repository:', err);
      }
    };

    fetchRepository();
  }, [params.repoId]);

  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      href: `/repos/${params.repoId}`,
      icon: LayoutDashboard,
    },
    {
      label: 'Chat',
      href: `/repos/${params.repoId}/chat`,
      icon: MessageSquare,
    },
    {
      label: 'Search',
      href: `/repos/${params.repoId}/search`,
      icon: Search,
    },
    {
      label: 'Files',
      href: `/repos/${params.repoId}/files`,
      icon: FileText,
    },
  ];

  const isActive = (href: string) => {
    if (href === `/repos/${params.repoId}`) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  };

  return (
    <div className="flex min-h-screen bg-surface">
      {/* Sidebar */}
      <motion.aside
        variants={slideInLeft}
        initial="hidden"
        animate="visible"
        className="w-64 bg-surface-container-low border-r border-outline-variant/15 flex flex-col"
      >
        {/* Back to Home */}
        <div className="p-4 border-b border-outline-variant/15">
          <Link
            href="/"
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg',
              'text-body-md text-text-secondary',
              'hover:bg-surface-container hover:text-text-primary',
              'transition-colors'
            )}
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>

        {/* Repository Info */}
        {repository && (
          <div className="p-4 border-b border-outline-variant/15">
            <div className="flex items-start gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
                <FolderGit2 className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-label-md text-text-primary font-medium truncate">
                  {repository.name}
                </p>
                <p className="text-label-sm text-text-secondary truncate">
                  {repository.owner}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'group relative flex items-center gap-3 px-3 py-2.5 rounded-lg',
                  'text-body-md transition-all',
                  active
                    ? 'bg-primary/10 text-primary'
                    : 'text-text-secondary hover:bg-surface-container hover:text-text-primary'
                )}
              >
                {/* Active indicator */}
                {active && (
                  <motion.div
                    layoutId="activeRepoNav"
                    className="absolute inset-0 rounded-lg bg-primary/10"
                    transition={{
                      type: 'spring',
                      stiffness: 380,
                      damping: 30,
                    }}
                  />
                )}

                <Icon className={cn('relative w-5 h-5', active && 'text-primary')} />
                <span className="relative">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
