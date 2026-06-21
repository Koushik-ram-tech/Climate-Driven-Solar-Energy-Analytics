/**
 * src/components/layout/Section.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Vertical rhythm wrapper for a page section. Wraps Container internally
 * so pages don't have to nest both manually for the common case.
 *
 * `divider` adds a top hairline rule — the product's one structural
 * signature — for sections that should read as a new beat in the page,
 * rather than a continuation of the previous one.
 *
 * Not in the original scaffold's component inventory; added because the
 * design system needs one canonical "page section" wrapper for every
 * later page to build on, instead of each page hand-rolling spacing.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@lib/utils/cn";
import { Container } from "@components/layout/Container";

export interface SectionProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  /** Renders a 1px hairline rule across the top of the section. */
  divider?: boolean;
  /** Vertical padding density. Defaults to "default". */
  spacing?: "compact" | "default" | "spacious";
  /** Skip the internal Container — use when the section needs full-bleed content. */
  fullBleed?: boolean;
}

const SPACING_CLASSES: Record<NonNullable<SectionProps["spacing"]>, string> = {
  compact: "py-12 md:py-16",
  default: "py-18 md:py-22",
  spacious: "py-22 md:py-30",
};

export function Section({
  children,
  divider = false,
  spacing = "default",
  fullBleed = false,
  className,
  ...rest
}: SectionProps) {
  return (
    <section
      className={cn(
        SPACING_CLASSES[spacing],
        divider && "border-t border-ink",
        className,
      )}
      {...rest}
    >
      {fullBleed ? children : <Container>{children}</Container>}
    </section>
  );
}
