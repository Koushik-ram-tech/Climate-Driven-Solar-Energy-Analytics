/**
 * src/features/readiness/api.ts
 * ─────────────────────────────────────────────────────────────────────────
 * API function for GET /readiness/{city}.
 * Accepts either a canonical city name or a URL slug — resolution happens
 * server-side in ReadinessService, so this function passes the raw value
 * through unchanged.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { apiClient } from "@lib/api/client";
import { ENDPOINTS } from "@lib/api/endpoints";
import type { ReadinessResponse } from "@types/api/readiness.types";

export function getReadiness(city: string): Promise<ReadinessResponse> {
  return apiClient.get<ReadinessResponse>(ENDPOINTS.readiness(city));
}
