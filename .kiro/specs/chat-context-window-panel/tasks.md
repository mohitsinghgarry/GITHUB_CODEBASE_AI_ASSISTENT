# Implementation Plan: Chat Context Window Panel

## Overview

This implementation plan breaks down the Chat Context Window Panel feature into discrete coding tasks. The feature adds a dedicated side panel to the chat interface that displays referenced code files with syntax highlighting, line numbers, and highlighted line ranges. The implementation follows a bottom-up approach: building individual components first, then integrating them into the chat page, and finally adding responsive behavior and polish.

## Tasks

- [x] 1. Create CodeDisplay component with syntax highlighting
  - Create `frontend/src/components/chat/CodeDisplay.tsx`
  - Implement syntax highlighting using react-syntax-highlighter with vscDarkPlus theme
  - Add line number display starting from startLine prop
  - Apply background highlighting to lines within [startLine, endLine] range
  - Handle null language by displaying as plain text
  - Add error boundary for syntax highlighter failures
  - _Requirements: 1.3, 1.4, 1.5_

- [ ]* 1.1 Write unit tests for CodeDisplay component
  - Test syntax highlighting renders correctly for various languages
  - Test line numbers start at correct value
  - Test highlighted lines have distinct background
  - Test null language displays as plain text
  - Test error boundary fallback for syntax highlighter failures
  - _Requirements: 1.3, 1.4, 1.5_

- [x] 2. Create ContextPanelHeader component
  - Create `frontend/src/components/chat/ContextPanelHeader.tsx`
  - Display "CONTEXT:" label with file path
  - Implement file path truncation with ellipsis for long paths
  - Add "Open in Viewer" button with external link icon
  - Apply distinct background styling consistent with Material Design 3 theme
  - _Requirements: 1.6, 1.7_

- [ ]* 2.1 Write unit tests for ContextPanelHeader component
  - Test file path displays correctly
  - Test long file paths are truncated with ellipsis
  - Test "Open in Viewer" button renders with icon
  - Test onOpenInViewer callback is triggered on button click
  - _Requirements: 1.6, 1.7_

- [x] 3. Create CitationNavigator component
  - Create `frontend/src/components/chat/CitationNavigator.tsx`
  - Display current index and total count (e.g., "1 / 3")
  - Render previous/next navigation buttons with icons
  - Disable previous button when currentIndex is 0
  - Disable next button when currentIndex is totalCount - 1
  - Apply hover and disabled states with appropriate styling
  - _Requirements: 1.8_

- [ ]* 3.1 Write unit tests for CitationNavigator component
  - Test current index and total count display correctly
  - Test previous button disabled at first citation
  - Test next button disabled at last citation
  - Test onNext and onPrevious callbacks triggered correctly
  - Test hover states apply correctly
  - _Requirements: 1.8_

- [x] 4. Create ContextPanel component
  - Create `frontend/src/components/chat/ContextPanel.tsx`
  - Implement empty state display when citation is null
  - Render ContextPanelHeader with file path and "Open in Viewer" button
  - Conditionally render CitationNavigator when citations.length > 1
  - Render CodeDisplay with citation content
  - Implement auto-scroll to highlighted line range on content change using scrollIntoView
  - Add independent scrolling with fixed header
  - _Requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 1.10, 1.11_

- [ ]* 4.1 Write unit tests for ContextPanel component
  - Test empty state renders when citation is null
  - Test header displays correct file path
  - Test navigation controls appear only when multiple citations exist
  - Test CodeDisplay renders with correct props
  - Test auto-scroll behavior on content change
  - Test independent scrolling with fixed header
  - _Requirements: 1.1, 1.2, 1.6, 1.7, 1.8, 1.10, 1.11_

- [x] 5. Checkpoint - Ensure all component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Update chat page with state management
  - Add state for selectedCitation, activeCitations, and currentCitationIndex in `frontend/src/app/chat/page.tsx`
  - Implement handleCitationClick to update selectedCitation and activeCitations
  - Implement handleNavigate to update currentCitationIndex and selectedCitation
  - Implement handleOpenInViewer to navigate to viewer page with file path
  - Auto-select first citation when new assistant message with citations arrives
  - _Requirements: 1.2, 1.7, 1.8_

- [ ]* 6.1 Write unit tests for chat page state management
  - Test selectedCitation updates on citation click
  - Test activeCitations updates with all citations from message
  - Test currentCitationIndex updates on navigation
  - Test first citation auto-selected on new assistant message
  - Test handleOpenInViewer navigates with correct file path
  - _Requirements: 1.2, 1.7, 1.8_

- [x] 7. Modify citation badge rendering with click handlers
  - Update citation badge rendering in `frontend/src/app/chat/page.tsx` renderMessage function
  - Add onClick handler to citation badges that calls handleCitationClick
  - Add active state styling to currently selected citation badge
  - Add hover state styling to citation badges
  - Add cursor pointer to indicate clickability
  - _Requirements: 1.2, 1.12_

- [ ]* 7.1 Write unit tests for citation badge interactions
  - Test citation badge click triggers handleCitationClick
  - Test active citation badge has distinct styling
  - Test hover state applies correctly
  - Test cursor pointer displays on citation badges
  - _Requirements: 1.2, 1.12_

- [x] 8. Integrate ContextPanel into chat page layout
  - Update chat page layout in `frontend/src/app/chat/page.tsx` to include ContextPanel
  - Create two-column layout using flexbox
  - Set message area to flex-1 with min-width of 600px
  - Set ContextPanel to fixed width of 500px
  - Add border-left to ContextPanel for visual separation
  - Pass state and handlers to ContextPanel component
  - _Requirements: 1.1, 1.9_

- [ ]* 8.1 Write integration tests for layout
  - Test two-column layout renders correctly
  - Test message area maintains minimum width
  - Test ContextPanel has correct fixed width
  - Test border separation between areas
  - Test ContextPanel receives correct props
  - _Requirements: 1.1, 1.9_

- [ ] 9. Checkpoint - Ensure integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement responsive behavior
  - Add media query at 1200px breakpoint in chat page styles
  - Below 1200px: Change ContextPanel to overlay mode with position fixed
  - Add dismiss button to ContextPanel when in overlay mode
  - Implement dismiss handler to hide ContextPanel in overlay mode
  - Test responsive behavior at various viewport widths
  - _Requirements: 1.9_

- [ ]* 10.1 Write tests for responsive behavior
  - Test ContextPanel switches to overlay mode below 1200px
  - Test dismiss button appears in overlay mode
  - Test dismiss handler hides ContextPanel
  - Test layout adapts correctly at breakpoint
  - _Requirements: 1.9_

- [x] 11. Add styling and theming
  - Apply Material Design 3 theme tokens to all components
  - Use bg-surface-container-low for ContextPanel background
  - Use border-outline-variant/10 for borders
  - Use text-on-surface for primary text
  - Use bg-primary/10 for highlighted lines
  - Use bg-primary/20 border-primary/50 for active citation badges
  - Ensure consistent spacing and typography across components
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.12_

- [ ]* 11.1 Write visual regression tests
  - Test component styling matches design specifications
  - Test theme tokens applied correctly
  - Test spacing and typography consistency
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.12_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- The implementation uses TypeScript/React with existing libraries (react-syntax-highlighter)
- All styling follows Material Design 3 theme tokens already in use
- Components are built bottom-up: CodeDisplay → Header/Navigator → ContextPanel → Integration
