'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { scaleInCenter, fadeIn, staggerContainer, staggerItem } from '@/lib/animation-presets';
// Material Symbols icons are used via className="material-symbols-outlined"
import { useRepositoryStore } from '@/store/repositoryStore';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Command {
  id: string;
  label: string;
  description?: string;
  icon: string; // Material Symbols icon name
  action: () => void;
  category: 'navigation' | 'actions' | 'recent';
  keywords?: string[];
}

/**
 * CommandPalette Component
 * 
 * Quick action palette triggered by ⌘K:
 * - Navigation shortcuts
 * - Quick actions
 * - Recent items
 * - Fuzzy search
 */
export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const { repositories } = useRepositoryStore();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Define available commands
  const commands: Command[] = [
    // Navigation
    {
      id: 'nav-home',
      label: 'Go to Home',
      icon: 'home',
      action: () => {
        router.push('/');
        onClose();
      },
      category: 'navigation',
      keywords: ['home', 'dashboard'],
    },
    {
      id: 'nav-repos',
      label: 'Go to Repositories',
      icon: 'folder_open',
      action: () => {
        router.push('/repositories');
        onClose();
      },
      category: 'navigation',
      keywords: ['repositories', 'repos', 'projects'],
    },
    {
      id: 'nav-search',
      label: 'Go to Search',
      icon: 'search',
      action: () => {
        router.push('/search');
        onClose();
      },
      category: 'navigation',
      keywords: ['search', 'find', 'query'],
    },
    {
      id: 'nav-chat',
      label: 'Go to Chat',
      icon: 'forum',
      action: () => {
        router.push('/chat');
        onClose();
      },
      category: 'navigation',
      keywords: ['chat', 'conversation', 'ask'],
    },
    {
      id: 'nav-review',
      label: 'Go to Code Review',
      icon: 'terminal',
      action: () => {
        router.push('/review');
        onClose();
      },
      category: 'navigation',
      keywords: ['review', 'code', 'analyze'],
    },
    {
      id: 'nav-diff-review',
      label: 'Go to Diff Review',
      icon: 'difference',
      action: () => {
        router.push('/diff-review');
        onClose();
      },
      category: 'navigation',
      keywords: ['diff', 'review', 'pr', 'pull request', 'changes'],
    },
    {
      id: 'nav-settings',
      label: 'Go to Settings',
      icon: 'settings',
      action: () => {
        router.push('/settings');
        onClose();
      },
      category: 'navigation',
      keywords: ['settings', 'preferences', 'config'],
    },
    // Actions
    {
      id: 'action-add-repo',
      label: 'Add Repository',
      description: 'Load a new GitHub repository',
      icon: 'add',
      action: () => {
        router.push('/repositories/new');
        onClose();
      },
      category: 'actions',
      keywords: ['add', 'new', 'repository', 'load'],
    },
  ];

  // Filter commands based on query
  const filteredCommands = query.trim()
    ? commands.filter((command) => {
        const searchText = query.toLowerCase();
        const labelMatch = command.label.toLowerCase().includes(searchText);
        const descriptionMatch = command.description?.toLowerCase().includes(searchText);
        const keywordsMatch = command.keywords?.some((keyword) =>
          keyword.toLowerCase().includes(searchText)
        );
        return labelMatch || descriptionMatch || keywordsMatch;
      })
    : commands;

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, command) => {
    if (!acc[command.category]) {
      acc[command.category] = [];
    }
    acc[command.category].push(command);
    return acc;
  }, {} as Record<string, Command[]>);

  // Reset selected index when filtered commands change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredCommands.length - 1 ? prev + 1 : prev
        );
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands]);

  const categoryLabels: Record<string, string> = {
    navigation: 'Navigation',
    actions: 'Actions',
    recent: 'Recent',
  };

  const categoryIcons: Record<string, string> = {
    navigation: 'trending_up',
    actions: 'add',
    recent: 'schedule',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Command palette modal */}
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
            <motion.div
              variants={scaleInCenter}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="w-full max-w-2xl overflow-hidden rounded-xl border border-outline-variant/30 shadow-float bg-[rgba(19,19,21,0.7)] backdrop-blur-xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Search input */}
              <div className="flex items-center border-b border-outline-variant/15 px-4">
                <span className="material-symbols-outlined text-on-surface-variant">search</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent px-4 py-4 text-body-md text-on-surface placeholder:text-on-surface-variant outline-none"
                />
                <kbd className="rounded border border-outline-variant/30 bg-surface-container-low px-2 py-1 text-label-sm text-on-surface-variant">
                  ESC
                </kbd>
              </div>

              {/* Commands list */}
              <div className="max-h-96 overflow-y-auto p-2">
                {filteredCommands.length === 0 ? (
                  <motion.div
                    variants={fadeIn}
                    initial="hidden"
                    animate="visible"
                    className="flex flex-col items-center justify-center py-12 text-center"
                  >
                    <span className="material-symbols-outlined text-on-surface-variant mb-3 text-5xl">search_off</span>
                    <p className="text-body-md text-on-surface-variant">
                      No commands found
                    </p>
                    <p className="mt-1 text-body-sm text-outline">
                      Try a different search term
                    </p>
                  </motion.div>
                ) : (
                  <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    animate="visible"
                    className="space-y-4"
                  >
                    {Object.entries(groupedCommands).map(([category, categoryCommands]) => {
                      return (
                        <div key={category}>
                          {/* Category header */}
                          <div className="mb-2 flex items-center space-x-2 px-2">
                            <span className="material-symbols-outlined text-sm text-outline">{categoryIcons[category]}</span>
                            <span className="text-label-sm uppercase text-outline">
                              {categoryLabels[category]}
                            </span>
                          </div>

                          {/* Category commands */}
                          <div className="space-y-1">
                            {categoryCommands.map((command, index) => {
                              const globalIndex = filteredCommands.indexOf(command);
                              const isSelected = globalIndex === selectedIndex;

                              return (
                                <motion.button
                                  key={command.id}
                                  variants={staggerItem}
                                  onClick={command.action}
                                  onMouseEnter={() => setSelectedIndex(globalIndex)}
                                  className={`flex w-full items-center space-x-3 rounded-lg px-3 py-2.5 text-left transition-colors ${
                                    isSelected
                                      ? 'bg-primary/10 text-primary'
                                      : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                                  }`}
                                >
                                  <span className={`material-symbols-outlined text-lg ${isSelected ? 'text-primary' : ''}`}>
                                    {command.icon}
                                  </span>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-body-md font-medium">
                                      {command.label}
                                    </p>
                                    {command.description && (
                                      <p className="text-body-sm text-outline">
                                        {command.description}
                                      </p>
                                    )}
                                  </div>
                                </motion.button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}
                  </motion.div>
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between border-t border-outline-variant/15 px-4 py-3">
                <div className="flex items-center space-x-4 text-label-sm text-outline">
                  <div className="flex items-center space-x-1">
                    <kbd className="rounded border border-outline-variant/30 bg-surface-container-low px-1.5 py-0.5">
                      ↑
                    </kbd>
                    <kbd className="rounded border border-outline-variant/30 bg-surface-container-low px-1.5 py-0.5">
                      ↓
                    </kbd>
                    <span>Navigate</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <kbd className="rounded border border-outline-variant/30 bg-surface-container-low px-1.5 py-0.5">
                      ↵
                    </kbd>
                    <span>Select</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
