import {
  ENACTED_CTC_PHASEOUT_INCREMENTS,
  ENACTED_CTC_PHASEOUT_THRESHOLDS,
} from './presets';
import type {
  BenefitAtIncome,
  HouseholdImpactResponse,
  HouseholdRequest,
  PhaseoutThresholds,
} from './types';
import { HOUSEHOLD_SWEEP_MAX, HOUSEHOLD_SWEEP_POINTS } from './buildHousehold';

type FilingStatus = keyof PhaseoutThresholds;

const CTC_AMOUNT = 330;
const PHASEOUT_RATE_PER_STEP = 0.2;

function filingStatusForHousehold(request: HouseholdRequest): FilingStatus {
  return request.age_spouse !== null ? 'JOINT' : 'SINGLE';
}

function eligibleChildren(request: HouseholdRequest): number {
  return request.dependent_ages.filter((age) => age <= 18).length;
}

export function enactedCtcForIncome(
  income: number,
  children: number,
  filingStatus: FilingStatus,
): number {
  const maximum = children * CTC_AMOUNT;
  if (maximum <= 0) return 0;

  const threshold = ENACTED_CTC_PHASEOUT_THRESHOLDS[filingStatus];
  const increment = ENACTED_CTC_PHASEOUT_INCREMENTS[filingStatus];
  const excess = Math.max(income - threshold, 0);
  const steps = excess > 0 ? Math.ceil(excess / increment) : 0;
  const phaseoutRate = Math.min(steps * PHASEOUT_RATE_PER_STEP, 1);

  return maximum * (1 - phaseoutRate);
}

export function calculateEnactedLawHouseholdImpact(
  request: HouseholdRequest,
): HouseholdImpactResponse {
  const filingStatus = filingStatusForHousehold(request);
  const children = eligibleChildren(request);
  const incomeRange = Array.from(
    { length: HOUSEHOLD_SWEEP_POINTS },
    (_, i) => (HOUSEHOLD_SWEEP_MAX * i) / (HOUSEHOLD_SWEEP_POINTS - 1),
  );
  const ctcRange = incomeRange.map((income) =>
    enactedCtcForIncome(income, children, filingStatus),
  );
  const ctcAtIncome = enactedCtcForIncome(request.income, children, filingStatus);
  const baselineAtIncome = request.income;

  const benefit_at_income: BenefitAtIncome = {
    baseline: baselineAtIncome,
    reform: baselineAtIncome + ctcAtIncome,
    difference: ctcAtIncome,
    ctc_component: ctcAtIncome,
    exemption_tax_benefit: 0,
  };

  return {
    income_range: incomeRange,
    ctc_baseline_range: incomeRange.map(() => 0),
    ctc_reform_range: ctcRange,
    ctc_component: ctcRange,
    exemption_tax_benefit: incomeRange.map(() => 0),
    benefit_at_income,
    x_axis_max: HOUSEHOLD_SWEEP_MAX,
  };
}
