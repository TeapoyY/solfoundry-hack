import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
}

function parseTimeRemaining(deadline: string): TimeRemaining {
  const now = Date.now();
  const end = new Date(deadline).getTime();
  const diff = Math.max(0, end - now);

  return {
    days: Math.floor(diff / 86400000),
    hours: Math.floor((diff % 86400000) / 3600000),
    minutes: Math.floor((diff % 3600000) / 60000),
    seconds: Math.floor((diff % 60000) / 1000),
    totalMs: diff,
  };
}

function getUrgency(totalMs: number): 'normal' | 'warning' | 'urgent' | 'expired' {
  const HOUR = 3600000;
  const DAY = 86400000;
  if (totalMs === 0) return 'expired';
  if (totalMs < HOUR) return 'urgent';
  if (totalMs < DAY) return 'warning';
  return 'normal';
}

const URGENCY_STYLES = {
  normal: 'text-text-muted',
  warning: 'text-status-warning',
  urgent: 'text-status-error',
  expired: 'text-text-muted',
};

interface BountyCountdownProps {
  deadline: string;
  /** Show seconds unit (default: false for compact cards) */
  showSeconds?: boolean;
  /** Compact layout for card use (default: false) */
  compact?: boolean;
}

export function BountyCountdown({ deadline, showSeconds = false, compact = false }: BountyCountdownProps) {
  const [time, setTime] = useState<TimeRemaining>(() => parseTimeRemaining(deadline));

  useEffect(() => {
    setTime(parseTimeRemaining(deadline));
    const id = setInterval(() => {
      setTime(parseTimeRemaining(deadline));
    }, 1000);
    return () => clearInterval(id);
  }, [deadline]);

  const urgency = getUrgency(time.totalMs);
  const style = URGENCY_STYLES[urgency];

  if (urgency === 'expired') {
    return (
      <span className={`inline-flex items-center gap-1 font-mono text-xs ${style}`}>
        <Clock className="w-3.5 h-3.5" />
        Expired
      </span>
    );
  }

  const parts: string[] = [];
  if (time.days > 0) parts.push(`${time.days}d`);
  if (time.hours > 0 || time.days > 0) parts.push(`${time.hours}h`);
  parts.push(`${time.minutes}m`);
  if (showSeconds && time.days === 0) parts.push(`${time.seconds}s`);

  const label = parts.join(' ');

  if (compact) {
    return (
      <span className={`inline-flex items-center gap-1 font-mono text-xs ${style}`} title={deadline}>
        <Clock className="w-3.5 h-3.5" />
        {label} left
      </span>
    );
  }

  return (
    <div className={`flex flex-col gap-1 ${style}`}>
      <span className="font-mono text-xs uppercase tracking-wide opacity-70">Time Left</span>
      <div className="flex items-center gap-1 font-mono text-sm font-semibold">
        <span className="w-8 text-center">{String(time.days).padStart(2, '0')}</span>
        <span>:</span>
        <span className="w-8 text-center">{String(time.hours).padStart(2, '0')}</span>
        <span>:</span>
        <span className="w-8 text-center">{String(time.minutes).padStart(2, '0')}</span>
        {showSeconds && (
          <>
            <span>:</span>
            <span className="w-8 text-center">{String(time.seconds).padStart(2, '0')}</span>
          </>
        )}
      </div>
      <span className="text-xs opacity-60">
        {time.days > 0 ? `${time.days}d ` : ''}{time.hours > 0 ? `${time.hours}h ` : ''}{time.minutes}m left
      </span>
    </div>
  );
}
