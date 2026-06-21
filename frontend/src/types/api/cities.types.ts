/**
 * src/types/api/cities.types.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Response contract for GET /cities.
 * Transcribed 1:1 from backend/schemas/cities_response.py
 * ─────────────────────────────────────────────────────────────────────────
 */

export interface CityItem {
  /** Canonical city name, exactly as it appears in sdsf_city_dashboard.csv. */
  city: string;
  /** URL-safe slug derived from the city name. */
  city_slug: string;
}

export interface CitiesResponse {
  /** Alphabetically sorted list of all 15 supported cities. */
  cities: CityItem[];
}
