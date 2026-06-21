/**
 * src/components/data-display/RecommendationBadge.tsx
 */

import type { InvestmentRecommendation } from "@app-types/shared.types";
import { cn } from "@lib/utils/cn";

export interface RecommendationBadgeProps {
  recommendation: InvestmentRecommendation;
}

const CONFIG: Record<InvestmentRecommendation, { className: string }> = {
  "Highly Recommended": { className: "bg-orange text-cream border-orange" },
  "Recommended": { className: "bg-ink text-cream border-ink" },
  "Consider Carefully": { className: "bg-cream text-ink border-ink" },
  "Not Recommended": { className: "bg-cream text-ink-300 border-ink-100" },
};

export function RecommendationBadge({ recommendation }: RecommendationBadgeProps) {
  const config = CONFIG[recommendation];
  return (
    <span
      className={cn(
        "inline-flex items-center border px-4 py-1.5 font-mono text-caption uppercase tracking-eyebrow",
        config.className,
      )}
    >
      {recommendation}
    </span>
  );
}
