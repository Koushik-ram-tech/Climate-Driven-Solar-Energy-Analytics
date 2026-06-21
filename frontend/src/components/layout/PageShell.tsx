/**
 * src/components/layout/PageShell.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Wraps every route's page content with Header + Footer + the locked
 * cream background. Used once per page component, or hoisted into a
 * layout route in router.tsx — decide at implementation time.
 * ─────────────────────────────────────────────────────────────────────────
 */

import type { ReactNode } from "react";
import { Header } from "@components/layout/Header";
import { Footer } from "@components/layout/Footer";

export interface PageShellProps {
  children: ReactNode;
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="flex min-h-screen flex-col bg-cream">
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}

