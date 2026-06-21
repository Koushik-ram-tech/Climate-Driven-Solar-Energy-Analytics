/**
 * src/features/advisor/components/ResultSummaryCard.tsx
 */

import type { AdvisorRequest } from "@types/api/advisor.types";
import { formatINR } from "@lib/format/currency";
import { Button } from "@components/ui/Button";

export interface ResultSummaryCardProps {
  values: AdvisorRequest;
  onEditStep: (step: "city" | "monthly_bill" | "roof_area_sqft" | "budget") => void;
}

export function ResultSummaryCard({ values, onEditStep }: ResultSummaryCardProps) {
  const rows = [
    { label: "City", value: values.city, step: "city" as const },
    { label: "Monthly Bill", value: formatINR(values.monthly_bill), step: "monthly_bill" as const },
    { label: "Roof Area", value: `${values.roof_area_sqft} sq ft`, step: "roof_area_sqft" as const },
    { label: "Budget", value: formatINR(values.budget), step: "budget" as const },
  ];

  return (
    <div className="border border-ink">
      {rows.map((row, i) => (
        <div
          key={row.step}
          className={`flex items-center justify-between px-5 py-4 ${i < rows.length - 1 ? "border-b border-ink" : ""}`}
        >
          <div className="flex flex-col gap-0.5">
            <span className="font-mono text-caption uppercase tracking-eyebrow text-ink-300">
              {row.label}
            </span>
            <span className="font-body text-body font-medium text-ink">{row.value}</span>
          </div>
          <button
            type="button"
            onClick={() => onEditStep(row.step)}
            className="font-mono text-caption text-orange underline hover:no-underline"
          >
            Edit
          </button>
        </div>
      ))}
    </div>
  );
}
