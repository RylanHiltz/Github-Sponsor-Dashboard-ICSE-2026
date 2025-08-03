import { theme } from './src/theme.js'; // Import the shared theme

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: theme, // Use the imported theme object
  plugins: [],
}