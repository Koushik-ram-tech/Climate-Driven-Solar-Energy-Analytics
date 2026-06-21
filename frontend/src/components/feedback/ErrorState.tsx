/**
 * src/components/feedback/ErrorState.tsx
 */

import { ApiError } from "@lib/api/client";
import { Button } from "@components/ui/Button";

export interface ErrorStateProps {
  error: ApiError | Error;
  onRetry?: () => void;
}

function getMessage(error: ApiError | Error): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "City not found. Please check the URL and try again.";
    if (error.status === 400 || error.status === 422) return "Invalid inputs. Please review your entries.";
    return "Something went wrong on our end. Please try again.";
  }
  return "Unable to retrieve results. Please try again.";
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 py-24 text-center">
      <div className="border border-ink p-6">
        <span className="font-mono text-4xl text-ink-100">✕</span>
      </div>
      <div className="flex flex-col gap-2">
        <h2 className="font-display text-display-sm font-bold text-ink">Error</h2>
        <p className="font-body text-body-sm text-ink-500 max-w-sm">{getMessage(error)}</p>
      </div>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
