/**
 * Page Transition Component
 * 
 * Wraps page content with smooth entry/exit animations.
 * Use this component to wrap the main content of each page.
 */

'use client';

import { motion } from 'framer-motion';
import { pageTransition } from '@/lib/animation-presets';

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export function PageTransition({ children, className }: PageTransitionProps) {
  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
}
