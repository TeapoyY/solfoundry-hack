import React, { useState, useEffect } from 'react';

interface CountdownTimerProps {
  deadline: string;
  className?: string;
}

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  expired: boolean;
}

function calculateTimeLeft(deadline: string): TimeLeft {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diffMs = deadlineDate.getTime() - now.getTime();

  if (diffMs <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
  }

  const totalSeconds = Math.floor(diffMs / 1000);
  return {
    days: Math.floor(totalSeconds / 86400),
    hours: Math.floor((totalSeconds % 86400) / 3600),
    minutes: Math.floor((totalSeconds % 3600) / 60),
    seconds: totalSeconds % 60,
    expired: false,
  };
}

export function CountdownTimer({ deadline, className = '' }: CountdownTimerProps) {
  const [timeLeft, setTimeLeft] = useState<TimeLeft>(() => calculateTimeLeft(deadline));

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft(deadline));
    }, 1000);

    return () => clearInterval(timer);
  }, [deadline]);

  if (timeLeft.expired) {
    return (
      <span className={`font-mono text-sm text-text-muted ${className}`}>
        Expired
      </span>
    );
  }

  const urgencyClass =
    timeLeft.days === 0 && timeLeft.hours === 0
      ? 'text-status-error'
      : timeLeft.days === 0
      ? 'text-status-warning'
      : 'text-text-secondary';

  const parts: string[] = [];
  if (timeLeft.days > 0) parts.push(`${timeLeft.days}d`);
  if (timeLeft.hours > 0 || timeLeft.days > 0) parts.push(`${timeLeft.hours}h`);
  parts.push(`${timeLeft.minutes}m`);
  if (timeLeft.days === 0 && timeLeft.hours === 0) {
    parts.push(`${timeLeft.seconds}s`);
  }

  return (
    <span className={`font-mono text-sm font-medium ${urgencyClass} ${className}`}>
      {parts.join(' ')}
    </span>
  );
}
