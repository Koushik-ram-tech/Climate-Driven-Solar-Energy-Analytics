import { useEffect, useRef, useState } from 'react'
import { useInView } from 'framer-motion'

export function AnimatedNumber({ value, decimals = 0, duration = 1400, suffix = '' }) {
  const ref     = useRef(null)
  const inView  = useInView(ref, { once: true })
  const [display, setDisplay] = useState(0)
  const start   = useRef(null)
  const raf     = useRef(null)

  useEffect(() => {
    if (!inView) return
    const target = parseFloat(value)
    start.current = null

    const step = (ts) => {
      if (!start.current) start.current = ts
      const progress = Math.min((ts - start.current) / duration, 1)
      // ease-out-quart
      const eased = 1 - Math.pow(1 - progress, 4)
      setDisplay(+(eased * target).toFixed(decimals))
      if (progress < 1) raf.current = requestAnimationFrame(step)
    }
    raf.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf.current)
  }, [inView, value, decimals, duration])

  return (
    <span ref={ref}>
      {display.toFixed(decimals)}{suffix}
    </span>
  )
}
