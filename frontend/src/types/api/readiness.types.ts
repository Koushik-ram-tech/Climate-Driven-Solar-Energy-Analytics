/**
 * src/types/api/readiness.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Response contract for GET /readiness/{city}.
 * Transcribed 1:1 from backend/schemas/readiness_response.py
 *
 * Every field maps directly to a column in sdsf_city_dashboard.csv or to
 * a deterministic derivation of one (city_slug). All fields are frozen
 * research outputs — never recomputed by the backend, and never
 * recomputed or re-derived on the frontend either.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { PredictionConfidence, RSCategory, Suitability } from "@app-types/shared.types";

export interface ReadinessResponse {
  /** City name, exactly as it appears in sdsf_city_dashboard.csv. */
  city: string;

  /** URL-safe slug derived from the city name. */
  city_slug: string;

  /** Annual mean predicted GHI in kWh/m²/day. */
  mean_ghi: number;

  /** 10th-percentile predicted GHI in kWh/m²/day (conservative scenario). */
  p10_ghi: number;

  /** Median predicted GHI in kWh/m²/day (base-case scenario). */
  p50_ghi: number;

  /** 90th-percentile predicted GHI in kWh/m²/day (optimistic scenario). */
  p90_ghi: number;

  /** Composite solar resource reliability score, 0–100. */
  reliability_score: number;

  /** Reliability Score category label. */
  rs_category: RSCategory;

  /** City-level XGBoost model Root Mean Squared Error (kWh/m²/day). */
  model_rmse: number;

  /** City-level XGBoost model Mean Absolute Percentage Error (%). */
  model_mape: number;

  /** Model prediction confidence tier for this city. */
  prediction_confidence: PredictionConfidence;

  /** Solar resource suitability classification. Emoji prefix stripped by backend. */
  suitability: Suitability;

  /** Plain-language suitability rationale. Served verbatim — do not rewrite. */
  explanation: string;
}
