/**
 * API client for the RI CTC Calculator.
 *
 * Two paths:
 *
 *   - **Preset (original / revised)** — load the precomputed JSON shipped
 *     under ``frontend/public/data/presets/{id}.json``. No network call to
 *     a backend.
 *   - **Custom reform** — POST directly to ``api.policyengine.org``:
 *     ``/us/calculate`` for the household income-sweep chart, and
 *     ``/us/policy`` + ``/us/economy`` for the statewide impact.
 *
 * The FastAPI backend the calculator used to ship has been removed —
 * the public PolicyEngine API now handles every custom calculation.
 */

import {
  buildHouseholdSituation,
  HOUSEHOLD_SWEEP_MAX,
  HOUSEHOLD_SWEEP_POINTS,
} from './buildHousehold';
import {
  buildExemptionOnlyReform,
  buildReform,
  type ReformOverrides,
} from './buildReform';
import type {
  AggregateImpactResponse,
  BenefitAtIncome,
  HealthResponse,
  HouseholdImpactResponse,
  HouseholdRequest,
  IncomeBracket,
  ReformParams,
} from './types';
import type { PresetPayload, StaticPresetId } from './presets';

const PE_API_URL = 'https://api.policyengine.org';

/** Baseline policy id in PolicyEngine's data store (no reform). */
const BASELINE_POLICY_ID = 2;

const FETCH_TIMEOUT = 180_000;

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

// ---------------------------------------------------------------------------
// basePath-aware preset fetching
// ---------------------------------------------------------------------------

const FALLBACK_BASE_PATH = '/us/rhode-island-ctc-calculator';

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

// ---------------------------------------------------------------------------
// Shared fetch helper
// ---------------------------------------------------------------------------

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout = FETCH_TIMEOUT,
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, {
      ...options,
      signal: options.signal ?? controller.signal,
    });
  } finally {
    clearTimeout(id);
  }
}

// ---------------------------------------------------------------------------
// /us/calculate — household-level income sweep
// ---------------------------------------------------------------------------

interface PECalculateResponse {
  status: string;
  message: string | null;
  result: {
    people: Record<string, Record<string, Record<string, number[]>>>;
    tax_units: Record<string, Record<string, Record<string, number[]>>>;
    households: Record<string, Record<string, Record<string, number[]>>>;
  };
}

async function peCalculate(
  household: ReturnType<typeof buildHouseholdSituation>,
  policy?: ReformOverrides,
): Promise<PECalculateResponse> {
  const body = policy ? { household, policy } : { household };
  const response = await fetchWithTimeout(`${PE_API_URL}/us/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const errBody = await response.json().catch(() => null);
    throw new ApiError(
      `PolicyEngine /us/calculate ${response.status}: ${JSON.stringify(errBody)}`,
      response.status,
      errBody,
    );
  }
  return response.json();
}

function interpolate(xs: number[], ys: number[], x: number): number {
  if (xs.length === 0) return 0;
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  for (let i = 1; i < xs.length; i++) {
    if (xs[i] >= x) {
      const frac = (x - xs[i - 1]) / (xs[i] - xs[i - 1] || 1);
      return ys[i - 1] + frac * (ys[i] - ys[i - 1]);
    }
  }
  return ys[ys.length - 1];
}

// ---------------------------------------------------------------------------
// /us/policy — mint a numeric policy_id for the /us/economy path
// ---------------------------------------------------------------------------

interface PEPolicyResponse {
  status?: string;
  result?: { policy_id?: number };
  policy_id?: number;
}

async function createPolicy(reform: ReformOverrides): Promise<number> {
  const response = await fetchWithTimeout(`${PE_API_URL}/us/policy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: reform }),
  });
  if (!response.ok) {
    const errBody = await response.json().catch(() => null);
    throw new ApiError(
      `PolicyEngine /us/policy ${response.status}: ${JSON.stringify(errBody)}`,
      response.status,
      errBody,
    );
  }
  const body = (await response.json()) as PEPolicyResponse;
  const policyId = body.result?.policy_id ?? body.policy_id;
  if (typeof policyId !== 'number') {
    throw new ApiError(
      `PolicyEngine /us/policy returned no policy_id: ${JSON.stringify(body)}`,
    );
  }
  return policyId;
}

// ---------------------------------------------------------------------------
// /us/economy — statewide impact (RI region)
// ---------------------------------------------------------------------------

interface PEEconomyResult {
  budget?: {
    budgetary_impact?: number;
    households?: number;
    baseline_net_income?: number;
  };
  decile?: Record<string, unknown>;
  intra_decile?: {
    all?: Record<string, number>;
    deciles?: Record<string, number[]>;
  };
  poverty?: {
    poverty?: {
      all?: { baseline: number; reform: number };
      child?: { baseline: number; reform: number };
    };
    deep_poverty?: {
      all?: { baseline: number; reform: number };
      child?: { baseline: number; reform: number };
    };
  };
  by_income_bracket?: Array<{
    bracket: string;
    beneficiaries: number;
    total_cost: number;
    avg_benefit: number;
  }>;
}

interface PEEconomyResponse {
  status: string; // 'ok' | 'computing' | 'error'
  message?: string | null;
  result?: PEEconomyResult | null;
}

async function pollEconomicImpact(
  policyId: number,
  year: number,
  signal?: AbortSignal,
): Promise<PEEconomyResult> {
  const url = `${PE_API_URL}/us/economy/${policyId}/over/${BASELINE_POLICY_ID}?region=ri&time_period=${year}`;
  const pollMs = 5000;
  while (true) {
    if (signal?.aborted) throw new Error('Aborted');
    const response = await fetchWithTimeout(url, { method: 'GET' }, FETCH_TIMEOUT);
    if (!response.ok) {
      const errBody = await response.json().catch(() => null);
      throw new ApiError(
        `PolicyEngine /us/economy ${response.status}: ${JSON.stringify(errBody)}`,
        response.status,
        errBody,
      );
    }
    const body = (await response.json()) as PEEconomyResponse;
    if (body.status === 'ok') {
      if (!body.result) {
        throw new ApiError(`/us/economy ok but no result: ${JSON.stringify(body)}`);
      }
      return body.result;
    }
    if (body.status === 'error') {
      throw new ApiError(`/us/economy error: ${body.message ?? 'unknown'}`);
    }
    // status === 'computing' — wait then retry.
    await new Promise<void>((resolve, reject) => {
      const t = setTimeout(() => resolve(), pollMs);
      if (signal) {
        signal.addEventListener(
          'abort',
          () => {
            clearTimeout(t);
            reject(new Error('Aborted'));
          },
          { once: true },
        );
      }
    });
  }
}

// ---------------------------------------------------------------------------
// Adapters — translate PE API responses into the existing dashboard shapes
// ---------------------------------------------------------------------------

const INTRA_KEY_MAP: Record<string, string> = {
  'Gain more than 5%': 'gain_more_than_5pct',
  'Gain less than 5%': 'gain_less_than_5pct',
  'No change': 'no_change',
  'Lose less than 5%': 'lose_less_than_5pct',
  'Lose more than 5%': 'lose_more_than_5pct',
};

function adaptEconomyToAggregate(
  result: PEEconomyResult,
): AggregateImpactResponse {
  const totalHouseholds = result.budget?.households ?? 0;
  // PE budgetary_impact is signed from the government's perspective —
  // negative means the reform costs money. Flip for the dashboard's
  // total_cost (positive = cost to RI).
  const budgetaryImpact = result.budget?.budgetary_impact ?? 0;
  const totalCost = -budgetaryImpact;

  // Winners / losers from intra_decile.all bucket shares.
  const intraAll = result.intra_decile?.all ?? {};
  const getShare = (snake: string): number => {
    if (snake in intraAll) return intraAll[snake] ?? 0;
    for (const [display, s] of Object.entries(INTRA_KEY_MAP)) {
      if (s === snake && display in intraAll) return intraAll[display] ?? 0;
    }
    return 0;
  };
  const gainShare =
    getShare('gain_more_than_5pct') + getShare('gain_less_than_5pct');
  const lossShare =
    getShare('lose_more_than_5pct') + getShare('lose_less_than_5pct');
  const winners = gainShare * totalHouseholds;
  const losers = lossShare * totalHouseholds;
  const winnersRate = gainShare * 100;
  const losersRate = lossShare * 100;

  const beneficiaries = winners;
  const avgBenefit = beneficiaries > 0 ? totalCost / beneficiaries : 0;

  const povAll = result.poverty?.poverty?.all;
  const povChild = result.poverty?.poverty?.child;
  const dpAll = result.poverty?.deep_poverty?.all;
  const dpChild = result.poverty?.deep_poverty?.child;
  const pct = (rate: number | undefined): number => (rate ?? 0) * 100;
  const ppChange = (b?: number, r?: number): number => pct(r) - pct(b);
  const pctChange = (b?: number, r?: number): number => {
    if (!b) return 0;
    return ((r! - b) / b) * 100;
  };

  const byBracket: IncomeBracket[] = result.by_income_bracket ?? [];

  return {
    total_cost: totalCost,
    beneficiaries,
    avg_benefit: avgBenefit,
    children_affected: 0,
    winners,
    losers,
    winners_rate: winnersRate,
    losers_rate: losersRate,
    poverty_baseline_rate: pct(povAll?.baseline),
    poverty_reform_rate: pct(povAll?.reform),
    poverty_rate_change: ppChange(povAll?.baseline, povAll?.reform),
    poverty_percent_change: pctChange(povAll?.baseline, povAll?.reform),
    child_poverty_baseline_rate: pct(povChild?.baseline),
    child_poverty_reform_rate: pct(povChild?.reform),
    child_poverty_rate_change: ppChange(povChild?.baseline, povChild?.reform),
    child_poverty_percent_change: pctChange(povChild?.baseline, povChild?.reform),
    deep_poverty_baseline_rate: pct(dpAll?.baseline),
    deep_poverty_reform_rate: pct(dpAll?.reform),
    deep_poverty_rate_change: ppChange(dpAll?.baseline, dpAll?.reform),
    deep_poverty_percent_change: pctChange(dpAll?.baseline, dpAll?.reform),
    deep_child_poverty_baseline_rate: pct(dpChild?.baseline),
    deep_child_poverty_reform_rate: pct(dpChild?.reform),
    deep_child_poverty_rate_change: ppChange(dpChild?.baseline, dpChild?.reform),
    deep_child_poverty_percent_change: pctChange(
      dpChild?.baseline,
      dpChild?.reform,
    ),
    by_income_bracket: byBracket,
  };
}

// ---------------------------------------------------------------------------
// Public api object
// ---------------------------------------------------------------------------

export const api = {
  /**
   * Calculate household impact via two parallel /us/calculate runs
   * (baseline + reform). Returns the income-sweep vectors + the
   * interpolated benefit at the user's AGI, packaged into the existing
   * HouseholdImpactResponse shape.
   */
  async calculateHouseholdImpact(
    request: HouseholdRequest,
  ): Promise<HouseholdImpactResponse> {
    const household = buildHouseholdSituation(request);
    const reform = buildReform(request.reform_params, request.year);
    const yearStr = String(request.year);

    const [baselineRes, reformRes] = await Promise.all([
      peCalculate(household),
      peCalculate(household, reform),
    ]);

    // PolicyEngine /us/calculate runs the axis sweep but echoes the
    // swept INPUT variable back at its original scalar (only the output
    // variables come back as N-point vectors). Synthesize the income
    // range from the axis spec instead.
    const incomeRange: number[] = Array.from(
      { length: HOUSEHOLD_SWEEP_POINTS },
      (_, i) =>
        (HOUSEHOLD_SWEEP_MAX * i) / (HOUSEHOLD_SWEEP_POINTS - 1),
    );
    const baselineNet =
      baselineRes.result.households['your household']['household_net_income'][
        yearStr
      ];
    const reformNet =
      reformRes.result.households['your household']['household_net_income'][
        yearStr
      ];

    const netDelta = reformNet.map((v, i) => v - baselineNet[i]);

    // If the exemption sub-reform is enabled, isolate its contribution
    // with a CTC=0 sim so the chart can stack CTC vs exemption.
    let ctcComponent = netDelta.slice();
    let exemptionBenefit = netDelta.map(() => 0);
    if (request.reform_params.enable_exemption_reform) {
      const exemptionReform = buildExemptionOnlyReform(
        request.reform_params,
        request.year,
      );
      const exemptionOnlyRes = await peCalculate(household, exemptionReform);
      const exemptionOnlyNet =
        exemptionOnlyRes.result.households['your household'][
          'household_net_income'
        ][yearStr];
      exemptionBenefit = exemptionOnlyNet.map((v, i) => v - baselineNet[i]);
      ctcComponent = netDelta.map((v, i) => v - exemptionBenefit[i]);
    }

    const baselineAtIncome = interpolate(incomeRange, baselineNet, request.income);
    const reformAtIncome = interpolate(incomeRange, reformNet, request.income);
    const ctcAtIncome = interpolate(incomeRange, ctcComponent, request.income);
    const exemptionAtIncome = interpolate(
      incomeRange,
      exemptionBenefit,
      request.income,
    );

    const benefit_at_income: BenefitAtIncome = {
      baseline: baselineAtIncome,
      reform: reformAtIncome,
      difference: reformAtIncome - baselineAtIncome,
      ctc_component: ctcAtIncome,
      exemption_tax_benefit: exemptionAtIncome,
    };

    return {
      income_range: incomeRange,
      ctc_baseline_range: incomeRange.map(() => 0),
      ctc_reform_range: netDelta,
      ctc_component: ctcComponent,
      exemption_tax_benefit: exemptionBenefit,
      benefit_at_income,
      x_axis_max: HOUSEHOLD_SWEEP_MAX,
    };
  },

  /**
   * Calculate statewide aggregate impact by minting a /us/policy id and
   * polling /us/economy?region=ri for the year. Adapts the response into
   * the existing AggregateImpactResponse shape so chart components don't
   * need to know whether they got precomputed JSON or live data.
   */
  async calculateAggregateImpact(
    reformParams: ReformParams,
    year: number,
    signal?: AbortSignal,
  ): Promise<AggregateImpactResponse> {
    const reform = buildReform(reformParams, year);
    const policyId = await createPolicy(reform);
    const result = await pollEconomicImpact(policyId, year, signal);
    return adaptEconomyToAggregate(result);
  },

  /** Health check — verifies api.policyengine.org is reachable. */
  async health(): Promise<HealthResponse> {
    const response = await fetchWithTimeout(`${PE_API_URL}/`, { method: 'GET' });
    return {
      status: response.ok ? 'ok' : 'error',
      dataset_loaded: response.ok,
      version: 'public-api',
    };
  },
};

export { HOUSEHOLD_SWEEP_MAX, HOUSEHOLD_SWEEP_POINTS };
