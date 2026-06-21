/**
 * src/features/readiness/components/ConfidenceTag.tsx
 */

import type { PredictionConfidence } from "@app-types/shared.types";
import { cn } from "@lib/utils/cn";

export interface ConfidenceTagProps {
  confidence: PredictionConfidence;
}

const CONFIG: Record<PredictionConfidence, string> = {
  High: "border-orange text-orange",
  Medium: "border-ink text-ink",
  Low: "border-ink-300 text-ink-300",
};

export function ConfidenceTag({ confidence }: ConfidenceTagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center border px-2.5 py-0.5 font-mono text-caption uppercase tracking-eyebrow",
        CONFIG[confidence],
      )}
    >
      {confidence} Confidence
    </span>
  );
}
