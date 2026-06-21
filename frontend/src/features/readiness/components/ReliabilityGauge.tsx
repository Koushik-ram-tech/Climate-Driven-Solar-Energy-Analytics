/**
 * src/features/readiness/components/ReliabilityGauge.tsx
 */

import type { RSCategory } from "@app-types/shared.types";
import { GaugeChart } from "@components/data-display/GaugeChart";

export interface ReliabilityGaugeProps {
  reliabilityScore: number;
  rsCategory?: RSCategory;
}

export function ReliabilityGauge({ reliabilityScore, rsCategory }: ReliabilityGaugeProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <GaugeChart value={reliabilityScore} />
      <div className="text-center">
        <div className="font-mono text-data-lg font-medium text-orange tabular-nums">
          {reliabilityScore.toFixed(0)}
        </div>
        <div className="font-mono text-caption text-ink-300 uppercase tracking-eyebrow">
          Reliability Score / 100
        </div>
        {rsCategory && (
          <div className="mt-2 font-mono text-caption text-ink-500">{rsCategory}</div>
        )}
      </div>
    </div>
  );
}
