/**
 * src/features/readiness/components/SuitabilityBadge.tsx
 */

import type { Suitability } from "@app-types/shared.types";
import { cn } from "@lib/utils/cn";

export interface SuitabilityBadgeProps {
  suitability: Suitability;
}

const CONFIG: Record<Suitability, { icon: string; className: string }> = {
  "Highly Suitable": { icon: "☀", className: "border-orange text-orange" },
  "Suitable": { icon: "◑", className: "border-ink text-ink" },
  "Moderately Suitable": { icon: "○", className: "border-ink-300 text-ink-300" },
};

export function SuitabilityBadge({ suitability }: SuitabilityBadgeProps) {
  const config = CONFIG[suitability];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 border px-3 py-1 font-mono text-caption uppercase tracking-eyebrow",
        config.className,
      )}
    >
      <span>{config.icon}</span>
      {suitability}
    </span>
  );
}
