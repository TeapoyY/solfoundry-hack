import { useQuery } from '@tanstack/react-query';
import { listActivity } from '../api/activity';
import type { ActivityEvent } from '../api/activity';

/** Mock events used as fallback when the API call fails or returns nothing. */
const MOCK_EVENTS: ActivityEvent[] = [
  {
    id: 'mock-1',
    type: 'completed',
    username: 'devbuilder',
    detail: '$500 USDC from Bounty #42',
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-2',
    type: 'submitted',
    username: 'KodeSage',
    detail: 'PR to Bounty #38',
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-3',
    type: 'posted',
    username: 'SolanaLabs',
    detail: 'Bounty #145 — $3,500 USDC',
    timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
  },
  {
    id: 'mock-4',
    type: 'review',
    username: 'AI Review',
    detail: 'Bounty #42 — 8.5/10',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
  },
];

export const REFRESH_INTERVAL_MS = 30_000;

/**
 * Fetches the platform activity feed from GET /api/activity.
 * Auto-refreshes every 30 seconds and falls back to mock data on failure
 * or when the API returns an empty list.
 */
export function useActivityFeed() {
  return useQuery({
    queryKey: ['activity-feed'],
    queryFn: async () => {
      try {
        const items = await listActivity({ limit: 4 });
        return items.length > 0 ? items : MOCK_EVENTS;
      } catch {
        return MOCK_EVENTS;
      }
    },
    // Keep stale data visible while fetching fresh data in the background
    staleTime: REFRESH_INTERVAL_MS - 1_000,
    // Auto-refresh every 30 seconds
    refetchInterval: REFRESH_INTERVAL_MS,
    // Don't retry on failure — we have mock fallback
    retry: false,
    // Start with mock data immediately (no initial data needed from server)
    initialData: MOCK_EVENTS,
  });
}
