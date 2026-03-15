import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#f1ead9',
        soot: '#111312',
        ember: '#b23a20',
        moss: '#566c54',
        brass: '#b28947',
      },
      boxShadow: {
        docket: '0 20px 60px rgba(10, 12, 11, 0.14)',
      },
      borderRadius: {
        docket: '1.75rem',
      },
      backgroundImage: {
        'forensic-grid': 'linear-gradient(rgba(17,19,18,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(17,19,18,0.08) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
};

export default config;
