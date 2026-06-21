/**
 * src/components/ui/Text.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Semantic typography primitives built on the type scale defined in
 * tailwind.config.ts (hero, section-title, display-sm, body, body-sm,
 * caption, eyebrow, data, data-lg).
 *
 * Three font roles only, per the locked design system:
 *   font-display  Inter Tight — headings, used tight and heavy
 *   font-body     Inter       — body copy, UI text
 *   font-mono     JetBrains Mono — eyebrows, data values, units
 *
 * These are layout-agnostic — no color beyond ink/orange (emphasis),
 * no spacing decisions. Pages compose these inside their own layout.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { ElementType, HTMLAttributes, ReactNode } from "react";
import { cn } from "@lib/utils/cn";

interface BaseTextProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  className?: string;
}

/** Largest editorial statement — one per page, typically the hero line. */
export function DisplayXL({ children, className, ...rest }: BaseTextProps) {
  return (
    <h1
      className={cn(
        "font-display font-extrabold tracking-tightest text-hero text-ink",
        className,
      )}
      {...rest}
    >
      {children}
    </h1>
  );
}

/** Section-level heading — introduces a major page section. */
export function DisplayLG({
  as: Tag = "h2",
  children,
  className,
  ...rest
}: BaseTextProps & { as?: ElementType }) {
  return (
    <Tag
      className={cn(
        "font-display font-bold tracking-tight text-section-title text-ink",
        className,
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** Sub-section / card-group heading. */
export function DisplaySM({
  as: Tag = "h3",
  children,
  className,
  ...rest
}: BaseTextProps & { as?: ElementType }) {
  return (
    <Tag
      className={cn(
        "font-display font-semibold text-display-sm text-ink",
        className,
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** Standard paragraph copy. */
export function Body({
  as: Tag = "p",
  children,
  className,
  ...rest
}: BaseTextProps & { as?: ElementType }) {
  return (
    <Tag className={cn("font-body text-body text-ink", className)} {...rest}>
      {children}
    </Tag>
  );
}

/** Secondary / supporting copy — slightly smaller, muted by default. */
export function BodySmall({
  as: Tag = "p",
  children,
  className,
  ...rest
}: BaseTextProps & { as?: ElementType }) {
  return (
    <Tag
      className={cn("font-body text-body-sm text-ink-500", className)}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/**
 * Tracked uppercase mono label — the structural device used directly
 * above section titles and as a tag prefix. Encodes "this is a labelled
 * finding," matching the research-instrument tone of the product.
 */
export function Eyebrow({ children, className, ...rest }: BaseTextProps) {
  return (
    <span
      className={cn(
        "text-eyebrow font-medium tracking-eyebrow text-orange",
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  );
}

/** Small mono caption — chart footnotes, field hints, fine print. */
export function Caption({ children, className, ...rest }: BaseTextProps) {
  return (
    <span
      className={cn("font-mono text-caption text-ink-500", className)}
      {...rest}
    >
      {children}
    </span>
  );
}

/**
 * Numeric/data value — set in mono so figures read as measured output.
 * `emphasis` renders the value in orange, per the "important metrics
 * are orange" design system rule.
 */
export function DataValue({
  children,
  emphasis = false,
  size = "default",
  className,
  ...rest
}: BaseTextProps & { emphasis?: boolean; size?: "default" | "large" }) {
  return (
    <span
      className={cn(
        "font-mono font-medium tabular-nums",
        size === "large" ? "text-data-lg" : "text-data",
        emphasis ? "text-orange" : "text-ink",
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  );
}
