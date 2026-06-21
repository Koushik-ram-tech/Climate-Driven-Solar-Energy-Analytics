/**
 * src/types/shared.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Literal types shared across multiple backend response contracts.
 *
 * Transcribed 1:1 from:
 *   - backend/schemas/readiness_response.py  (Suitability, RSCategory,
 *     PredictionConfidence)
 *   - backend/schemas/advisor_response.py    (InvestmentRecommendation)
 *   - backend/schemas/advisor_request.py     (SupportedCity)
 *
 * Do NOT add values here that the backend does not currently emit.
 * Reserved-but-unused future values (documented in backend comments) are
 * intentionally excluded until the backend actually ships them — adding
 * them speculatively would let the frontend silently accept a value the
 * API contract does not guarantee.
 * ─────────────────────────────────────────────────────────────────────────
 */

// Source: readiness_response.py → Suitability
// NOTE: "Less Suitable" is reserved in backend comments but NOT currently
// emitted by the 15-city dataset. Do not add until the backend ships it.
export type Suitability =
  | "Highly Suitable"
  | "Suitable"
  | "Moderately Suitable";

// Source: readiness_response.py → RSCategory
export type RSCategory = "Consistent Producer" | "Seasonal Producer";

// Source: readiness_response.py → PredictionConfidence
export type PredictionConfidence = "High" | "Medium" | "Low";

// Source: advisor_response.py → InvestmentRecommendation
export type InvestmentRecommendation =
  | "Highly Recommended"
  | "Recommended"
  | "Consider Carefully"
  | "Not Recommended";

// Source: advisor_request.py → SupportedCity
// Frozen: do not edit without a corresponding backend CSV update.
export type SupportedCity =
  | "Ahmedabad"
  | "Bengaluru"
  | "Bhopal"
  | "Bhubaneswar"
  | "Chandigarh"
  | "Chennai"
  | "Delhi"
  | "Guwahati"
  | "Hyderabad"
  | "Jaipur"
  | "Kochi"
  | "Kolkata"
  | "Mangalore"
  | "Mumbai"
  | "Pune";

export const SUPPORTED_CITIES: SupportedCity[] = [
  "Ahmedabad",
  "Bengaluru",
  "Bhopal",
  "Bhubaneswar",
  "Chandigarh",
  "Chennai",
  "Delhi",
  "Guwahati",
  "Hyderabad",
  "Jaipur",
  "Kochi",
  "Kolkata",
  "Mangalore",
  "Mumbai",
  "Pune",
];
