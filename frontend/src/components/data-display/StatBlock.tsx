/**
 * src/components/data-display/StatBlock.tsx
 */

import { cn } from "@lib/utils/cn";

export interface StatBlockProps {
  value: string;
  label: string;
  /** When placed on a dark background, use inverted label color */
  inverted?: boolean;
}

export function StatBlock({ value, label, inverted = false }: StatBlockProps) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono font-bold tabular-nums text-data-lg text-orange">
        {value}
      </span>
      <span className={cn("font-body text-body-sm", inverted ? "text-ink-100" : "text-ink-500")}>
        {label}
      </span>
    </div>
  );
}
