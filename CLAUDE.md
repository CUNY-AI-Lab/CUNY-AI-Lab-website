# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server at localhost:4321
npm run build    # Build production site to ./dist/
npm run preview  # Preview production build locally
```

## Architecture

Astro static site with Tailwind CSS. Auto-deploys to AWS Amplify (ailab.gc.cuny.edu) on push to main.

**Key Files:**
- `src/layouts/BaseLayout.astro` - Main layout wrapper (Header, Footer, fonts, favicon)
- `src/components/` - Header.astro, Footer.astro
- `src/pages/` - Route pages (index, about, tools, team, contact, request-access)
- `src/pages/models.astro` - Model registry with filters and collapsible guide
- `src/pages/models/guide.astro` - Field guide explaining registry UI elements
- `src/data/model-registry.json` - Model registry data. Update `updated_at` field when modifying.
- `tailwind.config.mjs` - Color palette and theme configuration

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

**JSON Data Loading:**
Use `fs.readFileSync` in Astro frontmatter to load JSON files from `src/data/`:
```javascript
import fs from 'node:fs';
import path from 'node:path';
const jsonPath = path.join(process.cwd(), 'src/data/filename.json');
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
```

**Client-side Scripts:**
Use `<script is:inline>` for vanilla JavaScript. Avoid TypeScript syntax in inline scripts.

**Astro Styles:**
Use `<style is:global>` when CSS selectors need to target dynamically generated elements or work across component boundaries (e.g., hover tooltips).

**Images:**
- Tool screenshots in `public/images/tools/`
- Team photos in `public/images/team/` — resize to max 800px width (`sips -Z 800 filename.jpg`)
- Partner logos in `public/images/partners/`
