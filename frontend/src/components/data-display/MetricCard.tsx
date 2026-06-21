/**
 * src/components/data-display/MetricCard.tsx
 */

import { cn } from "@lib/utils/cn";

export interface MetricCardProps {
  label: string;
  value: string;
  unit?: string;
  emphasis?: boolean;
}

export function MetricCard({ label, value, unit, emphasis = false }: MetricCardProps) {
  return (
    <div className="flex flex-col gap-1 border border-ink p-5">
      <span className="font-mono text-eyebrow text-xs uppercase tracking-eyebrow text-ink-300">
        {label}
      </span>
      <div className="flex items-baseline gap-1.5">
        <span
          className={cn(
            "font-mono text-data-lg font-medium tabular-nums",
            emphasis ? "text-orange" : "text-ink",
          )}
        >
          {value}
        </span>
        {unit && (
          <span className="font-mono text-caption text-ink-300">{unit}</span>
        )}
      </div>
    </div>
  );
}
