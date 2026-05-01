import { apiClient } from '../services/apiClient';
import type {
  Bounty,
  BountyCreatePayload,
  Submission,
  TreasuryDepositInfo,
  EscrowVerifyPayload,
  EscrowVerifyResult,
} from '../types/bounty';

export interface BountiesListParams {
  status?: string;
  limit?: number;
  offset?: number;
  skill?: string;
  tier?: string;
  reward_token?: string;
  query?: string;
}

export interface BountiesListResponse {
  items: Bounty[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Maps a raw Bounty object from the API to the frontend type, normalising
 * the `funding_token` / `reward_token` ambiguity in older backend responses.
 *
 * @param b - Raw bounty object as returned by the API.
 * @returns A fully-typed Bounty with `reward_token` always set (defaults to 'FNDRY').
 */
function mapBounty(b: Bounty): Bounty {
  const raw = b as Bounty & { funding_token?: string };
  if (!raw.reward_token && raw.funding_token) {
    raw.reward_token = raw.funding_token as Bounty['reward_token'];
  }
  if (!raw.reward_token) raw.reward_token = 'FNDRY';
  return raw;
}

/**
 * Fetches a paginated list of bounties, optionally filtered by status, skill,
 * tier, reward token, and free-text query.
 *
 * @param params - Filter and pagination parameters.
 * @returns Paginated list of bounty items with total count.
 */
export async function listBounties(params?: BountiesListParams): Promise<BountiesListResponse> {
  const response = await apiClient<BountiesListResponse | Bounty[]>('/api/bounties', {
    params: params as Record<string, string | number | boolean | undefined>,
  });
  // Handle both array and paginated response shapes
  if (Array.isArray(response)) {
    return { items: response.map(mapBounty), total: response.length, limit: params?.limit ?? 20, offset: params?.offset ?? 0 };
  }
  return { ...response, items: response.items.map(mapBounty) };
}

/**
 * Fetches a single bounty by its unique ID.
 *
 * @param id - The bounty UUID.
 * @returns The full bounty object.
 * @throws If the bounty is not found or the API returns an error.
 */
export async function getBounty(id: string): Promise<Bounty> {
  const raw = await apiClient<Bounty>(`/api/bounties/${id}`);
  return mapBounty(raw);
}

/**
 * Creates a new bounty on the platform.
 *
 * @param payload - Bounty creation fields (title, description, reward, deadline, etc.).
 * @returns The newly created bounty object.
 */
export async function createBounty(payload: BountyCreatePayload): Promise<Bounty> {
  return apiClient<Bounty>('/api/bounties', { method: 'POST', body: payload });
}

/**
 * Fetches all submissions for a given bounty.
 *
 * @param bountyId - The UUID of the bounty.
 * @returns Array of submission objects.
 */
export async function listSubmissions(bountyId: string): Promise<Submission[]> {
  return apiClient<Submission[]>(`/api/bounties/${bountyId}/submissions`);
}

/**
 * Submits a solution for a bounty.
 *
 * @param bountyId - UUID of the target bounty.
 * @param payload  - Submission fields: repo URL, PR URL, description, and optionally a tx signature.
 * @returns The created submission object.
 */
export async function createSubmission(
  bountyId: string,
  payload: { repo_url?: string; pr_url?: string; description?: string; tx_signature?: string }
): Promise<Submission> {
  return apiClient<Submission>(`/api/bounties/${bountyId}/submissions`, {
    method: 'POST',
    body: payload,
  });
}

/**
 * Fetches the on-chain treasury deposit info required to fund a bounty.
 *
 * @param bountyId - UUID of the bounty to be funded.
 * @returns Treasury deposit instruction data (amounts, token, destination).
 */
export async function getTreasuryDepositInfo(bountyId: string): Promise<TreasuryDepositInfo> {
  return apiClient<TreasuryDepositInfo>('/api/treasury/deposit-info', {
    params: { bounty_id: bountyId },
  });
}

/**
 * Verifies that a bounty funder has posted the required escrow deposit on-chain.
 *
 * @param payload - Escrow verification fields (bounty ID, deposit tx signature, etc.).
 * @returns Object indicating whether escrow is confirmed, with the verified FNS amount.
 */
export async function verifyEscrowDeposit(payload: EscrowVerifyPayload): Promise<EscrowVerifyResult> {
  return apiClient<EscrowVerifyResult>('/api/escrow/verify-deposit', {
    method: 'POST',
    body: payload,
  });
}

export interface ReviewFeeInfo {
  bounty_id: string;
  required: boolean;
  fndry_amount: number;
  fndry_price_usd: number;
  usdc_bounty_value: number;
  fee_percentage: number;
  exchange_rate: number;
  price_source: string;
}

/**
 * Looks up the review-fee schedule for a bounty — how much FNDRY is required
 * to enter the AI review pipeline, expressed in both FNDRY and USDC equivalent.
 *
 * @param bountyId - UUID of the bounty.
 * @returns Fee breakdown (amount, required flag, exchange rate, price source).
 */
export async function getReviewFee(bountyId: string): Promise<ReviewFeeInfo> {
  return apiClient<ReviewFeeInfo>(`/api/review-fee/${bountyId}`);
}

export async function verifyReviewFee(payload: {
  bounty_id: string;
  tx_signature: string;
  payer_wallet?: string;
}): Promise<{ verified: boolean; bounty_id: string; fndry_amount_verified?: number; error?: string }> {
  return apiClient('/api/review-fee/verify', { method: 'POST', body: payload });
}
