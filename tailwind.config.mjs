/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				'logo': {
					'navy': '#1D3A83',      // Logo dark navy
					'blue': '#3B73E6',      // Logo bright blue
					'azure': '#2A6FB8',     // Logo medium blue
					'teal': '#2FB8D6',      // Logo teal/cyan
				},
				'cuny': {
					'blue': '#1D3A83',      // Logo navy for hero backgrounds
					'indigo': '#0f172a',    // Deep dark blue
					'azure': '#2A6FB8',     // Logo medium blue
					'gold': '#ffb81c',      // Gold accent
					'cream': '#fffcd5',     // Cream
					'pearl': '#f7f4eb',     // Pearl
				},
				'teal': {
					'50': '#f0fdfd',        // Lightest teal
					'100': '#ccfafa',       // Very light teal
					'200': '#99f5f5',       // Light teal
					'300': '#5ce9e9',       // Soft teal
					'400': '#26dddd',       // Bright teal
					'500': '#00d7d7',       // Primary teal (cyan)
					'600': '#00b8b8',       // Medium-dark teal
					'700': '#009999',       // Deep teal
					'800': '#007a7a',       // Very deep teal
					'900': '#005b5b',       // Darkest teal
					'950': '#003838',       // Almost black teal
				},
				'vibrant': {
					'50': '#e8f4fc',
					'100': '#d1e9f9',
					'200': '#a3d3f3',
					'300': '#5ab8e8',
					'400': '#2FB8D6',       // Logo teal - accents
					'500': '#3B73E6',       // Logo bright blue
					'600': '#3B73E6',       // Primary CTA color
					'700': '#2A6FB8',       // Logo medium blue - hover
					'800': '#1D3A83',       // Logo navy
					'900': '#162d66',
					'950': '#0f1d40',
				},
				'neutral': {
					'cream': '#FAFCF8',     // Warm white background
					'stone': '#333333',     // Charcoal text
					'glass': 'rgba(255, 255, 255, 0.7)',
					'glass-dark': 'rgba(15, 23, 42, 0.6)',
				},
			},
			fontFamily: {
				'sans': ['Inter', 'system-ui', 'sans-serif'],
				'display': ['Outfit', 'system-ui', 'sans-serif'],
				'serif': ['Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
			},
			backgroundImage: {
				'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
				'hero-glow': 'conic-gradient(from 180deg at 50% 50%, #22d3ee 0deg, #00d7d7 180deg, #22d3ee 360deg)',
			},
			animation: {
				'blob': 'blob 7s infinite',
			},
			keyframes: {
				blob: {
					'0%': { transform: 'translate(0px, 0px) scale(1)' },
					'33%': { transform: 'translate(30px, -50px) scale(1.1)' },
					'66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
					'100%': { transform: 'translate(0px, 0px) scale(1)' },
				},
			},
		},
	},
	plugins: [],
}
