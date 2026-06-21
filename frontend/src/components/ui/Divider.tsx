/**
 * src/components/ui/Divider.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Thin horizontal/vertical rule primitive for section separation.
 * ─────────────────────────────────────────────────────────────────────────
 */

export interface DividerProps {
  orientation?: "horizontal" | "vertical";
  className?: string;
}

export function Divider({ orientation = "horizontal", className }: DividerProps) {
  if (orientation === "vertical") {
    return (
      <div
        role="separator"
        aria-orientation="vertical"
        className={`w-px self-stretch bg-ink ${className ?? ""}`}
      />
    );
  }

  return (
    <div
      role="separator"
      aria-orientation="horizontal"
      className={`h-px w-full bg-ink ${className ?? ""}`}
    />
  );
}

