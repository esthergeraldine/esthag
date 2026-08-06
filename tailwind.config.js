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
      colors: {
        'burgundy': '#7d3b47',
        'burgundy-dk': '#5c2a33',
        'cream': '#fdf8f5',
        'boss-text': '#3a2a2c',
        'boss-muted': '#8a6e72',
        'warm-white': '#fffcfa',
        'rose-pale': '#f5e6e8',
        'rose-mid': '#e8cdd0',
        'rose-deep': '#d4a5aa',
        'rose': '#c9a0a0',
        'blush': '#d4a0a0',
        'muted': '#b8a8a8',
        'ink': '#c17e88',
        'dark': '#3d2b2b',
      },
    },
  },
  plugins: [],
}
