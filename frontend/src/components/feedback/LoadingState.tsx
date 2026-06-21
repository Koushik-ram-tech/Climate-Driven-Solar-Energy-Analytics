/**
 * src/components/feedback/LoadingState.tsx
 */

export interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Loading…" }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-2 w-2 bg-orange animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
      <span className="font-mono text-caption text-ink-300 uppercase tracking-eyebrow">
        {label}
      </span>
    </div>
  );
}
