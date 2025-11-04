/**
 * React Query hook for aggregate impact calculations.
 */

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { ReformParams } from '@/lib/types';

export function useAggregateImpact(reformParams: ReformParams, enabled: boolean = true) {
  return useQuery({
    queryKey: ['aggregate-impact', reformParams],
    queryFn: () => api.calculateAggregateImpact(reformParams),
    enabled,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    retry: 1,
  });
}
