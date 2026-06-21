/**
 * src/components/feedback/EmptyState.tsx
 */

import type { ReactNode } from "react";

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 py-24 text-center">
      <div className="border border-ink p-6">
        <span className="font-mono text-4xl text-ink-100">○</span>
      </div>
      <div className="flex flex-col gap-2">
        <h2 className="font-display text-display-sm font-bold text-ink">{title}</h2>
        {description && (
          <p className="font-body text-body-sm text-ink-500 max-w-sm">{description}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
