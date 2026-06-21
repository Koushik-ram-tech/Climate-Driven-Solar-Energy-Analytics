/**
 * src/features/readiness/components/GHIPercentileChart.tsx
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export interface GHIPercentileChartProps {
  meanGhi: number;
  p10Ghi: number;
  p50Ghi: number;
  p90Ghi: number;
}

export function GHIPercentileChart({ meanGhi, p10Ghi, p50Ghi, p90Ghi }: GHIPercentileChartProps) {
  const data = [
    { label: "P10 (Conservative)", value: p10Ghi },
    { label: "P50 (Base Case)", value: p50Ghi },
    { label: "Mean", value: meanGhi },
    { label: "P90 (Optimistic)", value: p90Ghi },
  ];

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
        <CartesianGrid vertical={false} stroke="#D8D5CE" strokeWidth={1} />
        <XAxis
          dataKey="label"
          tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "#5C594F" }}
          axisLine={{ stroke: "#000" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "#5C594F" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `${v}`}
          domain={["auto", "auto"]}
        />
        <Tooltip
          formatter={(v: number) => [`${v.toFixed(2)} kWh/m²/day`, "GHI"]}
          contentStyle={{
            border: "1px solid #000",
            background: "#F5F0E8",
            fontFamily: "var(--font-mono)",
            fontSize: 11,
          }}
        />
        <ReferenceLine y={meanGhi} stroke="#FD5200" strokeDasharray="4 2" strokeWidth={1} />
        <Bar dataKey="value" fill="#000" radius={0} />
      </BarChart>
    </ResponsiveContainer>
  );
}
