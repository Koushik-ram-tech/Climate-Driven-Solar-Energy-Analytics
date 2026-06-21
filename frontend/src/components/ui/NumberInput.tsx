/**
 * src/components/ui/NumberInput.tsx
 */

import { useId } from "react";
import { cn } from "@lib/utils/cn";

export interface NumberInputProps {
  label: string;
  value: number | undefined;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  unit?: string;
  error?: string;
  placeholder?: string;
}

export function NumberInput({
  label,
  value,
  onChange,
  min,
  max,
  unit,
  error,
  placeholder,
}: NumberInputProps) {
  const id = useId();
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="font-body text-body-sm font-medium text-ink">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type="number"
          min={min}
          max={max}
          value={value ?? ""}
          placeholder={placeholder}
          onChange={(e) => {
            const num = parseFloat(e.target.value);
            if (!isNaN(num)) onChange(num);
          }}
          aria-invalid={Boolean(error)}
          className={cn(
            "h-12 w-full border bg-cream px-4 font-body text-body text-ink placeholder:text-ink-300",
            "transition-colors focus:outline-none focus:border-orange",
            unit ? "pr-16" : "",
            error ? "border-orange-700" : "border-ink",
          )}
        />
        {unit && (
          <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 font-mono text-caption text-ink-500">
            {unit}
          </span>
        )}
      </div>
      {min !== undefined && max !== undefined && (
        <span className="font-mono text-caption text-ink-300">
          Range: {min.toLocaleString("en-IN")} – {max.toLocaleString("en-IN")}
        </span>
      )}
      {error && <p className="font-mono text-caption text-orange-700">{error}</p>}
    </div>
  );
}
