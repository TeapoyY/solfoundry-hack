import React, { useState, useEffect, useCallback } from 'react';
import { Clock, AlertTriangle, Flame } from 'lucide-react';
import { getDeadlineStatus, formatSeconds } from '../../lib/utils';

export type CountdownVariant = 'card' | 'detail' | 'compact';

interface CountdownTimerProps {
  deadline: string | null | undefined;
  variant?: CountdownVariant;
  /** Override the urgency color manually */
  forceStatus?: 'normal' | 'warning' | 'urgent' | 'expired';
}

function getColorClasses(status: 'normal' | 'warning' | 'urgent' | 'expired', variant: CountdownVariant) {
  const isCompact = variant === 'compact';

  if (status === 'expired') {
    return isCompact
      ? 'text-text-muted'
      : 'text-text-muted bg-text-muted/10 border border-text-muted/20';
  }
  if (status === 'urgent') {
    return isCompact
      ? 'text-status-error'
      : 'text-status-error bg-status-error/10 border border-status-error/20';
  }
  if (status === 'warning') {
    return isCompact
      ? 'text-status-warning'
      : 'text-status-warning bg-status-warning/10 border border-status-warning/20';
  }
  // normal
  return isCompact
    ? 'text-text-secondary'
    : 'text-text-secondary';
}

function getIcon(status: 'normal' | 'warning' | 'urgent' | 'expired', size: number) {
  if (status === 'urgent') return <Flame className={`w-${size} h-${size}`} />;
  if (status === 'warning') return <AlertTriangle className={`w-${size} h-${size}`} />;
  return <Clock className={`w-${size} h-${size}`} />;
}

// Sub-components for different countdown parts
function CountdownUnit({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col items-center min-w-[2rem]">
      <span className="font-mono text-lg font-bold leading-none">
        {String(value).padStart(2, '0')}
      </span>
      <span className="text-[10px] text-text-muted mt-0.5 uppercase tracking-wide">{label}</span>
    </div>
  );
}

function CountdownSeparator() {
  return <span className="font-mono text-lg font-bold text-text-muted/40 self-start pt-0.5">:</span>;
}

// Full numeric countdown with days/hours/minutes/seconds
export function CountdownTimer({ deadline, variant = 'card', forceStatus }: CountdownTimerProps) {
  const getInitialSeconds = useCallback(() => {
    if (!deadline) return -1;
    const diff = new Date(deadline).getTime() - Date.now();
    return diff <= 0 ? 0 : Math.floor(diff / 1000);
  }, [deadline]);

  const [secondsLeft, setSecondsLeft] = useState<number>(getInitialSeconds);

  useEffect(() => {
    setSecondsLeft(getInitialSeconds());
    if (!deadline) return;

    const interval = setInterval(() => {
      const diff = new Date(deadline).getTime() - Date.now();
      setSecondsLeft(diff <= 0 ? 0 : Math.floor(diff / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [deadline, getInitialSeconds]);

  const computedStatus = forceStatus ?? (deadline ? getDeadlineStatus(deadline) : 'normal');
  const colorClass = getColorClasses(computedStatus, variant);
  const iconSize = variant === 'detail' ? 4 : 3;

  if (!deadline) {
    return (
      <span className={`inline-flex items-center gap-1 ${colorClass} ${variant !== 'compact' ? 'text-xs px-2 py-1 rounded-lg border' : ''}`}>
        <Clock className={`w-${iconSize} h-${iconSize}`} />
        No deadline
      </span>
    );
  }

  if (secondsLeft === 0) {
    return (
      <span className={`inline-flex items-center gap-1.5 font-mono font-semibold ${colorClass} ${variant !== 'compact' ? 'text-sm px-3 py-1.5 rounded-lg border' : 'text-xs'}`}>
        {getIcon('expired', iconSize)}
        Expired
      </span>
    );
  }

  // Detail variant: show full DD:HH:MM:SS
  if (variant === 'detail') {
    const d = Math.floor(secondsLeft / 86400);
    const h = Math.floor((secondsLeft % 86400) / 3600);
    const m = Math.floor((secondsLeft % 3600) / 60);
    const s = secondsLeft % 60;

    return (
      <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${colorClass}`}>
        {getIcon(computedStatus, 4)}
        <div className="flex items-center gap-1 font-mono">
          {d > 0 && <>
            <CountdownUnit value={d} label="d" />
            <CountdownSeparator />
          </>}
          <CountdownUnit value={h} label="h" />
          <CountdownSeparator />
          <CountdownUnit value={m} label="m" />
          <CountdownSeparator />
          <CountdownUnit value={s} label="s" />
        </div>
      </div>
    );
  }

  // Compact/card variant: show formatted string with urgency styling
  const formatted = formatSeconds(secondsLeft);
  const icon = getIcon(computedStatus, iconSize);

  if (variant === 'compact') {
    return (
      <span className={`inline-flex items-center gap-1 ${colorClass}`} title={`Expires: ${new Date(deadline).toLocaleString()}`}>
        {icon}
        {formatted}
      </span>
    );
  }

  // Card variant: inline badge with icon
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-mono font-medium px-2 py-1 rounded-lg border ${colorClass}`} title={`Expires: ${new Date(deadline).toLocaleString()}`}>
      {icon}
      {formatted}
    </span>
  );
}
