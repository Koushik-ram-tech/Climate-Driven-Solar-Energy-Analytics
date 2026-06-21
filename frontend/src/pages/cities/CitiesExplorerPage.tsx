/**
 * src/pages/cities/CitiesExplorerPage.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Route: /cities
 * Fetches GET /readiness/{city} for all 15 supported cities in parallel
 * (via useQueries) and ranks them by reliability_score — the only
 * continuous numeric resource-quality metric the backend exposes.
 * Clicking a row navigates to its existing readiness dashboard route.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { useQueries } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { PageShell } from "@components/layout/PageShell";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG, Body, Caption } from "@components/ui/Text";
import { LoadingState } from "@components/feedback/LoadingState";
import { SuitabilityBadge } from "@features/readiness/components/SuitabilityBadge";
import { ConfidenceTag } from "@features/readiness/components/ConfidenceTag";
import { ProgressBar } from "@components/data-display/ProgressBar";
import { getReadiness } from "@features/readiness/api";
import { SUPPORTED_CITIES } from "@app-types/shared.types";
import { toCitySlug } from "@lib/utils/slug";

export function CitiesExplorerPage() {
  const queries = useQueries({
    queries: SUPPORTED_CITIES.map((city) => ({
      queryKey: ["readiness", toCitySlug(city)],
      queryFn: () => getReadiness(toCitySlug(city)),
      staleTime: 5 * 60 * 1000,
    })),
  });

  const isLoading = queries.some((q) => q.isLoading);
  const results = queries
    .map((q) => q.data)
    .filter((d): d is NonNullable<typeof d> => Boolean(d))
    .sort((a, b) => b.reliability_score - a.reliability_score);

  return (
    <PageShell>
      <Section spacing="default">
        <div className="flex flex-col gap-3 max-w-2xl">
          <Eyebrow>Solar Readiness Explorer</Eyebrow>
          <DisplayLG>All 15 cities, ranked by reliability</DisplayLG>
          <Body className="text-ink-500">
            Cities are ranked by their composite Reliability Score — a 0–100 measure of
            solar resource consistency derived from the Solar Decision Support Framework.
          </Body>
        </div>
      </Section>

      <Section divider spacing="default">
        {isLoading ? (
          <LoadingState label="Loading city rankings…" />
        ) : (
          <div className="flex flex-col border border-ink">
            {results.map((city, i) => (
              <Link
                key={city.city_slug}
                to={`/readiness/${city.city_slug}`}
                className={`flex flex-col gap-4 px-6 py-5 transition-colors hover:bg-ink hover:text-cream md:flex-row md:items-center md:justify-between ${
                  i < results.length - 1 ? "border-b border-ink" : ""
                }`}
              >
                <div className="flex items-center gap-5">
                  <span className="w-8 font-mono text-data text-orange tabular-nums">
                    {(i + 1).toString().padStart(2, "0")}
                  </span>
                  <div className="flex flex-col gap-1">
                    <span className="font-display text-display-sm font-semibold">
                      {city.city}
                    </span>
                    <div className="flex flex-wrap gap-2">
                      <SuitabilityBadge suitability={city.suitability} />
                      <ConfidenceTag confidence={city.prediction_confidence} />
                    </div>
                  </div>
                </div>

                <div className="flex w-full flex-col gap-1 md:w-64">
                  <div className="flex items-baseline justify-between">
                    <Caption className="uppercase tracking-eyebrow opacity-70">
                      Reliability Score
                    </Caption>
                    <span className="font-mono text-data font-medium tabular-nums">
                      {city.reliability_score.toFixed(0)}
                    </span>
                  </div>
                  <ProgressBar value={city.reliability_score} max={100} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </Section>
    </PageShell>
  );
}
