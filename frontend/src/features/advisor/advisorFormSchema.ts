/**
 * src/features/advisor/advisorFormSchema.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Zod schema mirroring backend/schemas/advisor_request.py bounds exactly:
 *
 *   city:           one of the 15 SupportedCity values
 *   monthly_bill:   500.0 – 100,000.0   (₹)
 *   roof_area_sqft: 50.0 – 5,000.0      (sq ft)
 *   budget:         50,000.0 – 50,00,000.0 (₹)
 *
 * This schema exists for immediate client-side UX feedback only. It does
 * NOT replace backend validation — postAdvisor() callers must still
 * handle 400/422 ApiError responses regardless of this schema passing.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { z } from "zod";
import { SUPPORTED_CITIES } from "@app-types/shared.types";

export const advisorFormSchema = z.object({
  city: z.enum(SUPPORTED_CITIES as [string, ...string[]]),
  monthly_bill: z.number().min(500).max(100_000),
  roof_area_sqft: z.number().min(50).max(5_000),
  budget: z.number().min(50_000).max(50_00_000),
});

export type AdvisorFormValues = z.infer<typeof advisorFormSchema>;
