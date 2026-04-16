import { apiClient } from '../services/apiClient';
import type { ActivityEvent } from '../components/home/ActivityFeed';

export interface ActivityListResponse {
  items: ActivityEvent[];
  total: number;
}

export async function listActivity(): Promise<ActivityEvent[]> {
  try {
    const response = await apiClient<ActivityListResponse | ActivityEvent[]>('/api/activity');
    if (Array.isArray(response)) {
      return response;
    }
    return response.items ?? [];
  } catch {
    // Return empty array on failure — ActivityFeed will fall back to mock data
    return [];
  }
}
