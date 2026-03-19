/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#E1F5EE',
                    100: '#B3E6D4',
                    200: '#80D4B8',
                    300: '#4DC29C',
                    400: '#26B487',
                    500: '#1D9E75',
                    600: '#178E67',
                    700: '#0F6E56',
                    800: '#0A5C47',
                    900: '#064A38',
                    950: '#033224',
                },
                dark: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#64748b',
                    600: '#475569',
                    700: '#334155',
                    800: '#1e293b',
                    900: '#0f172a',
                    950: '#020617',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                display: ['Syne', 'Inter', 'system-ui', 'sans-serif'],
                mono: ['DM Mono', 'monospace'],
            },
            animation: {
                scan: 'scan 2.5s ease-in-out infinite',
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'slide-in': 'slideIn 0.4s ease-out forwards',
                'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
            },
            keyframes: {
                scan: {
                    '0%': { transform: 'translateY(-100%)', opacity: '0' },
                    '20%': { opacity: '1' },
                    '80%': { opacity: '1' },
                    '100%': { transform: 'translateY(100%)', opacity: '0' },
                },
                fadeIn: {
                    from: { opacity: '0', transform: 'translateY(10px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                slideIn: {
                    from: { opacity: '0', transform: 'translateX(-20px)' },
                    to: { opacity: '1', transform: 'translateX(0)' },
                },
                pulseGlow: {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(29, 158, 117, 0.3)' },
                    '50%': { boxShadow: '0 0 20px rgba(29, 158, 117, 0.6)' },
                },
            },
        },
    },
    plugins: [],
};
