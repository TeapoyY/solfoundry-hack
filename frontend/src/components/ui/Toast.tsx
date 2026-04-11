import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
  id: string;
  message: string;
  variant: ToastVariant;
  duration?: number;
}

interface ToastContextValue {
  toasts: ToastItem[];
  toast: (message: string, variant?: ToastVariant, duration?: number) => void;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx;
}

const ICONS: Record<ToastVariant, React.ReactNode> = {
  success: <CheckCircle className="w-4 h-4 text-emerald flex-shrink-0" />,
  error: <AlertCircle className="w-4 h-4 text-status-error flex-shrink-0" />,
  warning: <AlertTriangle className="w-4 h-4 text-status-warning flex-shrink-0" />,
  info: <Info className="w-4 h-4 text-status-info flex-shrink-0" />,
};

const VARIANT_STYLES: Record<ToastVariant, string> = {
  success: 'border-emerald/30 bg-emerald-bg/80',
  error: 'border-status-error/30 bg-status-error/10',
  warning: 'border-status-warning/30 bg-status-warning/10',
  info: 'border-status-info/30 bg-status-info/10',
};

function Toast({ item, onDismiss }: { item: ToastItem; onDismiss: (id: string) => void }) {
  const { id, message, variant, duration = 5000 } = item;

  // Auto-dismiss
  React.useEffect(() => {
    if (duration <= 0) return;
    const t = setTimeout(() => onDismiss(id), duration);
    return () => clearTimeout(t);
  }, [id, duration, onDismiss]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 60, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 60, scale: 0.95 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      role="alert"
      className={`flex items-start gap-3 rounded-xl border backdrop-blur-sm px-4 py-3 shadow-2xl shadow-black/50 pointer-events-auto ${VARIANT_STYLES[variant]}`}
    >
      {ICONS[variant]}
      <p className="flex-1 text-sm text-text-primary leading-relaxed">{message}</p>
      <button
        onClick={() => onDismiss(id)}
        className="flex-shrink-0 text-text-muted hover:text-text-primary transition-colors duration-150"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </motion.div>
  );
}

/** Must be placed in the app tree — provides context + renders the toast portal */
export function ToastProvider({ children }: { children?: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const toast = useCallback(
    (message: string, variant: ToastVariant = 'info', duration = 5000) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      setToasts((prev) => [...prev.slice(-4), { id, message, variant, duration }]);
    },
    []
  );

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, toast, dismiss }}>
      {children}
      <div
        aria-live="polite"
        aria-label="Notifications"
        className="fixed top-20 right-4 z-[100] flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]"
      >
        <AnimatePresence>
          {toasts.map((item) => (
            <Toast key={item.id} item={item} onDismiss={dismiss} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}
