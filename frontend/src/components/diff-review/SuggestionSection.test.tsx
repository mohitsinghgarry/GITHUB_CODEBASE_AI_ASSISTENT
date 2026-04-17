/**
 * SuggestionSection Component Tests
 * 
 * Note: This project does not currently have a test framework configured.
 * These tests are written for Vitest + React Testing Library.
 * To run these tests, install the following dependencies:
 * 
 * npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @vitejs/plugin-react jsdom
 * 
 * And create a vitest.config.ts file in the frontend directory.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SuggestionSection } from './SuggestionSection';

describe('SuggestionSection', () => {
  it('renders suggestion text with monospace font', () => {
    const suggestion = 'Use const instead of let for immutable variables';
    render(<SuggestionSection suggestion={suggestion} />);
    
    const suggestionText = screen.getByText(suggestion);
    expect(suggestionText).toBeInTheDocument();
    expect(suggestionText).toHaveClass('font-mono');
  });

  it('displays "Suggestion" label', () => {
    render(<SuggestionSection suggestion="Test suggestion" />);
    
    const label = screen.getByText('Suggestion');
    expect(label).toBeInTheDocument();
    expect(label).toHaveClass('text-tertiary');
  });

  it('renders lightbulb icon', () => {
    render(<SuggestionSection suggestion="Test suggestion" />);
    
    const icon = screen.getByText('lightbulb');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('text-tertiary');
  });

  it('applies correct styling classes', () => {
    const { container } = render(<SuggestionSection suggestion="Test" />);
    
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('bg-surface-container-lowest');
    expect(wrapper).toHaveClass('rounded-lg');
    expect(wrapper).toHaveClass('p-4');
  });

  it('preserves whitespace in suggestion text', () => {
    const multilineSuggestion = 'Line 1\n  Line 2 with indent\nLine 3';
    render(<SuggestionSection suggestion={multilineSuggestion} />);
    
    // Use container query since getByText normalizes whitespace
    const { container } = render(<SuggestionSection suggestion={multilineSuggestion} />);
    const pre = container.querySelector('pre');
    expect(pre).toHaveClass('whitespace-pre-wrap');
    expect(pre?.textContent).toContain('Line 1');
    expect(pre?.textContent).toContain('Line 2 with indent');
  });
});
