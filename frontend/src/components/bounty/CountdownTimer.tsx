import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

interface CountdownTimerProps {
  deadline: string | null | undefined;
  /** Show full precision: days, hours, minutes, seconds. Default: false (compact) */
  full?: boolean;
  /** Size variant: 'sm' | 'md' | 'lg'. Default: 'md' */
  size?: 'sm' | 'md' | 'lg';
  /** Optional className for custom styling */
  className?: string;
}

type UrgencyLevel = 'normal' | 'warning' | 'urgent' | 'expired';

function getUrgency(diffMs: number): UrgencyLevel {
  if (diffMs <= 0) return 'expired';
  const hours = diffMs / (1000 * 60 * 60);
  if (hours < 1) return 'urgent';
  if (hours < 24) return 'warning';
  return 'normal';
}

const urgencyStyles: Record<UrgencyLevel, { text: string; dot: string; bg?: string }> = {
  normal: { text: 'text-text-muted', dot: 'bg-text-muted' },
  warning: { text: 'text-status-warning', dot: 'bg-status-warning' },
  urgent:  { text: 'text-status-error',  dot: 'bg-status-error' },
  expired: { text: 'text-text-muted', dot: 'bg-text-muted' },
};

function pad(n: number): string {
  return n.toString().padStart(2, '0');
}

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
}

function calcTimeLeft(deadline: string): TimeLeft {
  const diff = new Date(deadline).getTime() - Date.now();
  if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0, totalMs: 0 };
  const totalSeconds = Math.floor(diff / 1000);
  return {
    days:    Math.floor(totalSeconds / 86400),
    hours:   Math.floor((totalSeconds % 86400) / 3600),
    minutes: Math.floor((totalSeconds % 3600) / 60),
    seconds: totalSeconds % 60,
    totalMs: diff,
  };
}

export function CountdownTimer({ deadline, full = false, size = 'md', className = '' }: CountdownTimerProps) {
  if (!deadline) {
    return (
      <span className={`inline-flex items-center gap-1 text-text-muted ${className}`}>
        <Clock className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
        <span className="text-xs">No deadline</span>
      </span>
    );
  }

  const initial = calcTimeLeft(deadline);
  const [time, setTime] = useState<TimeLeft>(initial);
  const urgency = getUrgency(time.totalMs);
  const styles = urgencyStyles[urgency];

  useEffect(() => {
    const id = setInterval(() => {
      setTime(calcTimeLeft(deadline));
    }, 1000);
    return () => clearInterval(id);
  }, [deadline]);

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }[size];

  if (urgency === 'expired') {
    return (
      <span className={`inline-flex items-center gap-1 ${styles.text} ${sizeClasses} ${className}`}>
        <Clock className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
        <span className="font-medium">Expired</span>
      </span>
    );
  }

  if (full) {
    const { days, hours, minutes, seconds } = time;
    return (
      <span className={`inline-flex items-center gap-1 ${styles.text} ${sizeClasses} ${className}`}>
        <Clock className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
        {days > 0 && <span>{days}d </span>}
        <span>{pad(hours)}:</span>
        <span>{pad(minutes)}:</span>
        <span>{pad(seconds)}</span>
        {days === 0 && hours === 0 && (
          <span className="ml-0.5 text-[0.7em] opacity-70">remaining</span>
        )}
      </span>
    );
  }

  // Compact display
  const { days, hours, minutes } = time;
  let label: string;
  if (days > 0) {
    label = `${days}d ${hours}h`;
  } else if (hours > 0) {
    label = `${hours}h ${minutes}m`;
  } else {
    label = `${minutes}m`;
  }

  return (
    <span className={`inline-flex items-center gap-1 ${styles.text} ${sizeClasses} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${styles.dot} flex-shrink-0`} />
      <Clock className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-3.5 h-3.5'} />
      <span className="font-medium">{label}</span>
    </span>
  );
}
