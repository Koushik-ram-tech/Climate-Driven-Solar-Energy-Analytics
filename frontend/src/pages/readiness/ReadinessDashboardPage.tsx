/**
 * src/pages/readiness/ReadinessDashboardPage.tsx
 */

import { useParams, Link } from "react-router-dom";
import { useReadiness } from "@features/readiness/hooks";
import { PageShell } from "@components/layout/PageShell";
import { Section } from "@components/layout/Section";
import { LoadingState } from "@components/feedback/LoadingState";
import { ErrorState } from "@components/feedback/ErrorState";
import { SuitabilityBadge } from "@features/readiness/components/SuitabilityBadge";
import { GHIPanel } from "@pages/readiness/sections/GHIPanel";
import { ReliabilityPanel } from "@pages/readiness/sections/ReliabilityPanel";
import { ModelAccuracyPanel } from "@pages/readiness/sections/ModelAccuracyPanel";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { buttonClasses } from "@components/ui/Button";
import { ApiError } from "@lib/api/client";

export function ReadinessDashboardPage() {
  const { citySlug } = useParams<{ citySlug: string }>();
  const { data, isLoading, isError, error, refetch } = useReadiness(citySlug);

  if (isLoading) {
    return (
      <PageShell>
        <LoadingState label="Loading solar readiness data…" />
      </PageShell>
    );
  }

  if (isError) {
    return (
      <PageShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <ErrorState
            error={error instanceof ApiError ? error : new Error(String(error))}
            onRetry={() => void refetch()}
          />
        </div>
      </PageShell>
    );
  }

  if (!data) return null;

  return (
    <PageShell>
      <Section spacing="compact">
        <div className="flex flex-col gap-4">
          <Eyebrow>Solar Readiness Explorer</Eyebrow>
          <div className="flex flex-wrap items-start gap-4">
            <DisplayLG>{data.city}</DisplayLG>
            <div className="mt-1">
              <SuitabilityBadge suitability={data.suitability} />
            </div>
          </div>
          <Link
            to="/assessment"
            className={buttonClasses("primary", "sm")}
            style={{ width: "fit-content" }}
          >
            Get personalised assessment →
          </Link>
        </div>
      </Section>

      <GHIPanel data={data} />
      <ReliabilityPanel data={data} />
      <ModelAccuracyPanel data={data} />
    </PageShell>
  );
}
