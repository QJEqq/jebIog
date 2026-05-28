/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./jeb_core/templates/**/*.html",        
    "./jeb_core/**/templates/**/*.html",    
    "./jeb_core/**/static/**/*.js",         
    ],
   safelist: [
    // Классы для динамических инпутов или элементов, если они добавляются через JS/HTMX
    'w-full', 'py-3', 'px-4', 'rounded-lg',
    'bg-slate-950/60', 'backdrop-blur-md',
    'border', 'border-white/10',
    'text-white', 'placeholder-slate-400',
    'hover:border-blue-500/50',
    'focus:border-blue-500', 'focus:ring-2', 'focus:ring-blue-500/20',
    'outline-none', 'transition', 'duration-200'
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        darkBg: '#0b0c10',
        darkCard: '#12131a',
        neonBlue: '#2563eb',
        neonPurple: '#7c3aed',
      }
    },
  },
  plugins: [],
}