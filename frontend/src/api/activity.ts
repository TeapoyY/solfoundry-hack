import { apiClient } from '../services/apiClient';

export interface ActivityEvent {
  id: string;
  type: 'completed' | 'submitted' | 'posted' | 'review' | 'paid';
  username: string;
  avatar_url?: string | null;
  detail: string;
  timestamp: string;
}

export async function listActivity(): Promise<ActivityEvent[]> {
  return apiClient<ActivityEvent[]>('/api/activity');
}
