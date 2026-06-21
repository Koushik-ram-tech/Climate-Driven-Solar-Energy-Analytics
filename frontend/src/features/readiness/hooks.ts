/**
 * src/features/readiness/hooks.ts
 * ─────────────────────────────────────────────────────────────────────────
 * React Query hook wrapping GET /readiness/{city}.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useQuery } from "@tanstack/react-query";
import { getReadiness } from "@features/readiness/api";

export function useReadiness(city: string | undefined) {
  return useQuery({
    queryKey: ["readiness", city],
    queryFn: () => getReadiness(city as string),
    enabled: Boolean(city),
  });
}
