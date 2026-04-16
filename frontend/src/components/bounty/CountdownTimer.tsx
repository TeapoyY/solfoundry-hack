import React, { useState, useEffect } from 'react';
import { getUrgency } from '../../lib/utils';

interface CountdownTimerProps {
  deadline: string | null | undefined;
  /** Compact inline text (e.g. "3d 5h") — used in cards */
  compact?: boolean;
  /** Inline with a Clock icon — used in card footers */
  inline?: boolean;
  /** Full display with label + large text — used in detail page sidebar */
  full?: boolean;
  /** Small inline label variant — used in detail page sidebar row */
  sm?: boolean;
  className?: string;
}

function pad(n: number) {
  return n.toString().padStart(2, '0');
}

function getTimeRemaining(deadline: string) {
  const now = Date.now();
  const end = new Date(deadline).getTime();
  const diff = end - now;
  if (diff <= 0) return null;

  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  return { days, hours, minutes, totalSeconds };
}

const URGENCY_STYLES = {
  normal: 'text-text-muted',
  warning: 'text-status-warning',
  urgent: 'text-status-error animate-pulse',
  expired: 'text-text-muted',
};

export function CountdownTimer({ deadline, compact, full, className = '' }: CountdownTimerProps) {
  const urgency = getUrgency(deadline);

  // Real-time tick
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (!deadline) return;
    const id = setInterval(() => setTick((t) => t + 1), 30_000);
    return () => clearInterval(id);
  }, [deadline]);

  if (!deadline) return null;

  const remaining = getTimeRemaining(deadline);

  if (!remaining) {
    return (
      <span className={`inline-flex items-center gap-1 text-text-muted text-xs font-mono ${className}`}>
        Expired
      </span>
    );
  }

  const { days, hours, minutes } = remaining;

  if (inline) {
    // Inline with Clock icon — used in card footers
    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0 || days > 0) parts.push(`${hours}h`);
    parts.push(`${minutes}m`);

    return (
      <span className={`inline-flex items-center gap-1 font-mono text-xs ${URGENCY_STYLES[urgency]} ${className}`}>
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {parts.join(' ')}
      </span>
    );
  }

  if (compact) {
    // Compact inline display — used in cards without icon
    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0 || days > 0) parts.push(`${hours}h`);
    parts.push(`${minutes}m`);

    return (
      <span className={`inline-flex items-center font-mono text-xs ${URGENCY_STYLES[urgency]} ${className}`}>
        {parts.join(' ')}
      </span>
    );
  }

  if (sm) {
    // Small inline — fits in sidebar info row
    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0 || days > 0) parts.push(`${hours}h`);
    parts.push(`${minutes}m`);

    return (
      <span className={`inline-flex items-center gap-1 font-mono text-sm ${URGENCY_STYLES[urgency]} ${className}`}>
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {parts.join(' ')}
      </span>
    );
  }

  if (full) {
    // Full display with label — used in bounty detail sidebar
    const urgencyDot: Record<string, string> = {
      normal: 'bg-text-muted',
      warning: 'bg-status-warning',
      urgent: 'bg-status-error',
      expired: 'bg-text-muted',
    };

    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${urgencyDot[urgency]}`} />
          <span className="text-xs text-text-muted font-medium uppercase tracking-wide">Time Remaining</span>
        </div>
        <div className={`font-mono text-2xl font-bold ${URGENCY_STYLES[urgency]}`}>
          {days > 0 && <span>{days}<span className="text-base mr-1">d</span></span>}
          {hours > 0 && <span>{pad(hours)}<span className="text-base mr-1">h</span></span>}
          <span>{pad(minutes)}<span className="text-base">m</span></span>
        </div>
        {urgency === 'warning' && (
          <p className="text-xs text-status-warning">Less than 24 hours remaining</p>
        )}
        {urgency === 'urgent' && (
          <p className="text-xs text-status-error animate-pulse">Less than 1 hour — submit now!</p>
        )}
      </div>
    );
  }

  return null;
}
