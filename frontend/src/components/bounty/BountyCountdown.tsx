import { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

interface TimeRemaining {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total: number;
}

function computeTimeRemaining(deadline: string): TimeRemaining {
  const now = Date.now();
  const end = new Date(deadline).getTime();
  const diff = Math.max(0, end - now);

  const days = Math.floor(diff / 86_400_000);
  const hours = Math.floor((diff % 86_400_000) / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);
  const seconds = Math.floor((diff % 60_000) / 1_000);

  return { days, hours, minutes, seconds, total: diff };
}

type Urgency = 'normal' | 'warning' | 'urgent' | 'expired';

function getUrgency(time: TimeRemaining): Urgency {
  if (time.total === 0) return 'expired';
  const hoursRemaining = time.total / 3_600_000;
  if (hoursRemaining < 1) return 'urgent';
  if (hoursRemaining < 24) return 'warning';
  return 'normal';
}

function urgencyStyles(urgency: Urgency): { text: string; icon?: string } {
  switch (urgency) {
    case 'expired':
      return { text: 'text-text-muted line-through' };
    case 'urgent':
      return { text: 'text-red-400' };
    case 'warning':
      return { text: 'text-amber-400' };
    default:
      return { text: 'text-text-muted' };
  }
}

function formatCountdown(time: TimeRemaining): string {
  const { days, hours, minutes, seconds } = time;
  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

interface BountyCountdownProps {
  deadline: string;
}

export function BountyCountdown({ deadline }: BountyCountdownProps) {
  const [time, setTime] = useState<TimeRemaining>(() => computeTimeRemaining(deadline));

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(computeTimeRemaining(deadline));
    }, 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  const urgency = getUrgency(time);
  const styles = urgencyStyles(urgency);

  return (
    <span className={`inline-flex items-center gap-1 ${styles.text}`}>
      <Clock className="w-3.5 h-3.5" />
      {urgency === 'expired' ? 'Expired' : formatCountdown(time)}
    </span>
  );
}
