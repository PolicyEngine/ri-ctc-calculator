/**
 * TypeScript types matching the backend API models.
 */

export interface ReformParams {
  ctc_amount: number;
  ctc_age_limit: number;
  ctc_refundability_cap: number;
  ctc_phaseout_rate: number;
  ctc_phaseout_thresholds: {
    SINGLE: number;
    JOINT: number;
    HEAD_OF_HOUSEHOLD: number;
    SURVIVING_SPOUSE: number;
    SEPARATE: number;
  };
  ctc_young_child_boost_amount: number;
  ctc_young_child_boost_age_limit: number;
  enable_exemption_reform: boolean;
  exemption_amount: number;
  exemption_age_limit_enabled: boolean;
  exemption_age_threshold: number;
  exemption_phaseout_rate: number;
  exemption_phaseout_thresholds: {
    SINGLE: number;
    JOINT: number;
    HEAD_OF_HOUSEHOLD: number;
    SURVIVING_SPOUSE: number;
    SEPARATE: number;
  } | null;
}

export interface HouseholdRequest {
  age_head: number;
  age_spouse: number | null;
  dependent_ages: number[];
  income: number;
  reform_params: ReformParams;
}

export interface BenefitAtIncome {
  baseline: number;
  reform: number;
  difference: number;
  ctc_component: number;
  exemption_tax_benefit: number;
}

export interface HouseholdImpactResponse {
  income_range: number[];
  ctc_baseline_range: number[];
  ctc_reform_range: number[];
  ctc_component: number[];
  exemption_tax_benefit: number[];
  benefit_at_income: BenefitAtIncome;
  x_axis_max: number;
  diagnostics?: any;
}

export interface IncomeBracket {
  bracket: string;
  beneficiaries: number;
  total_cost: number;
  avg_benefit: number;
}

export interface AggregateImpactResponse {
  total_cost: number;
  beneficiaries: number;
  avg_benefit: number;
  children_affected: number;
  winners: number;
  losers: number;
  winners_rate: number;
  losers_rate: number;
  poverty_baseline_rate: number;
  poverty_reform_rate: number;
  poverty_rate_change: number;
  poverty_percent_change: number;
  child_poverty_baseline_rate: number;
  child_poverty_reform_rate: number;
  child_poverty_rate_change: number;
  child_poverty_percent_change: number;
  by_income_bracket: IncomeBracket[];
}

export interface DatasetSummary {
  household_count: number;
  person_count: number;
  median_agi: number;
  p75_agi: number;
  p90_agi: number;
  total_children: number;
  households_with_children: number;
}