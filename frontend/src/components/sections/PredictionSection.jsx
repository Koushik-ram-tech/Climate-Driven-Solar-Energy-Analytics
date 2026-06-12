import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap, Sun, Wind, Droplets, Thermometer, Cloud,
  Loader2, AlertCircle, CalendarDays, MapPin,
} from 'lucide-react'
import { GlassCard } from '../ui/GlassCard'
import { Badge }     from '../ui/Badge'

// ─── GHI scale ───────────────────────────────────────────────────────────────
const GHI_SCALE = [
  { min: 0,   max: 2,   label: 'Very Low',  color: '#475569' },
  { min: 2,   max: 3.5, label: 'Low',       color: '#0ea5e9' },
  { min: 3.5, max: 5,   label: 'Moderate',  color: '#f59e0b' },
  { min: 5,   max: 6,   label: 'High',      color: '#f97316' },
  { min: 6,   max: 10,  label: 'Very High', color: '#ef4444' },
]

function ghiColor(val) {
  return GHI_SCALE.find(s => val >= s.min && val < s.max)?.color ?? '#f59e0b'
}
function ghiLabel(val) {
  return GHI_SCALE.find(s => val >= s.min && val < s.max)?.label ?? 'High'
}

// ─── FeatureChip ─────────────────────────────────────────────────────────────
function FeatureChip({ icon: Icon, label, value, unit }) {
  return (
    <div className="flex items-center gap-2 bg-ink-900/60 rounded-xl px-3 py-2.5 border border-white/[0.05]">
      <Icon size={13} className="text-data-400 shrink-0" />
      <div className="min-w-0">
        <div className="text-[10px] font-mono text-slate-500 truncate">{label}</div>
        <div className="text-xs font-medium text-white">
          {typeof value === 'number' ? value.toFixed(1) : value}{' '}
          <span className="text-slate-500 text-[10px]">{unit}</span>
        </div>
      </div>
    </div>
  )
}

// ─── Styled select / input helpers ───────────────────────────────────────────
/** Shared class string for control elements inside the glass card */
const inputCls =
  'w-full bg-ink-900/80 border border-white/[0.08] rounded-xl px-4 py-3 ' +
  'text-sm text-white focus:outline-none focus:border-solar-500/50 ' +
  'transition-colors appearance-none'

// ─── PredictionSection ───────────────────────────────────────────────────────
export function PredictionSection({
  cities = [],
  selectedCity,
  setSelectedCity,
  selectedDate,
  setSelectedDate,
  prediction,
  predLoading,
  predError,
  onPredict,
}) {
  // POST /predict returns a flat response — no nested .prediction object
  const ghi      = prediction?.predicted_ghi
  const weather  = prediction?.weather_snapshot

  return (
    <section id="predict" className="relative py-32 overflow-hidden">
      <div className="orb w-[400px] h-[400px] bg-solar-500/6 top-0 right-0" />

      <div className="max-w-7xl mx-auto px-6">

        {/* ── Section header — unchanged ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <p className="section-label mb-3">Section 02</p>
          <h2 className="text-4xl font-bold text-white mb-4">Prediction Center</h2>
          <p className="text-slate-400 max-w-xl">
            Select a city and date, then fire the live inference endpoint to see how the
            XGBoost model processes real-time climate features to estimate daily solar irradiance.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-6">

          {/* ── Controls panel ── */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-2 space-y-4"
          >
            <GlassCard className="space-y-5">
              <div>
                <p className="section-label mb-2">Prediction Configuration</p>
                <p className="text-xs text-slate-500">
                  Choose a city and date. The backend fetches live weather from Open-Meteo,
                  builds the 31-feature vector, and runs{' '}
                  <span className="font-mono text-data-400">POST /predict</span>.
                </p>
              </div>

              {/* City selector */}
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-2">
                  City
                </label>
                <div className="relative">
                  <MapPin
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-solar-400 pointer-events-none"
                  />
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className={`${inputCls} pl-9 cursor-pointer`}
                    style={{ colorScheme: 'dark' }}
                  >
                    {cities.length > 0
                      ? cities.map((c) => (
                          <option key={c} value={c} className="bg-ink-900">
                            {c}
                          </option>
                        ))
                      : /* Fallback while cities are loading */
                        ['Bengaluru'].map((c) => (
                          <option key={c} value={c} className="bg-ink-900">
                            {c}
                          </option>
                        ))}
                  </select>
                </div>
              </div>

              {/* Date selector */}
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-2">
                  Date
                </label>
                <div className="relative">
                  <CalendarDays
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-solar-400 pointer-events-none"
                  />
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    min="2019-01-01"
                    max={new Date().toISOString().split('T')[0]}
                    className={`${inputCls} pl-9 cursor-pointer`}
                    style={{ colorScheme: 'dark' }}
                  />
                </div>
              </div>

              {/* Info chips */}
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div className="bg-ink-900/60 rounded-lg p-2.5 border border-white/[0.04]">
                  <div className="font-mono text-[10px] text-slate-600 mb-1">Endpoint</div>
                  <code className="text-data-400 text-[11px]">POST /predict</code>
                </div>
                <div className="bg-ink-900/60 rounded-lg p-2.5 border border-white/[0.04]">
                  <div className="font-mono text-[10px] text-slate-600 mb-1">Features</div>
                  <div className="text-white">31 inputs</div>
                </div>
              </div>

              {/* Run button */}
              <button
                onClick={onPredict}
                disabled={predLoading || !selectedCity || !selectedDate}
                className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl font-semibold text-sm
                  bg-solar-500 hover:bg-solar-400 disabled:opacity-60 disabled:cursor-not-allowed
                  text-ink-950 transition-colors shadow-glow-solar"
              >
                {predLoading
                  ? <><Loader2 size={16} className="animate-spin" /> Running Inference…</>
                  : <><Zap size={16} /> Run Prediction</>
                }
              </button>
            </GlassCard>

            {/* Weather snapshot chips — shown after prediction */}
            <AnimatePresence>
              {weather && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <GlassCard className="space-y-3">
                    <p className="section-label">Live Weather Snapshot</p>
                    <div className="grid grid-cols-2 gap-2">
                      <FeatureChip icon={Thermometer} label="T2M_MAX"     value={weather.T2M_MAX}      unit="°C"  />
                      <FeatureChip icon={Thermometer} label="TEMP_RANGE"  value={weather.TEMP_RANGE}   unit="°C"  />
                      <FeatureChip icon={Droplets}    label="RH2M"        value={weather.RH2M}         unit="%"   />
                      <FeatureChip icon={Wind}        label="WS10M"       value={weather.WS10M}        unit="m/s" />
                      <FeatureChip icon={Cloud}       label="CLOUD_AMT"   value={weather.CLOUD_AMT}    unit="%"   />
                      <FeatureChip icon={Droplets}    label="PRECIP"      value={weather.PRECTOTCORR}  unit="mm"  />
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* ── Result card — unchanged structure, updated data bindings ── */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-3"
          >
            <GlassCard className="h-full min-h-[340px] flex flex-col" glow={ghi ? 'solar' : undefined}>
              <div className="flex items-center justify-between mb-6">
                <p className="section-label">Prediction Output</p>
                {ghi && <Badge variant="solar">Live Result</Badge>}
              </div>

              <AnimatePresence mode="wait">

                {/* Loading */}
                {predLoading && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex-1 flex flex-col items-center justify-center gap-4"
                  >
                    <div className="relative w-20 h-20">
                      <div className="absolute inset-0 rounded-full border-2 border-solar-500/20 animate-spin-slow" />
                      <div
                        className="absolute inset-2 rounded-full border-2 border-solar-400/40 animate-spin"
                        style={{ animationDuration: '2s', animationDirection: 'reverse' }}
                      />
                      <Sun size={28} className="absolute inset-0 m-auto text-solar-400 animate-pulse" />
                    </div>
                    <p className="text-sm text-slate-400 font-mono">Querying inference engine…</p>
                  </motion.div>
                )}

                {/* Error */}
                {!predLoading && predError && (
                  <motion.div
                    key="error"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex-1 flex flex-col items-center justify-center gap-3"
                  >
                    <AlertCircle size={32} className="text-red-400" />
                    <p className="text-sm font-medium text-red-300">Prediction failed</p>
                    <p className="text-xs text-slate-500 font-mono text-center max-w-xs">{predError}</p>
                    <p className="text-xs text-slate-600">Ensure the FastAPI backend is running on port 8000</p>
                  </motion.div>
                )}

                {/* Idle */}
                {!predLoading && !predError && !ghi && (
                  <motion.div
                    key="idle"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="flex-1 flex flex-col items-center justify-center gap-4 text-center"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-solar-500/10 border border-solar-500/20 flex items-center justify-center">
                      <Sun size={28} className="text-solar-400/50" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-400">No prediction yet</p>
                      <p className="text-xs text-slate-600 mt-1">Select a city and date, then click "Run Prediction"</p>
                    </div>
                  </motion.div>
                )}

                {/* Result */}
                {!predLoading && !predError && ghi && (
                  <motion.div
                    key="result"
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.4 }}
                    className="flex-1 flex flex-col"
                  >
                    {/* Big GHI number */}
                    <div className="flex-1 flex flex-col items-center justify-center py-8">
                      <div className="relative">
                        <div
                          className="absolute inset-0 rounded-full blur-3xl opacity-30"
                          style={{ background: ghiColor(ghi) }}
                        />
                        <div className="relative text-center">
                          <div
                            className="text-7xl font-bold mb-1"
                            style={{ color: ghiColor(ghi) }}
                          >
                            {ghi.toFixed(2)}
                          </div>
                          <div className="text-sm font-mono text-slate-400">kWh / m² / day</div>
                        </div>
                      </div>
                      <Badge className="mt-6" variant="solar">{ghiLabel(ghi)} Solar Irradiance</Badge>
                    </div>

                    {/* Meta row — city, date, model */}
                    <div className="grid grid-cols-3 gap-3 border-t border-white/[0.06] pt-4">
                      {[
                        { label: 'City',       value: prediction.city },
                        { label: 'Date',        value: prediction.date },
                        { label: 'Model',       value: prediction.model_type },
                      ].map(({ label, value }) => (
                        <div key={label} className="text-center">
                          <div className="text-[10px] font-mono text-slate-500 mb-0.5">{label}</div>
                          <div className="text-xs font-medium text-white truncate">{value}</div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

              </AnimatePresence>
            </GlassCard>
          </motion.div>

        </div>
      </div>
    </section>
  )
}
