import { motion } from 'framer-motion'
import clsx from 'clsx'

export function GlassCard({ children, className, hover = true, glow, ...rest }) {
  return (
    <motion.div
      whileHover={hover ? { y: -2, scale: 1.005 } : undefined}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      className={clsx(
        'glass rounded-2xl p-6',
        glow === 'solar' && 'shadow-glow-solar',
        glow === 'data'  && 'shadow-glow-data',
        className
      )}
      {...rest}
    >
      {children}
    </motion.div>
  )
}
