/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./static/**/*.{js,html}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'script': ['"Great Vibes"', 'cursive'],
        'sans': ['Jost', 'sans-serif'],
        'serif': ['"Cormorant Garamond"', 'serif'],
      },
    },
  },
  plugins: [],
}
