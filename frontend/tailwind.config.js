/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // PolicyEngine color palette from policyengine-app-v2
      colors: {
        // Primary brand colors - teal
        primary: {
          50: '#E6FFFA',
          100: '#B2F5EA',
          200: '#81E6D9',
          300: '#4FD1C5',
          400: '#38B2AC',
          500: '#319795', // Main primary color
          600: '#2C7A7B',
          700: '#285E61',
          800: '#234E52',
          900: '#1D4044',
          DEFAULT: '#319795',
        },

        // Secondary colors
        secondary: {
          50: '#F0F9FF',
          100: '#F2F4F7',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#344054',
          800: '#1E293B',
          900: '#101828',
          DEFAULT: '#64748B',
        },

        // Blue colors
        blue: {
          50: '#F0F9FF',
          100: '#E0F2FE',
          200: '#BAE6FD',
          300: '#7DD3FC',
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#026AA2',
          800: '#075985',
          900: '#0C4A6E',
          DEFAULT: '#0EA5E9',
        },

        // Gray scale
        gray: {
          50: '#F9FAFB',
          100: '#F2F4F7',
          200: '#E2E8F0',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#344054',
          800: '#1F2937',
          900: '#101828',
          DEFAULT: '#6B7280',
        },

        // Semantic colors
        success: '#22C55E',
        warning: '#FEC601',
        error: '#EF4444',
        info: '#1890FF',

        // Background colors
        background: {
          primary: '#FFFFFF',
          secondary: '#F5F9FF',
          tertiary: '#F1F5F9',
        },

        // Text colors
        text: {
          primary: '#000000',
          secondary: '#5A5A5A',
          tertiary: '#9CA3AF',
          inverse: '#FFFFFF',
        },

        // Border colors
        border: {
          light: '#E2E8F0',
          medium: '#CBD5E1',
          dark: '#94A3B8',
          DEFAULT: '#E2E8F0',
        },
      },

      // Typography from PolicyEngine
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        secondary: ['Public Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        body: ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },

      fontSize: {
        xs: ['12px', { lineHeight: '20px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['16px', { lineHeight: '24px' }],
        lg: ['18px', { lineHeight: '28px' }],
        xl: ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['28px', { lineHeight: '36px' }],
        '4xl': ['32px', { lineHeight: '40px' }],
      },

      // Spacing from PolicyEngine
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
        '3xl': '32px',
        '4xl': '48px',
        '5xl': '64px',
      },

      // Border radius
      borderRadius: {
        xs: '2px',
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
        '2xl': '16px',
        '3xl': '24px',
        '4xl': '32px',
      },

      // Box shadows
      boxShadow: {
        xs: '0px 1px 2px 0px rgba(16, 24, 40, 0.05)',
        sm: '0px 1px 3px 0px rgba(16, 24, 40, 0.1)',
        md: '0px 4px 6px -1px rgba(16, 24, 40, 0.1)',
        lg: '0px 10px 15px -3px rgba(16, 24, 40, 0.1)',
        xl: '0px 20px 25px -5px rgba(16, 24, 40, 0.1)',
      },
    },
  },
  plugins: [],
}
