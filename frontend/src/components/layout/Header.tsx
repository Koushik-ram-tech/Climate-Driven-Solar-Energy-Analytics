/**
 * src/components/layout/Header.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Site header / top navigation. Links to: Landing (/), Assessment
 * (/assessment), Methodology (/methodology).
 *
 * Sticky with a single 1px black bottom border — the same hairline
 * language used by Card, Divider, and Section dividers throughout the
 * product. No shadow is used to lift it off the page; the rule alone
 * separates it from content.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { NavLink, Link } from "react-router-dom";
import { Container } from "@components/layout/Container";
import { buttonClasses } from "@components/ui/Button";
import { cn } from "@lib/utils/cn";

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/cities", label: "Cities" },
  { to: "/methodology", label: "Methodology" },
] as const;

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink bg-cream">
      <Container>
        <div className="flex h-18 items-center justify-between">
          <NavLink
            to="/"
            className="font-display text-lg font-bold tracking-tight text-ink"
          >
            SolarIQ
          </NavLink>

          <nav className="hidden items-center gap-8 md:flex">
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) =>
                  cn(
                    "font-body text-body-sm transition-colors hover:text-orange",
                    isActive ? "text-orange" : "text-ink",
                  )
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          <Link to="/assessment" className={buttonClasses("primary", "sm")}>
            Get my assessment
          </Link>
        </div>
      </Container>
    </header>
  );
}

