/**
 * src/pages/readiness/sections/GHIPanel.tsx
 */

import type { ReadinessResponse } from "@app-types/api/readiness.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { MetricCard } from "@components/data-display/MetricCard";
import { GHIPercentileChart } from "@features/readiness/components/GHIPercentileChart";
import { formatGhi } from "@lib/format/number";

export interface GHIPanelProps {
  data: Pick<ReadinessResponse, "mean_ghi" | "p10_ghi" | "p50_ghi" | "p90_ghi">;
}

export function GHIPanel({ data }: GHIPanelProps) {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>Solar Irradiance</Eyebrow>
          <DisplayLG>Global Horizontal Irradiance (GHI)</DisplayLG>
        </div>

        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-4 max-w-3xl">
          <div className="bg-cream">
            <MetricCard label="Mean GHI" value={formatGhi(data.mean_ghi)} emphasis />
          </div>
          <div className="bg-cream">
            <MetricCard label="P10 Conservative" value={formatGhi(data.p10_ghi)} />
          </div>
          <div className="bg-cream">
            <MetricCard label="P50 Base Case" value={formatGhi(data.p50_ghi)} />
          </div>
          <div className="bg-cream">
            <MetricCard label="P90 Optimistic" value={formatGhi(data.p90_ghi)} />
          </div>
        </div>

        <div className="border border-ink p-6 max-w-3xl">
          <GHIPercentileChart
            meanGhi={data.mean_ghi}
            p10Ghi={data.p10_ghi}
            p50Ghi={data.p50_ghi}
            p90Ghi={data.p90_ghi}
          />
        </div>
      </div>
    </Section>
  );
}
