/**
 * src/pages/readiness/sections/ReliabilityPanel.tsx
 */

import type { ReadinessResponse } from "@types/api/readiness.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG, Body } from "@components/ui/Text";
import { ReliabilityGauge } from "@features/readiness/components/ReliabilityGauge";
import { SuitabilityBadge } from "@features/readiness/components/SuitabilityBadge";
import { ConfidenceTag } from "@features/readiness/components/ConfidenceTag";

export interface ReliabilityPanelProps {
  data: Pick<
    ReadinessResponse,
    "reliability_score" | "rs_category" | "suitability" | "prediction_confidence" | "explanation"
  >;
}

export function ReliabilityPanel({ data }: ReliabilityPanelProps) {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>Reliability Assessment</Eyebrow>
          <DisplayLG>Solar resource reliability</DisplayLG>
        </div>

        <div className="grid gap-px border border-ink bg-ink md:grid-cols-2 max-w-3xl">
          <div className="flex items-center justify-center bg-cream p-10">
            <ReliabilityGauge
              reliabilityScore={data.reliability_score}
              rsCategory={data.rs_category}
            />
          </div>
          <div className="flex flex-col gap-6 bg-cream p-8">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">Suitability</span>
              <SuitabilityBadge suitability={data.suitability} />
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">Prediction Confidence</span>
              <ConfidenceTag confidence={data.prediction_confidence} />
            </div>
            <Body className="text-ink-500 text-sm">{data.explanation}</Body>
          </div>
        </div>
      </div>
    </Section>
  );
}
