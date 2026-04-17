'use client';

import { useState, useEffect, useCallback } from 'react';

/**
 * Reusable resize hook for draggable panel dividers.
 *
 * @param defaultSize  Initial size in px
 * @param min          Minimum allowed size in px
 * @param max          Maximum allowed size in px
 * @param direction    'right' = dragging right edge grows panel from left
 *                     'left'  = dragging left edge grows panel from right
 */
export function useResize(
  defaultSize: number,
  min: number,
  max: number,
  direction: 'right' | 'left' = 'right',
) {
  const [size, setSize] = useState(defaultSize);
  const [dragging, setDragging] = useState(false);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  useEffect(() => {
    if (!dragging) return;

    const onMove = (e: MouseEvent) => {
      const raw =
        direction === 'right'
          ? e.clientX                        // distance from left edge
          : window.innerWidth - e.clientX;   // distance from right edge
      setSize(Math.max(min, Math.min(max, raw)));
    };

    const onUp = () => setDragging(false);

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    return () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [dragging, direction, min, max]);

  return { size, dragging, onMouseDown };
}
