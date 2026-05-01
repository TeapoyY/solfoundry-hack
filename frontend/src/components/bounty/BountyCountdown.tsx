import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, Zap } from 'lucide-react';
import { getTimeParts } from '../../lib/utils';

export type CountdownUrgency = 'normal' | 'warning' | 'urgent' | 'expired';

/**
 * Determines the urgency tier of a countdown based on time remaining.
 *
 * @param expired    - Whether the deadline has already passed.
 * @param days       - Whole days remaining.
 * @param hours      - Whole hours remaining (used when days === 0).
 * @returns Urgency level: expired > urgent (under 1h) > warning (under 1d) > normal.
 */
function getUrgency(expired: boolean, days: number, hours: number): CountdownUrgency {
  if (expired) return 'expired';
  if (days === 0 && hours < 1) return 'urgent';
  if (days === 0) return 'warning';
  return 'normal';
}

const urgencyStyles: Record<CountdownUrgency, { text: string; bg: string; border: string; icon: React.ReactNode }> = {
  normal: {
    text: 'text-text-muted',
    bg: 'bg-forge-800',
    border: 'border-border',
    icon: <Clock className="w-3.5 h-3.5" />,
  },
  warning: {
    text: 'text-status-warning',
    bg: 'bg-status-warning/10',
    border: 'border-status-warning/30',
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
  },
  urgent: {
    text: 'text-status-error',
    bg: 'bg-status-error/10',
    border: 'border-status-error/30',
    icon: <Zap className="w-3.5 h-3.5" />,
  },
  expired: {
    text: 'text-text-muted',
    bg: 'bg-forge-800',
    border: 'border-border',
    icon: <Clock className="w-3.5 h-3.5" />,
  },
};

interface BountyCountdownProps {
  deadline: string;
  /** Compact: single-line layout for cards. Default: false (detailed). */
  compact?: boolean;
  /** Show seconds tick. Default: false. */
  showSeconds?: boolean;
  /** Additional CSS classes. */
  className?: string;
}

/**
 * Live countdown timer for a bounty deadline.
 *
 * Updates every second via `setInterval`. Reflects urgency through
 * colour and icon changes as the deadline approaches.
 *
 * @param deadline    - ISO date string for the bounty deadline.
 * @param compact     - Single-line layout for use inside cards. Default: false.
 * @param showSeconds - Tick the seconds display. Default: false.
 * @param className   - Additional CSS classes to apply to the container.
 */
export function BountyCountdown({ deadline, compact = false, showSeconds = false, className = '' }: BountyCountdownProps) {
  const [parts, setParts] = useState(() => getTimeParts(deadline));

  useEffect(() => {
    // Update every second for real-time countdown
    const interval = setInterval(() => {
      setParts(getTimeParts(deadline));
    }, 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  const urgency = getUrgency(parts.expired, parts.days, parts.hours);
  const style = urgencyStyles[urgency];

  if (compact) {
    const icon = <Clock className="w-3.5 h-3.5" />;
    return (
      <span className={`inline-flex items-center gap-1 font-mono text-xs ${urgencyStyles[urgency].text}`}>
        {icon}
        {parts.expired ? 'Expired' : `${parts.days}d ${parts.hours}h ${parts.minutes}m`}
      </span>
    );
  }

  const icon = urgencyStyles[urgency].icon;
  const textStyle = urgencyStyles[urgency].text;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${urgencyStyles[urgency].bg} ${urgencyStyles[urgency].border} ${className}`}
    >
      <span className={textStyle}>{icon}</span>
      {parts.expired ? (
        <span className={`font-mono text-sm font-medium ${textStyle}`}>Expired</span>
      ) : (
        <span className={`font-mono text-sm font-medium ${textStyle}`}>
          {parts.days > 0 && <span>{parts.days}<span className="text-xs ml-0.5 mr-1">d</span></span>}
          {parts.days > 0 && parts.hours > 0 && <span>{parts.hours}<span className="text-xs ml-0.5 mr-1">h</span></span>}
          {parts.days === 0 && <span>{parts.hours}<span className="text-xs ml-0.5 mr-1">h</span></span>}
          <span>{parts.minutes}<span className="text-xs ml-0.5 mr-1">m</span></span>
          {showSeconds && <span>{parts.seconds}<span className="text-xs ml-0.5">s</span></span>}
        </span>
      )}
    </div>
  );
}
