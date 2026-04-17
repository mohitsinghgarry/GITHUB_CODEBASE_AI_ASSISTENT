/**
 * LanguageChart Component
 * 
 * Visual breakdown of programming languages in a repository.
 * 
 * Features:
 * - Horizontal bar chart with language percentages
 * - Color-coded language indicators
 * - Animated bars with stagger effect
 * - Hover interactions
 */

'use client';

import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animation-presets';
import { cn } from '@/lib/utils';
import { Code2 } from 'lucide-react';

interface LanguageData {
  /**
   * Language name
   */
  name: string;
  
  /**
   * Percentage (0-100)
   */
  percentage: number;
  
  /**
   * Number of files
   */
  fileCount: number;
  
  /**
   * Color for the language (optional, will use default if not provided)
   */
  color?: string;
}

interface LanguageChartProps {
  /**
   * Language data array
   */
  languages: LanguageData[];
  
  /**
   * Maximum number of languages to display
   * @default 10
   */
  maxLanguages?: number;
  
  /**
   * Show file counts
   * @default true
   */
  showFileCounts?: boolean;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Default language colors
 * Based on GitHub language colors
 */
const languageColors: Record<string, string> = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  Java: '#b07219',
  Go: '#00ADD8',
  Rust: '#dea584',
  'C++': '#f34b7d',
  C: '#555555',
  'C#': '#178600',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Swift: '#F05138',
  Kotlin: '#A97BFF',
  Dart: '#00B4AB',
  HTML: '#e34c26',
  CSS: '#563d7c',
  SCSS: '#c6538c',
  Shell: '#89e051',
  Markdown: '#083fa1',
  JSON: '#292929',
  YAML: '#cb171e',
  SQL: '#e38c00',
  Dockerfile: '#384d54',
};

/**
 * Get color for a language
 */
function getLanguageColor(language: string, customColor?: string): string {
  if (customColor) return customColor;
  return languageColors[language] || '#a3a6ff'; // Default to primary color
}

export function LanguageChart({
  languages,
  maxLanguages = 10,
  showFileCounts = true,
  className,
}: LanguageChartProps) {
  // Sort by percentage and limit
  const sortedLanguages = [...languages]
    .sort((a, b) => b.percentage - a.percentage)
    .slice(0, maxLanguages);

  // Calculate "Other" if there are more languages
  const hasOther = languages.length > maxLanguages;
  const otherPercentage = hasOther
    ? languages
        .slice(maxLanguages)
        .reduce((sum, lang) => sum + lang.percentage, 0)
    : 0;

  const displayLanguages = hasOther
    ? [
        ...sortedLanguages,
        {
          name: 'Other',
          percentage: otherPercentage,
          fileCount: languages
            .slice(maxLanguages)
            .reduce((sum, lang) => sum + lang.fileCount, 0),
          color: '#767577', // outline color
        },
      ]
    : sortedLanguages;

  if (languages.length === 0) {
    return (
      <div
        className={cn(
          'bg-surface-container rounded-xl p-6 border border-outline-variant/15',
          className
        )}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-tertiary/10">
            <Code2 className="w-5 h-5 text-tertiary" />
          </div>
          <h3 className="text-title-md text-text-primary font-medium">
            Language Breakdown
          </h3>
        </div>
        <p className="text-body-sm text-text-secondary">
          No language data available
        </p>
      </div>
    );
  }

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className={cn(
        'bg-surface-container rounded-xl p-6 border border-outline-variant/15',
        className
      )}
    >
      {/* Header */}
      <motion.div variants={staggerItem} className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-tertiary/10">
          <Code2 className="w-5 h-5 text-tertiary" />
        </div>
        <div>
          <h3 className="text-title-md text-text-primary font-medium">
            Language Breakdown
          </h3>
          <p className="text-body-sm text-text-secondary mt-0.5">
            {languages.length} {languages.length === 1 ? 'language' : 'languages'} detected
          </p>
        </div>
      </motion.div>

      {/* Language Bars */}
      <div className="space-y-4">
        {displayLanguages.map((language, index) => {
          const color = getLanguageColor(language.name, language.color);

          return (
            <motion.div
              key={language.name}
              variants={staggerItem}
              className="group"
            >
              {/* Language Info */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {/* Color Indicator */}
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-label-lg text-text-primary font-medium">
                    {language.name}
                  </span>
                  {showFileCounts && (
                    <span className="text-body-sm text-text-tertiary">
                      ({language.fileCount} {language.fileCount === 1 ? 'file' : 'files'})
                    </span>
                  )}
                </div>
                <span className="text-label-lg text-text-primary font-medium">
                  {language.percentage.toFixed(1)}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="h-2 bg-surface-container-low rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full transition-opacity group-hover:opacity-80"
                  style={{ backgroundColor: color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${language.percentage}%` }}
                  transition={{
                    duration: 0.5,
                    delay: index * 0.05,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legend Note */}
      {hasOther && (
        <motion.p
          variants={staggerItem}
          className="mt-4 pt-4 border-t border-outline-variant/15 text-body-sm text-text-tertiary"
        >
          Showing top {maxLanguages} languages. {languages.length - maxLanguages} other{' '}
          {languages.length - maxLanguages === 1 ? 'language' : 'languages'} grouped as "Other".
        </motion.p>
      )}
    </motion.div>
  );
}
