import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CollapsibleContent } from './CollapsibleContent';

describe('CollapsibleContent', () => {
  const shortContent = 'This is a short description.';
  const longContent = 'a'.repeat(250); // 250 characters
  const maxLength = 200;

  describe('Requirement 2.1: Display Collapsible_Section when content exceeds threshold', () => {
    it('should not show expand/collapse button when content is below maxLength', () => {
      render(
        <CollapsibleContent content={shortContent} maxLength={maxLength}>
          <p>{shortContent}</p>
        </CollapsibleContent>
      );

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });

    it('should show expand/collapse button when content exceeds maxLength', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Requirement 2.2: Initially show truncated preview', () => {
    it('should start in collapsed state with max-h-24 class', () => {
      const { container } = render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const contentContainer = container.querySelector('.overflow-hidden');
      expect(contentContainer).toHaveClass('max-h-24');
    });

    it('should have aria-expanded set to false initially', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'false');
    });
  });

  describe('Requirement 2.3: Expand content on click', () => {
    it('should expand content when "Show more" button is clicked', () => {
      const { container } = render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button', { name: /show more/i });
      fireEvent.click(button);

      const contentContainer = container.querySelector('.overflow-hidden');
      expect(contentContainer).toHaveClass('max-h-[2000px]');
    });

    it('should update aria-expanded to true after expanding', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(button).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Requirement 2.4: Collapse content on click', () => {
    it('should collapse content when "Show less" button is clicked', () => {
      const { container } = render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      
      // First expand
      fireEvent.click(button);
      expect(container.querySelector('.overflow-hidden')).toHaveClass('max-h-[2000px]');

      // Then collapse
      fireEvent.click(button);
      expect(container.querySelector('.overflow-hidden')).toHaveClass('max-h-24');
    });

    it('should update aria-expanded to false after collapsing', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      
      // Expand then collapse
      fireEvent.click(button);
      fireEvent.click(button);

      expect(button).toHaveAttribute('aria-expanded', 'false');
    });
  });

  describe('Requirement 2.5: Display visual indicator for expand/collapse state', () => {
    it('should show "Show more" text and expand_more icon when collapsed', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      expect(screen.getByText('Show more')).toBeInTheDocument();
      expect(screen.getByText('expand_more')).toBeInTheDocument();
    });

    it('should show "Show less" text and expand_less icon when expanded', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(screen.getByText('Show less')).toBeInTheDocument();
      expect(screen.getByText('expand_less')).toBeInTheDocument();
    });

    it('should update button aria-label based on state', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      
      // Initially collapsed
      expect(button).toHaveAttribute('aria-label', 'Show more');

      // After expanding
      fireEvent.click(button);
      expect(button).toHaveAttribute('aria-label', 'Show less');
    });
  });

  describe('Design System Compliance', () => {
    it('should apply smooth animation with duration-normal and ease-quart', () => {
      const { container } = render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const contentContainer = container.querySelector('.overflow-hidden');
      expect(contentContainer).toHaveClass('transition-all');
      expect(contentContainer).toHaveClass('duration-normal');
      expect(contentContainer).toHaveClass('ease-quart');
    });

    it('should use text-label-md for button text', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const buttonText = screen.getByText('Show more');
      expect(buttonText).toHaveClass('text-label-md');
    });

    it('should use primary color with hover state', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('text-primary');
      expect(button).toHaveClass('hover:text-primary-dim');
    });

    it('should use material-symbols-outlined for icons', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const icon = screen.getByText('expand_more');
      expect(icon).toHaveClass('material-symbols-outlined');
    });

    it('should follow 4px grid spacing (gap-1, mt-2)', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('gap-1');
      expect(button).toHaveClass('mt-2');
    });
  });

  describe('Accessibility', () => {
    it('should have proper button type attribute', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'button');
    });

    it('should be keyboard accessible', () => {
      render(
        <CollapsibleContent content={longContent} maxLength={maxLength}>
          <p>{longContent}</p>
        </CollapsibleContent>
      );

      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });
  });
});
