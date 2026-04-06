import React, { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';

export type CountdownUrgency = 'normal' | 'warning' | 'urgent' | 'expired';

function getUrgency(msLeft: number): CountdownUrgency {
  if (msLeft <= 0) return 'expired';
  const hours = msLeft / (1000 * 60 * 60);
  if (hours < 1) return 'urgent';
  if (hours < 24) return 'warning';
  return 'normal';
}

function pad(n: number): string {
  return n.toString().padStart(2, '0');
}

function getTimeRemaining(deadline: string): { days: number; hours: number; minutes: number; seconds: number; expired: boolean } {
  const now = Date.now();
  const end = new Date(deadline).getTime();
  const diff = Math.max(0, end - now);

  if (diff === 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
  }

  return {
    days: Math.floor(diff / 86_400_000),
    hours: Math.floor((diff % 86_400_000) / 3_600_000),
    minutes: Math.floor((diff % 3_600_000) / 60_000),
    seconds: Math.floor((diff % 60_000) / 1000),
    expired: false,
  };
}

const urgencyStyles: Record<CountdownUrgency, string> = {
  normal: 'text-text-secondary',
  warning: 'text-status-warning',
  urgent: 'text-status-error',
  expired: 'text-text-muted',
};

const urgencyDotStyles: Record<CountdownUrgency, string> = {
  normal: 'bg-text-secondary',
  warning: 'bg-status-warning',
  urgent: 'bg-status-error animate-pulse',
  expired: 'bg-text-muted',
};

interface CountdownTimerProps {
  deadline: string;
  /** Show full breakdown (Xh Ym Zs) instead of compact (Xd Xh). Default false. */
  fullBreakdown?: boolean;
  /** Custom class overrides */
  className?: string;
  /** Show seconds ticker. Default false (updates every minute). */
  showSeconds?: boolean;
}

/**
 * Real-time countdown timer for bounty deadlines.
 * Color changes: normal (>24h) → warning (<24h) → urgent (<1h) → expired.
 */
export function CountdownTimer({
  deadline,
  fullBreakdown = false,
  className = '',
  showSeconds = false,
}: CountdownTimerProps) {
  const [tick, setTick] = useState(0);
  const { days, hours, minutes, seconds, expired } = getTimeRemaining(deadline);
  const urgency = getUrgency(new Date(deadline).getTime() - Date.now());

  // Re-render every tick to keep timer live
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), showSeconds ? 1000 : 30_000);
    return () => clearInterval(interval);
  }, [showSeconds]);

  if (expired) {
    return (
      <span className={`inline-flex items-center gap-1.5 ${urgencyStyles.expired} ${className}`}>
        <span className={`w-2 h-2 rounded-full ${urgencyDotStyles.expired}`} />
        <Clock className="w-3.5 h-3.5" />
        Expired
      </span>
    );
  }

  const label = fullBreakdown
    ? `${days > 0 ? `${days}d ` : ''}${pad(hours)}h ${pad(minutes)}m${showSeconds ? ` ${pad(seconds)}s` : ''}`
    : days > 0
      ? `${days}d ${hours}h`
      : hours > 0
        ? `${hours}h ${minutes}m`
        : `${minutes}m`;

  return (
    <span className={`inline-flex items-center gap-1.5 ${urgencyStyles[urgency]} ${className}`}>
      <span className={`w-2 h-2 rounded-full ${urgencyDotStyles[urgency]}`} />
      <Clock className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}
