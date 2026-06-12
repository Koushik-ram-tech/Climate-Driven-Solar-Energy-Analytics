import { motion } from 'framer-motion'
import { GlassCard } from '../ui/GlassCard'
import { Badge } from '../ui/Badge'
import { CheckCircle2, XCircle, ArrowRight } from 'lucide-react'

const VIF_ROUNDS = [
  {
    round: 'Round 1 — Original Features',
    status: 'fail',
    rows: [
      { feature: 'T2M',      vif: '173.59', sev: 'Severe',  color: '#ef4444' },
      { feature: 'T2M_MIN',  vif: '72.57',  sev: 'Severe',  color: '#ef4444' },
      { feature: 'T2M_MAX',  vif: '49.31',  sev: 'Severe',  color: '#ef4444' },
      { feature: 'RH2M',     vif: '4.52',   sev: 'Low',     color: '#4ade80' },
      { feature: 'CLOUD_AMT',vif: '1.94',   sev: 'Low',     color: '#4ade80' },
      { feature: 'WS10M',    vif: '1.20',   sev: 'Low',     color: '#4ade80' },
    ],
    note: 'T2M, T2M_MIN, T2M_MAX are perfectly collinear — all encode air temperature.',
  },
  {
    round: 'Round 2B — Drop T2M',
    status: 'fail',
    rows: [
      { feature: 'T2M_MAX',   vif: '∞',    sev: 'Severe', color: '#ef4444' },
      { feature: 'T2M_MIN',   vif: '∞',    sev: 'Severe', color: '#ef4444' },
      { feature: 'TEMP_RANGE',vif: '∞',    sev: 'Severe', color: '#ef4444' },
      { feature: 'RH2M',      vif: '4.46', sev: 'Low',    color: '#4ade80' },
    ],
    note: 'Dropping T2M exposes perfect linear dependence between T2M_MAX, T2M_MIN, and TEMP_RANGE.',
  },
  {
    round: 'Round 2C — T2M_MAX + TEMP_RANGE (final)',
    status: 'pass',
    rows: [
      { feature: 'T2M_MAX',   vif: '1.55', sev: 'Low', color: '#4ade80' },
      { feature: 'TEMP_RANGE',vif: '4.87', sev: 'Low', color: '#4ade80' },
      { feature: 'RH2M',      vif: '4.46', sev: 'Low', color: '#4ade80' },
      { feature: 'CLOUD_AMT', vif: '1.94', sev: 'Low', color: '#4ade80' },
      { feature: 'WS10M',     vif: '1.16', sev: 'Low', color: '#4ade80' },
      { feature: 'PS',        vif: '1.15', sev: 'Low', color: '#4ade80' },
    ],
    note: 'Retaining T2M_MAX (peak heat) and TEMP_RANGE (diurnal swing) eliminates multicollinearity. All VIF < 10.',
  },
]

const ENGINEERED = [
  { name: 'log1p_PREC',    desc: 'Log-transform of precipitation — compresses right-skewed rainfall distribution', tag: 'transform' },
  { name: 'WIND_CLOUD',    desc: 'WS10M × CLOUD_AMT interaction — encodes how wind disperses cloud cover', tag: 'interaction' },
  { name: 'MONTH_SIN/COS', desc: 'Cyclic encoding of month — preserves Dec→Jan continuity in seasonal pattern', tag: 'cyclic' },
  { name: 'IS_MONSOON',    desc: 'Binary flag for June–September monsoon window — captures regime shift', tag: 'domain' },
  { name: 'GHI_LAG1',      desc: 'Yesterday\'s GHI — solar irradiance is autocorrelated day-to-day', tag: 'temporal' },
  { name: 'GHI_7DAY_MEAN', desc: 'Rolling 7-day mean GHI — smoothed trend baseline', tag: 'temporal' },
  { name: 'RH2M_LAG1',     desc: 'Lagged humidity — moisture persists across days', tag: 'temporal' },
  { name: 'CLOUD_LAG1',    desc: 'Lagged cloud cover — cloud patterns have inertia', tag: 'temporal' },
]

const TAG_COLORS = {
  transform:   'bg-solar-500/10 text-solar-300 border-solar-500/20',
  interaction: 'bg-data-500/10  text-data-300  border-data-500/20',
  cyclic:      'bg-violet-500/10 text-violet-300 border-violet-500/20',
  domain:      'bg-pink-500/10  text-pink-300   border-pink-500/20',
  temporal:    'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
}

export function VIFSection() {
  return (
    <section id="features" className="relative py-32 overflow-hidden">
      <div className="orb w-[400px] h-[400px] bg-emerald-500/5 bottom-0 right-0" />

      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ duration: 0.6 }} className="mb-12">
          <p className="section-label mb-3">Section 05</p>
          <h2 className="text-4xl font-bold text-white mb-4">Feature Engineering</h2>
          <p className="text-slate-400 max-w-xl">
            Multicollinearity analysis (VIF) drove principled feature selection.
            Eight additional features were engineered from domain knowledge and temporal autocorrelation.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-6 mb-10">
          {VIF_ROUNDS.map((r, i) => (
            <motion.div key={r.round}
              initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
              transition={{ delay: i * 0.1 }}>
              <GlassCard className="h-full flex flex-col">
                <div className="flex items-center gap-2 mb-4">
                  {r.status === 'pass'
                    ? <CheckCircle2 size={16} className="text-live-400 shrink-0" />
                    : <XCircle     size={16} className="text-red-400   shrink-0" />
                  }
                  <p className="text-xs font-semibold text-white">{r.round}</p>
                </div>
                <div className="space-y-1.5 flex-1 mb-4">
                  {r.rows.map(row => (
                    <div key={row.feature} className="flex items-center justify-between bg-ink-900/60 rounded-lg px-3 py-2 border border-white/[0.04]">
                      <span className="text-xs font-mono text-slate-300">{row.feature}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-semibold" style={{ color: row.color }}>{row.vif}</span>
                        <span className="text-[10px] text-slate-600">{row.sev}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 leading-relaxed border-t border-white/[0.06] pt-3">{r.note}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Engineered features */}
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ delay: 0.2 }}>
          <GlassCard hover={false}>
            <p className="section-label mb-1">Engineered Features</p>
            <p className="text-xs text-slate-500 mb-5">8 derived features added to the 16 raw meteorological inputs = 31 total (+ 15 city one-hot)</p>
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-3">
              {ENGINEERED.map((f, i) => (
                <motion.div key={f.name}
                  initial={{ opacity:0, scale:0.97 }} whileInView={{ opacity:1, scale:1 }} viewport={{ once:true }}
                  transition={{ delay: i * 0.04 }}
                  className="bg-ink-900/60 rounded-xl p-3.5 border border-white/[0.06]">
                  <div className="flex items-center justify-between mb-2">
                    <code className="text-xs font-mono font-semibold text-white">{f.name}</code>
                    <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded-full border ${TAG_COLORS[f.tag]}`}>
                      {f.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">{f.desc}</p>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  )
}
