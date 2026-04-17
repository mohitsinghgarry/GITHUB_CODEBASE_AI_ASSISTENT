'use client';

import { usePathname } from 'next/navigation';

interface TopNavProps {
  onMenuClick?: () => void;
}

export function TopNav({ onMenuClick }: TopNavProps) {
  const pathname = usePathname();

  // Generate breadcrumbs from pathname
  const generateBreadcrumbs = () => {
    const segments = pathname.split('/').filter(Boolean);
    
    if (segments.length === 0) {
      return 'Home';
    }

    return segments
      .map(segment => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(' / ');
  };

  return (
    <header 
      className="sticky top-0 h-14 w-full flex items-center justify-between px-8 border-b border-outline-variant/15 z-40"
      style={{
        background: 'rgba(19, 19, 21, 0.7)',
        backdropFilter: 'blur(20px)',
      }}
    >
      {/* Left: Breadcrumbs */}
      <div className="flex items-center gap-4">
        <nav className="flex text-sm">
          <span className="text-on-surface-variant">Projects</span>
          <span className="mx-2 text-outline">/</span>
          <span className="text-on-surface font-medium">repomind-core-engine</span>
        </nav>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-6">
        {/* Search */}
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-outline text-lg">
            search
          </span>
          <input
            className="bg-surface-container-low border-none rounded-md pl-10 pr-4 py-1.5 text-sm text-on-surface placeholder-outline w-64 focus:ring-1 focus:ring-primary-dim transition-all"
            placeholder="Search across files..."
            type="text"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="text-on-surface-variant hover:text-on-surface transition-colors relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full border-2 border-background"></span>
          </button>

          {/* User Profile */}
          <div className="w-8 h-8 rounded-full overflow-hidden bg-surface-container-high ring-1 ring-outline-variant/30">
            <img
              alt="User Profile"
              className="w-full h-full object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuC7Dznb782Ic1ztCSP8ewCQ-uufrsHJ7u_gvI6_BpSUVTyZxgJO5ogmdgntfyvWPpq_dd9gmeY3YK_ZWIXQnB5g1piEori1ZkDojcJeNEr2c2MbUX8_RDnf5KRI6J1b2zTr9i8jlVZv-VvqcFTX5bsYdpaVMNY7u19KT_1Xx_F_3WdUFv0BAXJw0aCBCCCm7MpFgFRY7qOvWBSzSg0mNAd13XQBKHdQ6qStoPsn0BpfPmZesSQNdhyUJBLBIJBn3gCw59bti6lzUQ"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
