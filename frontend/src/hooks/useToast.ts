/**
 * useToast — convenient hook to fire toast notifications from anywhere.
 *
 * Usage:
 *   const toast = useToast();
 *   toast.success('Saved!', 'Your changes were saved successfully.');
 *   toast.error('Failed', 'Could not connect to the server.');
 *   toast.warning('Heads up', 'Your session expires in 5 minutes.');
 *   toast.info('New update', 'Version 2.0 is now available.');
 *
 * Or use addToast directly for full control:
 *   toast.addToast({ title: 'Custom', variant: 'info', duration: 3000 });
 */
import { useCallback } from 'react';
import { useToastContext } from '../contexts/ToastContext';
import type { Toast, ToastVariant } from '../components/ui/Toast';

export function useToast() {
  const { addToast } = useToastContext();

  const fire = useCallback(
    (variant: ToastVariant, title: string, description?: string, duration?: number) => {
      return addToast({ title, description, variant, duration });
    },
    [addToast]
  );

  return {
    /** Returns the toast id */
    addToast,
    success: (title: string, description?: string, duration?: number) =>
      fire('success', title, description, duration),
    error: (title: string, description?: string, duration?: number) =>
      fire('error', title, description, duration),
    warning: (title: string, description?: string, duration?: number) =>
      fire('warning', title, description, duration),
    info: (title: string, description?: string, duration?: number) =>
      fire('info', title, description, duration),
  };
}
