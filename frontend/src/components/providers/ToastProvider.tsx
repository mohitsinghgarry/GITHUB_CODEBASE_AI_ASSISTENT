/**
 * Toast Provider
 * 
 * Provides toast notification functionality throughout the application.
 * Should be placed at the root layout level.
 */

'use client';

import { ToastContainer } from '@/components/ui/toast';
import { useToastStore } from '@/hooks/useToast';

export function ToastProvider() {
  const { toasts, dismissToast } = useToastStore();

  return <ToastContainer toasts={toasts} onDismiss={dismissToast} />;
}
