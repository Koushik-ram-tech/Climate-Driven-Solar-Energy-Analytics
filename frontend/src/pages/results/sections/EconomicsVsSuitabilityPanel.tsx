/**
 * src/pages/results/sections/EconomicsVsSuitabilityPanel.tsx
 */

import type { AdvisorResponse } from "@types/api/advisor.types";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG, Body } from "@components/ui/Text";
import { ReliabilityGauge } from "@features/readiness/components/ReliabilityGauge";
import { SuitabilityBadge } from "@features/readiness/components/SuitabilityBadge";
import { ConfidenceTag } from "@features/readiness/components/ConfidenceTag";
import { Link } from "react-router-dom";
import { buttonClasses } from "@components/ui/Button";

export interface EconomicsVsSuitabilityPanelProps {
  result: Pick<
    AdvisorResponse,
    "suitability" | "reliability_score" | "prediction_confidence" | "city_slug"
  >;
}

export function EconomicsVsSuitabilityPanel({ result }: EconomicsVsSuitabilityPanelProps) {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <Eyebrow>Solar Resource Quality</Eyebrow>
          <DisplayLG>How reliable is this city's solar potential?</DisplayLG>
        </div>

        <div className="grid gap-px border border-ink bg-ink md:grid-cols-2 max-w-3xl">
          <div className="flex flex-col items-center justify-center gap-4 bg-cream p-8">
            <ReliabilityGauge reliabilityScore={result.reliability_score} />
          </div>
          <div className="flex flex-col gap-5 bg-cream p-8">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">
                Suitability
              </span>
              <SuitabilityBadge suitability={result.suitability} />
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">
                Model Confidence
              </span>
              <ConfidenceTag confidence={result.prediction_confidence} />
            </div>
            <Body className="text-ink-500 text-sm">
              These scores reflect the city-level solar resource quality from the SDSF research framework.
            </Body>
            <Link
              to={`/readiness/${result.city_slug}`}
              className={buttonClasses("outline", "sm")}
            >
              Full readiness report →
            </Link>
          </div>
        </div>
      </div>
    </Section>
  );
}
