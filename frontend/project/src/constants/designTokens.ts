/**
 * FinanceGPT Pro Design System
 * Professional Light Theme with Enterprise Standards
 */

export const colors = {
  // Primary Palette - Professional Blues
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9', // Main brand color
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e'
  },

  // Neutral Palette - Professional Grays
  neutral: {
    0: '#ffffff',
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a'
  },

  // Status Colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d'
  },

  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309'
  },

  danger: {
    50: '#fef2f2',
    100: '#fee2e2',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c'
  },

  // Financial Colors
  financial: {
    profit: '#22c55e',
    loss: '#ef4444',
    neutral: '#64748b',
    gold: '#fbbf24',
    portfolio: '#0ea5e9'
  }
};

export const spacing = {
  0: '0px',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
  32: '128px',
  40: '160px',
  48: '192px',
  56: '224px',
  64: '256px'
};

export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
  },
  fontSize: {
    xs: ['12px', { lineHeight: '16px', letterSpacing: '0.05em' }],
    sm: ['14px', { lineHeight: '20px', letterSpacing: '0.025em' }],
    base: ['16px', { lineHeight: '24px', letterSpacing: '0em' }],
    lg: ['18px', { lineHeight: '28px', letterSpacing: '-0.025em' }],
    xl: ['20px', { lineHeight: '28px', letterSpacing: '-0.025em' }],
    '2xl': ['24px', { lineHeight: '32px', letterSpacing: '-0.05em' }],
    '3xl': ['30px', { lineHeight: '36px', letterSpacing: '-0.05em' }],
    '4xl': ['36px', { lineHeight: '40px', letterSpacing: '-0.05em' }],
    '5xl': ['48px', { lineHeight: '52px', letterSpacing: '-0.05em' }],
    '6xl': ['64px', { lineHeight: '64px', letterSpacing: '-0.05em' }]
  },
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700'
  }
};

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',

  // Financial Dashboard Shadows
  card: '0 4px 12px -2px rgba(0, 0, 0, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04)',
  widget: '0 8px 20px -4px rgba(14, 165, 233, 0.1), 0 4px 8px -2px rgba(0, 0, 0, 0.06)',
  floating: '0 12px 32px -8px rgba(14, 165, 233, 0.15), 0 8px 16px -4px rgba(0, 0, 0, 0.08)'
};

export const borderRadius = {
  none: '0px',
  sm: '4px',
  base: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '20px',
  '3xl': '24px',
  full: '9999px'
};

export const zIndex = {
  base: 0,
  dropdown: 10,
  sticky: 20,
  tooltip: 30,
  overlay: 40,
  modal: 50,
  notification: 60
};

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
};

export const layout = {
  header: {
    height: '64px'
  },
  sidebar: {
    width: '280px',
    collapsedWidth: '80px'
  },
  content: {
    maxWidth: '1440px',
    padding: '24px'
  }
};

export const animation = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms'
  },
  easing: {
    ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
};

// Component-specific design tokens
export const components = {
  button: {
    height: {
      sm: '32px',
      md: '40px',
      lg: '48px'
    },
    padding: {
      sm: '8px 16px',
      md: '12px 20px',
      lg: '16px 24px'
    }
  },

  card: {
    padding: '24px',
    borderRadius: borderRadius.xl,
    shadow: shadows.card,
    border: `1px solid ${colors.neutral[200]}`
  },

  dashboard: {
    widget: {
      minHeight: '240px',
      padding: '20px',
      borderRadius: borderRadius.xl,
      background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%)',
      border: `1px solid ${colors.neutral[200]}`,
      shadow: shadows.widget
    },

    kpi: {
      height: '120px',
      padding: '16px',
      borderRadius: borderRadius.lg,
      background: colors.neutral[0],
      border: `1px solid ${colors.neutral[200]}`,
      shadow: shadows.base
    }
  }
};

// Export theme object for easy consumption
export const theme = {
  colors,
  spacing,
  typography,
  shadows,
  borderRadius,
  zIndex,
  breakpoints,
  layout,
  animation,
  components
};

export default theme;