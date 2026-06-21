/**
 * src/components/ui/Input.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Generic text input primitive.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useId } from "react";
import type { InputHTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({
  label,
  error,
  id,
  className,
  ...rest
}: InputProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;

  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label
          htmlFor={inputId}
          className="font-body text-body-sm font-medium text-ink"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${inputId}-error` : undefined}
        className={cn(
          "h-12 border bg-cream px-4 font-body text-body text-ink placeholder:text-ink-300",
          "transition-colors focus:outline-none focus-visible:outline-none",
          "focus:border-orange",
          error ? "border-orange-700" : "border-ink",
          className,
        )}
        {...rest}
      />
      {error && (
        <p
          id={`${inputId}-error`}
          className="font-mono text-caption text-orange-700"
        >
          {error}
        </p>
      )}
    </div>
  );
}

