/**
 * src/features/cities/CitySelector.tsx
 */

import { useCities } from "@features/cities/hooks";
import { Select } from "@components/ui/Select";
import type { SupportedCity } from "@types/shared.types";
import { SUPPORTED_CITIES } from "@types/shared.types";

export interface CitySelectorProps {
  value: SupportedCity | null;
  onChange: (city: SupportedCity) => void;
}

export function CitySelector({ value, onChange }: CitySelectorProps) {
  const { data } = useCities();

  const options = (data?.cities ?? SUPPORTED_CITIES.map((c) => ({ city: c, city_slug: c.toLowerCase() }))).map(
    (c) => ({ value: c.city as SupportedCity, label: c.city }),
  );

  return (
    <Select
      options={options}
      value={value}
      onChange={onChange}
      placeholder="Select a city…"
      searchable
    />
  );
}
