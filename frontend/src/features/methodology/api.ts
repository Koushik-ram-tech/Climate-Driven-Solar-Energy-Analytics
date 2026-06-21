/**
 * src/features/methodology/api.ts
 * ─────────────────────────────────────────────────────────────────────────
 * API function for GET /methodology.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { apiClient } from "@lib/api/client";
import { ENDPOINTS } from "@lib/api/endpoints";
import type { MethodologyResponse } from "@app-types/api/methodology.types";

export function getMethodology(): Promise<MethodologyResponse> {
  return apiClient.get<MethodologyResponse>(ENDPOINTS.methodology);
}
