/**
 * src/features/methodology/hooks.ts
 * ─────────────────────────────────────────────────────────────────────────
 * React Query hook wrapping GET /methodology.
 *
 * staleTime: Infinity — this endpoint returns a frozen, project-level
 * constant per the backend's own docs ("constructed once at server
 * startup"), so it never needs revalidation within a session.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useQuery } from "@tanstack/react-query";
import { getMethodology } from "@features/methodology/api";

export function useMethodology() {
  return useQuery({
    queryKey: ["methodology"],
    queryFn: getMethodology,
    staleTime: Infinity,
  });
}
