/**
 * src/features/advisor/api.ts
 * ─────────────────────────────────────────────────────────────────────────
 * API function for POST /advisor.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { apiClient } from "@lib/api/client";
import { ENDPOINTS } from "@lib/api/endpoints";
import type { AdvisorRequest, AdvisorResponse } from "@types/api/advisor.types";

export function postAdvisor(payload: AdvisorRequest): Promise<AdvisorResponse> {
  return apiClient.post<AdvisorResponse>(ENDPOINTS.advisor, payload);
}
