/**
 * Focus Utilities
 * 
 * Utilities for managing keyboard navigation and focus states.
 * Ensures accessibility compliance with WCAG 2.1 guidelines.
 */

/**
 * Standard focus ring classes for interactive elements
 * Use this for custom components that need focus styling
 */
export const focusRing = 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:ring-offset-2 focus-visible:ring-offset-background';

/**
 * Focus ring for elements on colored backgrounds
 */
export const focusRingOnColor = 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent';

/**
 * Focus ring for elements in dark containers
 */
export const focusRingInDark = 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-container-lowest';

/**
 * Trap focus within a container (for modals, dialogs)
 * Returns a cleanup function
 */
export function trapFocus(element: HTMLElement): () => void {
  const focusableElements = element.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  function handleTabKey(e: KeyboardEvent) {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    }
  }

  element.addEventListener('keydown', handleTabKey);

  // Focus first element
  firstElement?.focus();

  return () => {
    element.removeEventListener('keydown', handleTabKey);
  };
}

/**
 * Restore focus to a previously focused element
 */
export function createFocusRestore() {
  const previouslyFocused = document.activeElement as HTMLElement;

  return () => {
    previouslyFocused?.focus();
  };
}

/**
 * Check if an element is keyboard-focusable
 */
export function isFocusable(element: HTMLElement): boolean {
  if (element.tabIndex < 0) return false;
  if (element.hasAttribute('disabled')) return false;
  if (element.getAttribute('aria-hidden') === 'true') return false;

  return true;
}

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const elements = container.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );

  return Array.from(elements).filter(isFocusable);
}

/**
 * Move focus to the next/previous focusable element
 */
export function moveFocus(direction: 'next' | 'previous', container?: HTMLElement) {
  const root = container || document.body;
  const focusableElements = getFocusableElements(root);
  const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);

  if (currentIndex === -1) {
    focusableElements[0]?.focus();
    return;
  }

  const nextIndex = direction === 'next'
    ? (currentIndex + 1) % focusableElements.length
    : (currentIndex - 1 + focusableElements.length) % focusableElements.length;

  focusableElements[nextIndex]?.focus();
}

/**
 * Announce to screen readers (for dynamic content updates)
 */
export function announce(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}
