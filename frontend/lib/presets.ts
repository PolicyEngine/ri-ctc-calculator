/**
 * Preset definitions for the RI CTC proposals.
 *
 * The two Governor's-proposal presets share every parameter except `ctc_amount`. The original
 * proposal sets the per-child credit at $325; the revised proposal raises it
 * to $650. The enacted law preset reflects 2026 R.I. H 7127 Substitute A
 * as amended.
 *
 * The precompute pipeline (`scripts/precompute_presets.py`) writes the
 * aggregate + per-example results for static presets into
 * `frontend/public/data/presets/{id}.json` — keep `EXAMPLE_PROFILES` and
 * `presetReformParams()` in sync with that script.
 */
import type { ReformParams } from './types';

export type PresetId = 'original' | 'revised' | 'enacted';
export type StaticPresetId = 'original' | 'revised';
export type LocalHouseholdPresetId = 'enacted';

export const PRESET_IDS: PresetId[] = ['original', 'revised', 'enacted'];

export interface ExampleProfile {
  id: string;
  label: string;
  age_head: number;
  age_spouse: number | null;
  married: boolean;
  dependent_ages: number[];
  income: number;
}

export const EXAMPLE_PROFILES: ExampleProfile[] = [
  {
    id: 'single-1kid-20k',
    label: 'Single filer, one child, $20k income',
    age_head: 30,
    age_spouse: null,
    married: false,
    dependent_ages: [5],
    income: 20000,
  },
  {
    id: 'single-2kid-50k',
    label: 'Single filer, two children, $50k income',
    age_head: 35,
    age_spouse: null,
    married: false,
    dependent_ages: [5, 8],
    income: 50000,
  },
  {
    id: 'married-2kid-150k',
    label: 'Married couple, two children, $150k income',
    age_head: 35,
    age_spouse: 35,
    married: true,
    dependent_ages: [5, 8],
    income: 150000,
  },
];

/** Effective tax year for the policy presets. */
export const PRESET_YEAR = 2027;

const EMPTY_THRESHOLDS = {
  SINGLE: 0,
  JOINT: 0,
  HEAD_OF_HOUSEHOLD: 0,
  SURVIVING_SPOUSE: 0,
  SEPARATE: 0,
};

export const ENACTED_CTC_PHASEOUT_THRESHOLDS = {
  SINGLE: 88500,
  JOINT: 110640,
  HEAD_OF_HOUSEHOLD: 88500,
  SURVIVING_SPOUSE: 88500,
  SEPARATE: 88500,
};

export const ENACTED_CTC_PHASEOUT_INCREMENTS = {
  SINGLE: 2875,
  JOINT: 3590,
  HEAD_OF_HOUSEHOLD: 2875,
  SURVIVING_SPOUSE: 2875,
  SEPARATE: 2875,
};

function baseReformParams(): Pick<
  ReformParams,
  | 'ctc_phaseout_rate'
  | 'ctc_phaseout_thresholds'
  | 'ctc_stepped_phaseout_thresholds'
  | 'ctc_stepped_phaseout_increments'
  | 'ctc_young_child_boost_amount'
  | 'ctc_young_child_boost_age_limit'
  | 'exemption_phaseout_rate'
  | 'exemption_phaseout_thresholds'
  | 'include_high_earner_tax'
  | 'high_earner_tax_threshold'
  | 'high_earner_tax_rates'
> {
  return {
    ctc_phaseout_rate: 0,
    ctc_phaseout_thresholds: { ...EMPTY_THRESHOLDS },
    ctc_stepped_phaseout_thresholds: null,
    ctc_stepped_phaseout_increments: null,
    ctc_young_child_boost_amount: 0,
    ctc_young_child_boost_age_limit: 6,
    exemption_phaseout_rate: 0,
    exemption_phaseout_thresholds: { ...EMPTY_THRESHOLDS },
    include_high_earner_tax: false,
    high_earner_tax_threshold: 0,
    high_earner_tax_rates: {},
  };
}

/** Reform parameters for a preset. */
export function presetReformParams(id: PresetId): ReformParams {
  if (id === 'enacted') {
    return {
      ...baseReformParams(),
      ctc_amount: 330,
      // The contrib CTC reform uses age < age_limit; 19 includes children
      // age 18 or under, matching the enacted statute.
      ctc_age_limit: 19,
      ctc_refundability_cap: 100000,
      ctc_stepped_phaseout: true,
      ctc_stepped_phaseout_threshold: ENACTED_CTC_PHASEOUT_THRESHOLDS.SINGLE,
      ctc_stepped_phaseout_increment: ENACTED_CTC_PHASEOUT_INCREMENTS.SINGLE,
      ctc_stepped_phaseout_rate_per_step: 0.2,
      ctc_stepped_phaseout_thresholds: {
        ...ENACTED_CTC_PHASEOUT_THRESHOLDS,
      },
      ctc_stepped_phaseout_increments: {
        ...ENACTED_CTC_PHASEOUT_INCREMENTS,
      },
      enable_exemption_reform: false,
      exemption_amount: 5200,
      exemption_age_limit_enabled: true,
      exemption_age_threshold: 19,
      include_high_earner_tax: true,
      high_earner_tax_threshold: 1000000,
      high_earner_tax_rates: {
        2027: 0.01,
        2028: 0.02,
        2029: 0.03,
      },
    };
  }

  const ctcAmount = id === 'revised' ? 650 : 325;
  return {
    ...baseReformParams(),
    ctc_amount: ctcAmount,
    ctc_age_limit: 19,
    ctc_refundability_cap: 100000,
    // Stepped phaseout: 20% reduction per $7,590 over $265,965 (2027 inflation-adjusted).
    ctc_stepped_phaseout: true,
    ctc_stepped_phaseout_threshold: 265965,
    ctc_stepped_phaseout_increment: 7590,
    ctc_stepped_phaseout_rate_per_step: 0.2,
    enable_exemption_reform: true,
    exemption_amount: 0,
    exemption_age_limit_enabled: true,
    exemption_age_threshold: 19,
  };
}

export interface PresetMeta {
  id: PresetId;
  label: string;
  shortLabel: string;
  description: string;
  ctcAmount: number;
  aggregateSource: 'precomputed' | 'api';
  householdSource: 'precomputed' | 'local';
}

export const PRESETS: Record<PresetId, PresetMeta> = {
  original: {
    id: 'original',
    label: "Governor's original proposal",
    shortLabel: 'Original',
    description:
      '$325 per child, fully refundable, ages 0–18, stepped phaseout (20% per $7,590 over $265,965), zeroes the dependent exemption for children.',
    ctcAmount: 325,
    aggregateSource: 'precomputed',
    householdSource: 'precomputed',
  },
  revised: {
    id: 'revised',
    label: "Governor's revised proposal",
    shortLabel: 'Revised',
    description:
      '$650 per child, fully refundable, ages 0–18, stepped phaseout (20% per $7,590 over $265,965), zeroes the dependent exemption for children.',
    ctcAmount: 650,
    aggregateSource: 'precomputed',
    householdSource: 'precomputed',
  },
  enacted: {
    id: 'enacted',
    label: 'Enacted 2027 law',
    shortLabel: 'Enacted',
    description:
      '$330 per child, fully refundable, ages 0-18, phaseout starts at $88,500 ($110,640 joint), the dependent exemption stays in place, and the high-income surtax phases in above $1M.',
    ctcAmount: 330,
    aggregateSource: 'api',
    householdSource: 'local',
  },
};

export function hasStaticPresetPayload(id: PresetId): id is StaticPresetId {
  return (
    PRESETS[id].aggregateSource === 'precomputed' &&
    PRESETS[id].householdSource === 'precomputed'
  );
}

export function hasLocalHouseholdCalculator(
  id: PresetId,
): id is LocalHouseholdPresetId {
  return PRESETS[id].householdSource === 'local';
}

/** Shape of `frontend/public/data/presets/{id}.json`. The aggregate +
 *  household-impact payloads are matched byte-for-byte to the backend's
 *  Pydantic response models so frontend types stay in sync. */
export interface PrecomputedExample {
  profile: ExampleProfile;
  household: import('./types').HouseholdImpactResponse;
}

export interface PresetPayload {
  preset_id: PresetId;
  year: number;
  reform_params: ReformParams;
  aggregate: import('./types').AggregateImpactResponse;
  examples: PrecomputedExample[];
}
