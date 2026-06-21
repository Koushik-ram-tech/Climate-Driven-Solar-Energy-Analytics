/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: { DEFAULT: "#F5F0E8" },
        ink: {
          DEFAULT: "#000000",
          100: "#D8D5CE",
          300: "#9C988C",
          500: "#5C594F",
          700: "#2A2822",
        },
        orange: {
          DEFAULT: "#FD5200",
          600: "#E04900",
          700: "#B83C00",
        },
      },
      fontFamily: {
        display: ["Inter Tight", "Inter", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        hero: ["4.5rem", { lineHeight: "1.02", letterSpacing: "-0.02em" }],
        "section-title": ["2.5rem", { lineHeight: "1.08", letterSpacing: "-0.01em" }],
        "display-sm": ["1.5rem", { lineHeight: "1.2" }],
        body: ["1rem", { lineHeight: "1.6" }],
        "body-sm": ["0.875rem", { lineHeight: "1.55" }],
        caption: ["0.75rem", { lineHeight: "1.4" }],
        eyebrow: ["0.75rem", { lineHeight: "1.2" }],
        data: ["1.125rem", { lineHeight: "1.2" }],
        "data-lg": ["2rem", { lineHeight: "1.1" }],
      },
      letterSpacing: {
        tightest: "-0.03em",
        eyebrow: "0.12em",
      },
      maxWidth: {
        container: "1280px",
      },
      borderRadius: {
        card: "0px",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
        30: "7.5rem",
      },
    },
  },
  plugins: [],
};
