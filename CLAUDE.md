# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server at localhost:4321
npm run build    # Build production site to ./dist/
npm run preview  # Preview production build locally
```

## Architecture

This is an Astro static site using Tailwind CSS. Deploys automatically to GitHub Pages on push to main.

**Structure:**
- `src/layouts/BaseLayout.astro` - Main layout wrapper (includes Header, Footer, fonts, favicon)
- `src/components/` - Header.astro, Footer.astro
- `src/pages/` - Route pages (index, about, tools, team, contact, request-access)
- `public/images/` - Static assets including logo and partner logos
- `tailwind.config.mjs` - Color palette and theme configuration

**Color System (defined in tailwind.config.mjs):**
- `vibrant-600` (#2A86FF) - Primary CTA buttons
- `vibrant-700` (#1C79B6) - Button hover states
- `cuny-blue` (#1D3A83) - Hero section backgrounds
- `neutral-stone` (#333333) - Body text
- `neutral-cream` (#FAFCF8) - Page backgrounds

**Fonts:**
- Display: Outfit (headings via `font-display`)
- Body: Inter (via `font-sans`)

**URL Handling:**
All internal links use `${base}` prefix from `import.meta.env.BASE_URL` for correct path resolution.

## Deployment

Pushes to `main` trigger GitHub Actions workflow that builds and deploys to GitHub Pages at cunyailab.org.
