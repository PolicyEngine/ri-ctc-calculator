/**
 * API client for RI CTC Calculator backend.
 */

import type {
  ReformParams,
  HouseholdRequest,
  HouseholdImpactResponse,
  AggregateImpactResponse,
  HealthResponse,
  DatasetSummary,
} from "./types";
import type { PresetId, PresetPayload } from "./presets";

// API base URL from environment variable, defaults to localhost:8080
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// Multi-zone basePath prefix. The calculator embeds under
// /us/rhode-island-ctc-calculator; static fetches must include this
// prefix or they 404. The env-block injection from next.config.js
// proved unreliable across Turbopack rebuilds, so derive from
// window.location at runtime with a hard-coded fallback for SSR.
const FALLBACK_BASE_PATH = "/us/rhode-island-ctc-calculator";

function getBasePath(): string {
  if (typeof window !== "undefined") {
    const path = window.location.pathname;
    const idx = path.indexOf(FALLBACK_BASE_PATH);
    if (idx !== -1) return path.slice(0, idx + FALLBACK_BASE_PATH.length);
  }
  return process.env.NEXT_PUBLIC_BASE_PATH || FALLBACK_BASE_PATH;
}

// Timeout for API requests (2 minutes for aggregate calculations)
const DEFAULT_TIMEOUT = 120000;

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Make a fetch request with timeout support.
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout: number = DEFAULT_TIMEOUT,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Fetch the precomputed payload for a Governor's-proposal preset from
 * ``/data/presets/{id}.json``. Uses ``NEXT_PUBLIC_BASE_PATH`` so it
 * works under the multizone embed.
 */
export async function fetchPresetPayload(
  presetId: PresetId,
): Promise<PresetPayload> {
  const url = `${getBasePath()}/data/presets/${presetId}.json`;
  console.log("[preset] fetching", url);
  const response = await fetch(url, { cache: "no-store" });
  console.log("[preset] response", response.status, response.url);
  if (!response.ok) {
    throw new ApiError(
      `Failed to load preset ${presetId}: HTTP ${response.status}`,
      response.status,
    );
  }
  return response.json();
}

/**
 * API client methods.
 */
export const api = {
  /**
   * Calculate household impact across income range.
   */
  async calculateHouseholdImpact(
    request: HouseholdRequest,
  ): Promise<HouseholdImpactResponse> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/household-impact`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      },
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        errorData?.detail || `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },

  /**
   * Calculate statewide aggregate impact.
   * Note: This takes ~90 seconds due to microsimulation calculations.
   */
  async calculateAggregateImpact(
    reformParams: ReformParams,
    year: number = 2027,
  ): Promise<AggregateImpactResponse> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/aggregate-impact`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ year: year, reform_params: reformParams }),
      },
      DEFAULT_TIMEOUT,
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        errorData?.detail || `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },

  /**
   * Health check endpoint.
   */
  async health(): Promise<HealthResponse> {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/health`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new ApiError(`Health check failed: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Get dataset summary statistics.
   */
  async getDatasetSummary(): Promise<DatasetSummary> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/dataset-summary`,
      {
        method: "GET",
      },
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        errorData?.detail || `HTTP error ${response.status}`,
        response.status,
        errorData,
      );
    }

    return response.json();
  },
};

export default api;
