/**
 * src/pages/assessment/steps/StepCity.tsx
 */

import { useFormContext } from "react-hook-form";
import type { AdvisorFormValues } from "@features/advisor/advisorFormSchema";
import { CitySelector } from "@features/cities/CitySelector";
import type { SupportedCity } from "@types/shared.types";
import { Button } from "@components/ui/Button";
import { DisplaySM } from "@components/ui/Text";

export function StepCity({ onNext }: { onNext: () => void }) {
  const { setValue, watch, formState: { errors } } = useFormContext<AdvisorFormValues>();
  const city = watch("city") as SupportedCity | undefined;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <DisplaySM>Which city is your home in?</DisplaySM>
        <p className="font-body text-body-sm text-ink-500">
          Solar irradiance data is available for 15 Indian cities.
        </p>
      </div>
      <CitySelector
        value={city ?? null}
        onChange={(c) => setValue("city", c, { shouldValidate: true })}
      />
      {errors.city && (
        <p className="font-mono text-caption text-orange-700">{errors.city.message}</p>
      )}
      <Button onClick={onNext} disabled={!city} className="w-full md:w-auto">
        Continue →
      </Button>
    </div>
  );
}
