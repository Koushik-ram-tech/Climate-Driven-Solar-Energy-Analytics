/**
 * src/types/api/health.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Response contract for GET /health.
 * Transcribed 1:1 from backend/schemas/health_response.py
 * ─────────────────────────────────────────────────────────────────────────
 */

export interface HealthResponse {
  status: "healthy";
}
