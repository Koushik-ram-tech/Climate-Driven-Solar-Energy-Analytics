/**
 * src/components/ui/Select.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Generic select primitive. Used by CitySelector (constrained to
 * SupportedCity values) and any other closed-set choice in the UI.
 *
 * Built as a custom listbox rather than a native <select> so the
 * `searchable` variant can filter options inline — native selects don't
 * support that without a third-party library.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@lib/utils/cn";

export interface SelectOption<T extends string = string> {
  value: T;
  label: string;
}

export interface SelectProps<T extends string = string> {
  options: SelectOption<T>[];
  value: T | null;
  onChange: (value: T) => void;
  placeholder?: string;
  searchable?: boolean;
}

export function Select<T extends string = string>({
  options,
  value,
  onChange,
  placeholder = "Select…",
  searchable = false,
}: SelectProps<T>) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);

  const selected = options.find((opt) => opt.value === value) ?? null;

  const filtered = useMemo(() => {
    if (!searchable || query.trim() === "") return options;
    const q = query.toLowerCase();
    return options.filter((opt) => opt.label.toLowerCase().includes(q));
  }, [options, query, searchable]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className={cn(
          "flex h-12 w-full items-center justify-between border border-ink bg-cream px-4",
          "font-body text-body text-ink transition-colors focus:outline-none focus-visible:border-orange",
        )}
      >
        <span className={selected ? "text-ink" : "text-ink-300"}>
          {selected ? selected.label : placeholder}
        </span>
        <span aria-hidden="true" className="font-mono text-caption text-ink-500">
          {open ? "▲" : "▼"}
        </span>
      </button>

      {open && (
        <div className="absolute left-0 right-0 top-full z-10 mt-1 max-h-64 overflow-y-auto border border-ink bg-cream">
          {searchable && (
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search…"
              className="w-full border-b border-ink bg-cream px-4 py-2.5 font-body text-body-sm text-ink placeholder:text-ink-300 focus:outline-none"
            />
          )}
          <ul role="listbox">
            {filtered.length === 0 && (
              <li className="px-4 py-3 font-body text-body-sm text-ink-300">
                No matches.
              </li>
            )}
            {filtered.map((opt) => (
              <li key={opt.value}>
                <button
                  type="button"
                  role="option"
                  aria-selected={opt.value === value}
                  onClick={() => {
                    onChange(opt.value);
                    setOpen(false);
                    setQuery("");
                  }}
                  className={cn(
                    "block w-full px-4 py-2.5 text-left font-body text-body-sm transition-colors hover:bg-orange hover:text-cream",
                    opt.value === value ? "text-orange" : "text-ink",
                  )}
                >
                  {opt.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

