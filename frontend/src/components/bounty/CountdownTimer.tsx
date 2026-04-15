import React, { useState, useEffect, useCallback } from 'react';
import { Clock, AlertTriangle, Flame } from 'lucide-react';

interface CountdownTimerProps {
  deadline: string | null | undefined;
  /** Compact mode for inline use (e.g. in a card). Full mode for detail pages. */
  compact?: boolean;
  /** Optional className to override defaults */
  className?: string;
}

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
}

function getTimeRemaining(deadline: string): TimeRemaining {
  const now = new Date().getTime();
  const end = new Date(deadline).getTime();
  const diff = Math.max(0, end - now);

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  return { days, hours, minutes, seconds, totalMs: diff };
}

type Urgency = 'normal' | 'warning' | 'urgent' | 'expired';

function getUrgency(time: TimeRemaining): Urgency {
  if (time.totalMs <= 0) return 'expired';
  if (time.days < 1) return time.hours < 1 ? 'urgent' : 'warning';
  return 'normal';
}

const urgencyConfig: Record<Urgency, {
  textClass: string;
  icon: React.ReactNode;
  label: string;
}> = {
  normal: {
    textClass: 'text-text-muted',
    icon: <Clock className="w-3.5 h-3.5" />,
    label: '',
  },
  warning: {
    textClass: 'text-status-warning',
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
    label: 'Less than 24h',
  },
  urgent: {
    textClass: 'text-status-error',
    icon: <Flame className="w-3.5 h-3.5" />,
    label: 'Less than 1h',
  },
  expired: {
    textClass: 'text-text-muted line-through',
    icon: <Clock className="w-3.5 h-3.5" />,
    label: 'Expired',
  },
};

export function CountdownTimer({ deadline, compact = false, className = '' }: CountdownTimerProps) {
  const calcTime = useCallback(() => (deadline ? getTimeRemaining(deadline) : null), [deadline]);
  const [time, setTime] = useState<TimeRemaining | null>(calcTime);

  useEffect(() => {
    if (!deadline) return;
    setTime(getTimeRemaining(deadline));

    const tick = setInterval(() => {
      setTime(getTimeRemaining(deadline));
    }, 1000);

    return () => clearInterval(tick);
  }, [deadline]);

  if (!deadline || !time) return null;

  const urgency = getUrgency(time);
  const config = urgencyConfig[urgency];

  if (compact) {
    return (
      <span className={`inline-flex items-center gap-1 text-xs font-mono ${config.textClass} ${className}`}>
        {config.icon}
        {urgency === 'expired' ? (
          'Expired'
        ) : (
          <>
            {time.days > 0 && <span>{time.days}d</span>}
            <span>{String(time.hours).padStart(2, '0')}h</span>
            <span>{String(time.minutes).padStart(2, '0')}m</span>
          </>
        )}
      </span>
    );
  }

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <div className={`inline-flex items-center gap-2 font-mono text-sm font-medium ${config.textClass}`}>
        {config.icon}
        {urgency === 'expired' ? (
          <span>Expired</span>
        ) : (
          <>
            {time.days > 0 && <span className="text-base font-bold">{time.days}d</span>}
            <span className="text-base font-bold">{String(time.hours).padStart(2, '0')}</span>
            <span className="text-text-muted">:</span>
            <span className="text-base font-bold">{String(time.minutes).padStart(2, '0')}</span>
            <span className="text-text-muted">:</span>
            <span className="text-base font-bold">{String(time.seconds).padStart(2, '0')}</span>
          </>
        )}
      </div>
      {urgency !== 'normal' && urgency !== 'expired' && (
        <span className={`text-xs ${config.textClass} opacity-75`}>{config.label} remaining</span>
      )}
      {urgency === 'expired' && (
        <span className="text-xs text-text-muted">This bounty has expired</span>
      )}
    </div>
  );
}
