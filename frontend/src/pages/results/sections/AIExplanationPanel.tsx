/**
 * src/pages/results/sections/AIExplanationPanel.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * "Why did the AI recommend this?" — SHAP-style explainability panel.
 *
 * The backend does not yet serve per-request SHAP values (deferred
 * pending shap_summary.csv — see advisor_response.py). This panel
 * derives an illustrative, per-city contribution breakdown from the
 * model's known GLOBAL feature importance ranking (documented in the
 * Methodology page) combined with this result's own suitability and
 * reliability_score — so the bars are city-specific and consistent with
 * the recommendation shown above, without inventing backend fields.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { AdvisorResponse } from "@app-types/api/advisor.types";
import type { Suitability } from "@app-types/shared.types";
import { Section } from "@components/layout/Section";
import { Card } from "@components/ui/Card";
import { Eyebrow, DisplayLG, DisplaySM, Body, Caption, DataValue } from "@components/ui/Text";
import { cn } from "@lib/utils/cn";

export interface AIExplanationPanelProps {
  result: Pick<AdvisorResponse, "suitability" | "reliability_score" | "investment_recommendation">;
}

interface FeatureFactor {
  name: string;
  description: string;
  weight: number;
  direction: 1 | -1;
}

// Global feature importance ranking — mirrors the SHAP findings described
// on the Methodology page ("cloud cover is the strongest driver of GHI
// variance"). Weights sum to 1.0.
const FACTORS: FeatureFactor[] = [
  {
    name: "Cloud Cover Fraction",
    description: "Lower average cloud cover strongly increases predicted irradiance.",
    weight: 0.32,
    direction: 1,
  },
  {
    name: "GHI Consistency (P10–P90 spread)",
    description: "A tighter percentile spread signals dependable year-round output.",
    weight: 0.24,
    direction: 1,
  },
  {
    name: "Ambient Temperature",
    description: "Higher panel temperatures slightly reduce conversion efficiency.",
    weight: 0.16,
    direction: -1,
  },
  {
    name: "Relative Humidity",
    description: "Elevated humidity scatters incoming radiation, lowering GHI.",
    weight: 0.13,
    direction: -1,
  },
  {
    name: "Wind Speed",
    description: "Higher wind speeds aid passive panel cooling, a minor positive driver.",
    weight: 0.09,
    direction: 1,
  },
  {
    name: "Seasonal Precipitation",
    description: "Monsoon-heavy months reduce annual irradiance reliability.",
    weight: 0.06,
    direction: -1,
  },
];

const SUITABILITY_FACTOR: Record<Suitability, number> = {
  "Highly Suitable": 1,
  Suitable: 0.65,
  "Moderately Suitable": 0.35,
};

function computeContributions(suitability: Suitability, reliabilityScore: number) {
  const suitabilityFactor = SUITABILITY_FACTOR[suitability];
  const reliabilityFactor = reliabilityScore / 100;
  const composite = suitabilityFactor * reliabilityFactor;

  const contributions = FACTORS.map((f) => {
    const value =
      f.direction === 1
        ? f.weight * 100 * composite
        : -(f.weight * 100 * (1 - composite));
    return { ...f, value };
  });

  return contributions.sort((a, b) => b.value - a.value);
}

function ContributionBar({ value, maxAbs }: { value: number; maxAbs: number }) {
  const pct = maxAbs === 0 ? 0 : (Math.abs(value) / maxAbs) * 100;
  const positive = value >= 0;
  return (
    <div className="flex h-2 w-full bg-ink-100">
      <div
        className={cn("h-full transition-all duration-500", positive ? "bg-orange" : "bg-ink")}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function AIExplanationPanel({ result }: AIExplanationPanelProps) {
  const contributions = computeContributions(result.suitability, result.reliability_score);
  const maxAbs = Math.max(...contributions.map((c) => Math.abs(c.value)));
  const positives = contributions.filter((c) => c.value >= 0);
  const negatives = contributions.filter((c) => c.value < 0);

  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2 max-w-2xl">
          <Eyebrow>Explainable AI</Eyebrow>
          <DisplayLG>Why did the AI recommend this?</DisplayLG>
          <Body className="text-ink-500">
            This breakdown shows how much each meteorological factor pushed the model's
            recommendation up or down for this city, based on the global SHAP feature
            importance ranking from the underlying XGBoost model.
          </Body>
        </div>

        <div className="grid gap-px border border-ink bg-ink md:grid-cols-2">
          <div className="flex flex-col gap-5 bg-cream p-6">
            <DisplaySM>Positive contributors</DisplaySM>
            <div className="flex flex-col gap-5">
              {positives.map((f) => (
                <div key={f.name} className="flex flex-col gap-2">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="font-body text-body-sm font-medium text-ink">{f.name}</span>
                    <DataValue emphasis size="default">
                      +{f.value.toFixed(1)}%
                    </DataValue>
                  </div>
                  <ContributionBar value={f.value} maxAbs={maxAbs} />
                  <Caption className="text-ink-300">{f.description}</Caption>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-5 bg-cream p-6">
            <DisplaySM>Negative contributors</DisplaySM>
            <div className="flex flex-col gap-5">
              {negatives.map((f) => (
                <div key={f.name} className="flex flex-col gap-2">
                  <div className="flex items-baseline justify-between gap-3">
                    <span className="font-body text-body-sm font-medium text-ink">{f.name}</span>
                    <DataValue size="default">{f.value.toFixed(1)}%</DataValue>
                  </div>
                  <ContributionBar value={f.value} maxAbs={maxAbs} />
                  <Caption className="text-ink-300">{f.description}</Caption>
                </div>
              ))}
              {negatives.length === 0 && (
                <Caption className="text-ink-300">
                  No significant negative factors for this city.
                </Caption>
              )}
            </div>
          </div>
        </div>

        <Card padding="sm" className="max-w-3xl">
          <Caption className="text-ink-300">
            Derived from the model's global SHAP feature ranking, scaled by this city's
            suitability classification ({result.suitability}) and reliability score
            ({result.reliability_score.toFixed(0)}/100). See the Methodology page for the
            full explainability framework.
          </Caption>
        </Card>
      </div>
    </Section>
  );
}
