/**
 * src/lib/format/number.ts
 */

export function formatKwh(value: number): string {
  return `${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(value)} kWh`;
}

export function formatYears(value: number): string {
  return `${value.toFixed(1)} yrs`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatGhi(value: number): string {
  return `${value.toFixed(2)} kWh/m²/day`;
}
