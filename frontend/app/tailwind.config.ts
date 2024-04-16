import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'global-gradient': 'bg-gradient-to-br from-slate-500 to-slate-800', 
        'other-gradient': 'gradient'
      },

      customColours: {
        
      }
    },
  },
  plugins: [],
};
export default config;
