import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { listBounties, getBounty } from '../api/bounties';
import type { BountiesListParams } from '../api/bounties';

/**
 * Single-shot query hook for fetching a paginated list of bounties.
 * Results are cached for 30 seconds.
 *
 * @param params - Filter parameters (status, skill, tier, reward_token, query, limit, offset).
 * @returns TanStack Query result containing BountiesListResponse.
 */
export function useBounties(params?: BountiesListParams) {
  return useQuery({
    queryKey: ['bounties', params],
    queryFn: () => listBounties(params),
    staleTime: 30_000,
  });
}

/**
 * Infinite-scroll query hook for loading bounties in pages of 12.
 * Combines skill/status filtering with server-side full-text search via the `query` param.
 * Automatically deduces the next page offset from accumulated pages.
 *
 * @param params - Filter + search parameters (excludes offset; derived internally).
 * @returns Infinite TanStack Query result with `data.pages`, `fetchNextPage`, `hasNextPage`.
 */
export function useInfiniteBounties(params?: Omit<BountiesListParams, 'offset'> & { query?: string }) {
  return useInfiniteQuery({
    queryKey: ['bounties-infinite', params],
    queryFn: ({ pageParam = 0 }) =>
      listBounties({ ...params, offset: pageParam as number, limit: 12 }),
    getNextPageParam: (lastPage, pages) => {
      const loaded = pages.reduce((sum, p) => sum + p.items.length, 0);
      if (loaded >= (lastPage.total ?? 0)) return undefined;
      return loaded;
    },
    initialPageParam: 0,
    staleTime: 30_000,
  });
}

export function useBounty(id: string | undefined) {
  return useQuery({
    queryKey: ['bounty', id],
    queryFn: () => getBounty(id!),
    enabled: !!id,
    staleTime: 30_000,
  });
}
