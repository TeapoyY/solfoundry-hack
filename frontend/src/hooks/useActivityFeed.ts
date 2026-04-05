import { useQuery } from '@tanstack/react-query';
import { listActivity } from '../api/activity';

const REFRESH_INTERVAL_MS = 30_000;

export function useActivityFeed() {
  return useQuery({
    queryKey: ['activity-feed'],
    queryFn: listActivity,
    refetchInterval: REFRESH_INTERVAL_MS,
    staleTime: REFRESH_INTERVAL_MS,
    retry: 1,
  });
}
