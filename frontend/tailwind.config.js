/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Cal Sans', 'Inter', 'sans-serif'],
      },
      colors: {
        // Midnight navy base
        ink: {
          950: '#04060f',
          900: '#080d1a',
          800: '#0d1526',
          700: '#131e33',
          600: '#1a2840',
          500: '#243352',
        },
        // Electric amber — solar accent
        solar: {
          300: '#fde68a',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        // Cyan data accent
        data: {
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
        },
        // Status greens
        live: {
          400: '#4ade80',
          500: '#22c55e',
        },
      },
      backgroundImage: {
        'grid-ink': `linear-gradient(rgba(34,211,238,0.04) 1px, transparent 1px),
                     linear-gradient(90deg, rgba(34,211,238,0.04) 1px, transparent 1px)`,
      },
      backgroundSize: {
        'grid-48': '48px 48px',
      },
      boxShadow: {
        'glow-solar': '0 0 40px rgba(251,191,36,0.15)',
        'glow-data':  '0 0 40px rgba(34,211,238,0.12)',
        'glass':      '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'spin-slow':  'spin 8s linear infinite',
        'drift':      'drift 20s ease-in-out infinite alternate',
      },
      keyframes: {
        drift: {
          '0%':   { transform: 'translate(0px, 0px) scale(1)' },
          '100%': { transform: 'translate(30px, -20px) scale(1.05)' },
        },
      },
    },
  },
  plugins: [],
}
