/**
 * src/pages/landing/sections/Hero.tsx
 */

import { Link } from "react-router-dom";
import { Section } from "@components/layout/Section";
import { DisplayXL, Body, Eyebrow } from "@components/ui/Text";
import { buttonClasses } from "@components/ui/Button";

export function Hero() {
  return (
    <Section spacing="spacious">
      <div className="flex flex-col gap-8 max-w-4xl">
        <Eyebrow>AI-Powered Solar Investment Advisor</Eyebrow>
        <DisplayXL>
          Find out whether solar is a smart investment for your home.
        </DisplayXL>
        <Body className="max-w-2xl text-ink-500">
          Built on five years of NASA POWER meteorological data across 15 Indian cities,
          SolarIQ uses XGBoost and SHAP explainability to give you a data-driven solar assessment — 
          not a sales pitch.
        </Body>
        <div className="flex flex-wrap gap-4">
          <Link to="/assessment" className={buttonClasses("primary", "lg")}>
            Start my assessment →
          </Link>
          <Link to="/methodology" className={buttonClasses("outline", "lg")}>
            Read the methodology
          </Link>
        </div>
      </div>
    </Section>
  );
}
