/**
 * src/pages/assessment/AssessmentPage.tsx
 */

import { PageShell } from "@components/layout/PageShell";
import { Section } from "@components/layout/Section";
import { Eyebrow, DisplayLG } from "@components/ui/Text";
import { AdvisorForm } from "@features/advisor/components/AdvisorForm";
import type { AdvisorResponse } from "@types/api/advisor.types";

export function AssessmentPage() {
  function handleSuccess(_result: AdvisorResponse) {
    // Navigation is handled inside AdvisorForm after mutation success
  }

  return (
    <PageShell>
      <Section spacing="default">
        <div className="grid gap-16 md:grid-cols-[1fr_2fr]">
          <div className="flex flex-col gap-3">
            <Eyebrow>Solar Assessment</Eyebrow>
            <DisplayLG>Tell us about your home.</DisplayLG>
            <p className="font-body text-body-sm text-ink-500 mt-2">
              Four inputs. Takes under two minutes. Powered by five years of NASA satellite data.
            </p>
          </div>
          <div className="max-w-lg">
            <AdvisorForm onSubmitSuccess={handleSuccess} />
          </div>
        </div>
      </Section>
    </PageShell>
  );
}
