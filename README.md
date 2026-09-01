# CUNY AI Lab website

This repository contains the CUNY AI Lab's Astro static website, including its
content collections, tools portal, model registry, and request-access flow.

## Project structure

```
/
├── public/              # Static assets and robots.txt
├── src/
│   ├── components/      # Shared header and footer
│   ├── content/         # Markdown pages and blog posts
│   ├── data/            # Structured page data
│   ├── layouts/         # Shared Astro layouts
│   └── pages/           # Site routes
├── astro.config.mjs
├── amplify.yml
├── package.json
└── tsconfig.json
```

## Commands

Run these commands from the repository root:

| Command | Action |
| :-- | :-- |
| `bun install --frozen-lockfile` | Install the locked dependencies |
| `bun run dev` | Start the local development server at `localhost:4321` |
| `bun run check` | Audit dependencies, run Astro's static check, and build the site |
| `bun run build` | Build the production site to `./dist/` |
| `bun run preview` | Preview the production build locally |
