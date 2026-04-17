/**
 * CitationNavigator Component Tests
 * 
 * Note: This project does not currently have a test framework configured.
 * These tests are written for Jest/Vitest + React Testing Library.
 * To run these tests, install the following dependencies:
 * 
 * npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @vitejs/plugin-react jsdom
 * 
 * And create a vitest.config.ts file in the frontend directory.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CitationNavigator } from './CitationNavigator';

describe('CitationNavigator', () => {
  it('renders current index and total count correctly', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={0}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    expect(screen.getByText('1 / 3')).toBeInTheDocument();
  });

  it('disables previous button when at first citation', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={0}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    const previousButton = screen.getByLabelText('Previous citation');
    expect(previousButton).toBeDisabled();
  });

  it('disables next button when at last citation', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={2}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    const nextButton = screen.getByLabelText('Next citation');
    expect(nextButton).toBeDisabled();
  });

  it('calls onPrevious when previous button is clicked', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={1}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    const previousButton = screen.getByLabelText('Previous citation');
    fireEvent.click(previousButton);
    
    expect(onPrevious).toHaveBeenCalledTimes(1);
  });

  it('calls onNext when next button is clicked', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={1}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    const nextButton = screen.getByLabelText('Next citation');
    fireEvent.click(nextButton);
    
    expect(onNext).toHaveBeenCalledTimes(1);
  });

  it('enables both buttons when in the middle of citations', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={1}
        totalCount={3}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    const previousButton = screen.getByLabelText('Previous citation');
    const nextButton = screen.getByLabelText('Next citation');
    
    expect(previousButton).not.toBeDisabled();
    expect(nextButton).not.toBeDisabled();
  });

  it('displays correct index for single citation', () => {
    const onNext = vi.fn();
    const onPrevious = vi.fn();
    
    render(
      <CitationNavigator
        currentIndex={0}
        totalCount={1}
        onNext={onNext}
        onPrevious={onPrevious}
      />
    );
    
    expect(screen.getByText('1 / 1')).toBeInTheDocument();
  });
});
