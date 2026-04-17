# RepoMind Assistant - Frontend

Next.js 14 frontend application for the GitHub Codebase RAG Assistant.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **Styling:** TailwindCSS with custom design tokens
- **Animations:** Framer Motion
- **UI Components:** shadcn/ui + Radix UI
- **State Management:** Zustand
- **Icons:** Lucide React

## Design System

The frontend implements the **RepoMind Assistant** design system from Stitch:

- **Project ID:** 607025827578097506
- **Theme:** Dark mode with "Monolithic Curator" philosophy
- **Colors:** Electric Indigo primary, Violet secondary, Emerald tertiary
- **Typography:** Inter for UI, JetBrains Mono for code
- **Spacing:** 4px grid system
- **Animations:** Quart easing for high-end feel

### Key Design Principles

1. **No-Line Rule:** Use background color shifts instead of borders
2. **Extreme Whitespace:** 64px+ between major sections
3. **Glassmorphism:** For floating elements (modals, tooltips)
4. **Tonal Layering:** Depth through color, not shadows
5. **Quart Easing:** `cubic-bezier(0.16, 1, 0.3, 1)` for all transitions

## Project Structure

```
src/
├── app/                          # Next.js App Router pages
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page
│   ├── repositories/             # Repository management
│   │   ├── page.tsx              # Repository list
│   │   └── [id]/                 # Repository detail
│   │       ├── layout.tsx        # Repository layout with sidebar
│   │       ├── page.tsx          # Repository dashboard
│   │       ├── chat/             # Chat interface
│   │       ├── search/           # Search interface
│   │       └── files/            # File explorer
│   ├── chat/                     # Global chat
│   └── search/                   # Global search
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   ├── layout/                   # Layout components
│   ├── repo/                     # Repository components
│   ├── chat/                     # Chat components
│   ├── search/                   # Search components
│   ├── files/                    # File explorer components
│   ├── code/                     # Code review components
│   └── common/                   # Shared components
├── lib/                          # Utilities and libraries
│   ├── design-tokens.ts          # RepoMind design system tokens
│   ├── animation-presets.ts      # Framer Motion presets
│   ├── api-client.ts             # Backend API client
│   └── utils.ts                  # Common utilities
├── hooks/                        # Custom React hooks
├── store/                        # Zustand state management
└── types/                        # TypeScript type definitions
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Available Routes

- `/` - Home page with feature overview
- `/repositories` - Repository management
- `/repositories/[id]` - Repository dashboard
- `/repositories/[id]/chat` - Chat with repository
- `/repositories/[id]/search` - Search within repository
- `/repositories/[id]/files` - File explorer
- `/chat` - Global chat across all repositories
- `/search` - Global search across all repositories

## Design Tokens

Custom design tokens are defined in `src/lib/design-tokens.ts`:

```typescript
import { repoMindTokens } from '@/lib/design-tokens';

// Access colors
repoMindTokens.colors.primary.DEFAULT // #a3a6ff
repoMindTokens.colors.surface.container // #19191c

// Access spacing
repoMindTokens.spacing.xl // 2rem (32px)

// Access typography
repoMindTokens.typography.fontSize.headlineLg // 2rem
```

## Animation Presets

Framer Motion animation presets in `src/lib/animation-presets.ts`:

```typescript
import { fadeIn, slideIn, scaleIn } from '@/lib/animation-presets';

<motion.div
  variants={fadeIn}
  initial="initial"
  animate="animate"
  exit="exit"
>
  Content
</motion.div>
```

## Tailwind Utilities

Custom utilities available:

- `.glass` - Glassmorphism effect
- `.gradient-primary` - Primary gradient
- `.gradient-secondary` - Secondary gradient
- `.gradient-signature` - Signature pulse gradient
- `.ghost-border` - 15% opacity border
- `.transition-quart` - Quart easing transition
- `.text-gradient` - Gradient text effect

## Component Development

### Using Design System Colors

```tsx
<div className="bg-surface-container text-on-surface">
  <h1 className="text-headline-lg">Title</h1>
  <p className="text-body-md text-on-surface-variant">Description</p>
</div>
```

### Adding Animations

```tsx
'use client';

import { motion } from 'framer-motion';
import { fadeIn, fadeInTransition } from '@/lib/animation-presets';

export function MyComponent() {
  return (
    <motion.div
      variants={fadeIn}
      transition={fadeInTransition}
      initial="initial"
      animate="animate"
    >
      Content
    </motion.div>
  );
}
```

### Using API Client

```tsx
import apiClient from '@/lib/api-client';

async function loadRepositories() {
  try {
    const repos = await apiClient.repositories.list();
    console.log(repos);
  } catch (error) {
    console.error('Failed to load repositories:', error);
  }
}
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run format` - Format code with Prettier

## Next Steps

1. Implement component library (buttons, inputs, cards)
2. Build repository management UI
3. Create chat interface with streaming
4. Implement search interface
5. Add file explorer with syntax highlighting
6. Build code review interface
7. Add state management with Zustand
8. Implement error handling and loading states
9. Add responsive design for mobile/tablet
10. Optimize performance and accessibility

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [RepoMind Design Reference](./DESIGN_REFERENCE.md)

## License

MIT
