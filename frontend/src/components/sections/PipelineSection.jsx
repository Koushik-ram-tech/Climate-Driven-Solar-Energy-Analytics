import { motion } from 'framer-motion'
import { Database, Wrench, GitBranch, TrendingUp, Brain, Server, Monitor } from 'lucide-react'
import { GlassCard } from '../ui/GlassCard'

const STEPS = [
  {
    icon: Database,
    label: 'NASA POWER',
    sublabel: 'Data Ingestion',
    desc: '6 years of daily climate data for 15 Indian cities fetched from NASA POWER API (2019–2024). Meteorological variables: T2M, RH2M, CLOUD_AMT, WS10M, PRECTOTCORR, PS.',
    color: '#22d3ee',
    tag: 'nb01–nb03',
  },
  {
    icon: Wrench,
    label: 'Data Cleaning',
    sublabel: 'Quality Assurance',
    desc: 'Missing value imputation, outlier detection, dtype normalisation. Temporal sorting to preserve day-over-day relationships needed for lag features.',
    color: '#a78bfa',
    tag: 'nb04',
  },
  {
    icon: GitBranch,
    label: 'Feature Engineering',
    sublabel: 'Domain + Statistical',
    desc: 'log1p(PREC), WIND_CLOUD interaction, cyclic MONTH_SIN/COS, IS_MONSOON flag, GHI lag features (1d, 7d rolling mean), lagged humidity and cloud.',
    color: '#f59e0b',
    tag: 'nb05–nb06',
  },
  {
    icon: TrendingUp,
    label: 'VIF Analysis',
    sublabel: 'Multicollinearity',
    desc: 'Iterative VIF rounds to eliminate collinear temperature variables. Final set: T2M_MAX + TEMP_RANGE retain thermal signal without redundancy.',
    color: '#4ade80',
    tag: 'nb06',
  },
  {
    icon: Brain,
    label: 'XGBoost Training',
    sublabel: 'GridSearchCV',
    desc: 'Train on 2019–2022 · GridSearchCV over learning_rate, max_depth, n_estimators. Best: lr=0.05, depth=6, n=200. StandardScaler applied pre-fit.',
    color: '#f472b6',
    tag: 'nb07–nb08',
  },
  {
    icon: Brain,
    label: 'SHAP Analysis',
    sublabel: 'Explainability',
    desc: 'shap.TreeExplainer on full test set. Global feature importances reveal precipitation and cloud cover dominate; city effects are absorbed by climate variables.',
    color: '#fb923c',
    tag: 'nb09',
  },
  {
    icon: Server,
    label: 'FastAPI',
    sublabel: 'Deployment',
    desc: 'Artefacts (XGBoost pkl, StandardScaler pkl, nb08_meta.json) loaded at startup via joblib. CORS-enabled REST API with /health and /test-predict endpoints.',
    color: '#22d3ee',
    tag: 'backend/',
  },
  {
    icon: Monitor,
    label: 'Dashboard',
    sublabel: 'This Interface',
    desc: 'React + Vite + Tailwind CSS + Framer Motion frontend consuming live FastAPI endpoints. SHAP visualisation, VIF explorer, pipeline view.',
    color: '#f59e0b',
    tag: 'frontend/',
  },
]

export function PipelineSection() {
  return (
    <section id="pipeline" className="relative py-32 overflow-hidden">
      <div className="orb w-[500px] h-[500px] bg-solar-500/5 -top-20 left-1/2 -translate-x-1/2" />

      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ duration: 0.6 }} className="mb-16">
          <p className="section-label mb-3">Section 06</p>
          <h2 className="text-4xl font-bold text-white mb-4">ML Pipeline</h2>
          <p className="text-slate-400 max-w-xl">
            End-to-end journey from raw climate data to a live inference API,
            across 9 Jupyter notebooks and a production FastAPI deployment.
          </p>
        </motion.div>

        {/* Desktop: horizontal timeline */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Connecting line */}
            <motion.div
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
              style={{ transformOrigin: 'left' }}
              className="absolute top-10 left-0 right-0 h-px bg-gradient-to-r from-data-500/20 via-solar-500/40 to-data-500/20"
            />

            <div className="grid grid-cols-8 gap-3">
              {STEPS.map((step, i) => {
                const Icon = step.icon
                return (
                  <motion.div
                    key={step.label}
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.08, duration: 0.5 }}
                    className="relative group"
                  >
                    {/* Node */}
                    <div className="flex justify-center mb-4">
                      <div className="w-10 h-10 rounded-full border-2 flex items-center justify-center z-10 relative
                        bg-ink-900 transition-all duration-300 group-hover:scale-125 group-hover:shadow-lg"
                        style={{ borderColor: step.color, boxShadow: `0 0 0 0 ${step.color}` }}>
                        <Icon size={16} style={{ color: step.color }} />
                      </div>
                    </div>

                    {/* Label */}
                    <div className="text-center mb-2">
                      <div className="text-xs font-semibold text-white leading-tight">{step.label}</div>
                      <div className="text-[10px] font-mono text-slate-500 mt-0.5">{step.tag}</div>
                    </div>

                    {/* Hover tooltip */}
                    <div className="absolute top-16 left-1/2 -translate-x-1/2 w-48 z-20 pointer-events-none
                      opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <div className="bg-ink-800 border rounded-xl p-3 shadow-xl text-center"
                        style={{ borderColor: `${step.color}30` }}>
                        <p className="text-[10px] font-mono mb-1" style={{ color: step.color }}>{step.sublabel}</p>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{step.desc}</p>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Mobile: vertical list */}
        <div className="lg:hidden space-y-4">
          {STEPS.map((step, i) => {
            const Icon = step.icon
            return (
              <motion.div key={step.label}
                initial={{ opacity:0, x:-20 }} whileInView={{ opacity:1, x:0 }} viewport={{ once:true }}
                transition={{ delay: i * 0.06 }}>
                <GlassCard className="flex gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                    style={{ background: `${step.color}15`, border: `1px solid ${step.color}30` }}>
                    <Icon size={16} style={{ color: step.color }} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-white">{step.label}</span>
                      <code className="text-[10px] font-mono text-slate-500">{step.tag}</code>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
                  </div>
                </GlassCard>
              </motion.div>
            )
          })}
        </div>

        {/* Architecture boxes */}
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ delay: 0.3 }} className="mt-12">
          <GlassCard hover={false}>
            <p className="section-label mb-5">System Architecture</p>
            <div className="grid md:grid-cols-5 gap-3">
              {[
                { tier: 'Data Layer',    items: ['NASA POWER API','15 cities, 2019–2024','~32K daily records'], color: '#22d3ee' },
                { tier: 'ML Layer',      items: ['XGBoost (pkl)','StandardScaler (pkl)','nb08_meta.json'],      color: '#f59e0b' },
                { tier: 'XAI Layer',     items: ['SHAP TreeExplainer','Feature importances','Trust & audit'],   color: '#a78bfa' },
                { tier: 'API Layer',     items: ['FastAPI 0.115','GET /health',  'GET /test-predict'],          color: '#4ade80' },
                { tier: 'Frontend',      items: ['React + Vite','Recharts + Framer','Tailwind dark theme'],     color: '#f472b6' },
              ].map(({ tier, items, color }) => (
                <div key={tier} className="rounded-xl p-4 border" style={{ background: `${color}08`, borderColor: `${color}20` }}>
                  <div className="text-xs font-semibold mb-3" style={{ color }}>{tier}</div>
                  {items.map(it => (
                    <div key={it} className="text-[11px] text-slate-400 py-0.5 border-b border-white/[0.03] last:border-0">{it}</div>
                  ))}
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  )
}
