/**
 * src/features/advisor/components/AdvisorForm.tsx
 */

import { useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { advisorFormSchema, type AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import { useAdvisorMutation } from "@features/advisor/hooks";
import type { AdvisorResponse } from "@app-types/api/advisor.types";
import { StepCity } from "@pages/assessment/steps/StepCity";
import { StepBill } from "@pages/assessment/steps/StepBill";
import { StepRoof } from "@pages/assessment/steps/StepRoof";
import { StepBudget } from "@pages/assessment/steps/StepBudget";
import { StepReview } from "@pages/assessment/steps/StepReview";
import { ProgressDots } from "@components/ui/ProgressDots";
import type { SupportedCity } from "@app-types/shared.types";

export interface AdvisorFormProps {
  onSubmitSuccess: (result: AdvisorResponse) => void;
}

const STEPS = ["city", "monthly_bill", "roof_area_sqft", "budget", "review"] as const;
type StepKey = (typeof STEPS)[number];

export function AdvisorForm({ onSubmitSuccess }: AdvisorFormProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();
  const mutation = useAdvisorMutation();

  const methods = useForm<AdvisorFormValues>({
    resolver: zodResolver(advisorFormSchema),
    mode: "onChange",
  });

  const stepKey: StepKey = STEPS[currentStep] ?? "city";

  function goNext() {
    setCurrentStep((s) => Math.min(s + 1, STEPS.length - 1));
  }

  function goBack() {
    setCurrentStep((s) => Math.max(s - 1, 0));
  }

  function goToStep(key: StepKey) {
    const idx = STEPS.indexOf(key);
    if (idx !== -1) setCurrentStep(idx);
  }

  async function handleFinalSubmit(values: AdvisorFormValues) {
    try {
      const result = await mutation.mutateAsync({
        ...values,
        city: values.city as SupportedCity,
    });
      onSubmitSuccess(result);
      navigate(`/results/${result.city_slug}`, { state: { result } });
    } catch {
      // Error surfaced via mutation.error in StepReview
    }
  }

  return (
    <FormProvider {...methods}>
      <div className="flex flex-col gap-8">
        <ProgressDots totalSteps={STEPS.length} currentStep={currentStep} />

        {stepKey === "city" && <StepCity onNext={goNext} />}
        {stepKey === "monthly_bill" && <StepBill onNext={goNext} onBack={goBack} />}
        {stepKey === "roof_area_sqft" && <StepRoof onNext={goNext} onBack={goBack} />}
        {stepKey === "budget" && <StepBudget onNext={goNext} onBack={goBack} />}
        {stepKey === "review" && (
          <StepReview
            onBack={goBack}
            onEditStep={goToStep}
            onSubmit={methods.handleSubmit(handleFinalSubmit)}
            isSubmitting={mutation.isPending}
            error={mutation.error}
          />
        )}
      </div>
    </FormProvider>
  );
}
