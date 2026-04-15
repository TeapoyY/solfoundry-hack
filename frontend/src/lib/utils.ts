export function timeLeft(deadline: string): string {
  const now = new Date().getTime();
  const end = new Date(deadline).getTime();
  const diff = end - now;

  if (diff <= 0) return 'Expired';

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

export function timeAgo(dateStr: string): string {
  const now = new Date().getTime();
  const date = new Date(dateStr).getTime();
  const diff = now - date;

  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'just now';
}

export function formatCurrency(amount: number, token: string): string {
  if (token === 'USDC') {
    return `$${amount.toLocaleString()}`;
  }
  return `${amount.toLocaleString()} $${token}`;
}

export const LANG_COLORS: Record<string, string> = {
  TypeScript: '#3178C6',
  JavaScript: '#F7DF1E',
  Python: '#3572A5',
  Rust: '#DEA584',
  Go: '#00ADD8',
  Solidity: '#AA36FF',
  Cairo: '#WIP',
  Move: '#4FC3F7',
  React: '#61DAFB',
  Vue: '#41B883',
  Svelte: '#FF3E00',
  HTML: '#E34F26',
  CSS: '#1572B6',
  SCSS: '#CC6699',
  Shell: '#89E051',
  Dockerfile: '#384D54',
  'C#': '#178600',
  'C++': '#F34B7D',
  Java: '#B07219',
  Swift: '#FA7343',
  Kotlin: '#A97BFF',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Dart: '#00B4AB',
  Lua: '#000080',
};
