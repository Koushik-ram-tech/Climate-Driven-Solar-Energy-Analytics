/**
 * src/components/layout/Container.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Centered max-width content wrapper with consistent horizontal padding.
 * Used inside every page section to keep margins aligned across the site.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { HTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface ContainerProps extends HTMLAttributes<HTMLDivElement> {}

export function Container({ className, children, ...rest }: ContainerProps) {
  return (
    <div
      className={cn("mx-auto w-full max-w-container px-6 md:px-10", className)}
      {...rest}
    >
      {children}
    </div>
  );
}

