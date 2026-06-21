/**
 * src/pages/landing/sections/CTASection.tsx
 */

import { Link } from "react-router-dom";
import { Section } from "@components/layout/Section";
import { DisplayLG, Body, Eyebrow } from "@components/ui/Text";
import { buttonClasses } from "@components/ui/Button";

export function CTASection() {
  return (
    <Section divider spacing="spacious">
      <div className="flex flex-col gap-8 max-w-2xl">
        <Eyebrow>Get Started</Eyebrow>
        <DisplayLG>Ready to find out if solar pays off for you?</DisplayLG>
        <Body className="text-ink-500">
          The assessment takes under two minutes. Enter your city, bill, roof area, and budget —
          and receive a data-driven answer backed by five years of satellite observations.
        </Body>
        <div className="flex flex-wrap gap-4">
          <Link to="/assessment" className={buttonClasses("primary", "lg")}>
            Start my assessment →
          </Link>
          <Link to="/readiness/bengaluru" className={buttonClasses("outline", "lg")}>
            Explore solar readiness
          </Link>
        </div>
      </div>
    </Section>
  );
}
