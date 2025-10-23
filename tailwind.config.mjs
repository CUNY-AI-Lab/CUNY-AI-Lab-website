/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				'cuny': {
					'blue': '#0033a1',      // Primary CUNY Blue (PMS 286C)
					'indigo': '#011d49',    // Secondary Indigo (darker)
					'azure': '#0040f0',     // Secondary Azure (brighter)
					'gold': '#ffb81c',      // Gold Accent
					'cream': '#fffcd5',     // Cream
					'pearl': '#f7f4eb',     // Pearl (light neutral)
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
