/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Neutral dark scale — the app's base surface language (no purple).
        ink: {
          950: "#08080b",
          900: "#101114",
          850: "#15161b",
          800: "#1c1d24",
          700: "#292a33",
          600: "#3c3e4a",
          500: "#5a5c6b",
          400: "#848696",
          300: "#9a9cab",
          200: "#c2c3cf",
          100: "#e4e5eb",
          50: "#f5f5f8",
        },
        // Electric yellow — the one accent color, used sparingly and deliberately.
        accent: {
          300: "#fff082",
          400: "#f6e94d",
          500: "#e6d100",
          600: "#b8a600",
        },
        good: "#4ade80",
        bad: "#fb7185",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
