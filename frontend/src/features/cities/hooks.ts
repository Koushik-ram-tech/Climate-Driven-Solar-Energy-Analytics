/**
 * src/features/cities/hooks.ts
 * ─────────────────────────────────────────────────────────────────────────
 * React Query hook wrapping GET /cities.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useQuery } from "@tanstack/react-query";
import { getCities } from "@features/cities/api";

export function useCities() {
  return useQuery({
    queryKey: ["cities"],
    queryFn: getCities,
  });
}
