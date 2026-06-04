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
        },
        accent: {
          DEFAULT: "#4a8fd4",
          light: "#7eb8e8",
          muted: "#3d6a9a",
          glow: "#5ba3e8",
        },
        glass: {
          DEFAULT: "rgba(255, 255, 255, 0.07)",
          border: "rgba(255, 255, 255, 0.12)",
          strong: "rgba(255, 255, 255, 0.11)",
        },
      },
      fontFamily: {
        sans: ["Heebo", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.28)",
        glow: "0 0 40px rgba(74, 143, 212, 0.15)",
        card: "0 4px 24px rgba(0, 0, 0, 0.2)",
      },
      animation: {
        "fade-in": "fadeIn 0.35s ease-out",
        "pulse-soft": "pulseSoft 1.4s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
