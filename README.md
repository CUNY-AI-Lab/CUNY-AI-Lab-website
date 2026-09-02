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
| `bun run preview:cloudflare` | Serve the build through local Cloudflare Workers at `localhost:4321` |
| `bun run deploy:cloudflare` | Deploy static assets to the Cloudflare preview |

## Hosting

The public site remains at https://ailab.gc.cuny.edu on AWS Amplify. Current
`main` also deploys to https://cail-website.ailab-452.workers.dev for reviewing
the Cloudflare hosting path. Both hosts serve the same Astro build; there is
no custom Worker runtime, storage, or application binding.

Build before running either local preview command. The Cloudflare preview
preserves canonical links to the live site and tools. Request-access identity
and form submission are allowed only from the canonical website origin; use
the production application page for that flow.

A production move is separate: establish Cloudflare zone and domain routing,
coordinate the CUNY DNS change, verify the canonical site, then retire Amplify.
No email migration is planned.
