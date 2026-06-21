/**
 * src/app/router.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Route tree. Exactly the 6 routes defined in the architecture doc Step 3:
 *
 *   /                      → LandingPage
 *   /assessment            → AssessmentPage
 *   /results/:citySlug     → ResultsPage
 *   /readiness/:citySlug   → ReadinessDashboardPage
 *   /methodology           → MethodologyPage
 *   *                      → NotFoundPage
 * ─────────────────────────────────────────────────────────────────────────
 */

import { createBrowserRouter } from "react-router-dom";
import { LandingPage } from "@pages/landing/LandingPage";
import { AssessmentPage } from "@pages/assessment/AssessmentPage";
import { ResultsPage } from "@pages/results/ResultsPage";
import { ReadinessDashboardPage } from "@pages/readiness/ReadinessDashboardPage";
import { MethodologyPage } from "@pages/methodology/MethodologyPage";
import { CitiesExplorerPage } from "@pages/cities/CitiesExplorerPage";
import { NotFoundPage } from "@pages/not-found/NotFoundPage";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/assessment", element: <AssessmentPage /> },
  { path: "/results/:citySlug", element: <ResultsPage /> },
  { path: "/readiness/:citySlug", element: <ReadinessDashboardPage /> },
  { path: "/methodology", element: <MethodologyPage /> },
  { path: "/cities", element: <CitiesExplorerPage /> },
  { path: "*", element: <NotFoundPage /> },
]);
