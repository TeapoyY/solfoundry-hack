import React, { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';

export type CountdownUrgency = 'normal' | 'warning' | 'urgent' | 'expired';

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
  urgency: CountdownUrgency;
}

/** Compute time remaining from a deadline ISO string. */
function computeTimeRemaining(deadline: string): TimeRemaining {
  const now = Date.now();
  const end = new Date(deadline).getTime();
  const diff = Math.max(0, end - now);

  if (diff === 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, totalMs: 0, urgency: 'expired' };
  }

  const days = Math.floor(diff / 86_400_000);
  const hours = Math.floor((diff % 86_400_000) / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);
  const seconds = Math.floor((diff % 60_000) / 1_000);

  let urgency: CountdownUrgency = 'normal';
  if (diff < 3_600_000) {
    urgency = 'urgent'; // < 1 hour
  } else if (diff < 86_400_000) {
    urgency = 'warning'; // < 24 hours
  }

  return { days, hours, minutes, seconds, totalMs: diff, urgency };
}

const urgencyStyles: Record<CountdownUrgency, { text: string; dot: string; pulse: boolean }> = {
  normal: {
    text: 'text-emerald',
    dot: 'bg-emerald',
    pulse: false,
  },
  warning: {
    text: 'text-status-warning',
    dot: 'bg-status-warning',
    pulse: false,
  },
  urgent: {
    text: 'text-status-error',
    dot: 'bg-status-error',
    pulse: true,
  },
  expired: {
    text: 'text-text-muted',
    dot: 'bg-text-muted',
    pulse: false,
  },
};

interface BountyCountdownProps {
  /** ISO 8601 deadline string */
  deadline: string;
  /** Show seconds in the countdown (default: false for compact) */
  showSeconds?: boolean;
  /** Compact layout for inline use (default: false) */
  compact?: boolean;
  /** Additional CSS class */
  className?: string;
}

/**
 * Real-time countdown timer for bounty deadlines.
 * Updates every second, changes color based on urgency.
 *
 * - < 1 hour: urgent (red)
 * - < 24 hours: warning (amber)
 * - > 24 hours: normal (green)
 * - expired: muted
 */
export function BountyCountdown({ deadline, showSeconds = false, compact = false, className = '' }: BountyCountdownProps) {
  const [time, setTime] = useState<TimeRemaining>(() => computeTimeRemaining(deadline));

  useEffect(() => {
    // Reset when deadline changes
    setTime(computeTimeRemaining(deadline));

    if (deadline && computeTimeRemaining(deadline).urgency !== 'expired') {
      const interval = setInterval(() => {
        setTime(computeTimeRemaining(deadline));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [deadline]);

  const { days, hours, minutes, seconds, urgency } = time;
  const style = urgencyStyles[urgency];

  if (urgency === 'expired') {
    return (
      <span className={`inline-flex items-center gap-1.5 text-xs font-mono ${style.text} ${className}`}>
        <Clock className="w-3.5 h-3.5" />
        Expired
      </span>
    );
  }

  const pad = (n: number) => String(n).padStart(2, '0');

  const segments = compact
    ? days > 0
      ? `${days}d ${pad(hours)}h ${pad(minutes)}m`
      : hours > 0
        ? `${pad(hours)}h ${pad(minutes)}m`
        : `${pad(minutes)}m`
    : days > 0
      ? `${days}d ${pad(hours)}h ${pad(minutes)}m`
      : hours > 0
        ? `${pad(hours)}:${pad(minutes)}${showSeconds ? `:${pad(seconds)}` : ''}`
        : `${pad(minutes)}:${pad(seconds)}`;

  const dotClass = style.pulse ? 'animate-pulse-glow' : '';

  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-mono ${style.text} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot} ${dotClass}`} />
      {segments}
    </span>
  );
}

/**
 * Full countdown display with days/hours/minutes/seconds in separate segments.
 * Use this for bounty detail pages where space is available.
 */
export function BountyCountdownFull({ deadline, className = '' }: { deadline: string; className?: string }) {
  const [time, setTime] = useState<TimeRemaining>(() => computeTimeRemaining(deadline));

  useEffect(() => {
    setTime(computeTimeRemaining(deadline));
    if (deadline && computeTimeRemaining(deadline).urgency !== 'expired') {
      const interval = setInterval(() => {
        setTime(computeTimeRemaining(deadline));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [deadline]);

  const { days, hours, minutes, seconds, urgency } = time;
  const style = urgencyStyles[urgency];

  if (urgency === 'expired') {
    return (
      <div className={`inline-flex items-center gap-2 font-mono ${style.text} ${className}`}>
        <Clock className="w-5 h-5" />
        <span className="text-sm font-semibold">Expired</span>
      </div>
    );
  }

  const pad = (n: number) => String(n).padStart(2, '0');

  return (
    <div className={`inline-flex items-center gap-1 font-mono ${className}`}>
      {days > 0 && (
        <>
          <CountdownUnit value={days} label="d" urgency={urgency} />
          <span className={`text-xs ${style.text}`}>:</span>
        </>
      )}
      <CountdownUnit value={hours} label="h" urgency={urgency} />
      <span className={`text-xs ${style.text}`}>:</span>
      <CountdownUnit value={minutes} label="m" urgency={urgency} />
      <span className={`text-xs ${style.text}`}>:</span>
      <CountdownUnit value={seconds} label="s" urgency={urgency} />
    </div>
  );
}

function CountdownUnit({ value, label, urgency }: { value: number; label: string; urgency: CountdownUrgency }) {
  const style = urgencyStyles[urgency];
  const pad = label !== 'd' ? String(value).padStart(2, '0') : value;
  return (
    <span className={`inline-flex items-baseline gap-0.5 ${style.text}`}>
      <span className="text-sm font-semibold tabular-nums">{pad}</span>
      <span className="text-xs opacity-70">{label}</span>
    </span>
  );
}
