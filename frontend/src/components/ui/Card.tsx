/**
 * src/components/ui/Card.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Primitive card surface: cream background, black (ink) border, sharp
 * corners per the locked design system (no shadows, no rounded corners
 * unless the design system lock is revisited).
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { HTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Padding density. Defaults to "default". */
  padding?: "none" | "sm" | "default" | "lg";
}

const PADDING_CLASSES: Record<NonNullable<CardProps["padding"]>, string> = {
  none: "",
  sm: "p-4",
  default: "p-6",
  lg: "p-8",
};

export function Card({
  padding = "default",
  className,
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-card border border-ink bg-cream",
        PADDING_CLASSES[padding],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

