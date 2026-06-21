/**
 * src/pages/landing/sections/HowItWorks.tsx
 */

import { Section } from "@components/layout/Section";
import { DisplayLG, DisplaySM, Body, Eyebrow, BodySmall } from "@components/ui/Text";

const STEPS = [
  {
    n: "1",
    title: "Enter your details",
    desc: "City, monthly electricity bill, available roof area, and installation budget.",
  },
  {
    n: "2",
    title: "We run the model",
    desc: "SolarIQ sizes a system to your roof and budget, then applies city-level GHI forecasts.",
  },
  {
    n: "3",
    title: "Review your results",
    desc: "Payback period, annual savings, and a clear investment recommendation — with reasoning.",
  },
];

export function HowItWorks() {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-12">
        <div className="flex flex-col gap-3 max-w-xl">
          <Eyebrow>How It Works</Eyebrow>
          <DisplayLG>Three inputs. One clear answer.</DisplayLG>
        </div>
        <div className="grid gap-px border border-ink bg-ink md:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.n} className="flex flex-col gap-4 bg-cream p-8">
              <span className="font-mono text-4xl font-bold text-orange">{step.n}</span>
              <DisplaySM as="h3">{step.title}</DisplaySM>
              <BodySmall>{step.desc}</BodySmall>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
