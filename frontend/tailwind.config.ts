import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#edf4ff',
        soot: '#040816',
        ember: '#5d7cff',
        moss: '#7ee6ff',
        brass: '#9db8ff',
      },
      boxShadow: {
        docket: '0 30px 80px rgba(6, 14, 42, 0.42)',
      },
      borderRadius: {
        docket: '1.75rem',
      },
      backgroundImage: {
        'forensic-grid': 'linear-gradient(rgba(141,170,255,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(141,170,255,0.12) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
};

export default config;
