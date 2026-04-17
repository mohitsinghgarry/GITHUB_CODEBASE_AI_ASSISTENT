/**
 * Animation Presets: RepoMind Assistant
 * 
 * Framer Motion variants for consistent animations across the application
 * Uses Quart easing (cubic-bezier(0.16, 1, 0.3, 1)) for high-end, responsive "snap"
 */

import { Variants, Transition } from 'framer-motion';

/**
 * Standard Easing Functions
 */
export const easing = {
  quart: [0.16, 1, 0.3, 1],           // High-end snap (primary)
  standard: [0.4, 0, 0.2, 1],         // Material standard
  decelerate: [0, 0, 0.2, 1],         // Deceleration curve
  accelerate: [0.4, 0, 1, 1],         // Acceleration curve
} as const;

/**
 * Standard Durations
 */
export const duration = {
  fast: 0.15,
  normal: 0.25,
  slow: 0.35,
} as const;

/**
 * Standard Transition
 */
export const standardTransition: Transition = {
  duration: duration.normal,
  ease: easing.quart,
};

/**
 * Fade In Animation
 * Use for: General content appearance, overlays
 */
export const fadeIn: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Fade In Up Animation
 * Use for: Cards, modals, toast notifications
 */
export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Fade In Down Animation
 * Use for: Dropdowns, tooltips
 */
export const fadeInDown: Variants = {
  hidden: {
    opacity: 0,
    y: -20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Slide In Left Animation
 * Use for: Sidebar, side panels
 */
export const slideInLeft: Variants = {
  hidden: {
    x: -100,
    opacity: 0,
  },
  visible: {
    x: 0,
    opacity: 1,
    transition: standardTransition,
  },
  exit: {
    x: -100,
    opacity: 0,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Slide In Right Animation
 * Use for: Right panels, context menus
 */
export const slideInRight: Variants = {
  hidden: {
    x: 100,
    opacity: 0,
  },
  visible: {
    x: 0,
    opacity: 1,
    transition: standardTransition,
  },
  exit: {
    x: 100,
    opacity: 0,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Scale In Animation
 * Use for: Buttons, interactive elements, success states
 */
export const scaleIn: Variants = {
  hidden: {
    scale: 0.9,
    opacity: 0,
  },
  visible: {
    scale: 1,
    opacity: 1,
    transition: standardTransition,
  },
  exit: {
    scale: 0.95,
    opacity: 0,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Scale In Center Animation
 * Use for: Modals, dialogs
 */
export const scaleInCenter: Variants = {
  hidden: {
    scale: 0.95,
    opacity: 0,
  },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  },
  exit: {
    scale: 0.95,
    opacity: 0,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Stagger Container Animation
 * Use for: Lists, grids, multiple items appearing in sequence
 */
export const staggerContainer: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.03,
      staggerDirection: -1,
    },
  },
};

/**
 * Stagger Item Animation
 * Use with staggerContainer for individual items
 */
export const staggerItem: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: { duration: duration.fast, ease: easing.quart },
  },
};

/**
 * Expand Animation
 * Use for: Accordions, expandable sections
 */
export const expand: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    overflow: 'hidden',
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    overflow: 'visible',
    transition: {
      height: {
        duration: duration.normal,
        ease: easing.quart,
      },
      opacity: {
        duration: duration.fast,
        ease: easing.quart,
      },
    },
  },
};

/**
 * Pulse Animation
 * Use for: Loading states, attention-grabbing elements
 */
export const pulse: Variants = {
  initial: {
    scale: 1,
    opacity: 1,
  },
  animate: {
    scale: [1, 1.05, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: easing.standard,
    },
  },
};

/**
 * Shimmer Animation
 * Use for: Skeleton loaders
 */
export const shimmer: Variants = {
  initial: {
    backgroundPosition: '-200% 0',
  },
  animate: {
    backgroundPosition: '200% 0',
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Rotate Animation
 * Use for: Loading spinners
 */
export const rotate: Variants = {
  initial: {
    rotate: 0,
  },
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Bounce Animation
 * Use for: Success indicators, playful interactions
 */
export const bounce: Variants = {
  initial: {
    y: 0,
  },
  animate: {
    y: [-10, 0, -5, 0],
    transition: {
      duration: 0.6,
      ease: easing.quart,
    },
  },
};

/**
 * Slide Up Animation (for bottom sheets, mobile)
 * Use for: Mobile bottom sheets, drawers
 */
export const slideUp: Variants = {
  hidden: {
    y: '100%',
    opacity: 0,
  },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  },
  exit: {
    y: '100%',
    opacity: 0,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Page Transition Animation
 * Use for: Page-level transitions
 */
export const pageTransition: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Hover Scale Animation
 * Use for: Interactive cards, buttons
 */
export const hoverScale = {
  rest: {
    scale: 1,
  },
  hover: {
    scale: 1.02,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
  tap: {
    scale: 0.98,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Hover Lift Animation
 * Use for: Cards that should "lift" on hover
 */
export const hoverLift = {
  rest: {
    y: 0,
  },
  hover: {
    y: -4,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Focus Ring Animation
 * Use for: Focus states on interactive elements
 */
export const focusRing: Variants = {
  initial: {
    boxShadow: '0 0 0 0px rgba(163, 166, 255, 0)',
  },
  focused: {
    boxShadow: '0 0 0 4px rgba(163, 166, 255, 0.1)',
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Message Bubble Animation
 * Use for: Chat messages
 */
export const messageBubble: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 10,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  },
};

/**
 * Code Block Animation
 * Use for: Code snippets appearing
 */
export const codeBlock: Variants = {
  hidden: {
    opacity: 0,
    y: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: duration.slow,
      ease: easing.quart,
    },
  },
};

/**
 * Tree Node Animation
 * Use for: File tree nodes expanding/collapsing
 */
export const treeNode: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: {
      height: {
        duration: duration.normal,
        ease: easing.quart,
      },
      opacity: {
        duration: duration.fast,
        ease: easing.quart,
        delay: 0.05,
      },
    },
  },
};

/**
 * Toast Notification Animation
 * Use for: Toast notifications
 */
export const toast: Variants = {
  hidden: {
    opacity: 0,
    y: -20,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: duration.fast,
      ease: easing.quart,
    },
  },
};

/**
 * Progress Bar Animation
 * Use for: Progress indicators
 */
export const progressBar = {
  initial: {
    scaleX: 0,
    originX: 0,
  },
  animate: (progress: number) => ({
    scaleX: progress / 100,
    transition: {
      duration: duration.normal,
      ease: easing.quart,
    },
  }),
};

/**
 * Skeleton Loader Animation
 * Use for: Loading skeletons
 */
export const skeleton: Variants = {
  initial: {
    opacity: 0.5,
  },
  animate: {
    opacity: [0.5, 0.8, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};
