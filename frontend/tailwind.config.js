/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        reuse: '#16a34a',
        resale: '#2563eb',
        recycle: '#dc2626',
        flag: '#d97706',
      },
    },
  },
  plugins: [],
}
