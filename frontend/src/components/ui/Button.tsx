/**
 * src/components/ui/Button.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Primitive button. Variants are restricted to the locked design system —
 * "primary" (orange fill) and "outline" (black border, cream fill) only.
 * No other color variants should be added without revisiting the design
 * system lock.
 *
 * This renders a native <button>. For navigation CTAs that should look
 * like a button but behave like a link, wrap react-router's <Link> and
 * apply the same `buttonClasses()` helper exported below rather than
 * extending this component's prop surface.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { ButtonHTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline";
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-10 px-4 text-body-sm",
  md: "h-12 px-6 text-body",
  lg: "h-14 px-8 text-body",
};

const VARIANT_CLASSES: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-orange text-cream border border-orange hover:bg-orange-600 hover:border-orange-600 active:bg-orange-700",
  outline:
    "bg-cream text-ink border border-ink hover:bg-ink hover:text-cream",
};

/**
 * Shared class builder so non-<button> elements (e.g. a router Link
 * styled as a CTA) can render with identical visual treatment without
 * widening Button's own prop contract.
 */
export function buttonClasses(
  variant: NonNullable<ButtonProps["variant"]> = "primary",
  size: NonNullable<ButtonProps["size"]> = "md",
  className?: string,
): string {
  return cn(
    "inline-flex items-center justify-center gap-2 font-body font-medium",
    "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-40",
    SIZE_CLASSES[size],
    VARIANT_CLASSES[variant],
    className,
  );
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button className={buttonClasses(variant, size, className)} {...rest}>
      {children}
    </button>
  );
}

