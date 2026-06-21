/**
 * src/pages/assessment/steps/StepReview.tsx
 */

import { useFormContext } from "react-hook-form";
import type { AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import type { AdvisorRequest } from "@types/api/advisor.types";
import { ResultSummaryCard } from "@features/advisor/components/ResultSummaryCard";
import { Button } from "@components/ui/Button";
import { DisplaySM, BodySmall } from "@components/ui/Text";
import { ApiError } from "@lib/api/client";

interface StepReviewProps {
  onBack: () => void;
  onEditStep: (step: "city" | "monthly_bill" | "roof_area_sqft" | "budget") => void;
  onSubmit: () => void;
  isSubmitting: boolean;
  error: Error | null;
}

export function StepReview({ onBack, onEditStep, onSubmit, isSubmitting, error }: StepReviewProps) {
  const { watch } = useFormContext<AdvisorFormValues>();
  const values = watch() as AdvisorRequest;

  function getErrorMessage(err: Error | null): string {
    if (!err) return "";
    if (err instanceof ApiError) {
      if (err.status === 400 || err.status === 422) return "Invalid inputs — please review your entries.";
      return "Something went wrong. Please try again.";
    }
    return "Unable to reach the server. Please check your connection.";
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <DisplaySM>Review your inputs</DisplaySM>
        <BodySmall>Confirm your details before we calculate your solar assessment.</BodySmall>
      </div>

      <ResultSummaryCard values={values} onEditStep={onEditStep} />

      {error && (
        <p className="font-mono text-caption text-orange-700">{getErrorMessage(error)}</p>
      )}

      <div className="flex gap-3">
        <Button variant="outline" onClick={onBack} disabled={isSubmitting}>← Back</Button>
        <Button onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Calculating…" : "Get my assessment →"}
        </Button>
      </div>
    </div>
  );
}
