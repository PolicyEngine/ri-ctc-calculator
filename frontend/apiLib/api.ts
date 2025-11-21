/**
 * API client for communicating with the FastAPI backend.
 */

import axios from 'axios';
import type {
  HouseholdRequest,
  HouseholdImpactResponse,
  AggregateImpactResponse,
  DatasetSummary,
  ReformParams,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes for heavy PolicyEngine calculations
});

export interface BenefitAtIncome {
  baseline: number;
  reform: number;
  difference: number;
  ctc_component: number;
  exemption_tax_benefit: number;
}

export const api = {
  /**
   * Quick calculation: benefit at specific income only (no chart).
   * Much faster than calculateHouseholdImpact.
   */
  async calculateHouseholdBenefitQuick(
    request: HouseholdRequest
  ): Promise<BenefitAtIncome> {
    const response = await apiClient.post<BenefitAtIncome>(
      '/api/household-benefit-quick',
      request
    );
    return response.data;
  },

  /**
   * Full calculation: household impact across income range with chart data.
   * Slower than quick calculation due to income sweep.
   */
  async calculateHouseholdImpact(
    request: HouseholdRequest
  ): Promise<HouseholdImpactResponse> {
    const response = await apiClient.post<HouseholdImpactResponse>(
      '/api/household-impact',
      request
    );
    return response.data;
  },

  /**
   * Calculate aggregate/statewide impact.
   */
  async calculateAggregateImpact(
    reformParams: ReformParams
  ): Promise<AggregateImpactResponse> {
    const response = await apiClient.post<AggregateImpactResponse>(
      '/api/aggregate-impact',
      { reform_params: reformParams }
    );
    return response.data;
  },

  /**
   * Get dataset summary statistics.
   */
  async getDatasetSummary(): Promise<DatasetSummary> {
    const response = await apiClient.get<DatasetSummary>('/api/dataset-summary');
    return response.data;
  },

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string; dataset_loaded: boolean }> {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};