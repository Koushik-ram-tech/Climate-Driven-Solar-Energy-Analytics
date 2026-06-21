/**
 * src/pages/results/sections/Recommendation.tsx
 */

import type { AdvisorResponse } from "@app-types/api/advisor.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, Body } from "@components/ui/Text";
import { RecommendationBadge } from "@components/data-display/RecommendationBadge";

export interface RecommendationProps {
  result: Pick<AdvisorResponse, "investment_recommendation" | "recommendation_explanation" | "city">;
}

export function Recommendation({ result }: RecommendationProps) {
  return (
    <Section spacing="compact">
      <div className="flex flex-col gap-5">
        <Eyebrow>{result.city} — Solar Assessment</Eyebrow>
        <RecommendationBadge recommendation={result.investment_recommendation} />
        <Body className="max-w-2xl text-ink-500">{result.recommendation_explanation}</Body>
      </div>
    </Section>
  );
}
