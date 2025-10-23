/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				'cuny': {
					'blue': '#0033a1',      // CUNY Blue (keep for minimal use)
					'indigo': '#011d49',    // Dark blue
					'azure': '#0040f0',     // Bright blue
					'gold': '#ffb81c',      // Gold
					'cream': '#fffcd5',     // Cream
					'pearl': '#f7f4eb',     // Pearl
				},
				'teal': {
					'50': '#f0fdfd',        // Lightest teal (almost white)
					'100': '#ccfafa',       // Very light teal
					'200': '#99f5f5',       // Light teal
					'300': '#5ce9e9',       // Soft teal
					'400': '#26dddd',       // Bright teal
					'500': '#00d7d7',       // Primary teal (cyan)
					'600': '#00b8b8',       // Medium-dark teal
					'700': '#009999',       // Deep teal
					'800': '#007a7a',       // Very deep teal
					'900': '#005b5b',       // Darkest teal
				},
				'neutral': {
					'cream': '#FAFCF8',     // Warm white background
					'stone': '#333333',     // Charcoal text
				},
			},
			fontFamily: {
				'sans': ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
				'serif': ['Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
			},
		},
	},
	plugins: [],
}
