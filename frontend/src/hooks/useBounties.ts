import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { listBounties, getBounty } from '../api/bounties';
import type { BountiesListParams } from '../api/bounties';

export function useBounties(params?: BountiesListParams) {
  return useQuery({
    queryKey: ['bounties', params],
    queryFn: () => listBounties(params),
    staleTime: 30_000,
  });
}

export function useInfiniteBounties(params?: Omit<BountiesListParams, 'offset'>) {
  return useInfiniteQuery({
    queryKey: ['bounties-infinite', params],
    queryFn: ({ pageParam = 0 }) =>
      listBounties({ ...params, offset: pageParam as number, limit: 12 }),
    getNextPageParam: (lastPage, pages) => {
      const loaded = pages.reduce((sum, p) => sum + p.items.length, 0);
      if (loaded >= lastPage.total) return undefined;
      return loaded;
    },
    initialPageParam: 0,
    staleTime: 30_000,
  });
}

// Returns the total count from the first page (only reliable when not loading more)
export function useBountyCount(params?: Omit<BountiesListParams, 'offset'>) {
  const { data } = useQuery({
    queryKey: ['bounties', params],
    queryFn: () => listBounties({ ...params, limit: 1 }),
    staleTime: 30_000,
  });
  return data?.total ?? 0;
}

export function useBounty(id: string | undefined) {
  return useQuery({
    queryKey: ['bounty', id],
    queryFn: () => getBounty(id!),
    enabled: !!id,
    staleTime: 30_000,
  });
}
