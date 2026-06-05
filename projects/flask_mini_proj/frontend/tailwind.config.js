/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0f1b2d",
          soft: "#162436",
          deep: "#0a1220",
          card: "#1a2d45",
          elevated: "#1e3352",
        },
        accent: {
          DEFAULT: "#4a8fd4",
          light: "#8ec5f0",
          muted: "#3d6a9a",
          glow: "#5ba3e8",
          dim: "#2a5080",
        },
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.06)",
          border: "rgba(255, 255, 255, 0.1)",
          strong: "rgba(255, 255, 255, 0.09)",
          highlight: "rgba(255, 255, 255, 0.14)",
        },
      },
      fontFamily: {
        sans: ["Heebo", "system-ui", "sans-serif"],
      },
      fontSize: {
        "2xs": ["0.65rem", { lineHeight: "1rem" }],
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      maxWidth: {
        chat: "48rem",
        content: "72rem",
      },
      boxShadow: {
        glass: "0 8px 40px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255,255,255,0.06)",
        "glass-lg": "0 16px 48px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255,255,255,0.08)",
        glow: "0 0 48px rgba(74, 143, 212, 0.18)",
        "inner-soft": "inset 0 1px 0 rgba(255,255,255,0.08)",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "pulse-soft": "pulseSoft 1.4s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
    },
  },
  plugins: [],
};
