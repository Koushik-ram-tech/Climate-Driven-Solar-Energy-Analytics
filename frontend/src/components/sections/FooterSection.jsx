import { Sun, Github } from 'lucide-react'

export function FooterSection() {
  return (
    <footer className="border-t border-white/[0.06] py-12">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-solar-400 to-amber-600 flex items-center justify-center">
            <Sun size={13} className="text-ink-950" />
          </div>
          <span className="text-sm font-medium text-slate-400">
            SolarIQ — Climate-Driven Solar Energy Analytics
          </span>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono text-slate-600">
          <span>XGBoost · FastAPI · React</span>
          <span>MCA Major Project · 2024</span>
          <span>R² = 0.8831</span>
        </div>
      </div>
    </footer>
  )
}
