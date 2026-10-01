/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        indigo: {
          50: 'var(--color-accent-bg)',
          100: 'var(--color-accent-bg)',
          200: 'var(--color-border)',
          300: 'var(--color-accent)',
          400: 'var(--color-accent)',
          500: 'var(--color-accent)',
          600: 'var(--color-accent)',
          700: 'var(--color-accent-hover)',
        },
        gray: {
          50: 'var(--color-surface-alt)',
          100: 'var(--color-surface-alt)',
          200: 'var(--color-border)',
          300: 'var(--color-border)',
          400: 'var(--color-text-tertiary)',
          500: 'var(--color-text-secondary)',
          600: 'var(--color-text-secondary)',
          700: 'var(--color-text)',
          800: 'var(--color-text)',
        },
      },
      borderRadius: {
        md: '8px',
        xl: '8px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(22,119,255,0.06)',
      },
    },
  },
  plugins: [],
}
