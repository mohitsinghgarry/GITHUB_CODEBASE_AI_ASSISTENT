/**
 * SuggestedQuestions Component
 * 
 * Displays suggested questions for empty chat state.
 * Features:
 * - Clickable question cards
 * - Category grouping
 * - Smooth animations
 * - Empty state illustration
 */

'use client';

import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import {
  MessageSquare,
  Search,
  FileCode,
  GitBranch,
  Bug,
  Lightbulb,
} from 'lucide-react';

interface SuggestedQuestionsProps {
  /**
   * Callback when a question is clicked
   */
  onQuestionClick: (question: string) => void;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

interface QuestionCategory {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  questions: string[];
}

const questionCategories: QuestionCategory[] = [
  {
    title: 'Understanding Code',
    icon: FileCode,
    questions: [
      'What does this codebase do?',
      'Explain the main architecture',
      'How does authentication work?',
    ],
  },
  {
    title: 'Finding Code',
    icon: Search,
    questions: [
      'Where is the user authentication logic?',
      'Show me the database models',
      'Find the API endpoints',
    ],
  },
  {
    title: 'Code Quality',
    icon: Bug,
    questions: [
      'Are there any security vulnerabilities?',
      'What are the code quality issues?',
      'Suggest improvements for performance',
    ],
  },
  {
    title: 'Best Practices',
    icon: Lightbulb,
    questions: [
      'How can I improve error handling?',
      'What testing strategy should I use?',
      'Suggest refactoring opportunities',
    ],
  },
];

export function SuggestedQuestions({
  onQuestionClick,
  className,
}: SuggestedQuestionsProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center h-full py-12', className)}>
      {/* Empty State Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="text-center mb-12"
      >
        <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/10">
          <MessageSquare className="w-8 h-8 text-primary" />
        </div>
        <h3 className="text-headline-sm text-text-primary font-semibold mb-2">
          Start a Conversation
        </h3>
        <p className="text-body-md text-text-secondary max-w-md">
          Ask questions about your codebase, find specific code, or get suggestions for improvements
        </p>
      </motion.div>

      {/* Suggested Questions Grid */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl"
      >
        {questionCategories.map((category) => {
          const Icon = category.icon;
          
          return (
            <motion.div
              key={category.title}
              variants={staggerItem}
              className="space-y-3"
            >
              {/* Category Header */}
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-text-secondary" />
                <h4 className="text-label-lg text-text-secondary font-medium uppercase tracking-wider">
                  {category.title}
                </h4>
              </div>

              {/* Questions */}
              <div className="space-y-2">
                {category.questions.map((question, index) => (
                  <motion.button
                    key={index}
                    onClick={() => onQuestionClick(question)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={cn(
                      'w-full text-left px-4 py-3 rounded-lg',
                      'bg-surface-container-low border border-outline-variant/15',
                      'hover:bg-surface-container-high hover:border-outline-variant/30',
                      'transition-all duration-150',
                      'focus:outline-none focus:ring-2 focus:ring-primary/20',
                      'group'
                    )}
                  >
                    <span className="text-body-md text-text-primary group-hover:text-primary transition-colors">
                      {question}
                    </span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Footer Hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.35 }}
        className="text-body-sm text-text-tertiary mt-12 text-center"
      >
        Or type your own question below
      </motion.p>
    </div>
  );
}
