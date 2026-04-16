import { useQuery } from '@tanstack/react-query';
import { listActivity } from '../api/activity';

/**
 * Fetch real activity events from the API.
 * Auto-refreshes every 30 seconds as required by the bounty spec.
 * Returns empty array on error so the ActivityFeed falls back to mock data.
 */
export function useActivity() {
  return useQuery({
    queryKey: ['activity'],
    queryFn: listActivity,
    refetchInterval: 30_000, // auto-refresh every 30 seconds
    staleTime: 15_000,
    retry: 1,
  });
}
