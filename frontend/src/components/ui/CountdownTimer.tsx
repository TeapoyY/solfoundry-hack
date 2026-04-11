import React from 'react';
import { Clock, AlertTriangle, Timer } from 'lucide-react';
import { useCountdown } from '../../hooks/useCountdown';

interface CountdownTimerProps {
  deadline: string | null | undefined;
  /** Show seconds even when > 0 minutes remain (default: false) */
  showSeconds?: boolean;
  /** Optional custom class */
  className?: string;
}

/**
 * Live countdown timer for bounty deadlines.
 *
 * Displays days / hours / minutes / seconds remaining.
 * Color transitions:
 *   - Normal  : text-text-muted
 *   - Warning : text-status-warning  (< 24 hours)
 *   - Urgent  : text-status-error   (< 1 hour)
 *   - Expired : "Expired" in text-status-error
 *
 * Updates every second via useCountdown hook.
 */
export function CountdownTimer({ deadline, showSeconds = false, className = '' }: CountdownTimerProps) {
  const { days, hours, minutes, seconds, isExpired, isUrgent, isWarning } = useCountdown(deadline);

  const colorClass = isExpired
    ? 'text-status-error'
    : isUrgent
    ? 'text-status-error'
    : isWarning
    ? 'text-status-warning'
    : 'text-text-muted';

  const Icon = isExpired ? Timer : isUrgent ? AlertTriangle : Clock;

  if (isExpired) {
    return (
      <span className={`inline-flex items-center gap-1 font-mono text-xs font-medium ${colorClass} ${className}`}>
        <Icon className="w-3.5 h-3.5" />
        Expired
      </span>
    );
  }

  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0 || days > 0) parts.push(`${hours}h`);
  parts.push(`${minutes}m`);
  if (showSeconds || (days === 0 && hours === 0)) parts.push(`${seconds}s`);

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono text-xs font-medium ${colorClass} ${className}`}
      title={`Expires ${deadline ? new Date(deadline).toLocaleString() : ''}`}
    >
      <Icon className="w-3.5 h-3.5 flex-shrink-0" />
      {parts.join(' ')}
    </span>
  );
}
