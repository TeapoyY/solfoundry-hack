// Language colors for skill tags
export const LANG_COLORS: Record<string, string> = {
  TypeScript: '#3178c6',
  JavaScript: '#f7df1e',
  Python: '#3572A5',
  Rust: '#dea584',
  Go: '#00ADD8',
  Solidity: '#AA6746',
  HTML: '#E34C26',
  CSS: '#563d7c',
  React: '#61dafb',
  Vue: '#41b883',
  Angular: '#dd0031',
  Node: '#339933',
  'C++': '#f34b7d',
  C: '#555555',
  Java: '#b07219',
  Swift: '#ffac45',
  Kotlin: '#F18E33',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Shell: '#89e051',
};

// Format currency amount with token
export function formatCurrency(amount: number, token: string): string {
  if (token === 'USDC') {
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} USDC`;
  }
  if (token === 'FNDRY') {
    return `${amount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} FNDRY`;
  }
  return `${amount} ${token}`;
}

// Time urgency status based on deadline
export type DeadlineStatus = 'normal' | 'warning' | 'urgent' | 'expired';

export function getDeadlineStatus(deadline: string | null | undefined): DeadlineStatus {
  if (!deadline) return 'normal';
  const now = Date.now();
  const ms = new Date(deadline).getTime();
  const diff = ms - now;
  if (diff <= 0) return 'expired';
  if (diff < 60 * 60 * 1000) return 'urgent';   // < 1 hour
  if (diff < 24 * 60 * 60 * 1000) return 'warning'; // < 24 hours
  return 'normal';
}

// Human-readable time remaining string (e.g. "3d 5h", "2h 30m", "45m")
export function timeLeft(deadline: string | null | undefined): string {
  if (!deadline) return 'No deadline';
  const now = Date.now();
  const ms = new Date(deadline).getTime();
  const diff = ms - now;
  if (diff <= 0) return 'Expired';

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    const remainingHours = hours % 24;
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
  }
  if (hours > 0) {
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  }
  return `${minutes}m`;
}

// Parse deadline into total seconds remaining (for countdown timer)
export function getSecondsLeft(deadline: string | null | undefined): number {
  if (!deadline) return -1;
  const now = Date.now();
  const ms = new Date(deadline).getTime();
  const diff = ms - now;
  return diff <= 0 ? 0 : Math.floor(diff / 1000);
}

// Format seconds into "Xd Xh Xm" string
export function formatSeconds(seconds: number): string {
  if (seconds <= 0) return 'Expired';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const parts: string[] = [];
  if (d > 0) parts.push(`${d}d`);
  if (h > 0) parts.push(`${h}h`);
  if (m > 0 || parts.length === 0) parts.push(`${m}m`);
  return parts.join(' ');
}

// Time ago string (e.g. "2 hours ago", "3 days ago")
export function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diff = now - then;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'Just now';
}
