/**
 * src/pages/results/sections/Financials.tsx
 */

import type { AdvisorResponse } from "@types/api/advisor.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { MetricCard } from "@components/data-display/MetricCard";
import { ProgressBar } from "@components/data-display/ProgressBar";
import { formatINR, formatINRCompact } from "@lib/format/currency";
import { formatYears } from "@lib/format/number";

export interface FinancialsProps {
  result: Pick<
    AdvisorResponse,
    "annual_savings" | "payback_years" | "lifetime_savings" | "net_benefit_inr"
  >;
}

export function Financials({ result }: FinancialsProps) {
  const metrics = [
    { label: "Annual Savings", value: formatINRCompact(result.annual_savings), emphasis: true },
    { label: "Payback Period", value: formatYears(result.payback_years) },
    { label: "Lifetime Savings (25yr)", value: formatINRCompact(result.lifetime_savings), emphasis: true },
    { label: "Net Benefit (25yr)", value: formatINR(result.net_benefit_inr) },
  ];

  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>Financial Projection</Eyebrow>
          <DisplayLG>25-year investment outlook</DisplayLG>
        </div>
        <div className="grid grid-cols-2 gap-px border border-ink bg-ink md:grid-cols-4">
          {metrics.map((m) => (
            <div key={m.label} className="bg-cream">
              <MetricCard label={m.label} value={m.value} emphasis={m.emphasis} />
            </div>
          ))}
        </div>
        <div className="flex flex-col gap-2 max-w-xl">
          <span className="font-mono text-caption text-ink-300">
            Payback progress ({result.payback_years.toFixed(1)} of 25 years)
          </span>
          <ProgressBar value={result.payback_years} max={25} />
        </div>
      </div>
    </Section>
  );
}
