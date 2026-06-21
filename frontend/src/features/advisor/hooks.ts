/**
 * src/features/advisor/hooks.ts
 * ─────────────────────────────────────────────────────────────────────────
 * React Query mutation hook wrapping POST /advisor.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useMutation } from "@tanstack/react-query";
import { postAdvisor } from "@features/advisor/api";

export function useAdvisorMutation() {
  return useMutation({
    mutationFn: postAdvisor,
  });
}
