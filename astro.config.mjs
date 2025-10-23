import { defineConfig } from 'astro/config';

import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://cuny-ai-lab.github.io',
  // Only use base path in production, not in development
  base: process.env.NODE_ENV === 'production' ? '/CUNY-AI-Lab-website' : '/',
  integrations: [tailwind()]
});