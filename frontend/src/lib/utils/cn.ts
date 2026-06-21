/**
 * src/lib/utils/cn.ts
 * ─────────────────────────────────────────────────────────────────────────
 * Minimal className joiner (the same calling convention as `clsx`,
 * implemented locally to avoid adding a dependency for the design
 * system layer). Accepts strings, falsy values, and objects mapping
 * class name → boolean condition.
 * ─────────────────────────────────────────────────────────────────────────
 */

export type ClassValue =
  | string
  | number
  | null
  | undefined
  | false
  | Record<string, boolean | undefined>;

export function cn(...inputs: ClassValue[]): string {
  const classes: string[] = [];

  for (const input of inputs) {
    if (!input) continue;

    if (typeof input === "string" || typeof input === "number") {
      classes.push(String(input));
      continue;
    }

    for (const [key, value] of Object.entries(input)) {
      if (value) classes.push(key);
    }
  }

  return classes.join(" ");
}
