/**
 * src/components/ui/Badge.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Generic small label/tag primitive. Domain-specific badges
 * (RecommendationBadge, SuitabilityBadge, ConfidenceTag) compose this
 * rather than duplicating its styling.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { HTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "neutral" | "accent";
}

const TONE_CLASSES: Record<NonNullable<BadgeProps["tone"]>, string> = {
  neutral: "border-ink text-ink",
  accent: "border-orange text-orange",
};

export function Badge({ tone = "neutral", className, children, ...rest }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center border px-3 py-1 font-mono text-caption uppercase tracking-eyebrow",
        TONE_CLASSES[tone],
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  );
}

