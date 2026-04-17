/**
 * Landing Page - RepoMind Assistant
 * 
 * Pixel-perfect implementation of Stitch design
 * "Obsidian Intelligence" Framework with glassmorphism and gradient accents
 */

'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <>
      {/* Top Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center justify-between px-6 bg-[rgba(19,19,21,0.7)] backdrop-blur-xl border-b border-outline-variant/15">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded flex items-center justify-center">
            <span className="material-symbols-outlined text-on-primary text-xl">psychology</span>
          </div>
          <span className="text-xl font-bold tracking-tighter text-on-surface">RepoMind</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a className="text-sm font-medium text-on-surface transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] hover:text-primary" href="#">
            Breadcrumbs
          </a>
          <div className="h-4 w-[1px] bg-outline-variant/30"></div>
          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:text-on-surface transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <div className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant/30">
              <img 
                alt="User Profile" 
                className="w-full h-full object-cover" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBZlvTJRMxE1TuOtRBkochsLxLzRKRfoCS_knr1AmlS5O4m96taRhsSQU896-ow6eRq1BjHmJGpNq5z9W0eQr88rjx_4O74e8DxqUl4pEd6853F5LqZ81ZycbGmnQkbVsnSby89jefXXgqkOCJywoNBCTHAit1FodWQihfZ81HDej47Y-Sbq69G5fPSB0FwCvukDgRqvDlP8xHVtHisIHWOHSr_Soc2G06CqNCDWA2URmfxakWRRnwyPhUNb6uF8qNSUqvTYe8KwA"
              />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative min-h-screen flex flex-col items-center justify-center pt-24 px-6 overflow-hidden">
        {/* Ambient Background Pulse */}
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-primary/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] bg-secondary/10 rounded-full blur-[120px] pointer-events-none"></div>
        
        <div className="max-w-5xl w-full text-center space-y-8 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-high border border-outline-variant/15">
            <span className="w-2 h-2 rounded-full bg-tertiary"></span>
            <span className="text-[10px] uppercase tracking-widest font-bold text-on-surface-variant">v2.0 Now Live</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter leading-[1.1]">
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Understand any GitHub repository
            </span>{' '}
            in seconds
          </h1>
          
          <p className="text-lg md:text-xl text-on-surface-variant max-w-2xl mx-auto leading-relaxed">
            RepoMind connects your codebase with advanced AI intelligence to provide instant architectural insights, bug detection, and documentation generation.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/load">
              <button className="px-8 py-3 bg-gradient-to-r from-primary to-secondary text-on-primary font-bold rounded-lg shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
                Load a Repository
              </button>
            </Link>
            <button className="px-8 py-3 bg-surface-bright text-on-surface font-semibold rounded-lg border border-outline-variant/15 hover:bg-surface-container-highest transition-colors duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">terminal</span>
              View on GitHub
            </button>
          </div>
        </div>

        {/* Live-looking Demo Mockup */}
        <div className="mt-20 w-full max-w-6xl mx-auto relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/30 to-secondary/30 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative bg-surface-container-lowest border border-outline-variant/15 rounded-xl shadow-2xl overflow-hidden aspect-video flex">
            {/* Sidebar Mock */}
            <div className="w-16 border-r border-outline-variant/15 bg-surface-container-low flex flex-col items-center py-4 gap-6">
              <span className="material-symbols-outlined text-primary">dashboard</span>
              <span className="material-symbols-outlined text-on-surface-variant">folder_open</span>
              <span className="material-symbols-outlined text-on-surface-variant">search</span>
              <span className="material-symbols-outlined text-on-surface-variant">settings</span>
            </div>
            {/* Main Content Mock */}
            <div className="flex-1 flex flex-col">
              <div className="h-10 border-b border-outline-variant/15 bg-surface-container flex items-center px-4 justify-between">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-error-dim/50"></div>
                  <div className="w-3 h-3 rounded-full bg-tertiary-dim/50"></div>
                  <div className="w-3 h-3 rounded-full bg-primary-dim/50"></div>
                </div>
                <span className="text-[10px] font-mono text-outline uppercase tracking-widest">src/main.ts</span>
              </div>
              <div className="flex flex-1 overflow-hidden">
                {/* Chat Column */}
                <div className="w-1/3 border-r border-outline-variant/15 p-4 space-y-4 bg-surface-container-low/50">
                  <div className="p-3 rounded bg-surface-container border border-outline-variant/15">
                    <p className="text-xs text-on-surface-variant font-mono">Analyze the authentication flow in this module.</p>
                  </div>
                  <div className="p-3 rounded bg-primary/10 border border-primary/20">
                    <p className="text-xs text-on-surface font-mono">The authentication uses an OAuth2 provider via the `authService`. It validates JWT tokens on lines 42-58...</p>
                  </div>
                </div>
                {/* Code Column */}
                <div className="flex-1 p-6 font-mono text-xs bg-surface-container-lowest overflow-hidden">
                  <div className="flex gap-4">
                    <span className="text-outline">01</span>
                    <span className="text-tertiary">import</span> <span className="text-on-surface">{'{ AuthService } from "./services";'}</span>
                  </div>
                  <div className="flex gap-4">
                    <span className="text-outline">02</span>
                    <span className="text-tertiary">import</span> <span className="text-on-surface">{'{ User } from "./models";'}</span>
                  </div>
                  <div className="flex gap-4 mt-2">
                    <span className="text-outline">03</span>
                    <span className="text-error-dim">export class</span> <span className="text-primary">AuthHandler</span> <span className="text-on-surface">{'{'}</span>
                  </div>
                  <div className="flex gap-4 pl-4">
                    <span className="text-outline">04</span>
                    <span className="text-on-surface-variant">private readonly service: AuthService;</span>
                  </div>
                  <div className="flex gap-4 pl-4 mt-2">
                    <span className="text-outline">05</span>
                    <span className="text-primary">async</span> <span className="text-tertiary">validate</span><span className="text-on-surface">(token: string) {'{'}</span>
                  </div>
                  <div className="flex gap-4 pl-8">
                    <span className="text-outline">06</span>
                    <span className="text-on-surface-variant">// AI Suggestion: Add error handling for expired tokens</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Feature Highlights Strip */}
      <section className="py-12 border-y border-outline-variant/15 bg-surface-container-low">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center">
              <span className="material-symbols-outlined text-primary">search_spark</span>
            </div>
            <div>
              <h3 className="font-bold text-on-surface">Semantic Search</h3>
              <p className="text-sm text-on-surface-variant">Find logic, not just strings.</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center">
              <span className="material-symbols-outlined text-secondary">forum</span>
            </div>
            <div>
              <h3 className="font-bold text-on-surface">AI Chat</h3>
              <p className="text-sm text-on-surface-variant">Converse with your logic.</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center">
              <span className="material-symbols-outlined text-tertiary">terminal</span>
            </div>
            <div>
              <h3 className="font-bold text-on-surface">Code Review</h3>
              <p className="text-sm text-on-surface-variant">Automated architectural audits.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-32 bg-surface">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-24">
            <h2 className="text-4xl font-bold tracking-tight mb-4">Architecture to Insights</h2>
            <p className="text-on-surface-variant">A streamlined pipeline for repository intelligence.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-1">
            {/* Step 1 */}
            <div className="p-8 bg-surface-container-low border border-outline-variant/15 rounded-xl group hover:bg-surface-container transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
              <div className="text-6xl font-black text-outline/10 mb-6 group-hover:text-primary/20 transition-colors">01</div>
              <h4 className="font-bold mb-2">Sync Repo</h4>
              <p className="text-sm text-on-surface-variant leading-relaxed">Connect any public or private GitHub repository in one click.</p>
            </div>
            {/* Step 2 */}
            <div className="p-8 bg-surface-container-low border border-outline-variant/15 rounded-xl group hover:bg-surface-container transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] md:mt-8">
              <div className="text-6xl font-black text-outline/10 mb-6 group-hover:text-secondary/20 transition-colors">02</div>
              <h4 className="font-bold mb-2">AI Indexing</h4>
              <p className="text-sm text-on-surface-variant leading-relaxed">Our models map dependencies and logic flows in minutes.</p>
            </div>
            {/* Step 3 */}
            <div className="p-8 bg-surface-container-low border border-outline-variant/15 rounded-xl group hover:bg-surface-container transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
              <div className="text-6xl font-black text-outline/10 mb-6 group-hover:text-tertiary/20 transition-colors">03</div>
              <h4 className="font-bold mb-2">Chat & Query</h4>
              <p className="text-sm text-on-surface-variant leading-relaxed">Ask questions like &quot;Where is state managed?&quot; or &quot;Find vulnerabilities.&quot;</p>
            </div>
            {/* Step 4 */}
            <div className="p-8 bg-surface-container-low border border-outline-variant/15 rounded-xl group hover:bg-surface-container transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] md:mt-8">
              <div className="text-6xl font-black text-outline/10 mb-6 group-hover:text-primary/20 transition-colors">04</div>
              <h4 className="font-bold mb-2">Ship Faster</h4>
              <p className="text-sm text-on-surface-variant leading-relaxed">Onboard developers in days, not weeks, with instant context.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Case Cards */}
      <section className="py-32 bg-surface-container-lowest">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-8">
            <div className="max-w-xl">
              <h2 className="text-4xl font-bold tracking-tight mb-4">Engineered for Dev Teams</h2>
              <p className="text-on-surface-variant leading-relaxed">RepoMind integrates seamlessly into your workflow, providing value from day one.</p>
            </div>
            <div className="flex gap-4">
              <div className="w-12 h-12 flex items-center justify-center rounded-full border border-outline-variant/15 hover:bg-surface-bright transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] cursor-pointer">
                <span className="material-symbols-outlined">arrow_back</span>
              </div>
              <div className="w-12 h-12 flex items-center justify-center rounded-full border border-outline-variant/15 hover:bg-surface-bright transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] cursor-pointer">
                <span className="material-symbols-outlined">arrow_forward</span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Case 1 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-primary/40 transition-colors group">
              <img 
                alt="Tech Onboarding" 
                className="w-full h-40 object-cover rounded-lg mb-6 grayscale group-hover:grayscale-0 transition-all duration-500" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAU8ZE7US7_r4i98UdEAk5jeOafYdw2ZN7PdBdXnOmy_MwwAaVO6rHpcPfK8MQf7SM3iTQQGZVgczBzG5hpMEmIt6A_OlS-x754JUHrK83Ncerv9vJkBl8NPaJwSdmHOWsMPuJNVfL-jI6NtWNVF0UC9iEUwDoVfVT269-l0YOVW2BF1PGqz8_P-t1zKLXITf80I77xfad7gB_QxkSWw1x3jogRzP-N9oycCwaA2Rkij7RGHkwQdX0_VQ6QX8i2wkKbchLjAN0k3g"
              />
              <h4 className="font-bold mb-2 text-on-surface">Developer Onboarding</h4>
              <p className="text-sm text-on-surface-variant">Let new hires explore the codebase through AI-guided tours instead of hunting through stale docs.</p>
            </div>
            {/* Case 2 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-secondary/40 transition-colors group">
              <img 
                alt="Code Refactor" 
                className="w-full h-40 object-cover rounded-lg mb-6 grayscale group-hover:grayscale-0 transition-all duration-500" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuC8owLmw3kUxOKCopCMlHXk0j7VEh07IXrmPv0NKxMVal0bsmlA197W8gD7GkUpdsDpB1AnxGKWQGBFIj336SIMhMd_GGKtIbm8KS3P6GWgisb85ltbDC0lWrva7jc3bsEcte3v__jlR8RxooGsD7m3OEcX_TXAJ2BHE4SLfklPZyrwHaANzc0Y9AMR9GdmLlhiqdMT7TDi4MwKimL8aGgyYRNQpICoyhbPr7yNO7I3WijOAwVYtm8azhSO4_WPYZZgEXqlu7Lzug"
              />
              <h4 className="font-bold mb-2 text-on-surface">Legacy Refactoring</h4>
              <p className="text-sm text-on-surface-variant">Map out complex monolithic structures and safely decouple services with automated impact analysis.</p>
            </div>
            {/* Case 3 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-tertiary/40 transition-colors group">
              <img 
                alt="Security Audit" 
                className="w-full h-40 object-cover rounded-lg mb-6 grayscale group-hover:grayscale-0 transition-all duration-500" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBoJ5bihS0l9bh7fLVzdy2aDUy9jmo4FIZtTZt6-S3Z7NeiQKZ9Cd3u9pqvZbf-6h3L8UZzq2QmKIaLb-QpQ3NYvD0iqVSG7CBoKH3ifpNzuMmFLd_irpjjLb6vH84vxxNfo4htSJmwGhyghmetufq1PBIAQAbeRHkYBtDIxqHokiFftL1HiNlYfKMGpuEgamlq5OEYwtU3TzHAbY2QyaaqHo8pUzimpBXQeruM40dSUavP5VhMua3wuMDo971kdfHjO2tx-L8Utg"
              />
              <h4 className="font-bold mb-2 text-on-surface">Security Auditing</h4>
              <p className="text-sm text-on-surface-variant">Find logic vulnerabilities that traditional static analysis tools miss by understanding intent.</p>
            </div>
            {/* Case 4 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-primary/40 transition-colors group">
              <div className="w-full h-40 bg-surface-container-highest rounded-lg mb-6 flex items-center justify-center">
                <span className="material-symbols-outlined text-4xl text-outline-variant">description</span>
              </div>
              <h4 className="font-bold mb-2 text-on-surface">Live Documentation</h4>
              <p className="text-sm text-on-surface-variant">Generate and maintain READMEs and internal wikis that update automatically as code changes.</p>
            </div>
            {/* Case 5 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-secondary/40 transition-colors group">
              <div className="w-full h-40 bg-surface-container-highest rounded-lg mb-6 flex items-center justify-center">
                <span className="material-symbols-outlined text-4xl text-outline-variant">bug_report</span>
              </div>
              <h4 className="font-bold mb-2 text-on-surface">Bug Triage</h4>
              <p className="text-sm text-on-surface-variant">Paste a stack trace and let RepoMind locate the exact failure point and suggest a fix.</p>
            </div>
            {/* Case 6 */}
            <div className="p-6 bg-surface-container rounded-xl border border-outline-variant/10 hover:border-tertiary/40 transition-colors group">
              <div className="w-full h-40 bg-surface-container-highest rounded-lg mb-6 flex items-center justify-center">
                <span className="material-symbols-outlined text-4xl text-outline-variant">account_tree</span>
              </div>
              <h4 className="font-bold mb-2 text-on-surface">Feature Scoping</h4>
              <p className="text-sm text-on-surface-variant">Predict how a new feature will affect your existing architecture before writing a single line of code.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface-container-lowest border-t border-outline-variant/15 pt-24 pb-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-12 mb-20">
            <div className="col-span-2">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
                  <span className="material-symbols-outlined text-on-primary text-sm">psychology</span>
                </div>
                <span className="text-lg font-bold tracking-tighter">RepoMind</span>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed max-w-xs">
                The intelligence layer for your development workflow. Built by developers, for the next generation of code.
              </p>
            </div>
            <div>
              <h5 className="text-[10px] uppercase tracking-[0.2em] font-bold text-outline mb-6">Product</h5>
              <ul className="space-y-4 text-sm text-on-surface-variant">
                <li><a className="hover:text-primary transition-colors" href="#">Features</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Pricing</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">API Docs</a></li>
              </ul>
            </div>
            <div>
              <h5 className="text-[10px] uppercase tracking-[0.2em] font-bold text-outline mb-6">Company</h5>
              <ul className="space-y-4 text-sm text-on-surface-variant">
                <li><a className="hover:text-primary transition-colors" href="#">About</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Changelog</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Terms</a></li>
              </ul>
            </div>
            <div>
              <h5 className="text-[10px] uppercase tracking-[0.2em] font-bold text-outline mb-6">Social</h5>
              <ul className="space-y-4 text-sm text-on-surface-variant">
                <li><a className="hover:text-primary transition-colors" href="#">Twitter</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">GitHub</a></li>
                <li><a className="hover:text-primary transition-colors" href="#">Discord</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-outline-variant/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-xs text-outline">© 2024 RepoMind Intelligence Inc. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <span className="text-xs text-tertiary flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-tertiary"></span>
                All Systems Operational
              </span>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
