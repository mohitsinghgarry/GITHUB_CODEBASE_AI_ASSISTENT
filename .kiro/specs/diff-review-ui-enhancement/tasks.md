# Implementation Plan: Diff Review UI Enhancement

## Overview

This implementation enhances the diff review interface by creating reusable React components for markdown rendering, collapsible content, and improved visual hierarchy. The implementation follows the "Obsidian Intelligence" design system with Tailwind CSS and integrates react-markdown for rich text formatting.

## Tasks

- [x] 1. Create MarkdownDescription component with custom renderers
  - Create new file `frontend/src/components/diff-review/MarkdownDescription.tsx`
  - Implement ReactMarkdown with remark-gfm plugin
  - Create custom component renderers for headings (h1, h2, h3), paragraphs, code blocks, lists, and text formatting
  - Apply Tailwind classes matching design system (surface-container-lowest for code, proper spacing, typography scale)
  - Add error boundary with fallback to plain text rendering
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.3, 5.5_

- [ ]* 1.1 Write unit tests for MarkdownDescription component
  - Test markdown rendering for headings, bold, italic, inline code, code blocks, and lists
  - Test error handling with malformed markdown
  - Test fallback to plain text on parsing errors
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create CollapsibleContent component
  - Create new file `frontend/src/components/diff-review/CollapsibleContent.tsx`
  - Implement useState hook for expand/collapse state
  - Add logic to truncate content at maxLength threshold (default 200 characters)
  - Create expand/collapse button with chevron icons and proper aria-labels
  - Apply smooth animation using Tailwind transitions (max-h with duration-normal and ease-quart)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 2.1 Write unit tests for CollapsibleContent component
  - Test initial collapsed state when content exceeds threshold
  - Test full display when content is below threshold
  - Test expand/collapse toggle functionality
  - Test button text and icon changes
  - Test aria-expanded attribute updates
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Create SuggestionSection component
  - Create new file `frontend/src/components/diff-review/SuggestionSection.tsx`
  - Implement component with suggestion prop
  - Apply distinct styling: surface-container-lowest background, rounded-lg, p-4 padding
  - Add lightbulb icon in tertiary color
  - Use monospace font (font-mono text-sm) for suggestion text
  - Add "Suggestion" label with proper typography
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 3.1 Write unit tests for SuggestionSection component
  - Test rendering of suggestion text with monospace font
  - Test background color and padding application
  - Test icon display
  - Test label rendering
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4. Create IssueCard component
  - Create new file `frontend/src/components/diff-review/IssueCard.tsx`
  - Define CodeIssue interface with severity, title, description, line_number, and suggestion fields
  - Implement IssueCard component with IssueCardProps interface
  - Create issue header section with severity badge and title
  - Integrate MarkdownDescription component for issue description
  - Wrap MarkdownDescription with CollapsibleContent when description exceeds 200 characters
  - Add line number badge display (conditional rendering)
  - Integrate SuggestionSection component (conditional rendering)
  - Apply proper spacing and visual hierarchy using Tailwind classes
  - Use React.memo for performance optimization
  - _Requirements: 1.1, 2.1, 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 5.4, 6.1_

- [ ]* 4.1 Write unit tests for IssueCard component
  - Test rendering of all issue fields (severity, title, description, line number, suggestion)
  - Test conditional rendering of line number and suggestion
  - Test severity color and icon mapping
  - Test integration with MarkdownDescription and CollapsibleContent
  - Test memoization behavior
  - _Requirements: 1.1, 2.1, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Integrate IssueCard into DiffReviewPage
  - Import IssueCard component in `frontend/src/app/diff-review/page.tsx`
  - Replace existing issue rendering logic (lines 300-350) with IssueCard component
  - Map over issues array and render IssueCard for each issue
  - Pass issue object and index as props
  - Remove old inline issue rendering code (severity badge, title, description, suggestion sections)
  - Preserve existing container styling and spacing
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.2, 6.1_

- [x] 7. Add accessibility enhancements
  - Add aria-label to severity badges in IssueCard
  - Add role="status" to severity badges
  - Ensure expand/collapse buttons have aria-expanded attribute
  - Add descriptive aria-labels to expand/collapse buttons
  - Verify keyboard navigation works (Tab, Enter, Space)
  - Add focus-visible styles to interactive elements
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 7.1 Write accessibility tests
  - Test keyboard navigation through expand/collapse buttons
  - Test aria-label presence on severity badges
  - Test aria-expanded attribute updates
  - Test focus indicators visibility
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 8. Final checkpoint - Verify integration and styling
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The design document uses TypeScript, so all components will be implemented in TypeScript
- react-markdown and remark-gfm are already installed in the project
- The design system uses Tailwind CSS with custom color tokens (surface-container-lowest, on-surface, etc.)
- Checkpoints ensure incremental validation
- All spacing follows 4px grid system (p-4, mb-3, gap-4, etc.)
- No borders are used for separation (No-Line Rule) - use background color shifts instead
