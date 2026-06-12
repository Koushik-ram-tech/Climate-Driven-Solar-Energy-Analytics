import { motion } from 'framer-motion'
import { Sun, Zap, TrendingUp, Globe } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { GlassCard } from '../ui/GlassCard'

const fade   = (delay = 0) => ({ initial: { opacity:0, y:20 }, animate: { opacity:1, y:0 }, transition: { duration:0.7, delay, ease:'easeOut' } })
const CITIES = ['Bengaluru','Delhi','Mumbai','Chennai','Kolkata','Hyderabad','Jaipur','Pune','Ahmedabad','Kochi']

export function HeroSection({ health }) {
  return (
    <section id="hero" className="relative min-h-screen flex flex-col justify-center overflow-hidden pt-20">

      {/* ── Ambient background ── */}
      <div className="absolute inset-0 bg-grid-ink bg-grid-48 opacity-100 pointer-events-none" />
      <div className="orb w-[600px] h-[600px] bg-solar-500/8 -top-40 -left-40 animate-drift" />
      <div className="orb w-[500px] h-[500px] bg-data-500/6 top-1/3 -right-32" style={{ animationDelay: '-5s' }} />
      <div className="orb w-[300px] h-[300px] bg-amber-600/5 bottom-10 left-1/3" />

      <div className="relative max-w-7xl mx-auto px-6 py-24">
        <div className="grid lg:grid-cols-2 gap-16 items-center">

          {/* ── Left copy ── */}
          <div>
            <motion.div {...fade(0.1)} className="flex items-center gap-3 mb-8">
              <Badge variant="solar">MCA Major Project · 2024</Badge>
              <Badge variant="live" dot>XGBoost Active</Badge>
            </motion.div>

            <motion.h1 {...fade(0.2)} className="text-5xl lg:text-6xl font-bold leading-[1.05] tracking-tight mb-6">
              <span className="text-white">Climate-Driven</span>
              <br />
              <span className="text-gradient-solar">Solar Energy</span>
              <br />
              <span className="text-white">Analytics</span>
            </motion.h1>

            <motion.p {...fade(0.35)} className="text-slate-400 text-lg leading-relaxed max-w-lg mb-10">
              XGBoost regression model predicting Global Horizontal Irradiance (GHI) 
              across <span className="text-slate-200">15 Indian cities</span> using 
              NASA POWER climate data, engineered features, and SHAP explainability.
            </motion.p>

            <motion.div {...fade(0.45)} className="flex flex-wrap gap-3 mb-12">
              {[
                { icon: TrendingUp, label: 'R² = 0.8831', sub: 'Explained Variance' },
                { icon: Zap,        label: '9.71% MAPE',  sub: 'Prediction Error' },
                { icon: Globe,      label: '15 Cities',   sub: 'Across India' },
              ].map(({ icon: Icon, label, sub }) => (
                <div key={label} className="flex items-center gap-2.5 bg-white/[0.04] border border-white/[0.07] rounded-xl px-4 py-2.5">
                  <Icon size={14} className="text-solar-400" />
                  <div>
                    <div className="text-sm font-semibold text-white">{label}</div>
                    <div className="text-[10px] text-slate-500">{sub}</div>
                  </div>
                </div>
              ))}
            </motion.div>

            <motion.div {...fade(0.55)} className="flex gap-3">
              <a href="#predict" className="px-6 py-3 bg-solar-500 hover:bg-solar-400 text-ink-950 font-semibold rounded-xl text-sm transition-colors shadow-glow-solar">
                Run Prediction
              </a>
              <a href="#performance" className="px-6 py-3 bg-white/[0.06] hover:bg-white/[0.10] text-white font-medium rounded-xl text-sm border border-white/[0.08] transition-colors">
                View Metrics
              </a>
            </motion.div>
          </div>

          {/* ── Right: live status panel ── */}
          <motion.div {...fade(0.4)} className="space-y-4">
            <GlassCard className="border-solar-500/10" glow="solar">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="section-label mb-1">Backend Status</p>
                  <p className="text-base font-semibold text-white">Inference Engine</p>
                </div>
                <div className={`w-2 h-2 rounded-full mt-1 ${health ? 'bg-live-400 animate-pulse' : 'bg-red-500'}`} />
              </div>
              {health ? (
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { k: 'Model',    v: health.model },
                    { k: 'Features', v: `${health.n_features} inputs` },
                    { k: 'R²',       v: health.xgboost_test_r2 },
                    { k: 'RMSE',     v: `${health.xgboost_test_rmse} kWh/m²` },
                  ].map(({ k, v }) => (
                    <div key={k} className="bg-ink-900/60 rounded-lg px-3 py-2.5">
                      <div className="text-[10px] text-slate-500 font-mono mb-0.5">{k}</div>
                      <div className="text-sm font-medium text-white">{String(v)}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-slate-500 font-mono">Backend not reachable — start FastAPI on :8000</div>
              )}
            </GlassCard>

            {/* Scrolling city ticker */}
            <GlassCard hover={false} className="overflow-hidden py-4">
              <p className="section-label mb-3">Coverage — 15 Indian Cities</p>
              <div className="relative overflow-hidden">
                <motion.div
                  animate={{ x: ['0%', '-50%'] }}
                  transition={{ duration: 24, repeat: Infinity, ease: 'linear' }}
                  className="flex gap-2 whitespace-nowrap"
                >
                  {[...CITIES, ...CITIES].map((c, i) => (
                    <span key={i} className="inline-flex items-center gap-1.5 bg-ink-900/80 border border-white/[0.06] rounded-full px-3 py-1 text-xs text-slate-300">
                      <Sun size={10} className="text-solar-400" />
                      {c}
                    </span>
                  ))}
                </motion.div>
              </div>
            </GlassCard>

            <GlassCard hover={false} className="py-4">
              <p className="section-label mb-3">Training Data</p>
              <div className="flex gap-2">
                {[2019,2020,2021,2022,2023,2024].map(y => (
                  <div key={y} className={`flex-1 text-center py-2 rounded-lg text-xs font-mono font-medium border transition-colors
                    ${y <= 2022
                      ? 'bg-solar-500/10 text-solar-300 border-solar-500/20'
                      : 'bg-data-500/10  text-data-300  border-data-500/20'
                    }`}>
                    {y}
                    <div className="text-[9px] text-current/60 mt-0.5">{y<=2022?'Train':'Test'}</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
