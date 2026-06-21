/**
 * src/pages/methodology/sections/DatasetModelInsights.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Expanded statistics grid covering dataset scale and model accuracy,
 * for quick reference during a viva. Reuses MetricCard — same primitive
 * as the readiness dashboard's accuracy panel.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { MetricCard } from "@components/data-display/MetricCard";

const INSIGHTS = [
  { label: "Cities Covered", value: "15", unit: undefined },
  { label: "Data Range", value: "5", unit: "years" },
  { label: "Training Records", value: "65,000+", unit: undefined },
  { label: "Engineered Features", value: "12", unit: undefined },
  { label: "Model R²", value: "0.8831", unit: undefined, emphasis: true },
  { label: "RMSE", value: "0.4941", unit: "kWh/m²/day" },
  { label: "MAPE", value: "9.71", unit: "%" },
] as const;

export function DatasetModelInsights() {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2 max-w-2xl">
          <Eyebrow>Dataset &amp; Model Insights</Eyebrow>
          <DisplayLG>The numbers behind the model</DisplayLG>
        </div>

        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-4">
          {INSIGHTS.map((s) => (
            <div key={s.label} className="bg-cream">
              <MetricCard
                label={s.label}
                value={s.value}
                unit={s.unit}
                emphasis={"emphasis" in s ? s.emphasis : false}
              />
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
