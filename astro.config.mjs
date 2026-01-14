import { defineConfig } from 'astro/config';

import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://www.cunyailab.org',
  // Base path set to root for custom domain
  base: '/',
  integrations: [tailwind()]
});