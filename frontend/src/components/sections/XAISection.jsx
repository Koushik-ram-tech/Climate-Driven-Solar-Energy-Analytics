/**
 * XAISection.jsx
 * Consumes live data from POST /predict-explain via the `explain` prop.
 * All hardcoded SHAP values and mock insight cards have been removed.
 */

import { motion, AnimatePresence } from 'framer-motion'
import { Sun, Loader2, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { GlassCard } from '../ui/GlassCard'
import { Badge }     from '../ui/Badge'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Cell, ResponsiveContainer, ReferenceLine,
} from 'recharts'

// ─── helpers ─────────────────────────────────────────────────────────────────

/**
 * Convert feature_shap_values dict → sorted array for Recharts.
 * Sorted by absolute value descending, top N only.
 * Also returns the symmetric X-axis domain needed for signed bars.
 */
function shapToChartData(featureShapValues, topN = 10) {
  if (!featureShapValues || typeof featureShapValues !== 'object') {
    return { data: [], domain: [-0.1, 0.1] }
  }

  const data = Object.entries(featureShapValues)
    .map(([feature, shap]) => ({
      feature,
      shap,
      absShap: Math.abs(shap),
      direction: shap >= 0 ? 'positive' : 'negative',
    }))
    .sort((a, b) => b.absShap - a.absShap)
    .slice(0, topN)

  if (data.length === 0) return { data: [], domain: [-0.1, 0.1] }

  const maxAbs = Math.max(...data.map((d) => d.absShap))
  // Add 15 % padding and round to 3 dp for clean tick labels
  const bound = Math.ceil(maxAbs * 1.15 * 1000) / 1000
  const domain = [-bound, bound]

  return { data, domain }
}

/** Colour by direction — green lifts GHI, red suppresses it */
const DIRECTION_COLOR = {
  positive: '#f59e0b',  // solar amber — pushes GHI up
  negative: '#38bdf8',  // sky blue    — pushes GHI down
}

/** Pretty-print a feature name for display */
function formatFeature(name) {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// ─── sub-components ──────────────────────────────────────────────────────────

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-ink-800 border border-white/10 rounded-xl px-4 py-3 shadow-xl">
      <p className="text-xs font-mono text-slate-400 mb-0.5">{d.feature}</p>
      <p className="text-sm font-semibold text-white">{formatFeature(d.feature)}</p>
      <p
        className="text-xs mt-1 font-mono"
        style={{ color: DIRECTION_COLOR[d.direction] }}
      >
        SHAP = {d.shap > 0 ? '+' : ''}{d.shap.toFixed(4)}
      </p>
    </div>
  )
}

/** One positive or negative feature insight card */
function FeatureCard({ index, feature, shapValue, featureValue, colorHex }) {
  const sign = shapValue >= 0 ? '+' : ''
  const Icon = shapValue >= 0 ? TrendingUp : TrendingDown

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
    >
      <GlassCard className="h-full">
        <div className="flex items-start justify-between mb-3">
          <span
            className="text-2xl font-bold font-mono"
            style={{ color: colorHex }}
          >
            {String(index + 1).padStart(2, '0')}
          </span>
          <Icon size={14} style={{ color: colorHex }} className="mt-1 shrink-0" />
        </div>

        <code className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 mb-2 inline-block">
          {feature}
        </code>

        <p className="text-sm font-semibold text-white mb-1">
          {formatFeature(feature)}
        </p>

        <div className="mt-auto pt-3 border-t border-white/[0.06] grid grid-cols-2 gap-2">
          <div>
            <div className="text-[9px] font-mono text-slate-600 mb-0.5">SHAP</div>
            <div className="text-xs font-medium" style={{ color: colorHex }}>
              {sign}{shapValue.toFixed(4)}
            </div>
          </div>
          {featureValue != null && (
            <div>
              <div className="text-[9px] font-mono text-slate-600 mb-0.5">Value</div>
              <div className="text-xs font-medium text-white">
                {typeof featureValue === 'number' ? featureValue.toFixed(3) : featureValue}
              </div>
            </div>
          )}
        </div>
      </GlassCard>
    </motion.div>
  )
}

/** Summary strip: base_value → + delta → = predicted_ghi */
function PredictionSummary({ baseValue, delta, predictedGhi }) {
  return (
    <GlassCard className="mb-8">
      <p className="section-label mb-4">Prediction Decomposition</p>
      <div className="flex flex-wrap items-center gap-3 text-sm font-mono">
        <div className="text-center">
          <div className="text-[10px] text-slate-500 mb-1">Base Value</div>
          <span className="text-white font-semibold text-lg">{baseValue.toFixed(3)}</span>
        </div>

        <span className="text-slate-600 text-xl">+</span>

        <div className="text-center">
          <div className="text-[10px] text-slate-500 mb-1">SHAP Δ</div>
          <span
            className="font-semibold text-lg"
            style={{ color: delta >= 0 ? '#f59e0b' : '#38bdf8' }}
          >
            {delta >= 0 ? '+' : ''}{delta.toFixed(3)}
          </span>
        </div>

        <span className="text-slate-600 text-xl">=</span>

        <div className="text-center">
          <div className="text-[10px] text-slate-500 mb-1">Predicted GHI</div>
          <span className="text-solar-400 font-bold text-lg">{predictedGhi.toFixed(3)}</span>
          <span className="text-slate-500 text-[10px] ml-1">kWh/m²/day</span>
        </div>
      </div>
    </GlassCard>
  )
}

// ─── main component ───────────────────────────────────────────────────────────

export function XAISection({ explain, explainLoading, explainError }) {
  const { data: chartData, domain: xDomain } = shapToChartData(explain?.feature_shap_values)

  const positiveFeatures = explain?.top_positive_features ?? []
  const negativeFeatures = explain?.top_negative_features ?? []

  // Show data pane whenever we have explain data, regardless of whether a
  // new load is in flight (keep-previous UX — old result stays visible).
  const hasData = !!explain && !explainError
  // Show the full-screen loading placeholder only on the very first load
  // (no previous data to show yet).
  const showFullLoader  = explainLoading && !explain
  // Show idle placeholder only when nothing has ever been fetched
  const showIdle = !explainLoading && !explainError && !explain

  return (
    <section id="xai" className="relative py-32 overflow-hidden">
      <div className="orb w-[500px] h-[500px] bg-violet-500/5 top-0 right-0" />

      <div className="max-w-7xl mx-auto px-6">

        {/* ── Section header ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <p className="section-label mb-3">Section 04</p>
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-4xl font-bold text-white">Explainable AI</h2>
            <Badge variant="data">SHAP</Badge>
          </div>
          <p className="text-slate-400 max-w-xl">
            SHAP (SHapley Additive exPlanations) decomposes each prediction to show
            exactly how much each feature pushes the GHI estimate up or down.
            Run a prediction above to populate live explanations.
          </p>
        </motion.div>

        {/* ── States: idle / loading / error / data ── */}
        <AnimatePresence mode="wait">

          {/* Idle — no prediction run yet */}
          {showIdle && (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            >
              <GlassCard className="flex flex-col items-center justify-center py-20 gap-4 text-center">
                <div className="w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                  <Sun size={28} className="text-violet-400/50" />
                </div>
                <p className="text-sm font-medium text-slate-400">No explanation yet</p>
                <p className="text-xs text-slate-600">
                  Run a prediction in Section 02 to see live SHAP values here.
                </p>
              </GlassCard>
            </motion.div>
          )}

          {/* Full-screen loader — only on first ever load (no prior data) */}
          {showFullLoader && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            >
              <GlassCard className="flex flex-col items-center justify-center py-20 gap-4">
                <Loader2 size={32} className="text-violet-400 animate-spin" />
                <p className="text-sm text-slate-400 font-mono">Computing SHAP values…</p>
              </GlassCard>
            </motion.div>
          )}

          {/* Error — full-screen only when there is no previous data to fall back on */}
          {!explainLoading && explainError && !explain && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            >
              <GlassCard className="flex flex-col items-center justify-center py-20 gap-3">
                <AlertCircle size={32} className="text-red-400" />
                <p className="text-sm font-medium text-red-300">Explanation failed</p>
                <p className="text-xs text-slate-500 font-mono text-center max-w-xs">{explainError}</p>
                <p className="text-xs text-slate-600">
                  Ensure <code className="font-mono">POST /predict-explain</code> is available on the backend.
                </p>
              </GlassCard>
            </motion.div>
          )}

          {/* Live data — also shown while a refresh is loading (keep-previous UX) */}
          {hasData && (
            <motion.div
              key="data"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* In-data refresh indicator — shown while a new request is in-flight */}
              {explainLoading && (
                <motion.div
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 text-xs text-slate-500 font-mono"
                >
                  <Loader2 size={12} className="animate-spin text-violet-400" />
                  Refreshing SHAP values…
                </motion.div>
              )}

              {/* Inline error banner when prior data is still visible */}
              {!explainLoading && explainError && (
                <div className="flex items-center gap-2 text-xs text-red-400 font-mono bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                  <AlertCircle size={12} />
                  Last refresh failed: {explainError} — showing previous result.
                </div>
              )}

              {/* Prediction decomposition summary */}
              <PredictionSummary
                baseValue={explain.base_value}
                delta={explain.prediction_delta}
                predictedGhi={explain.predicted_ghi}
              />

              {/* SHAP bar chart */}
              <div className="grid lg:grid-cols-2 gap-6 mb-8">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                >
                  <GlassCard className="h-full">
                    <p className="section-label mb-1">Feature SHAP Values</p>
                    <p className="text-xs text-slate-500 mb-4">
                      Signed impact on GHI · top 10 by |SHAP| · amber = lifts, blue = suppresses
                    </p>
                    <div className="flex gap-4 mb-4">
                      {Object.entries(DIRECTION_COLOR).map(([dir, color]) => (
                        <span key={dir} className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                          <span className="w-2 h-2 rounded-full" style={{ background: color }} />
                          {dir === 'positive' ? 'Lifts GHI' : 'Suppresses GHI'}
                        </span>
                      ))}
                    </div>

                    {chartData.length === 0 ? (
                      <p className="text-xs text-slate-500 py-8 text-center">No SHAP data available.</p>
                    ) : (
                      <ResponsiveContainer width="100%" height={320}>
                        <BarChart
                          data={chartData}
                          layout="vertical"
                          barSize={14}
                          margin={{ left: 10, right: 30 }}
                        >
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="rgba(255,255,255,0.04)"
                            horizontal={false}
                          />
                          <XAxis
                            type="number"
                            domain={xDomain}
                            tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(v) => v.toFixed(3)}
                          />
                          <YAxis
                            type="category"
                            dataKey="feature"
                            width={120}
                            tick={{ fill: '#94a3b8', fontSize: 10, fontFamily: 'JetBrains Mono' }}
                            axisLine={false}
                            tickLine={false}
                          />
                          {/* Zero-line so negative bars have a clear visual anchor */}
                          <ReferenceLine
                            x={0}
                            stroke="rgba(255,255,255,0.15)"
                            strokeWidth={1}
                          />
                          <Tooltip
                            content={<CustomTooltip />}
                            cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                          />
                          {/*
                            radius must NOT be applied here via the Bar prop when bars
                            span both sides of zero — Recharts applies the radius to
                            the wrong end for negative values. We apply it per-Cell
                            instead, rounding only the "far" end away from the axis.
                          */}
                          <Bar dataKey="shap">
                            {chartData.map((d, i) => (
                              <Cell
                                key={i}
                                fill={DIRECTION_COLOR[d.direction]}
                                fillOpacity={0.85}
                                radius={
                                  d.shap >= 0
                                    ? [0, 4, 4, 0]   // positive: round right end
                                    : [4, 0, 0, 4]   // negative: round left end
                                }
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </GlassCard>
                </motion.div>

                {/* Stats panel */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                >
                  <GlassCard className="h-full flex flex-col gap-4">
                    <div>
                      <p className="section-label mb-1">Explanation Summary</p>
                      <p className="text-xs text-slate-500">Derived from live SHAP computation</p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 flex-1">
                      {[
                        {
                          label: 'Predicted GHI',
                          value: `${explain.predicted_ghi.toFixed(3)} kWh/m²/d`,
                          color: '#f59e0b',
                        },
                        {
                          label: 'Base Value',
                          value: explain.base_value.toFixed(3),
                          color: '#94a3b8',
                        },
                        {
                          label: 'SHAP Δ',
                          value: `${explain.prediction_delta >= 0 ? '+' : ''}${explain.prediction_delta.toFixed(3)}`,
                          color: explain.prediction_delta >= 0 ? '#f59e0b' : '#38bdf8',
                        },
                        {
                          label: 'Features Explained',
                          value: Object.keys(explain.feature_shap_values ?? {}).length,
                          color: '#a78bfa',
                        },
                        {
                          label: 'Top Positive',
                          value: positiveFeatures.length,
                          color: '#f59e0b',
                        },
                        {
                          label: 'Top Negative',
                          value: negativeFeatures.length,
                          color: '#38bdf8',
                        },
                      ].map(({ label, value, color }) => (
                        <div
                          key={label}
                          className="bg-ink-900/60 rounded-xl px-3 py-3 border border-white/[0.05]"
                        >
                          <div className="text-[10px] font-mono text-slate-500 mb-1">{label}</div>
                          <div className="text-sm font-semibold" style={{ color }}>{value}</div>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                </motion.div>
              </div>

              {/* Positive feature cards */}
              {positiveFeatures.length > 0 && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <TrendingUp size={16} className="text-solar-400" />
                    <p className="text-sm font-semibold text-white">
                      Top Features <span className="text-solar-400">Lifting GHI</span>
                    </p>
                    <Badge variant="solar">{positiveFeatures.length} features</Badge>
                  </div>
                  <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
                    {positiveFeatures.map((f, i) => (
                      <FeatureCard
                        key={f.feature ?? i}
                        index={i}
                        feature={f.feature}
                        shapValue={f.shap_value}
                        featureValue={f.feature_value}
                        colorHex="#f59e0b"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Negative feature cards */}
              {negativeFeatures.length > 0 && (
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <TrendingDown size={16} className="text-sky-400" />
                    <p className="text-sm font-semibold text-white">
                      Top Features <span className="text-sky-400">Suppressing GHI</span>
                    </p>
                    <Badge variant="data">{negativeFeatures.length} features</Badge>
                  </div>
                  <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
                    {negativeFeatures.map((f, i) => (
                      <FeatureCard
                        key={f.feature ?? i}
                        index={i}
                        feature={f.feature}
                        shapValue={f.shap_value}
                        featureValue={f.feature_value}
                        colorHex="#38bdf8"
                      />
                    ))}
                  </div>
                </div>
              )}

            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}
