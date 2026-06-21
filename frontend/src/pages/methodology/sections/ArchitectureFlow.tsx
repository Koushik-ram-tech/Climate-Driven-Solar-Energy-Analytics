/**
 * src/pages/methodology/sections/ArchitectureFlow.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * End-to-end pipeline visualization: data → model → explainability →
 * serving → presentation → output. Built entirely from existing UI
 * primitives (Card, Text) — no new design tokens introduced.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { Section } from "@components/layout/Section";
import { Card } from "@components/ui/Card";
import { Eyebrow, DisplayLG, DisplaySM, Caption } from "@components/ui/Text";

const STAGES = [
  { n: "01", title: "NASA POWER Dataset", desc: "5 years of hourly meteorological observations, 15 cities." },
  { n: "02", title: "Feature Engineering", desc: "12 derived features: cloud cover, temperature, humidity, wind, seasonality." },
  { n: "03", title: "XGBoost Model", desc: "Gradient-boosted regressor predicting Global Horizontal Irradiance." },
  { n: "04", title: "SHAP Explainability", desc: "Per-feature contribution values make every prediction auditable." },
  { n: "05", title: "FastAPI Backend", desc: "Serves /cities, /readiness, /advisor, /methodology as frozen research outputs." },
  { n: "06", title: "React Frontend", desc: "Assessment wizard, dashboards, and explainability views." },
  { n: "07", title: "Solar Recommendation", desc: "Investment verdict, payback estimate, and savings projection." },
] as const;

export function ArchitectureFlow() {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2 max-w-2xl">
          <Eyebrow>System Architecture</Eyebrow>
          <DisplayLG>From raw satellite data to a recommendation</DisplayLG>
        </div>

        <div className="flex flex-col gap-3 md:flex-row md:flex-wrap md:items-stretch">
          {STAGES.map((stage, i) => (
            <div key={stage.n} className="flex items-center gap-3">
              <Card padding="default" className="flex w-56 flex-col gap-2">
                <span className="font-mono text-caption text-orange tracking-eyebrow">
                  {stage.n}
                </span>
                <DisplaySM as="h3" className="text-display-sm leading-tight">
                  {stage.title}
                </DisplaySM>
                <Caption className="text-ink-300">{stage.desc}</Caption>
              </Card>
              {i < STAGES.length - 1 && (
                <span
                  aria-hidden="true"
                  className="hidden font-mono text-2xl text-ink-300 md:inline-block"
                >
                  →
                </span>
              )}
              {i < STAGES.length - 1 && (
                <span aria-hidden="true" className="font-mono text-2xl text-ink-300 md:hidden">
                  ↓
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
