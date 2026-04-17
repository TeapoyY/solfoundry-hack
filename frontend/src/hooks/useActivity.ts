import { useQuery } from '@tanstack/react-query';
import { getActivity } from '../api/stats';

const REFRESH_INTERVAL_MS = 30_000;

export function useActivity() {
  return useQuery({
    queryKey: ['activity'],
    queryFn: getActivity,
    refetchInterval: REFRESH_INTERVAL_MS,
    staleTime: 15_000,
    retry: 1,
  });
}
