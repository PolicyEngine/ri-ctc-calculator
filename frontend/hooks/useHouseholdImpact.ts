/**
 * React Query hook for household impact calculations.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '@/apiLib/api';
import type { HouseholdRequest } from '@/apiLib/types';

export function useHouseholdImpact(request: HouseholdRequest, enabled: boolean = true) {
  return useQuery({
    queryKey: ['household-impact', request],
    queryFn: () => api.calculateHouseholdImpact(request),
    enabled,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    retry: 1,
  });
}
