/**
 * src/pages/methodology/MethodologyPage.tsx
 */

import { useMethodology } from "@features/methodology/hooks";
import { PageShell } from "@components/layout/PageShell";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG, DisplaySM, Body, BodySmall } from "@components/ui/Text";
import { StatBlock } from "@components/data-display/StatBlock";
import { LoadingState } from "@components/feedback/LoadingState";
import { ArchitectureFlow } from "@pages/methodology/sections/ArchitectureFlow";
import { DatasetModelInsights } from "@pages/methodology/sections/DatasetModelInsights";
import { ModelPerformanceVisualisation } from "@pages/methodology/sections/ModelPerformanceVisualisation";
import { Card } from "@components/ui/Card";
import shapGlobalBar from "@assets/model/01_global_importance_bar.png";
import shapBeeswarm from "@assets/model/02_shap_summary_beeswarm.png";

const FRAMEWORK_SECTIONS = [
  {
    title: "Dataset",
    content:
      "NASA POWER hourly meteorological data (2019–2024) for 15 Indian cities. Features include cloud cover fraction, temperature, relative humidity, wind speed, and precipitation. Over 260,000 hourly observations per city were used for training and validation.",
  },
  {
    title: "XGBoost Model",
    content:
      "A gradient-boosted decision tree regressor trained to predict Global Horizontal Irradiance (GHI) from meteorological inputs. Hyperparameter tuning via cross-validation. Global model R² = 0.8831, demonstrating strong predictive power across diverse Indian climates.",
  },
  {
    title: "SHAP Explainability",
    content:
      "SHapley Additive exPlanations (SHAP) quantify each feature's contribution to each prediction. Cloud cover fraction is consistently the strongest driver of GHI variance. SHAP values allow users to understand why a city received its reliability score, not just what the score is.",
  },
  {
    title: "Solar Decision Support Framework (SDSF)",
    content:
      "City-level research output: GHI percentile distribution (P10/P50/P90), Reliability Score (composite 0–100), prediction confidence tier, and suitability classification. All fields are frozen research outputs — never recomputed per request.",
  },
  {
    title: "Residential Solar Investment Advisor (RSIA)",
    content:
      "Personalised financial modelling: system sizing (constrained by roof area, budget, and city-level GHI), annual generation estimate, Year-1 savings, 25-year lifetime savings, and net benefit. Tariff assumption: ₹7.0/kWh.",
  },
  {
    title: "Limitations",
    content:
      "Point estimates, not guarantees. Actual savings depend on local tariffs, shading, panel degradation, and grid policy changes. The ₹7.0/kWh tariff assumption is a simplification. 15-city coverage excludes many Indian metros. Model accuracy varies by city (see MAPE scores in city readiness pages).",
  },
  {
    title: "Future Work",
    content:
      "Time-series forecasting for seasonal output curves. Real-time satellite feed integration. Expanded city coverage. Dynamic tariff adjustment. Grid export (net metering) modelling. Regional installer price benchmarks.",
  },
];

const STATS = [
  { value: "0.8831", label: "Global R²" },
  { value: "15", label: "Cities" },
  { value: "5 yrs", label: "Data range" },
  { value: "₹7/kWh", label: "Tariff assumption" },
];

export function MethodologyPage() {
  const { data, isLoading } = useMethodology();

  return (
    <PageShell>
      <Section spacing="default">
        <div className="flex flex-col gap-6 max-w-2xl">
          <Eyebrow>Research Methodology</Eyebrow>
          <DisplayLG>
            {isLoading ? "Loading…" : (data?.title ?? "AI-Powered Residential Solar Investment Advisor")}
          </DisplayLG>
          {isLoading ? (
            <LoadingState />
          ) : (
            <Body className="text-ink-500">
              {data?.description ?? ""}
            </Body>
          )}
          {data?.version && (
            <BodySmall>Framework version: {data.version}</BodySmall>
          )}
        </div>
      </Section>

      <Section divider spacing="compact">
        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.value} className="bg-cream p-6">
              <StatBlock value={s.value} label={s.label} />
            </div>
          ))}
        </div>
      </Section>

      <ArchitectureFlow />
      <DatasetModelInsights />
      <ModelPerformanceVisualisation />

      {FRAMEWORK_SECTIONS.map((sec, i) => (
        <Section key={sec.title} divider={i > 0} spacing="default">
          <div className="flex flex-col gap-6 max-w-2xl">
            <DisplaySM>{sec.title}</DisplaySM>
            <Body className="text-ink-500">{sec.content}</Body>
          </div>

          {sec.title === "SHAP Explainability" && (
            <div className="mt-8 grid gap-6 md:grid-cols-2">
              <Card padding="none" className="flex flex-col gap-0">
                <img
                  src={shapGlobalBar}
                  alt="Global SHAP feature importance bar chart"
                  className="w-full border-b border-ink"
                />
                <div className="flex flex-col gap-2 p-6">
                  <BodySmall className="font-medium text-ink">
                    Global Feature Importance (mean |SHAP value|)
                  </BodySmall>
                  <BodySmall className="text-ink-300">
                    Ranks every feature by its average impact on GHI predictions across
                    the full test set.
                  </BodySmall>
                </div>
              </Card>
              <Card padding="none" className="flex flex-col gap-0">
                <img
                  src={shapBeeswarm}
                  alt="SHAP summary beeswarm plot"
                  className="w-full border-b border-ink"
                />
                <div className="flex flex-col gap-2 p-6">
                  <BodySmall className="font-medium text-ink">
                    SHAP Summary (Beeswarm)
                  </BodySmall>
                  <BodySmall className="text-ink-300">
                    Shows the direction and magnitude of each feature's effect for every
                    individual prediction, not just its average.
                  </BodySmall>
                </div>
              </Card>
            </div>
          )}
        </Section>
      ))}
    </PageShell>
  );
}
