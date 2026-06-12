import { motion } from 'framer-motion'
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell } from 'recharts'
import { GlassCard } from '../ui/GlassCard'
import { AnimatedNumber } from '../ui/AnimatedNumber'
import { Badge } from '../ui/Badge'

const KPIs = [
  { label: 'R² Score',       value: 0.8831, display: '0.8831', suffix: '',   unit: 'Explained Variance', color: '#f59e0b', description: '88.3% of GHI variance explained by the model' },
  { label: 'RMSE',           value: 0.4941, display: '0.4941', suffix: '',   unit: 'kWh/m²/day',         color: '#22d3ee', description: 'Root Mean Squared Error on 2023–2024 test set' },
  { label: 'MAE',            value: 0.3583, display: '0.3583', suffix: '',   unit: 'kWh/m²/day',         color: '#a78bfa', description: 'Mean Absolute Error — robust to outliers' },
  { label: 'MAPE',           value: 9.71,   display: '9.71',   suffix: '%',  unit: 'Error Rate',         color: '#4ade80', description: 'Mean Absolute Percentage Error — industry standard' },
  { label: 'Features',       value: 31,     display: '31',     suffix: '',   unit: 'Input Dimensions',   color: '#fb923c', description: '16 meteorological + 15 city one-hot encodings' },
  { label: 'Cities',         value: 15,     display: '15',     suffix: '',   unit: 'Across India',       color: '#f472b6', description: 'Diverse climate zones from Guwahati to Kochi' },
]

const TRAIN_TEST = [
  { year: '2019', type: 'Train', ghi: 5.2, fill: '#f59e0b' },
  { year: '2020', type: 'Train', ghi: 5.0, fill: '#f59e0b' },
  { year: '2021', type: 'Train', ghi: 5.3, fill: '#f59e0b' },
  { year: '2022', type: 'Train', ghi: 5.1, fill: '#f59e0b' },
  { year: '2023', type: 'Test',  ghi: 5.2, fill: '#22d3ee' },
  { year: '2024', type: 'Test',  ghi: 5.15,fill: '#22d3ee' },
]

const R2_RADIAL = [{ name: 'R²', value: 88.31, fill: '#f59e0b' }, { name: 'Gap', value: 11.69, fill: '#1a2840' }]

function KPICard({ kpi, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
    >
      <GlassCard className="relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-20 h-20 rounded-full blur-2xl opacity-20 transition-opacity group-hover:opacity-40"
          style={{ background: kpi.color }} />
        <div className="relative">
          <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-3">{kpi.label}</p>
          <div className="text-4xl font-bold mb-1" style={{ color: kpi.color }}>
            <AnimatedNumber value={kpi.value} decimals={kpi.suffix === '%' ? 2 : 4} />{kpi.suffix}
          </div>
          <p className="text-[11px] text-slate-500 font-mono mb-3">{kpi.unit}</p>
          <p className="text-xs text-slate-400 leading-relaxed">{kpi.description}</p>
        </div>
      </GlassCard>
    </motion.div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-ink-800 border border-white/10 rounded-xl px-4 py-3 shadow-xl">
      <p className="text-xs font-mono text-slate-400 mb-1">{label}</p>
      <p className="text-sm font-semibold" style={{ color: payload[0].fill }}>
        {payload[0].value} kWh/m²/day (avg)
      </p>
      <p className="text-[10px] text-slate-500">{payload[0].payload.type} set</p>
    </div>
  )
}

export function PerformanceSection() {
  return (
    <section id="performance" className="relative py-32 overflow-hidden">
      <div className="orb w-[500px] h-[500px] bg-data-500/5 -bottom-20 -left-20" />

      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ duration: 0.6 }} className="mb-12">
          <p className="section-label mb-3">Section 03</p>
          <h2 className="text-4xl font-bold text-white mb-4">Model Performance</h2>
          <p className="text-slate-400 max-w-xl">
            Evaluated on held-out 2023–2024 data — two full years the model never saw during training.
          </p>
        </motion.div>

        {/* KPI grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-10">
          {KPIs.map((kpi, i) => <KPICard key={kpi.label} kpi={kpi} index={i} />)}
        </div>

        {/* Charts row */}
        <div className="grid lg:grid-cols-3 gap-6">

          {/* Radial R² */}
          <motion.div initial={{ opacity:0, scale:0.95 }} whileInView={{ opacity:1, scale:1 }} viewport={{ once:true }}>
            <GlassCard className="flex flex-col items-center py-8">
              <p className="section-label mb-6">R² Gauge</p>
              <div className="relative w-48 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="65%" outerRadius="90%"
                    data={R2_RADIAL} startAngle={90} endAngle={-270}
                  >
                    <RadialBar dataKey="value" cornerRadius={6} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-solar-400">88.3</span>
                  <span className="text-xs text-slate-400 font-mono">% R²</span>
                </div>
              </div>
              <p className="text-xs text-slate-500 mt-4 text-center max-w-[180px]">
                Model explains 88.3% of variance in solar irradiance
              </p>
            </GlassCard>
          </motion.div>

          {/* Year bar chart */}
          <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
            transition={{ delay: 0.1 }} className="lg:col-span-2">
            <GlassCard>
              <p className="section-label mb-1">Dataset Split</p>
              <p className="text-xs text-slate-500 mb-5">
                Mean GHI by year · <span className="text-solar-400">■ Train</span>
                <span className="text-data-400 ml-3">■ Test</span>
              </p>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={TRAIN_TEST} barSize={32}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="year" tick={{ fill: '#64748b', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} domain={[4.5, 5.5]} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar dataKey="ghi" radius={[6,6,0,0]}>
                    {TRAIN_TEST.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.85} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </GlassCard>
          </motion.div>
        </div>

        {/* Params row */}
        <motion.div initial={{ opacity:0, y:20 }} whileInView={{ opacity:1, y:0 }} viewport={{ once:true }}
          transition={{ delay: 0.2 }} className="mt-6">
          <GlassCard hover={false}>
            <p className="section-label mb-4">Best XGBoost Hyperparameters (GridSearchCV)</p>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
              {[
                { k: 'learning_rate', v: '0.05' },
                { k: 'max_depth',     v: '6' },
                { k: 'n_estimators',  v: '200' },
                { k: 'objective',     v: 'reg:squarederror' },
                { k: 'booster',       v: 'gbtree' },
                { k: 'eval_metric',   v: 'rmse' },
              ].map(({ k, v }) => (
                <div key={k} className="bg-ink-900/60 rounded-xl p-3 border border-white/[0.05]">
                  <div className="text-[10px] font-mono text-slate-500 mb-1 truncate">{k}</div>
                  <div className="text-sm font-semibold text-solar-300">{v}</div>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  )
}
