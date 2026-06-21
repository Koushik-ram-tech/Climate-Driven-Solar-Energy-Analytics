/**
 * src/pages/not-found/NotFoundPage.tsx
 */

import { Link } from "react-router-dom";
import { PageShell } from "@components/layout/PageShell";
import { Section } from "@components/layout/Section";
import { DisplayXL, Eyebrow, Body } from "@components/ui/Text";
import { buttonClasses } from "@components/ui/Button";

export function NotFoundPage() {
  return (
    <PageShell>
      <Section spacing="spacious">
        <div className="flex flex-col gap-6 max-w-xl">
          <Eyebrow>404 — Not Found</Eyebrow>
          <DisplayXL>This page doesn't exist.</DisplayXL>
          <Body className="text-ink-500">
            The URL you followed doesn't match any page in SolarIQ. Check the address or return home.
          </Body>
          <div className="flex gap-4">
            <Link to="/" className={buttonClasses("primary", "md")}>
              Go home →
            </Link>
            <Link to="/assessment" className={buttonClasses("outline", "md")}>
              Start assessment
            </Link>
          </div>
        </div>
      </Section>
    </PageShell>
  );
}
