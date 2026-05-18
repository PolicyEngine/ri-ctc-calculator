/**
 * Build a PolicyEngine parameter-overrides dict for the custom-reform
 * path. TypeScript port of ``ri_ctc_calc.calculations.reforms.create_custom_reform``.
 *
 * Only the parameters that differ from baseline are emitted. The
 * resulting dict is sent as the ``policy`` field of ``POST /us/calculate``
 * or used to mint a policy via ``POST /us/policy``.
 */
import type { ReformParams } from './types';

type Primitive = number | boolean | string;
type Periodised<T extends Primitive = Primitive> = Record<string, T>;
export type ReformOverrides = Record<string, Periodised>;

const FILING_STATUSES = [
  'SINGLE',
  'JOINT',
  'HEAD_OF_HOUSEHOLD',
  'SURVIVING_SPOUSE',
  'SEPARATE',
] as const;

export function buildReform(params: ReformParams, year: number): ReformOverrides {
  const dateRange = `${year}-01-01.2100-12-31`;
  const set = <T extends Primitive>(value: T): Periodised<T> => ({
    [dateRange]: value,
  });

  const reform: ReformOverrides = {
    'gov.contrib.states.ri.ctc.in_effect': set(true),
    'gov.contrib.states.ri.ctc.amount': set(params.ctc_amount),
    'gov.contrib.states.ri.ctc.age_limit': set(params.ctc_age_limit),
    'gov.contrib.states.ri.ctc.refundability.cap': set(params.ctc_refundability_cap),
    'gov.contrib.states.ri.ctc.young_child_boost.amount': set(
      params.ctc_young_child_boost_amount,
    ),
    'gov.contrib.states.ri.ctc.young_child_boost.age_limit': set(
      params.ctc_young_child_boost_age_limit,
    ),
  };

  // Stepped phaseout (Governor's-proposal style) takes precedence over
  // the rate-based phaseout when both are configured.
  if (
    params.ctc_stepped_phaseout &&
    params.ctc_stepped_phaseout_increment > 0
  ) {
    reform['gov.contrib.states.ri.ctc.stepped_phaseout.threshold'] = set(
      params.ctc_stepped_phaseout_threshold,
    );
    reform['gov.contrib.states.ri.ctc.stepped_phaseout.increment'] = set(
      params.ctc_stepped_phaseout_increment,
    );
    reform['gov.contrib.states.ri.ctc.stepped_phaseout.rate_per_step'] = set(
      params.ctc_stepped_phaseout_rate_per_step,
    );
  } else if (
    params.ctc_phaseout_rate > 0 ||
    FILING_STATUSES.some((s) => params.ctc_phaseout_thresholds[s] > 0)
  ) {
    reform['gov.contrib.states.ri.ctc.phaseout.rate'] = set(params.ctc_phaseout_rate);
    for (const status of FILING_STATUSES) {
      reform[`gov.contrib.states.ri.ctc.phaseout.threshold.${status}`] = set(
        params.ctc_phaseout_thresholds[status],
      );
    }
  }

  // Dependent-exemption sub-reform.
  if (params.enable_exemption_reform) {
    reform['gov.contrib.states.ri.dependent_exemption.in_effect'] = set(true);
    reform['gov.contrib.states.ri.dependent_exemption.amount'] = set(
      params.exemption_amount,
    );
    reform['gov.contrib.states.ri.dependent_exemption.age_limit.in_effect'] = set(
      params.exemption_age_limit_enabled,
    );
    reform['gov.contrib.states.ri.dependent_exemption.age_limit.threshold'] = set(
      params.exemption_age_threshold,
    );
    reform['gov.contrib.states.ri.dependent_exemption.phaseout.rate'] = set(
      params.exemption_phaseout_rate,
    );
    for (const status of FILING_STATUSES) {
      reform[
        `gov.contrib.states.ri.dependent_exemption.phaseout.threshold.${status}`
      ] = set(params.exemption_phaseout_thresholds[status]);
    }
  }

  return reform;
}

/**
 * Same as ``buildReform`` but with CTC amount forced to zero — useful
 * for isolating the dependent-exemption component of a reform.
 */
export function buildExemptionOnlyReform(
  params: ReformParams,
  year: number,
): ReformOverrides {
  return buildReform({ ...params, ctc_amount: 0 }, year);
}
