/**
 * useToast Hook
 * 
 * A hook for managing toast notifications throughout the application.
 * Provides methods to show success, error, warning, and info toasts.
 */

'use client';

import { create } from 'zustand';
import type { Toast, ToastVariant } from '@/components/ui/toast';

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  dismissToast: (id: string) => void;
  clearAll: () => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2, 9);
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));
  },
  dismissToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },
  clearAll: () => {
    set({ toasts: [] });
  },
}));

interface ToastOptions {
  title: string;
  description?: string;
  duration?: number;
}

export function useToast() {
  const { addToast, dismissToast, clearAll } = useToastStore();

  const toast = React.useCallback(
    (options: ToastOptions & { variant: ToastVariant }) => {
      addToast(options);
    },
    [addToast]
  );

  const success = React.useCallback(
    (options: ToastOptions) => {
      addToast({ ...options, variant: 'success' });
    },
    [addToast]
  );

  const error = React.useCallback(
    (options: ToastOptions) => {
      addToast({ ...options, variant: 'error' });
    },
    [addToast]
  );

  const warning = React.useCallback(
    (options: ToastOptions) => {
      addToast({ ...options, variant: 'warning' });
    },
    [addToast]
  );

  const info = React.useCallback(
    (options: ToastOptions) => {
      addToast({ ...options, variant: 'info' });
    },
    [addToast]
  );

  return {
    toast,
    success,
    error,
    warning,
    info,
    dismiss: dismissToast,
    clearAll,
  };
}

// Import React for useCallback
import * as React from 'react';
