/**
 * src/features/cities/api.ts
 * ─────────────────────────────────────────────────────────────────────────
 * API function for GET /cities.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { apiClient } from "@lib/api/client";
import { ENDPOINTS } from "@lib/api/endpoints";
import type { CitiesResponse } from "@types/api/cities.types";

export function getCities(): Promise<CitiesResponse> {
  return apiClient.get<CitiesResponse>(ENDPOINTS.cities);
}
