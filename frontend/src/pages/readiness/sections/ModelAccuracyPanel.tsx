/**
 * src/pages/readiness/sections/ModelAccuracyPanel.tsx
 */

import type { ReadinessResponse } from "@app-types/api/readiness.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { MetricCard } from "@components/data-display/MetricCard";
import { formatPercent } from "@lib/format/number";

export interface ModelAccuracyPanelProps {
  data: Pick<ReadinessResponse, "model_rmse" | "model_mape" | "prediction_confidence">;
}

export function ModelAccuracyPanel({ data }: ModelAccuracyPanelProps) {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>Model Performance</Eyebrow>
          <DisplayLG>XGBoost accuracy for this city</DisplayLG>
        </div>
        <div className="grid grid-cols-2 gap-px border border-ink bg-ink max-w-xl">
          <div className="bg-cream">
            <MetricCard
              label="RMSE"
              value={data.model_rmse.toFixed(3)}
              unit="kWh/m²/day"
            />
          </div>
          <div className="bg-cream">
            <MetricCard
              label="MAPE"
              value={formatPercent(data.model_mape)}
              emphasis
            />
          </div>
        </div>
        <p className="font-mono text-caption text-ink-300 max-w-prose">
          RMSE = Root Mean Squared Error. MAPE = Mean Absolute Percentage Error.
          Lower values indicate better model accuracy. Global R² = 0.8831.
        </p>
      </div>
    </Section>
  );
}
