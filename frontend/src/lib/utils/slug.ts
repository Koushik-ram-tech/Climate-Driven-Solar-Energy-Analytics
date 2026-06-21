/**
 * src/lib/utils/slug.ts
 */

export function toCitySlug(cityName: string): string {
  return cityName
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}
