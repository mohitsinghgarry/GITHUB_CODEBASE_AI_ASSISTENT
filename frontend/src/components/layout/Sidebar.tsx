'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

export function Sidebar({ isOpen = true, onToggle }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { icon: 'dashboard', label: 'Dashboard', href: '/dashboard' },
    { icon: 'forum', label: 'Chat', href: '/chat' },
    { icon: 'folder_open', label: 'File Explorer', href: '/files' },
    { icon: 'search', label: 'Search', href: '/search' },
    { icon: 'terminal', label: 'Code Review', href: '/review' },
    { icon: 'difference', label: 'Diff Review', href: '/diff-review' },
    { icon: 'auto_fix_high', label: 'Refactor', href: '/refactor' },
    { icon: 'settings', label: 'Settings', href: '/settings' },
  ];

  return (
    <aside 
      className={`fixed left-0 top-0 h-screen w-64 border-r border-outline-variant/15 flex flex-col p-4 z-50 transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0`}
      style={{
        background: 'rgba(19, 19, 21, 0.7)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 mb-10 px-2">
        <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
          <span 
            className="material-symbols-outlined text-on-primary text-xl" 
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            psychology
          </span>
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tighter text-on-surface leading-none">RepoMind</h1>
          <p className="text-[10px] uppercase tracking-widest text-outline mt-1 font-bold">AI-Powered Dev Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={`px-2 py-2 rounded-md flex items-center gap-3 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] cursor-pointer ${
                  isActive
                    ? 'text-primary font-semibold bg-surface-container'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
                }`}
              >
                <span className="material-symbols-outlined text-lg">{item.icon}</span>
                <span className="text-sm tracking-tight">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="mt-auto pt-6 space-y-4">
        <Link href="/load">
          <button className="w-full py-2.5 bg-gradient-to-r from-primary to-secondary text-on-primary font-semibold text-xs rounded-lg active:scale-95 transition-transform">
            Select Repository
          </button>
        </Link>
        <div className="space-y-2">
          <div className="px-2 flex items-center gap-3 text-on-surface-variant">
            <span className="material-symbols-outlined text-lg">dns</span>
            <span className="text-sm tracking-tight">Health Status</span>
          </div>
          <div className="px-2 flex items-center gap-3 text-on-surface-variant">
            <span className="material-symbols-outlined text-lg">psychology</span>
            <span className="text-sm tracking-tight">Model Indicator</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
