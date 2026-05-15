/**
 * Preset definitions for the Governor's CTC proposals.
 *
 * Both presets share every parameter except `ctc_amount`. The original
 * proposal sets the per-child credit at $325; the revised proposal raises it
 * to $650.
 *
 * The precompute pipeline (`scripts/precompute_presets.py`) writes the
 * aggregate + per-example results for each preset into
 * `frontend/public/data/presets/{id}.json` — keep `EXAMPLE_PROFILES` and
 * `presetReformParams()` in sync with that script.
 */
import type { ReformParams } from './types';

export type PresetId = 'original' | 'revised';

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
    id: 'married-2kid-100k',
    label: 'Married couple, two children, $100k income',
    age_head: 35,
    age_spouse: 35,
    married: true,
    dependent_ages: [5, 8],
    income: 100000,
  },
];

/** Effective tax year for both proposals. */
export const PRESET_YEAR = 2027;

/** Reform parameters for a preset. The revised proposal differs only in
 *  `ctc_amount` ($650 vs $325); everything else is identical to the
 *  original Governor's proposal. */
export function presetReformParams(id: PresetId): ReformParams {
  const ctcAmount = id === 'revised' ? 650 : 325;
  return {
    ctc_amount: ctcAmount,
    ctc_age_limit: 19,
    ctc_refundability_cap: 100000,
    ctc_phaseout_rate: 0,
    ctc_phaseout_thresholds: {
      SINGLE: 0,
      JOINT: 0,
      HEAD_OF_HOUSEHOLD: 0,
      SURVIVING_SPOUSE: 0,
      SEPARATE: 0,
    },
    // Stepped phaseout: 20% reduction per $7,590 over $265,965 (2027 inflation-adjusted).
    ctc_stepped_phaseout: true,
    ctc_stepped_phaseout_threshold: 265965,
    ctc_stepped_phaseout_increment: 7590,
    ctc_stepped_phaseout_rate_per_step: 0.2,
    ctc_young_child_boost_amount: 0,
    ctc_young_child_boost_age_limit: 6,
    enable_exemption_reform: true,
    exemption_amount: 0,
    exemption_age_limit_enabled: true,
    exemption_age_threshold: 19,
    exemption_phaseout_rate: 0,
    exemption_phaseout_thresholds: {
      SINGLE: 0,
      JOINT: 0,
      HEAD_OF_HOUSEHOLD: 0,
      SURVIVING_SPOUSE: 0,
      SEPARATE: 0,
    },
  };
}

export interface PresetMeta {
  id: PresetId;
  label: string;
  shortLabel: string;
  description: string;
  ctcAmount: number;
}

export const PRESETS: Record<PresetId, PresetMeta> = {
  original: {
    id: 'original',
    label: "Governor's original proposal",
    shortLabel: 'Original',
    description:
      '$325 per child, fully refundable, ages 0–18, stepped phaseout (20% per $7,590 over $265,965), zeroes the dependent exemption for children.',
    ctcAmount: 325,
  },
  revised: {
    id: 'revised',
    label: "Governor's revised proposal",
    shortLabel: 'Revised',
    description:
      '$650 per child, fully refundable, ages 0–18, stepped phaseout (20% per $7,590 over $265,965), zeroes the dependent exemption for children.',
    ctcAmount: 650,
  },
};

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
