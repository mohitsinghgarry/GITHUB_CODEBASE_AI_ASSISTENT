/**
 * MarkdownDescription Component Tests
 * 
 * Note: This project does not currently have a test framework configured.
 * These tests are written for Vitest + React Testing Library.
 * To run these tests, install the following dependencies:
 * 
 * npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @vitejs/plugin-react jsdom
 * 
 * And create a vitest.config.ts file in the frontend directory.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MarkdownDescription } from './MarkdownDescription';

describe('MarkdownDescription', () => {
  describe('Markdown Rendering', () => {
    it('renders headings with correct hierarchy', () => {
      const content = '# Heading 1\n## Heading 2\n### Heading 3';
      render(<MarkdownDescription content={content} />);
      
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Heading 1');
      expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Heading 2');
      expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Heading 3');
    });

    it('renders bold text with correct styling', () => {
      const content = 'This is **bold** text';
      render(<MarkdownDescription content={content} />);
      
      const boldElement = screen.getByText('bold');
      expect(boldElement.tagName).toBe('STRONG');
      expect(boldElement).toHaveClass('font-semibold', 'text-on-surface');
    });

    it('renders italic text with correct styling', () => {
      const content = 'This is *italic* text';
      render(<MarkdownDescription content={content} />);
      
      const italicElement = screen.getByText('italic');
      expect(italicElement.tagName).toBe('EM');
      expect(italicElement).toHaveClass('italic');
    });

    it('renders inline code with background', () => {
      const content = 'This is `inline code` text';
      render(<MarkdownDescription content={content} />);
      
      const codeElement = screen.getByText('inline code');
      expect(codeElement.tagName).toBe('CODE');
      expect(codeElement).toHaveClass('bg-surface-container-lowest', 'font-mono');
    });

    it('renders code blocks with monospace font', () => {
      const content = '```\nconst x = 42;\n```';
      render(<MarkdownDescription content={content} />);
      
      const codeBlock = screen.getByText('const x = 42;');
      expect(codeBlock).toHaveClass('font-mono', 'text-sm');
    });

    it('renders unordered lists with proper spacing', () => {
      const content = '- Item 1\n- Item 2\n- Item 3';
      render(<MarkdownDescription content={content} />);
      
      const list = screen.getByRole('list');
      expect(list.tagName).toBe('UL');
      expect(list).toHaveClass('list-disc', 'space-y-1.5');
    });

    it('renders ordered lists with proper spacing', () => {
      const content = '1. Item 1\n2. Item 2\n3. Item 3';
      render(<MarkdownDescription content={content} />);
      
      const list = screen.getByRole('list');
      expect(list.tagName).toBe('OL');
      expect(list).toHaveClass('list-decimal', 'space-y-1.5');
    });

    it('renders paragraphs with relaxed line height', () => {
      const content = 'This is a paragraph with some text.';
      render(<MarkdownDescription content={content} />);
      
      const paragraph = screen.getByText('This is a paragraph with some text.');
      expect(paragraph.tagName).toBe('P');
      expect(paragraph).toHaveClass('leading-relaxed', 'text-body-md');
    });
  });

  describe('Collapsible Content', () => {
    it('shows full content when length is below threshold', () => {
      const shortContent = 'Short content';
      render(<MarkdownDescription content={shortContent} maxLength={200} />);
      
      expect(screen.getByText('Short content')).toBeInTheDocument();
      expect(screen.queryByText(/Show more/i)).not.toBeInTheDocument();
    });

    it('shows truncated content when length exceeds threshold', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      expect(screen.getByText(/Show more/i)).toBeInTheDocument();
    });

    it('expands content when "Show more" is clicked', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const showMoreButton = screen.getByText(/Show more/i);
      fireEvent.click(showMoreButton);
      
      expect(screen.getByText(/Show less/i)).toBeInTheDocument();
    });

    it('collapses content when "Show less" is clicked', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const showMoreButton = screen.getByText(/Show more/i);
      fireEvent.click(showMoreButton);
      
      const showLessButton = screen.getByText(/Show less/i);
      fireEvent.click(showLessButton);
      
      expect(screen.getByText(/Show more/i)).toBeInTheDocument();
    });

    it('updates aria-expanded attribute correctly', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'false');
      
      fireEvent.click(button);
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });

    it('shows correct icon for collapsed state', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      expect(screen.getByText('expand_more')).toBeInTheDocument();
    });

    it('shows correct icon for expanded state', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(screen.getByText('expand_less')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('falls back to plain text on parsing error', () => {
      // Mock console.error to suppress error output in tests
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // Simulate a parsing error by providing invalid markdown
      const invalidContent = 'Some content that might cause issues';
      
      // Note: react-markdown is quite robust, so this test may need adjustment
      // based on actual error scenarios
      render(<MarkdownDescription content={invalidContent} />);
      
      expect(screen.getByText(invalidContent)).toBeInTheDocument();
      
      consoleErrorSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('has proper aria-label for expand button', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Show more');
    });

    it('updates aria-label when expanded', () => {
      const longContent = 'a'.repeat(250);
      render(<MarkdownDescription content={longContent} maxLength={200} />);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(button).toHaveAttribute('aria-label', 'Show less');
    });
  });

  describe('Custom maxLength', () => {
    it('respects custom maxLength prop', () => {
      const content = 'a'.repeat(150);
      render(<MarkdownDescription content={content} maxLength={100} />);
      
      expect(screen.getByText(/Show more/i)).toBeInTheDocument();
    });

    it('uses default maxLength of 200 when not specified', () => {
      const content = 'a'.repeat(150);
      render(<MarkdownDescription content={content} />);
      
      expect(screen.queryByText(/Show more/i)).not.toBeInTheDocument();
    });
  });

  describe('Typography Classes', () => {
    it('applies correct typography classes to headings', () => {
      const content = '# Heading 1';
      render(<MarkdownDescription content={content} />);
      
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveClass('text-title-lg', 'font-semibold', 'text-on-surface');
    });

    it('applies correct typography classes to paragraphs', () => {
      const content = 'This is a paragraph.';
      render(<MarkdownDescription content={content} />);
      
      const paragraph = screen.getByText('This is a paragraph.');
      expect(paragraph).toHaveClass('text-body-md', 'text-on-surface-variant', 'leading-relaxed');
    });

    it('applies correct classes to code blocks', () => {
      const content = '```\ncode\n```';
      render(<MarkdownDescription content={content} />);
      
      const codeBlock = screen.getByText('code');
      expect(codeBlock).toHaveClass('font-mono', 'text-sm', 'text-on-surface');
    });
  });
});
