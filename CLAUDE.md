# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server at localhost:4321
npm run build    # Build production site to ./dist/
npm run preview  # Preview production build locally
```

## Architecture

Astro static site with Tailwind CSS. Auto-deploys to AWS Amplify on push to main (requires PR with 1 approval). Production URL: ailab.gc.cuny.edu

**Data Layer:**
Pages pull content from two sources:
- `src/content/pages/*.md` — Astro content collections for prose-heavy pages (about, contact). Loaded via `getEntry('pages', 'slug')` with `.render()` for markdown body and `.data` for frontmatter fields.
- `src/data/*.json` — JSON files for structured/list data (team, tools, events, resources, homepage, request-access, model-registry). Loaded via `fs.readFileSync` in Astro frontmatter:
```javascript
import fs from 'node:fs';
import path from 'node:path';
const jsonPath = path.join(process.cwd(), 'src/data/filename.json');
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
```
- `src/content/config.ts` — Content collection schema (passthrough, so frontmatter fields are flexible)

**Key Files:**
- `src/layouts/BaseLayout.astro` - Main layout wrapper (Header, Footer, fonts, favicon)
- `src/components/` - Header.astro, Footer.astro
- `src/pages/` - Route pages (index, about, tools, team, contact, request-access, events, resources, models)
- `src/pages/models.astro` - Model registry with filters and collapsible guide
- `src/pages/models/guide.astro` - Field guide explaining registry UI elements
- `src/data/model-registry.json` - Model registry data. Update `updated_at` field when modifying.
- `tailwind.config.mjs` - Color palette and theme configuration

**Tailwind Content Scanning:**
The Tailwind content glob includes `.json` files: `'./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue,json}'`. This is required because some JSON data files contain Tailwind class names (e.g., `bg_class` in team.json). If you add Tailwind classes in JSON data, they will be picked up automatically.

**External Tool URLs:**
- Open WebUI: https://chat.ailab.gc.cuny.edu/
- Tools subdomain: https://tools.ailab.gc.cuny.edu/ (asr, alt-text, ocr, agent-studio, site-studio)

**Color System (tailwind.config.mjs):**
- `vibrant-600` (#3B73E6) - Primary CTA buttons
- `vibrant-700` (#2A6FB8) - Button hover states
- `cuny-blue` (#1D3A83) - Hero section backgrounds
- `neutral-stone` (#333333) - Body text
- `neutral-cream` (#FAFCF8) - Page backgrounds

**Fonts:**
- Display: Outfit (headings via `font-display`)
- Body: Inter (via `font-sans`)

**Page Pattern:**
All inner pages share the same hero: dark `cuny-blue` gradient background with a subtle SVG cross pattern overlay, then alternating `bg-white` / `bg-neutral-cream` section blades below.

**Accessibility:**
All changes must be accessible. Every interactive element needs: `aria-label` on icon-only buttons, `aria-expanded` on toggles, `aria-hidden="true"` on decorative SVGs, `role="tab"`/`role="tabpanel"` on tab interfaces, and `aria-pressed` on toggle filters. The site has a skip-to-content link in BaseLayout — preserve it. Test that new components are keyboard-navigable and screen-reader friendly.

**Client-side Scripts:**
Use `<script is:inline>` for vanilla JavaScript. Avoid TypeScript syntax in inline scripts.

**Astro Styles:**
Use `<style is:global>` when CSS selectors need to target dynamically generated elements or work across component boundaries (e.g., markdown-rendered content, hover tooltips). When rendering markdown via `<Content />`, the generated HTML won't have Tailwind classes — use global CSS with explicit `font-family` declarations to ensure fonts inherit correctly.

**Images:**
- Tool screenshots in `public/images/tools/` — avoid `screenshot-*.png` prefix (blocked by `.gitignore`); use `tool-` or `demo-` prefix instead
- Team photos in `public/images/team/` — resize to max 800px width (`sips -Z 800 filename.jpg`)
- Partner logos in `public/images/partners/`
- Animated GIFs from screenshots: `magick -delay 250 -loop 0 frame1.png frame2.png frame3.png output.gif` (2.5s per frame)
