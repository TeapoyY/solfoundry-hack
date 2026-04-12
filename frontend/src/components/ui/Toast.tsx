import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: ToastVariant;
  /** Auto-dismiss after N ms. Defaults to 5000. Pass 0 to disable. */
  duration?: number;
}

const variantConfig: Record<
  ToastVariant,
  { icon: React.ElementType; wrapper: string; iconColor: string }
> = {
  success: {
    icon: CheckCircle,
    wrapper: 'border-emerald/30 bg-emerald-bg',
    iconColor: 'text-emerald',
  },
  error: {
    icon: AlertCircle,
    wrapper: 'border-status-error/30 bg-status-error/10',
    iconColor: 'text-status-error',
  },
  warning: {
    icon: AlertTriangle,
    wrapper: 'border-status-warning/30 bg-status-warning/10',
    iconColor: 'text-status-warning',
  },
  info: {
    icon: Info,
    wrapper: 'border-status-info/30 bg-status-info/10',
    iconColor: 'text-status-info',
  },
};

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const { id, title, description, variant = 'info', duration = 5000 } = toast;
  const config = variantConfig[variant];
  const Icon = config.icon;

  useEffect(() => {
    if (duration === 0) return;
    const timer = setTimeout(() => onRemove(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onRemove]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      role="alert"
      aria-live="assertive"
      className={`flex items-start gap-3 rounded-xl border px-4 py-3 shadow-xl shadow-black/40 backdrop-blur-sm max-w-sm w-full ${config.wrapper}`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${config.iconColor}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text-primary">{title}</p>
        {description && (
          <p className="mt-0.5 text-xs text-text-secondary leading-relaxed">{description}</p>
        )}
      </div>
      <button
        onClick={() => onRemove(id)}
        className="flex-shrink-0 p-0.5 rounded text-text-muted hover:text-text-primary transition-colors cursor-pointer"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </motion.div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div
      aria-label="Notifications"
      className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none"
    >
      <AnimatePresence mode="popLayout">
        {toasts.map(toast => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onRemove={onRemove} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
}
