/**
 * src/types/api/advisor.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Request/response contract for POST /advisor.
 * Transcribed 1:1 from:
 *   - backend/schemas/advisor_request.py
 *   - backend/schemas/advisor_response.py
 *
 * Bounds documented below (monthly_bill, roof_area_sqft, budget) mirror
 * the backend's Pydantic Field(ge=..., le=...) constraints exactly. These
 * exist client-side for UX only (immediate inline validation) — the
 * backend remains the final authority and the API layer must always
 * handle 400/422 responses regardless of client-side validation passing.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type {
  InvestmentRecommendation,
  PredictionConfidence,
  Suitability,
  SupportedCity,
} from "@app-types/shared.types";

export interface AdvisorRequest {
  /** Must be one of the 15 supported Indian cities. */
  city: SupportedCity;

  /** Average monthly electricity bill in ₹. Bounds: 500 – 100,000. */
  monthly_bill: number;

  /** Total flat roof area available, in sq ft. Bounds: 50 – 5,000. */
  roof_area_sqft: number;

  /** Maximum capital available in ₹. Bounds: 50,000 – 50,00,000. */
  budget: number;
}

export interface AdvisorResponse {
  /** City name, echoed from the request. */
  city: string;

  /** URL-safe slug for the city. */
  city_slug: string;

  /** Recommended solar system size in kW, snapped to nearest 0.5 kW. */
  system_size_kw: number;

  /** Estimated annual electricity generation in kWh. */
  annual_generation_kwh: number;

  /** Estimated Year-1 electricity savings in ₹. */
  annual_savings: number;

  /** Estimated payback period in years. */
  payback_years: number;

  /** Estimated cumulative electricity savings over 25 years in ₹. */
  lifetime_savings: number;

  /** Net financial benefit over 25 years in ₹ (lifetime_savings − net system cost). */
  net_benefit_inr: number;

  /** Investment recommendation from the rule-based engine. */
  investment_recommendation: InvestmentRecommendation;

  /** Plain-language investment rationale. Served verbatim — do not rewrite. */
  recommendation_explanation: string;

  /** Solar resource suitability classification, joined from SDSF. */
  suitability: Suitability;

  /** Composite solar resource reliability score, 0–100, joined from SDSF. */
  reliability_score: number;

  /** Model prediction confidence tier for this city, joined from SDSF. */
  prediction_confidence: PredictionConfidence;
}
