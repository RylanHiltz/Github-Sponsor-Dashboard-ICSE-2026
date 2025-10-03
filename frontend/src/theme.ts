
// File that contains the theme colors for the website, will be passed in as color 

// Main color pallete for repeated colors
const bluePrimary = '#3779E3'
const blueSecondary = '#3879E4'



export const theme = {
  extend: {
    colors: {
      primary: {
        light: bluePrimary,
        dark: bluePrimary
      },
      background: {
        light: '#ffffff',
        dark: '#111111'
      },
      surface: {
        light: '#f0f0f0',
        dark: '#1f1f1f'
      },
      border: {
        light: '#D9D9D9',
        dark: '#2A2E31',
      },
      text: {
        primary: {
          light: '#1f2937',
          dark: '#e5e7eb'
        },
        secondary: {
          light: '#484848',
          dark: '#c5c5c5'
        },
        linkHover: {
          light: blueSecondary,
          dark: blueSecondary
        }
      },
      cardBg: {
        light: '#FAFAFA',
        dark: '#141414',
      },
      gridColor: {
        light: '#D1D1D1',
        dark: '#393E46',
      },
      tooltipBg: {
        light: '',
        dark: '#292c30',
      }
    },
  },
};