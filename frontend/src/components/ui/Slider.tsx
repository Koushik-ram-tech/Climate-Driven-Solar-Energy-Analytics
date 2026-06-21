/**
 * src/components/ui/Slider.tsx
 */

import { cn } from "@lib/utils/cn";

export interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  className?: string;
}

export function Slider({ value, onChange, min, max, step = 1, className }: SliderProps) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div className={cn("relative py-2", className)}>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full cursor-pointer appearance-none bg-transparent [&::-webkit-slider-runnable-track]:h-px [&::-webkit-slider-runnable-track]:bg-ink [&::-webkit-slider-thumb]:mt-[-7px] [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:border [&::-webkit-slider-thumb]:border-ink [&::-webkit-slider-thumb]:bg-orange"
        style={{ background: `linear-gradient(to right, #000 ${pct}%, #D8D5CE ${pct}%)` }}
      />
    </div>
  );
}
