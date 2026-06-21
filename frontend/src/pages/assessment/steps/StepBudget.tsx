/**
 * src/pages/assessment/steps/StepBudget.tsx
 */

import { useFormContext } from "react-hook-form";
import type { AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import { NumberInput } from "@components/ui/NumberInput";
import { Slider } from "@components/ui/Slider";
import { Button } from "@components/ui/Button";
import { DisplaySM } from "@components/ui/Text";

export function StepBudget({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { setValue, watch, formState: { errors } } = useFormContext<AdvisorFormValues>();
  const value = watch("budget");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <DisplaySM>What is your maximum installation budget?</DisplaySM>
        <p className="font-body text-body-sm text-ink-500">
          The system will be sized to fit within this capital limit.
        </p>
      </div>
      <NumberInput
        label="Budget (₹)"
        value={value}
        onChange={(v) => setValue("budget", v, { shouldValidate: true })}
        min={50000}
        max={5000000}
        unit="₹"
        error={errors.budget?.message}
      />
      <Slider
        value={value ?? 50000}
        onChange={(v) => setValue("budget", v, { shouldValidate: true })}
        min={50000}
        max={5000000}
        step={50000}
      />
      <div className="flex gap-3">
        <Button variant="outline" onClick={onBack}>← Back</Button>
        <Button onClick={onNext} disabled={!value || !!errors.budget}>Continue →</Button>
      </div>
    </div>
  );
}
