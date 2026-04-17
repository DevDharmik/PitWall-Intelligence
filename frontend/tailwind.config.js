/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        f1red: {
          DEFAULT: "#C8102E",
          dark:    "#9b0a22",
          light:   "#fde8ec",
        },
      },
      fontFamily: {
        mono: ["'DM Mono'", "monospace"],
        sans: ["'DM Sans'", "sans-serif"],
      },
    },
  },
  plugins: [],
}
