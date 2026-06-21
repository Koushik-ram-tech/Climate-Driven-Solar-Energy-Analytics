/**
 * src/components/data-display/ProgressBar.tsx
 */

export interface ProgressBarProps {
  value: number;
  max: number;
}

export function ProgressBar({ value, max }: ProgressBarProps) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="h-1 w-full bg-ink-100">
      <div
        className="h-full bg-orange transition-all duration-500"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
