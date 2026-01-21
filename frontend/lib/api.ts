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

// API base URL from environment variable, defaults to localhost:8080
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

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
