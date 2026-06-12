import clsx from 'clsx'

const variants = {
  solar:  'bg-solar-500/10 text-solar-300 border border-solar-500/20',
  data:   'bg-data-500/10  text-data-300  border border-data-500/20',
  live:   'bg-live-500/10  text-live-400  border border-live-500/20',
  muted:  'bg-white/5      text-slate-400 border border-white/10',
  danger: 'bg-red-500/10   text-red-400   border border-red-500/20',
}

export function Badge({ children, variant = 'muted', className, dot }) {
  return (
    <span className={clsx(
      'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium font-mono tracking-wide',
      variants[variant], className
    )}>
      {dot && (
        <span className={clsx(
          'w-1.5 h-1.5 rounded-full',
          variant === 'live' ? 'bg-live-400 animate-pulse' : 'bg-current opacity-60'
        )} />
      )}
      {children}
    </span>
  )
}
