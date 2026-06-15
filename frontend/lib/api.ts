/**
 * API client for the RI CTC Calculator.
 *
 * Presets load precomputed JSON from the frontend bundle. Live custom
 * calculations use the pinned Modal FastAPI backend rather than the public
 * PolicyEngine API, so the calculator stays on the model version selected
 * for this PR.
 */

import type {
  AggregateImpactResponse,
  DatasetSummary,
  HealthResponse,
  HouseholdImpactResponse,
  HouseholdRequest,
  ReformParams,
} from './types';
import type { PresetPayload, StaticPresetId } from './presets';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
const FALLBACK_BASE_PATH = '/us/rhode-island-ctc-calculator';
const DEFAULT_TIMEOUT = 180_000;

function getBasePath(): string {
  if (typeof window !== 'undefined') {
    const path = window.location.pathname;
    const idx = path.indexOf(FALLBACK_BASE_PATH);
    if (idx !== -1) return path.slice(0, idx + FALLBACK_BASE_PATH.length);
  }
  return process.env.NEXT_PUBLIC_BASE_PATH || FALLBACK_BASE_PATH;
}

export async function fetchPresetPayload(
  presetId: StaticPresetId,
): Promise<PresetPayload> {
  const url = `${getBasePath()}/data/presets/${presetId}.json`;
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) {
    throw new ApiError(
      `Failed to load preset ${presetId}: HTTP ${response.status}`,
      response.status,
    );
  }
  return response.json();
}

export class ApiError extends Error {
  status?: number;
  response?: unknown;

  constructor(message: string, status?: number, response?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout = DEFAULT_TIMEOUT,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, {
      ...options,
      signal: options.signal ?? controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function parseError(response: Response): Promise<unknown> {
  return response.json().catch(() => null);
}

export const api = {
  async calculateHouseholdImpact(
    request: HouseholdRequest,
  ): Promise<HouseholdImpactResponse> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/household-impact`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      },
    );

    if (!response.ok) {
      const errorData = await parseError(response);
      throw new ApiError(
        (errorData as { detail?: string } | null)?.detail ??
          `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },

  async calculateAggregateImpact(
    reformParams: ReformParams,
    year = 2027,
    signal?: AbortSignal,
  ): Promise<AggregateImpactResponse> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/aggregate-impact`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year, reform_params: reformParams }),
        signal,
      },
      DEFAULT_TIMEOUT,
    );

    if (!response.ok) {
      const errorData = await parseError(response);
      throw new ApiError(
        (errorData as { detail?: string } | null)?.detail ??
          `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },

  async health(): Promise<HealthResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new ApiError(`Health check failed: ${response.status}`);
    }

    return response.json();
  },

  async getDatasetSummary(): Promise<DatasetSummary> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/dataset-summary`,
      { method: 'GET' },
    );

    if (!response.ok) {
      const errorData = await parseError(response);
      throw new ApiError(
        (errorData as { detail?: string } | null)?.detail ??
          `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },
};

export default api;
