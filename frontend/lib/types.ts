/**
 * TypeScript type definitions for RI CTC Calculator.
 * These types mirror the Pydantic models in the backend.
 */

/**
 * Filing status phaseout thresholds.
 */
export interface PhaseoutThresholds {
  SINGLE: number;
  JOINT: number;
  HEAD_OF_HOUSEHOLD: number;
  SURVIVING_SPOUSE: number;
  SEPARATE: number;
}

/**
 * Reform parameters for RI CTC calculations.
 */
export interface ReformParams {
  // CTC parameters
  ctc_amount: number;
  ctc_age_limit: number;
  ctc_refundability_cap: number;
  ctc_phaseout_rate: number;
  ctc_phaseout_thresholds: PhaseoutThresholds;
  // Stepped phaseout parameters (Governor's proposal style)
  ctc_stepped_phaseout: boolean;
  ctc_stepped_phaseout_threshold: number;
  ctc_stepped_phaseout_increment: number;
  ctc_stepped_phaseout_rate_per_step: number;
  ctc_young_child_boost_amount: number;
  ctc_young_child_boost_age_limit: number;

  // Dependent exemption parameters
  enable_exemption_reform: boolean;
  exemption_amount: number;
  exemption_age_limit_enabled: boolean;
  exemption_age_threshold: number;
  exemption_phaseout_rate: number;
  exemption_phaseout_thresholds: PhaseoutThresholds;
}

/**
 * Request for household impact calculation.
 */
export interface HouseholdRequest {
  age_head: number;
  age_spouse: number | null;
  dependent_ages: number[];
  income: number;
  year: number;
  reform_params: ReformParams;
}

/**
 * Request for aggregate/statewide impact calculation.
 */
export interface AggregateImpactRequest {
  year: number;
  reform_params: ReformParams;
}

/**
 * Benefit breakdown at a specific income level.
 */
export interface BenefitAtIncome {
  baseline: number;
  reform: number;
  difference: number;
  ctc_component: number;
  exemption_tax_benefit: number;
}

/**
 * Response for household impact calculation.
 */
export interface HouseholdImpactResponse {
  // Income sweep arrays for charts
  income_range: number[];
  ctc_baseline_range: number[];
  ctc_reform_range: number[];

  // Component breakdowns
  ctc_component: number[];
  exemption_tax_benefit: number[];

  // Specific benefit at user's income
  benefit_at_income: BenefitAtIncome;

  // Chart configuration
  x_axis_max: number;

  // Diagnostic data (optional)
  diagnostics?: Record<string, unknown>;
}

/**
 * Impact by income bracket.
 */
export interface IncomeBracket {
  bracket: string;
  beneficiaries: number;
  total_cost: number;
  avg_benefit: number;
}

/**
 * Response for aggregate/statewide impact calculation.
 */
export interface AggregateImpactResponse {
  // Top-level metrics
  total_cost: number;
  beneficiaries: number;
  avg_benefit: number;
  children_affected: number;

  // Winners/losers
  winners: number;
  losers: number;
  winners_rate: number;
  losers_rate: number;

  // Poverty impacts
  poverty_baseline_rate: number;
  poverty_reform_rate: number;
  poverty_rate_change: number;
  poverty_percent_change: number;

  child_poverty_baseline_rate: number;
  child_poverty_reform_rate: number;
  child_poverty_rate_change: number;
  child_poverty_percent_change: number;

  // Deep poverty impacts (below 50% of poverty line)
  deep_poverty_baseline_rate: number;
  deep_poverty_reform_rate: number;
  deep_poverty_rate_change: number;
  deep_poverty_percent_change: number;

  deep_child_poverty_baseline_rate: number;
  deep_child_poverty_reform_rate: number;
  deep_child_poverty_rate_change: number;
  deep_child_poverty_percent_change: number;

  // Income bracket breakdown
  by_income_bracket: IncomeBracket[];
}

/**
 * Health check response.
 */
export interface HealthResponse {
  status: string;
  dataset_loaded: boolean;
  version: string;
}

/**
 * Dataset summary response.
 */
export interface DatasetSummary {
  household_count: number;
  person_count: number;
  median_agi: number;
  p75_agi: number;
  p90_agi: number;
  total_children: number;
  households_with_children: number;
}
