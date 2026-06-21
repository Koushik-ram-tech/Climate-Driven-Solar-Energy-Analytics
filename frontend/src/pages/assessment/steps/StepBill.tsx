/**
 * src/pages/assessment/steps/StepBill.tsx
 */

import { useFormContext } from "react-hook-form";
import type { AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import { NumberInput } from "@components/ui/NumberInput";
import { Slider } from "@components/ui/Slider";
import { Button } from "@components/ui/Button";
import { DisplaySM } from "@components/ui/Text";

export function StepBill({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { setValue, watch, formState: { errors } } = useFormContext<AdvisorFormValues>();
  const value = watch("monthly_bill");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <DisplaySM>What is your average monthly electricity bill?</DisplaySM>
        <p className="font-body text-body-sm text-ink-500">
          This helps estimate how much solar can offset your current spending.
        </p>
      </div>
      <NumberInput
        label="Monthly Bill (₹)"
        value={value}
        onChange={(v) => setValue("monthly_bill", v, { shouldValidate: true })}
        min={500}
        max={100000}
        unit="₹"
        error={errors.monthly_bill?.message}
      />
      <Slider
        value={value ?? 500}
        onChange={(v) => setValue("monthly_bill", v, { shouldValidate: true })}
        min={500}
        max={100000}
        step={500}
      />
      <div className="flex gap-3">
        <Button variant="outline" onClick={onBack}>← Back</Button>
        <Button onClick={onNext} disabled={!value || !!errors.monthly_bill}>Continue →</Button>
      </div>
    </div>
  );
}
