import { useState, useEffect, useCallback } from 'react';

export interface CountdownParts {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  isExpired: boolean;
  isUrgent: boolean;    // < 1 hour
  isWarning: boolean;  // < 24 hours
}

/**
 * Hook that provides live countdown parts for a given deadline.
 * Updates every second while the deadline hasn't passed.
 */
export function useCountdown(deadline: string | null | undefined): CountdownParts {
  const compute = useCallback((): CountdownParts => {
    if (!deadline) {
      return { days: 0, hours: 0, minutes: 0, seconds: 0, isExpired: false, isUrgent: false, isWarning: false };
    }

    const now = new Date();
    const target = new Date(deadline);
    const diffMs = target.getTime() - now.getTime();

    if (diffMs <= 0) {
      return { days: 0, hours: 0, minutes: 0, seconds: 0, isExpired: true, isUrgent: false, isWarning: false };
    }

    const totalSeconds = Math.floor(diffMs / 1000);
    const days    = Math.floor(totalSeconds / 86400);
    const hours   = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return {
      days,
      hours,
      minutes,
      seconds,
      isExpired: false,
      isUrgent: diffMs < 60 * 60 * 1000,       // < 1 hour
      isWarning: diffMs < 24 * 60 * 60 * 1000, // < 24 hours
    };
  }, [deadline]);

  const [parts, setParts] = useState<CountdownParts>(compute);

  useEffect(() => {
    setParts(compute()); // re-sync when deadline changes
    if (!deadline) return;

    const interval = setInterval(() => {
      setParts(compute());
    }, 1000);

    return () => clearInterval(interval);
  }, [deadline, compute]);

  return parts;
}
