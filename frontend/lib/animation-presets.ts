/**
 * Animation Presets for RepoMind Assistant
 * Using Framer Motion for smooth, high-end animations
 * 
 * All animations use Quart easing: cubic-bezier(0.16, 1, 0.3, 1)
 * for a high-end, responsive "snap"
 * 
 * @see frontend/DESIGN_REFERENCE.md for animation guidelines
 */

import { Variants, Transition } from 'framer-motion';

/**
 * Standard easing function (Quart easing)
 */
export const quartEasing = [0.16, 1, 0.3, 1] as const;

/**
 * Standard transition with Quart easing
 */
export const standardTransition: Transition = {
  duration: 0.2,
  ease: quartEasing,
};

/**
 * Slow transition with Quart easing
 */
export const slowTransition: Transition = {
  duration: 0.3,
  ease: quartEasing,
};

/**
 * Fast transition with Quart easing
 */
export const fastTransition: Transition = {
  duration: 0.15,
  ease: quartEasing,
};

/**
 * Fade In Animation
 * Use for: Page loads, modal appearances
 */
export const fadeIn: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    transition: fastTransition,
  },
};

/**
 * Fade In (Delayed)
 * Use for: Sequential content reveals
 */
export const fadeInDelayed: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      ...standardTransition,
      delay: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: fastTransition,
  },
};

/**
 * Slide In (From Left)
 * Use for: Sidebar, drawer animations
 */
export const slideInLeft: Variants = {
  initial: {
    opacity: 0,
    x: -20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: slowTransition,
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: standardTransition,
  },
};

/**
 * Slide In (From Right)
 * Use for: Panel animations
 */
export const slideInRight: Variants = {
  initial: {
    opacity: 0,
    x: 20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: slowTransition,
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: standardTransition,
  },
};

/**
 * Slide In (From Top)
 * Use for: Dropdown menus, notifications
 */
export const slideInTop: Variants = {
  initial: {
    opacity: 0,
    y: -20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: slowTransition,
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: standardTransition,
  },
};

/**
 * Slide In (From Bottom)
 * Use for: Modals, bottom sheets
 */
export const slideInBottom: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: slowTransition,
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: standardTransition,
  },
};

/**
 * Scale In
 * Use for: Button presses, card interactions
 */
export const scaleIn: Variants = {
  initial: {
    opacity: 0,
    scale: 0.95,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: fastTransition,
  },
};

/**
 * Scale In (Large)
 * Use for: Modal appearances
 */
export const scaleInLarge: Variants = {
  initial: {
    opacity: 0,
    scale: 0.9,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: slowTransition,
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: standardTransition,
  },
};

/**
 * Stagger Container
 * Use for: List items, search results
 * Children will animate sequentially with 50ms delay
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.03,
      staggerDirection: -1,
    },
  },
};

/**
 * Stagger Item
 * Use with staggerContainer for list items
 */
export const staggerItem: Variants = {
  initial: {
    opacity: 0,
    y: 10,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: fastTransition,
  },
};

/**
 * Hover Scale
 * Use for: Interactive cards, buttons
 */
export const hoverScale = {
  scale: 1.02,
  transition: fastTransition,
};

/**
 * Tap Scale
 * Use for: Button press feedback
 */
export const tapScale = {
  scale: 0.98,
  transition: fastTransition,
};

/**
 * Pulse Animation
 * Use for: Loading indicators, attention-grabbing elements
 */
export const pulse: Variants = {
  initial: {
    opacity: 1,
  },
  animate: {
    opacity: [1, 0.5, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Skeleton Pulse
 * Use for: Loading skeletons
 */
export const skeletonPulse: Variants = {
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

/**
 * Rotate In
 * Use for: Icon animations, loading spinners
 */
export const rotateIn: Variants = {
  initial: {
    opacity: 0,
    rotate: -10,
  },
  animate: {
    opacity: 1,
    rotate: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    rotate: 10,
    transition: fastTransition,
  },
};

/**
 * Spin
 * Use for: Loading spinners
 */
export const spin: Variants = {
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
 * Expand Height
 * Use for: Accordion, collapsible sections
 */
export const expandHeight: Variants = {
  initial: {
    height: 0,
    opacity: 0,
  },
  animate: {
    height: 'auto',
    opacity: 1,
    transition: slowTransition,
  },
  exit: {
    height: 0,
    opacity: 0,
    transition: standardTransition,
  },
};

/**
 * Expand Width
 * Use for: Sidebar expansion
 */
export const expandWidth: Variants = {
  initial: {
    width: 0,
    opacity: 0,
  },
  animate: {
    width: 'auto',
    opacity: 1,
    transition: slowTransition,
  },
  exit: {
    width: 0,
    opacity: 0,
    transition: standardTransition,
  },
};

/**
 * Glow Effect
 * Use for: Focus states, active elements
 */
export const glowEffect: Variants = {
  initial: {
    boxShadow: '0 0 0 0 rgba(163, 166, 255, 0)',
  },
  animate: {
    boxShadow: '0 0 0 4px rgba(163, 166, 255, 0.1)',
    transition: fastTransition,
  },
  exit: {
    boxShadow: '0 0 0 0 rgba(163, 166, 255, 0)',
    transition: fastTransition,
  },
};

/**
 * Message Bubble (Chat)
 * Use for: Chat message animations
 */
export const messageBubble: Variants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.95,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      ...slowTransition,
      type: 'spring',
      stiffness: 300,
      damping: 30,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.95,
    transition: fastTransition,
  },
};

/**
 * Page Transition
 * Use for: Page navigation
 */
export const pageTransition: Variants = {
  initial: {
    opacity: 0,
    x: -20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.4,
      ease: quartEasing,
    },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: 0.3,
      ease: quartEasing,
    },
  },
};

/**
 * Modal Backdrop
 * Use for: Modal overlay backgrounds
 */
export const modalBackdrop: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Modal Content
 * Use for: Modal content container
 */
export const modalContent: Variants = {
  initial: {
    opacity: 0,
    scale: 0.9,
    y: 20,
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: quartEasing,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    y: 20,
    transition: {
      duration: 0.2,
      ease: quartEasing,
    },
  },
};

/**
 * Tooltip
 * Use for: Tooltip animations
 */
export const tooltip: Variants = {
  initial: {
    opacity: 0,
    scale: 0.9,
    y: -5,
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: fastTransition,
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    y: -5,
    transition: fastTransition,
  },
};

/**
 * Drawer (Sidebar)
 * Use for: Drawer/sidebar animations
 */
export const drawer: Variants = {
  initial: {
    x: '-100%',
  },
  animate: {
    x: 0,
    transition: {
      duration: 0.3,
      ease: quartEasing,
    },
  },
  exit: {
    x: '-100%',
    transition: {
      duration: 0.25,
      ease: quartEasing,
    },
  },
};

/**
 * Notification Toast
 * Use for: Toast notifications
 */
export const toast: Variants = {
  initial: {
    opacity: 0,
    y: -50,
    scale: 0.9,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: quartEasing,
    },
  },
  exit: {
    opacity: 0,
    y: -50,
    scale: 0.9,
    transition: {
      duration: 0.2,
      ease: quartEasing,
    },
  },
};

/**
 * Code Block Reveal
 * Use for: Code snippet animations
 */
export const codeBlockReveal: Variants = {
  initial: {
    opacity: 0,
    y: 10,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: quartEasing,
    },
  },
};

/**
 * Search Result
 * Use for: Search result card animations
 */
export const searchResult: Variants = {
  initial: {
    opacity: 0,
    x: -10,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: standardTransition,
  },
  exit: {
    opacity: 0,
    x: 10,
    transition: fastTransition,
  },
};

/**
 * File Tree Node
 * Use for: File tree expand/collapse
 */
export const fileTreeNode: Variants = {
  initial: {
    opacity: 0,
    height: 0,
  },
  animate: {
    opacity: 1,
    height: 'auto',
    transition: {
      height: {
        duration: 0.3,
        ease: quartEasing,
      },
      opacity: {
        duration: 0.2,
        ease: quartEasing,
      },
    },
  },
  exit: {
    opacity: 0,
    height: 0,
    transition: {
      height: {
        duration: 0.2,
        ease: quartEasing,
      },
      opacity: {
        duration: 0.15,
        ease: quartEasing,
      },
    },
  },
};

/**
 * Progress Bar
 * Use for: Loading progress animations
 */
export const progressBar: Variants = {
  initial: {
    scaleX: 0,
    originX: 0,
  },
  animate: (progress: number) => ({
    scaleX: progress / 100,
    transition: {
      duration: 0.5,
      ease: quartEasing,
    },
  }),
};

/**
 * Shimmer Effect
 * Use for: Loading placeholders
 */
export const shimmer: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};
