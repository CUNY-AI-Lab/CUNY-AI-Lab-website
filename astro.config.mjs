import { defineConfig, fontProviders } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import sandboxDocsLinks from './src/plugins/sandbox-docs-links.mjs';
import { satteri } from '@astrojs/markdown-satteri';

// https://astro.build/config
export default defineConfig({
  site: 'https://ailab.gc.cuny.edu',
  base: '/',
  // Amplify restores node_modules between builds. Do not restore previously
  // rendered Markdown when a link transformation changes but the source does not.
  cacheDir: './.astro/cache',
  // The old /<guide>-docs/ URLs only forward to /docs/<guide>/; keep them out of the sitemap.
  integrations: [sitemap({ filter: (page) => !/\/(sandbox|stem-splitter|systems-mapping)-docs\//.test(new URL(page).pathname) })],
  markdown: { processor: satteri({ hastPlugins: [sandboxDocsLinks] }) },
  // Fonts are downloaded at build time and served same-origin from /_astro/fonts/
  // with preload links, so the first paint already has them (no fallback flash).
  fonts: [
    {
      provider: fontProviders.google(),
      name: 'Inter',
      cssVariable: '--font-inter',
      weights: ['400 700'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['sans-serif'],
    },
    {
      provider: fontProviders.google(),
      name: 'Outfit',
      cssVariable: '--font-outfit',
      weights: ['400 800'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['sans-serif'],
    },
  ],
  vite: {
    plugins: [tailwindcss()]
  }
});
