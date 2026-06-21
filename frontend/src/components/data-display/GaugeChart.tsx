/**
 * src/components/data-display/GaugeChart.tsx
 */

export interface GaugeChartProps {
  value: number;
  min?: number;
  max?: number;
}

export function GaugeChart({ value, min = 0, max = 100 }: GaugeChartProps) {
  const pct = Math.min(1, Math.max(0, (value - min) / (max - min)));
  const angle = -130 + pct * 260;
  const r = 56;
  const cx = 80;
  const cy = 80;

  function arcPath(startDeg: number, endDeg: number, radius: number) {
    const toRad = (d: number) => (d * Math.PI) / 180;
    const x1 = cx + radius * Math.cos(toRad(startDeg));
    const y1 = cy + radius * Math.sin(toRad(startDeg));
    const x2 = cx + radius * Math.cos(toRad(endDeg));
    const y2 = cy + radius * Math.sin(toRad(endDeg));
    const large = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2}`;
  }

  return (
    <svg viewBox="0 0 160 100" className="w-full max-w-[180px]">
      <path d={arcPath(-130, 130, r)} fill="none" stroke="#D8D5CE" strokeWidth="8" strokeLinecap="round" />
      <path d={arcPath(-130, -130 + pct * 260, r)} fill="none" stroke="#FD5200" strokeWidth="8" strokeLinecap="round" />
      <line
        x1={cx}
        y1={cy}
        x2={cx + (r - 10) * Math.cos(((angle) * Math.PI) / 180)}
        y2={cy + (r - 10) * Math.sin(((angle) * Math.PI) / 180)}
        stroke="#000"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx={cx} cy={cy} r="4" fill="#000" />
    </svg>
  );
}
