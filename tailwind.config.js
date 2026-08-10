/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
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
        'navy-950': '#011C40',
        'navy-900': '#023859',
        'navy-800': '#052659',
        'navy-500': '#5482B4',
        'navy-300': '#7EA0C5',
        'navy-100': '#C2E8FF',
      },
    },
  },
  plugins: [],
}
