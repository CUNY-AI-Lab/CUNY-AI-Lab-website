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

**Structure:**
- `src/layouts/BaseLayout.astro` - Main layout wrapper (Header, Footer, fonts, favicon)
- `src/components/` - Header.astro, Footer.astro
- `src/pages/` - Route pages (index, about, tools, team, contact, request-access)
- `src/pages/models.astro` - Model registry grid view
- `src/pages/models/list.astro` - Model registry single-column list view
- `src/pages/models/guide.astro` - Field guide explaining registry UI elements
- `src/data/` - JSON data files (model-registry.json)
- `public/images/` - Static assets (logos, partner logos)
- `tailwind.config.mjs` - Color palette and theme configuration

**Data Files:**
- `src/data/model-registry.json` - Model registry data displayed on /models and /models/list pages. Update `updated_at` field when modifying.

**Color System (tailwind.config.mjs):**
- `vibrant-600` (#3B73E6) - Primary CTA buttons
- `vibrant-700` (#2A6FB8) - Button hover states
- `cuny-blue` (#1D3A83) - Hero section backgrounds
- `neutral-stone` (#333333) - Body text
- `neutral-cream` (#FAFCF8) - Page backgrounds

**Fonts:**
- Display: Outfit (headings via `font-display`)
- Body: Inter (via `font-sans`)

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

**Images:**
- Team photos in `public/images/team/` should be resized to max 800px width for faster builds
- Use `sips -Z 800 filename.jpg` on macOS to resize
