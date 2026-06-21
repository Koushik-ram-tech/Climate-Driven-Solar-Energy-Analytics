/**
 * src/pages/landing/LandingPage.tsx
 */

import { PageShell } from "@components/layout/PageShell";
import { Hero } from "@pages/landing/sections/Hero";
import { ResearchOverview } from "@pages/landing/sections/ResearchOverview";
import { HowItWorks } from "@pages/landing/sections/HowItWorks";
import { ResearchContributions } from "@pages/landing/sections/ResearchContributions";
import { CitiesStrip } from "@pages/landing/sections/CitiesStrip";
import { CTASection } from "@pages/landing/sections/CTASection";

export function LandingPage() {
  return (
    <PageShell>
      <Hero />
      <ResearchOverview />
      <HowItWorks />
      <ResearchContributions />
      <CitiesStrip />
      <CTASection />
    </PageShell>
  );
}
