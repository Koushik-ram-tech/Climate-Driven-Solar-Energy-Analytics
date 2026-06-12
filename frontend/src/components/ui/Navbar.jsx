import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sun, Activity, Menu, X } from 'lucide-react'
import { Badge } from './Badge'

const NAV = [
  { label: 'Overview',    href: '#hero' },
  { label: 'Prediction',  href: '#predict' },
  { label: 'Performance', href: '#performance' },
  { label: 'XAI',         href: '#xai' },
  { label: 'Pipeline',    href: '#pipeline' },
  { label: 'Research',    href: '#research' },
]

export function Navbar({ apiOnline }) {
  const [scrolled, setScrolled] = useState(false)
  const [open,     setOpen]     = useState(false)

  useEffect(() => {
    const handle = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handle, { passive: true })
    return () => window.removeEventListener('scroll', handle)
  }, [])

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-ink-950/90 backdrop-blur-xl border-b border-white/[0.06]' : ''
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#hero" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-solar-400 to-amber-600 flex items-center justify-center shadow-glow-solar">
            <Sun size={16} className="text-ink-950" />
          </div>
          <span className="text-sm font-semibold tracking-tight text-white">
            Solar<span className="text-gradient-solar">IQ</span>
          </span>
        </a>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {NAV.map((n) => (
            <a
              key={n.href}
              href={n.href}
              className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
            >
              {n.label}
            </a>
          ))}
        </div>

        {/* Status */}
        <div className="hidden md:flex items-center gap-3">
          <Badge variant={apiOnline ? 'live' : 'danger'} dot>
            API {apiOnline ? 'Online' : 'Offline'}
          </Badge>
        </div>

        {/* Mobile burger */}
        <button
          className="md:hidden text-slate-400 hover:text-white"
          onClick={() => setOpen(!open)}
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile drawer */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{   opacity: 0, height: 0 }}
            className="md:hidden bg-ink-900/95 backdrop-blur-xl border-b border-white/[0.06] px-6 pb-4"
          >
            {NAV.map((n) => (
              <a
                key={n.href}
                href={n.href}
                onClick={() => setOpen(false)}
                className="block py-2.5 text-sm text-slate-300 hover:text-white border-b border-white/[0.04] last:border-0"
              >
                {n.label}
              </a>
            ))}
            <div className="pt-3">
              <Badge variant={apiOnline ? 'live' : 'danger'} dot>
                API {apiOnline ? 'Online' : 'Offline'}
              </Badge>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}
