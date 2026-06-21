/**
 * src/types/api/methodology.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Response contract for GET /methodology.
 * Transcribed 1:1 from backend/schemas/methodology_response.py
 *
 * Deliberately minimal — research statistics (R², RMSE, city count, date
 * range) are static frontend copy concerns per the backend's own docs,
 * not served through this API. Do not add fields here speculatively.
 * ─────────────────────────────────────────────────────────────────────────
 */

export interface MethodologyResponse {
  /** Project title. */
  title: string;

  /** One-sentence description of the product and its methodology. */
  description: string;

  /** Framework version string. */
  version: string;
}
