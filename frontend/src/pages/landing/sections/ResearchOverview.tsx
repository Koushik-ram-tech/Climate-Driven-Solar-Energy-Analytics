/**
 * src/pages/landing/sections/ResearchOverview.tsx
 */

import { Section } from "@components/layout/Section";
import { DisplayLG, Body, Eyebrow } from "@components/ui/Text";
import { StatBlock } from "@components/data-display/StatBlock";

const STATS = [
  { value: "0.8831", label: "Model R² — strong predictive accuracy" },
  { value: "15", label: "Indian cities supported" },
  { value: "5 yrs", label: "NASA POWER data (2019–2024)" },
  { value: "25 yr", label: "Investment horizon modelled" },
];

export function ResearchOverview() {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-4 max-w-2xl">
          <Eyebrow>Research Foundation</Eyebrow>
          <DisplayLG>Forecasting built on evidence, not estimates.</DisplayLG>
          <Body className="text-ink-500">
            SolarIQ's Solar Decision Support Framework trains an XGBoost regressor on hourly
            meteorological observations — cloud cover, temperature, humidity, wind speed — to predict
            Global Horizontal Irradiance for each supported city. SHAP values then make the model's
            reasoning transparent and auditable.
          </Body>
        </div>

        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.value} className="bg-cream p-6">
              <StatBlock value={s.value} label={s.label} />
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
