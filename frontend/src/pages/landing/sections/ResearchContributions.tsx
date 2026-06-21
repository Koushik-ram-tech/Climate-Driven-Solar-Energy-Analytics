/**
 * src/pages/landing/sections/ResearchContributions.tsx
 */

import { Section } from "@components/layout/Section";
import { DisplayLG, Body, Eyebrow } from "@components/ui/Text";
import { StatBlock } from "@components/data-display/StatBlock";

const CONTRIBUTIONS = [
  { value: "SDSF", label: "Solar Decision Support Framework — city-level GHI prediction" },
  { value: "RSIA", label: "Residential Solar Investment Advisor — personalised financials" },
  { value: "SHAP", label: "Explainability layer — cloud cover identified as top driver" },
  { value: "XGBoost", label: "Gradient-boosted model trained on hourly NASA POWER data" },
];

export function ResearchContributions() {
  return (
    <Section divider spacing="default" className="bg-ink">
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-4 max-w-2xl">
          <Eyebrow className="text-orange">Research Contributions</Eyebrow>
          <DisplayLG className="text-cream">Two frameworks. One decision.</DisplayLG>
          <Body className="text-ink-100">
            Cloud cover is the strongest factor affecting solar irradiance predictions. SolarIQ's
            SHAP explainability layer surfaces exactly which meteorological signals drove each
            city's assessment — giving you the confidence to act on the numbers.
          </Body>
        </div>
        <div className="grid gap-px border border-ink-700 bg-ink-700 md:grid-cols-4">
          {CONTRIBUTIONS.map((c) => (
            <div key={c.value} className="bg-ink p-6">
              <StatBlock value={c.value} label={c.label} inverted />
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
