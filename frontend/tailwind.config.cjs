/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {},
    fontFamily: {
      heading: ['sans-serif']
    }
  },
  plugins: [require('@tailwindcss/typography')]
};
