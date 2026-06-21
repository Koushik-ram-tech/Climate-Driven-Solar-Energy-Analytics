/**
 * src/app/providers.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Top-level provider composition: QueryClientProvider (TanStack Query).
 * An ErrorBoundary may be added here at implementation time to catch
 * render-time errors app-wide, separate from per-query error handling
 * (which uses ErrorState within each page).
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { ReactNode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@lib/query/queryClient";

export interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
