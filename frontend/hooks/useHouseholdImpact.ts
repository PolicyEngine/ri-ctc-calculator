/**
 * React Query hook for household impact calculations.
 *
 * Presets can source household impacts from precomputed JSON or a local
 * law-specific calculator. Other requests fall through to the pinned
 * Modal backend so custom households still work.
 */

import { useQuery } from '@tanstack/react-query';
import { api, fetchPresetPayload } from '@/lib/api';
import {
  EXAMPLE_PROFILES,
  hasLocalHouseholdCalculator,
  hasStaticPresetPayload,
  type PresetId,
} from '@/lib/presets';
import { calculateEnactedLawHouseholdImpact } from '@/lib/enactedLaw';
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
  const usesLocalHouseholdCalculator =
    presetId !== null && hasLocalHouseholdCalculator(presetId);
  const exampleId =
    presetId && hasStaticPresetPayload(presetId)
      ? matchingExampleId(request)
      : null;
  return useQuery<HouseholdImpactResponse>({
    queryKey: usesLocalHouseholdCalculator
      ? ['household-impact', 'preset', presetId, request]
      : exampleId
      ? ['household-impact', 'preset', presetId, exampleId]
      : ['household-impact', 'custom', request],
    queryFn: async () => {
      if (usesLocalHouseholdCalculator) {
        return calculateEnactedLawHouseholdImpact(request);
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
