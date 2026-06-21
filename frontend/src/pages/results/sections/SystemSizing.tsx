/**
 * src/pages/results/sections/SystemSizing.tsx
 */

import type { AdvisorResponse } from "@types/api/advisor.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { MetricCard } from "@components/data-display/MetricCard";
import { formatKwh } from "@lib/format/number";

export interface SystemSizingProps {
  result: Pick<AdvisorResponse, "system_size_kw" | "annual_generation_kwh">;
}

export function SystemSizing({ result }: SystemSizingProps) {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>System Design</Eyebrow>
          <DisplayLG>Your recommended system</DisplayLG>
        </div>
        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-2 max-w-xl">
          <div className="bg-cream">
            <MetricCard
              label="System Size"
              value={`${result.system_size_kw}`}
              unit="kW"
              emphasis
            />
          </div>
          <div className="bg-cream">
            <MetricCard
              label="Annual Generation"
              value={formatKwh(result.annual_generation_kwh)}
            />
          </div>
        </div>
      </div>
    </Section>
  );
}
