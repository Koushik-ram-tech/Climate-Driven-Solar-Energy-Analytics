import { motion } from 'framer-motion'
import { Sun, Leaf, MapPin, Cpu, BarChart2, Building } from 'lucide-react'
import { GlassCard } from '../ui/GlassCard'
import { AnimatedNumber } from '../ui/AnimatedNumber'

const IMPACT_STATS = [
  { icon: Sun,      value: 748,  suffix: ' GW', label: 'India\'s solar potential',    color: '#f59e0b', src: 'MNRE 2023' },
  { icon: Leaf,     value: 40,   suffix: '%',   label: 'Non-fossil target by 2030',   color: '#4ade80', src: 'India NDC' },
  { icon: MapPin,   value: 15,   suffix: '',    label: 'Cities modelled',             color: '#22d3ee', src: 'This project' },
  { icon: BarChart2,value: 88.3, suffix: '%',   label: 'Variance explained (R²)',     color: '#a78bfa', src: 'XGBoost model' },
]

const APPLICATIONS = [
  {
    icon: Building,
    title: 'Utility-Scale Grid Planning',
    desc: 'Accurate daily GHI forecasts help grid operators schedule storage dispatch and balance supply with intermittent solar generation.',
    color: '#f59e0b',
  },
  {
    icon: Sun,
    title: 'Rooftop Solar Sizing',
    desc: 'Site-specific irradiance estimates enable accurate panel sizing for residential and commercial rooftop installations across India.',
    color: '#22d3ee',
  },
  {
    icon: Cpu,
    title: 'Agricultural Solar Pumps',
    desc: 'Forecasting helps farmers schedule irrigation based on expected solar availability, reducing dependence on diesel pumps.',
    color: '#4ade80',
  },
  {
    icon: Leaf,
    title: 'Carbon Offset Verification',
    desc: 'Baseline irradiance models are a component of Measurement, Reporting and Verification (MRV) frameworks for renewable projects.',
    color: '#a78bfa',
  },
]

export function ResearchSection() {
  return (
    <section id="research" className="relative py-32 overflow-hidden">
      <div className="orb w-[500px] h-[500px] bg-solar-500/6 bottom-0 left-0" />

      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ duration: 0.6 }} className="mb-12">
          <p className="section-label mb-3">Section 08</p>
          <h2 className="text-4xl font-bold text-white mb-4">Research Impact</h2>
          <p className="text-slate-400 max-w-xl">
            Solar irradiance forecasting is a foundational problem in renewable energy — 
            accurate predictions enable smarter grid operations, better investment decisions,
            and India's transition to clean energy.
          </p>
        </motion.div>

        {/* Impact stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {IMPACT_STATS.map((s, i) => {
            const Icon = s.icon
            return (
              <motion.div key={s.label}
                initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
                transition={{ delay: i * 0.08 }}>
                <GlassCard className="text-center">
                  <div className="w-10 h-10 rounded-xl mx-auto mb-4 flex items-center justify-center"
                    style={{ background: `${s.color}15`, border: `1px solid ${s.color}30` }}>
                    <Icon size={18} style={{ color: s.color }} />
                  </div>
                  <div className="text-3xl font-bold mb-1" style={{ color: s.color }}>
                    <AnimatedNumber value={s.value} decimals={s.value % 1 !== 0 ? 1 : 0} />{s.suffix}
                  </div>
                  <div className="text-xs text-slate-400 mb-1">{s.label}</div>
                  <div className="text-[10px] font-mono text-slate-600">{s.src}</div>
                </GlassCard>
              </motion.div>
            )
          })}
        </div>

        {/* Applications */}
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4 mb-10">
          {APPLICATIONS.map((app, i) => {
            const Icon = app.icon
            return (
              <motion.div key={app.title}
                initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
                transition={{ delay: i * 0.07 }}>
                <GlassCard className="h-full">
                  <div className="w-9 h-9 rounded-lg mb-4 flex items-center justify-center"
                    style={{ background: `${app.color}15`, border: `1px solid ${app.color}30` }}>
                    <Icon size={16} style={{ color: app.color }} />
                  </div>
                  <p className="text-sm font-semibold text-white mb-2">{app.title}</p>
                  <p className="text-xs text-slate-400 leading-relaxed">{app.desc}</p>
                </GlassCard>
              </motion.div>
            )
          })}
        </div>

        {/* Model summary card */}
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ delay: 0.2 }}>
          <GlassCard hover={false} glow="solar">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <p className="section-label mb-3">About the Model</p>
                <h3 className="text-2xl font-bold text-white mb-4">XGBoost Regressor</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-6">
                  Gradient boosted tree ensemble trained on 4 years of daily observations across 
                  15 Indian cities. SHAP-explainable, StandardScaler-preprocessed, 
                  and deployable via FastAPI with sub-millisecond inference latency.
                </p>
                <div className="flex flex-wrap gap-2">
                  {['SHAP Explainable','31 Features','15 Cities','6 Years Data','GridSearchCV Tuned','FastAPI Ready'].map(t => (
                    <span key={t} className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-solar-500/10 text-solar-300 border border-solar-500/20">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { k: 'Algorithm',    v: 'XGBoost',           c: '#f59e0b' },
                  { k: 'Objective',    v: 'reg:squarederror',  c: '#22d3ee' },
                  { k: 'R² (test)',    v: '0.8831',            c: '#4ade80' },
                  { k: 'RMSE',        v: '0.4941 kWh/m²',     c: '#a78bfa' },
                  { k: 'MAE',         v: '0.3583 kWh/m²',     c: '#f472b6' },
                  { k: 'MAPE',        v: '9.71%',              c: '#fb923c' },
                ].map(({ k, v, c }) => (
                  <div key={k} className="bg-ink-900/60 rounded-xl px-3 py-3 border border-white/[0.05]">
                    <div className="text-[10px] font-mono text-slate-500 mb-0.5">{k}</div>
                    <div className="text-sm font-semibold" style={{ color: c }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  )
}
