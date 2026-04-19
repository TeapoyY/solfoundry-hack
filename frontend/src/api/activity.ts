import { apiClient } from '../services/apiClient';

/** Shape returned by GET /api/activity */
export interface ActivityEvent {
  id: string;
  type: 'completed' | 'submitted' | 'posted' | 'review';
  username: string;
  avatar_url?: string | null;
  detail: string;
  timestamp: string;
}

export interface ActivityListResponse {
  items: ActivityEvent[];
  total: number;
}

export interface ActivityListParams {
  limit?: number;
  offset?: number;
}

const DEFAULT_LIMIT = 10;

export async function listActivity(params?: ActivityListParams): Promise<ActivityEvent[]> {
  const response = await apiClient<ActivityEvent[] | ActivityListResponse>('/api/activity', {
    params: { limit: params?.limit ?? DEFAULT_LIMIT, offset: params?.offset ?? 0 },
  });
  if (Array.isArray(response)) return response.slice(0, 4);
  return (response.items ?? []).slice(0, 4);
}
