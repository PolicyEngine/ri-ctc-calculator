/**
 * React Query hook for aggregate impact calculations.
 *
 * Two sources, switched by ``presetId``:
 *   - ``presetId`` set  → fetch the precomputed JSON under
 *     ``/data/presets/{id}.json`` (no API call, instant).
 *   - ``presetId`` null → POST to the live Modal-hosted FastAPI endpoint
 *     for a custom reform.
 */

import { useQuery } from '@tanstack/react-query';
import { api, fetchPresetPayload } from '@/lib/api';
import type { PresetId } from '@/lib/presets';
import type { ReformParams } from '@/lib/types';

export function useAggregateImpact(
  reformParams: ReformParams,
  year: number = 2027,
  enabled: boolean = true,
  presetId: PresetId | null = null,
) {
  return useQuery({
    queryKey: presetId
      ? ['aggregate-impact', 'preset', presetId]
      : ['aggregate-impact', 'custom', reformParams, year],
    queryFn: async () => {
      if (presetId) {
        const payload = await fetchPresetPayload(presetId);
        return payload.aggregate;
      }
      return api.calculateAggregateImpact(reformParams, year);
    },
    enabled,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    retry: 1,
  });
}
