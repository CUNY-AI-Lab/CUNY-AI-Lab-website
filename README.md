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

## Model registry availability

The registry keeps reviewed notes in `src/data/model-registry.json`. Entries
marked `hidden: true` remain in source but are omitted from the page. The original
Qwen3-235B-A22B card is hidden because current Gateway offerings are different
revisions or VL variants.

The browser reads the public Gateway `/v1/catalog` once on load and when the
reader chooses **Refresh availability**, without credentials. The displayed
check time applies to availability, route capabilities, context, and prices;
these values can change. Failed or malformed discovery clears prior offerings
and shows an unknown state while the reviewed notes remain usable.

`src/data/model-gateway-links.json` owns exact card-to-offering matches. A row
must match an explicitly listed native API ID or Gateway's verified `model_group`.
Names and model-family prefixes never establish identity. Native variants stay
separate, and every matched provider offering remains visible. The explicit
Mantle mappings for DeepSeek V3.2 and GLM 5 follow their
[AWS DeepSeek card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-deepseek-deepseek-v3-2.html)
and [AWS GLM card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-zai-glm-5.html).
Gemma 3's exact Mantle ID is not explicitly matched while AWS's corresponding
page inconsistently identifies its checkpoint as PT and IT; a verified Gateway
group can still establish identity.

Prices come only from Gateway's optional `pricing` field, in USD per million
input/output tokens. Missing prices stay unknown; zero is displayed only when
the catalog reports zero. Workers AI and Mantle expose standard token rates.
OpenRouter reports independently lowest input/output rates from the healthy
ZDR endpoint inventory, labeled **from**; those minima need not come from the
same endpoint. The selected route can cost more, and additional provider fees
are outside these token rates. These are provider prices, not personal spending,
quota balances, or estimates of a particular request's cost.

The website is the caller and Gateway is the receiver. Deploy and verify the
additive Gateway pricing contract before releasing a website consumer. Browser
tests inject catalogs for failure and identity cases; rollout verification must
also load the deployed page against the real public Gateway without intercepting
that request. No inference or API key is needed for this integration.

## Accessibility checks

After building, run `bun run preview:cloudflare`, then
`uv run --with playwright python tests/accessibility_browser.py`. CI runs this
alongside the keyboard and form journeys. Axe checks the rendered pages and
expanded tool/model states against WCAG A/AA rules, with representative mobile
views. It does not certify conformance or replace testing with assistive
technology. The scanner is a development dependency, not a website script.
