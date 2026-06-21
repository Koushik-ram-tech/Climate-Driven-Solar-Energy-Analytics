/**
 * src/pages/results/ResultsPage.tsx
 */

import { useLocation, useParams, Link } from "react-router-dom";
import type { AdvisorResponse } from "@types/api/advisor.types";
import { PageShell } from "@components/layout/PageShell";
import { EmptyState } from "@components/feedback/EmptyState";
import { buttonClasses } from "@components/ui/Button";
import { Recommendation } from "@pages/results/sections/Recommendation";
import { SystemSizing } from "@pages/results/sections/SystemSizing";
import { Financials } from "@pages/results/sections/Financials";
import { EconomicsVsSuitabilityPanel } from "@pages/results/sections/EconomicsVsSuitabilityPanel";
import { ScoreBreakdown } from "@pages/results/sections/ScoreBreakdown";
import { AIExplanationPanel } from "@pages/results/sections/AIExplanationPanel";

interface ResultsLocationState {
  result?: AdvisorResponse;
}

export function ResultsPage() {
  const { citySlug } = useParams<{ citySlug: string }>();
  const location = useLocation();
  const state = location.state as ResultsLocationState | null;
  const result = state?.result;

  void citySlug;

  if (!result) {
    return (
      <PageShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <EmptyState
            title="Assessment session expired"
            description="Your results are only available immediately after completing the assessment. Start a new one to get your personalised solar recommendation."
            action={
              <Link to="/assessment" className={buttonClasses("primary", "md")}>
                Start assessment →
              </Link>
            }
          />
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Recommendation result={result} />
      <SystemSizing result={result} />
      <Financials result={result} />
      <ScoreBreakdown result={result} />
      <EconomicsVsSuitabilityPanel result={result} />
      <AIExplanationPanel result={result} />
    </PageShell>
  );
}
