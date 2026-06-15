/**
 * React Query hook for household impact calculations.
 *
 * When ``presetId`` is set AND the request matches one of the three
 * preloaded example profiles, the hook returns the precomputed
 * household impact from the static preset JSON. Otherwise it falls
 * through to the live Modal endpoint so custom households still work.
 */

import { useQuery } from '@tanstack/react-query';
import { api, fetchPresetPayload } from '@/lib/api';
import {
  EXAMPLE_PROFILES,
  hasStaticPresetPayload,
  type PresetId,
} from '@/lib/presets';
import { calculateEnactedBudgetHouseholdImpact } from '@/lib/enactedBudget';
import type { HouseholdRequest, HouseholdImpactResponse } from '@/lib/types';

function matchingExampleId(request: HouseholdRequest): string | null {
  for (const profile of EXAMPLE_PROFILES) {
    const sameDeps =
      profile.dependent_ages.length === request.dependent_ages.length &&
      profile.dependent_ages.every((a, i) => a === request.dependent_ages[i]);
    if (
      profile.age_head === request.age_head &&
      (profile.married ? request.age_spouse !== null : request.age_spouse === null) &&
      sameDeps &&
      profile.income === request.income
    ) {
      return profile.id;
    }
  }
  return null;
}

export function useHouseholdImpact(
  request: HouseholdRequest,
  enabled: boolean = true,
  presetId: PresetId | null = null,
) {
  const exampleId =
    presetId && hasStaticPresetPayload(presetId)
      ? matchingExampleId(request)
      : null;
  return useQuery<HouseholdImpactResponse>({
    queryKey: presetId === 'enacted'
      ? ['household-impact', 'preset', presetId, request]
      : exampleId
      ? ['household-impact', 'preset', presetId, exampleId]
      : ['household-impact', 'custom', request],
    queryFn: async () => {
      if (presetId === 'enacted') {
        return calculateEnactedBudgetHouseholdImpact(request);
      }
      if (presetId && hasStaticPresetPayload(presetId) && exampleId) {
        const payload = await fetchPresetPayload(presetId);
        const match = payload.examples.find((e) => e.profile.id === exampleId);
        if (match) return match.household;
        // Fallthrough: profile no longer matches; hit live API.
      }
      return api.calculateHouseholdImpact(request);
    },
    enabled,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 1,
  });
}
