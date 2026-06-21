/**
 * src/pages/results/sections/ScoreBreakdown.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Recommendation Score Breakdown — decomposes the recommendation into
 * Suitability, Financial, and Reliability sub-scores plus a weighted
 * Overall score, so a viva panel can see exactly what drove the verdict.
 *
 * Suitability and Financial scores are deterministic numeric mappings of
 * fields already returned by POST /advisor (suitability classification,
 * payback_years) — no new backend fields required.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { AdvisorResponse } from "@app-types/api/advisor.types";
import type { Suitability } from "@app-types/shared.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG, Caption } from "@components/ui/Text";
import { GaugeChart } from "@components/data-display/GaugeChart";
import { ProgressBar } from "@components/data-display/ProgressBar";

export interface ScoreBreakdownProps {
  result: Pick<AdvisorResponse, "suitability" | "reliability_score" | "payback_years" | "investment_recommendation">;
}

const SUITABILITY_SCORE: Record<Suitability, number> = {
  "Highly Suitable": 92,
  Suitable: 72,
  "Moderately Suitable": 50,
};

function clamp(n: number, min: number, max: number) {
  return Math.min(max, Math.max(min, n));
}

function computeFinancialScore(paybackYears: number): number {
  // 4 years payback → ~100, 25 years payback → ~0
  return clamp(100 - (paybackYears - 4) * (100 / 21), 0, 100);
}

function computeOverall(suitability: number, financial: number, reliability: number): number {
  return suitability * 0.35 + financial * 0.35 + reliability * 0.3;
}

function ScoreRow({ label, score }: { label: string; score: number }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">
          {label}
        </span>
        <span className="font-mono text-data font-medium tabular-nums text-ink">
          {score.toFixed(0)}
          <span className="text-ink-300">/100</span>
        </span>
      </div>
      <ProgressBar value={score} max={100} />
    </div>
  );
}

export function ScoreBreakdown({ result }: ScoreBreakdownProps) {
  const suitabilityScore = SUITABILITY_SCORE[result.suitability];
  const financialScore = computeFinancialScore(result.payback_years);
  const reliabilityScore = result.reliability_score;
  const overall = computeOverall(suitabilityScore, financialScore, reliabilityScore);

  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2 max-w-2xl">
          <Eyebrow>Recommendation Score Breakdown</Eyebrow>
          <DisplayLG>How the verdict was weighted</DisplayLG>
        </div>

        <div className="grid gap-px border border-ink bg-ink md:grid-cols-2">
          <div className="flex flex-col items-center justify-center gap-3 bg-cream p-10">
            <GaugeChart value={overall} />
            <div className="text-center">
              <div className="font-mono text-data-lg font-medium text-orange tabular-nums">
                {overall.toFixed(0)}
              </div>
              <div className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">
                Overall Score / 100
              </div>
              <div className="mt-2 font-mono text-caption text-ink-500">
                {result.investment_recommendation}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-6 bg-cream p-8">
            <ScoreRow label="Suitability Score" score={suitabilityScore} />
            <ScoreRow label="Financial Score" score={financialScore} />
            <ScoreRow label="Reliability Score" score={reliabilityScore} />
            <Caption className="text-ink-300">
              Overall = 35% Suitability + 35% Financial + 30% Reliability.
            </Caption>
          </div>
        </div>
      </div>
    </Section>
  );
}
