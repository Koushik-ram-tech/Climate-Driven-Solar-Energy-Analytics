/**
 * src/pages/assessment/steps/StepRoof.tsx
 */

import { useFormContext } from "react-hook-form";
import type { AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import { NumberInput } from "@components/ui/NumberInput";
import { Slider } from "@components/ui/Slider";
import { Button } from "@components/ui/Button";
import { DisplaySM } from "@components/ui/Text";

export function StepRoof({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const { setValue, watch, formState: { errors } } = useFormContext<AdvisorFormValues>();
  const value = watch("roof_area_sqft");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <DisplaySM>How much flat roof area is available?</DisplaySM>
        <p className="font-body text-body-sm text-ink-500">
          Usable flat roof area determines the maximum system size that can be installed.
        </p>
      </div>
      <NumberInput
        label="Roof Area"
        value={value}
        onChange={(v) => setValue("roof_area_sqft", v, { shouldValidate: true })}
        min={50}
        max={5000}
        unit="sq ft"
        error={errors.roof_area_sqft?.message}
      />
      <Slider
        value={value ?? 50}
        onChange={(v) => setValue("roof_area_sqft", v, { shouldValidate: true })}
        min={50}
        max={5000}
        step={50}
      />
      <div className="flex gap-3">
        <Button variant="outline" onClick={onBack}>← Back</Button>
        <Button onClick={onNext} disabled={!value || !!errors.roof_area_sqft}>Continue →</Button>
      </div>
    </div>
  );
}
