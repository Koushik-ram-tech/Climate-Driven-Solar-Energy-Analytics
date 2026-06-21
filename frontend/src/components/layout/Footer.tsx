/**
 * src/components/layout/Footer.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Site footer. Static links/credits — no API dependency.
 *
 * Mirrors Header's hairline language with a top border instead of a
 * bottom one, closing the page the same way it opened.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { Link } from "react-router-dom";
import { Container } from "@components/layout/Container";

const FRAMEWORK_LINKS = [
  { to: "/methodology", label: "Methodology" },
  { to: "/readiness/bengaluru", label: "Solar Readiness Explorer" },
] as const;

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-ink bg-cream">
      <Container>
        <div className="flex flex-col gap-8 py-14 md:flex-row md:items-start md:justify-between">
          <div className="max-w-prose">
            <span className="font-display text-lg font-bold tracking-tight text-ink">
              SolarIQ
            </span>
            <p className="mt-3 font-body text-body-sm text-ink-500">
              Explainable, data-driven residential solar investment
              recommendations for 15 Indian cities, built on five years of
              NASA POWER meteorological data.
            </p>
          </div>

          <nav className="flex flex-col gap-3 md:flex-row md:gap-8">
            {FRAMEWORK_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="font-body text-body-sm text-ink transition-colors hover:text-orange"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex flex-col gap-2 border-t border-ink py-6 font-mono text-caption text-ink-500 md:flex-row md:items-center md:justify-between">
          <span>© {year} SolarIQ. Research framework — not financial advice.</span>
          <span>Tariff assumption: ₹7.0/kWh</span>
        </div>
      </Container>
    </footer>
  );
}

