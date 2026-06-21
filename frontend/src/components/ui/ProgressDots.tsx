/**
 * src/components/ui/ProgressDots.tsx
 */

import { cn } from "@lib/utils/cn";

export interface ProgressDotsProps {
  totalSteps: number;
  currentStep: number;
}

export function ProgressDots({ totalSteps, currentStep }: ProgressDotsProps) {
  return (
    <div className="flex items-center gap-2" aria-label={`Step ${currentStep + 1} of ${totalSteps}`}>
      {Array.from({ length: totalSteps }).map((_, i) => (
        <span
          key={i}
          className={cn(
            "h-1.5 transition-all duration-200",
            i === currentStep
              ? "w-6 bg-orange"
              : i < currentStep
              ? "w-3 bg-ink"
              : "w-3 bg-ink-100",
          )}
        />
      ))}
    </div>
  );
}
