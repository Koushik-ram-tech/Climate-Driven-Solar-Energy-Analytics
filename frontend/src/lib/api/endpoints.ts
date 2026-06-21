/**
 * src/lib/api/endpoints.ts
 * ─────────────────────────────────────────────────────────────────────────
 * String constants for the 5 backend routes. Exactly the 5 endpoints
 * defined in backend/main.py — no invented endpoints.
 * ─────────────────────────────────────────────────────────────────────────
 */

export const ENDPOINTS = {
  health: "/health",
  cities: "/cities",
  readiness: (city: string) => `/readiness/${city}`,
  advisor: "/advisor",
  methodology: "/methodology",
} as const;
