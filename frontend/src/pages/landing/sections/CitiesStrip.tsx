/**
 * src/pages/landing/sections/CitiesStrip.tsx
 */

import { Link } from "react-router-dom";
import { Section } from "@components/layout/Section";
import { Eyebrow } from "@components/ui/Text";
import { SUPPORTED_CITIES } from "@app-types/shared.types";
import { toCitySlug } from "@lib/utils/slug";

export function CitiesStrip() {
  return (
    <Section divider spacing="compact">
      <div className="flex flex-col gap-6">
        <Eyebrow>15 Supported Cities</Eyebrow>
        <div className="flex flex-wrap gap-2">
          {SUPPORTED_CITIES.map((city) => (
            <Link
              key={city}
              to={`/readiness/${toCitySlug(city)}`}
              className="inline-flex items-center border border-ink px-3 py-1.5 font-mono text-caption text-ink transition-colors hover:bg-ink hover:text-cream"
            >
              {city}
            </Link>
          ))}
        </div>
      </div>
    </Section>
  );
}
