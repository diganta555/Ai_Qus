/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#7c3aed",
        primaryDark: "#6d28d9",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
}
