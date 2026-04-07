/**
 * ToastContext — Global toast notification state and management.
 * Provides success, error, warning, and info toast notifications
 * with auto-dismiss, manual close, and Framer Motion animations.
 */
import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
  /** Auto-dismiss delay in ms. 0 = never auto-dismiss. Default 5000. */
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (message: string, variant?: ToastVariant, duration?: number) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const DEFAULT_DURATION = 5000;

const variantStyles: Record<
  ToastVariant,
  { bg: string; border: string; icon: typeof CheckCircle; iconColor: string }
> = {
  success: {
    bg: 'bg-emerald/10',
    border: 'border-emerald/30',
    icon: CheckCircle,
    iconColor: 'text-emerald',
  },
  error: {
    bg: 'bg-status-error/10',
    border: 'border-status-error/30',
    icon: AlertCircle,
    iconColor: 'text-status-error',
  },
  warning: {
    bg: 'bg-status-warning/10',
    border: 'border-status-warning/30',
    icon: AlertTriangle,
    iconColor: 'text-status-warning',
  },
  info: {
    bg: 'bg-status-info/10',
    border: 'border-status-info/30',
    icon: Info,
    iconColor: 'text-status-info',
  },
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef(new Map<string, ReturnType<typeof setTimeout>>());

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const addToast = useCallback(
    (message: string, variant: ToastVariant = 'info', duration: number = DEFAULT_DURATION) => {
      // Prevent duplicate toasts with the same message within 2s
      const toastId = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      const toast: Toast = { id: toastId, message, variant, duration };

      setToasts((prev) => {
        const recent = prev.some(
          (t) => t.message === message && Date.now() - parseInt(t.id.split('-')[1] ?? '0', 10) < 2000
        );
        if (recent) return prev;
        return [...prev, toast];
      });

      if (duration > 0) {
        const timer = setTimeout(() => removeToast(toastId), duration);
        timers.current.set(toastId, timer);
      }
    },
    [removeToast]
  );

  const success = useCallback(
    (message: string, duration?: number) => addToast(message, 'success', duration),
    [addToast]
  );
  const error = useCallback(
    (message: string, duration?: number) => addToast(message, 'error', duration),
    [addToast]
  );
  const warning = useCallback(
    (message: string, duration?: number) => addToast(message, 'warning', duration),
    [addToast]
  );
  const info = useCallback(
    (message: string, duration?: number) => addToast(message, 'info', duration),
    [addToast]
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

function ToastContainer({
  toasts,
  removeToast,
}: {
  toasts: Toast[];
  removeToast: (id: string) => void;
}) {
  return (
    <div
      className="fixed top-20 right-4 z-[9999] flex flex-col gap-3 max-w-sm w-full pointer-events-none"
      aria-live="polite"
      role="region"
      aria-label="Notifications"
    >
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
        ))}
      </AnimatePresence>
    </div>
  );
}

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
  const { message, variant } = toast;
  const styles = variantStyles[variant];
  const Icon = styles.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 100, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1, transition: { duration: 0.25, ease: 'easeOut' } }}
      exit={{ opacity: 0, x: 100, scale: 0.95, transition: { duration: 0.2 } }}
      role="alert"
      aria-live="assertive"
      className={`
        pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border
        backdrop-blur-xl shadow-2xl shadow-black/40
        ${styles.bg} ${styles.border}
      `}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${styles.iconColor}`} />
      <p className="flex-1 text-sm text-text-primary font-sans leading-snug">{message}</p>
      <button
        onClick={onRemove}
        className="flex-shrink-0 p-1 rounded-lg hover:bg-white/10 transition-colors text-text-muted hover:text-text-primary"
        aria-label="Dismiss notification"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
  return ctx;
}
