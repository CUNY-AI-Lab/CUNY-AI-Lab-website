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

## CAIL Sandbox Docs

`/sandbox-docs/` and its article routes are built from
`src/content/sandbox-docs/*.md`. The initial import preserved all 14 published
Markdown files from `CUNY-AI-Lab/sandbox-docs` at revision
`74ce09d2bb6cc58b37e1f7296a3a01e988009222`, including examples, tables, and
expandable sections. `src/data/sandbox-docs-source.json` records that import's
source revision and SHA-256 hashes. It is provenance for the initial import,
not a requirement to keep future documentation frozen.

Make future documentation edits here through the normal website pull request
and deployment workflow. Builds do not fetch GitHub Pages or depend on its
runtime Markdown renderer. The original GitHub Pages site redirects to these
routes, including legacy article hashes and direct article paths. Its retained
Markdown files are a historical source snapshot, not the editing destination.

The docs use the shared website header, footer, fonts, and canonical URLs,
with the original three sidebar groups plus links to the three supplementary
articles. Relative `.md` links become website routes during rendering, and
legacy links such as `/sandbox-docs/#student-onboarding` resolve to the article.
The imported Markdown text is unchanged by these transformations. The landing
page heading was subsequently renamed to **CAIL Sandbox Docs**. Student
Onboarding now foregrounds the instructor course-access checkpoint and the
course invitation, group, and channel enrollment process. Getting Started uses
the current lab support address, `ailab@gc.cuny.edu`. Other imported article
text is unchanged.

## Live model registry

The registry renders every offering from the public Gateway `/v1/catalog`,
loaded in the browser without credentials on page load and **Refresh catalog**.
Models are organized by name, with their provider offerings underneath. Gateway
`model_group` establishes shared identity, falling back to the exact API ID when
no group is supplied; similar names never merge models. Each provider retains its
exact API ID, capabilities, context, and prices. Search and provider/capability
filters match individual offerings, so different providers cannot jointly satisfy
a filter that neither supports alone. There is no curated allowlist, review data,
or fixed set of featured models.

Gateway supplies clean `model_name` labels and optional sourced `specifications`
with their own check date. Cards summarize size, weights, and license; the native
**Details and sources** disclosure contains architecture and per-field evidence.
The website has no static metadata lookup. Published
size, architecture, weights, and license facts link to their sources. Checkpoint
parameter counts are distinguished from advertised sizes. Missing facts are
omitted; conflicting facts within a group are withheld independently, while
agreeing facts use the oldest supporting check date. Malformed optional fields
are ignored without removing valid provider offerings. An invalid specifications
check date discards those specifications. Capability icons and the 100K
long-context indicator come from each current provider offering.
New catalog offerings appear automatically, including non-text routes.

The check time applies to catalog availability, route capabilities, context, and
prices. Failed or malformed discovery clears previous results and offers retry.
An empty catalog and a search with no matches have separate messages. JavaScript
is required for the interactive list; a public JSON catalog link remains usable
without it. No inference request is sent by browsing, filtering, or copying IDs.

Prices come only from Gateway's optional `pricing` field, in USD per million
input/output tokens. Missing prices stay unknown; zero is displayed only when
the catalog reports zero. Workers AI and Mantle expose standard token rates.
OpenRouter reports independently lowest input/output rates from the healthy
ZDR endpoint inventory, labeled **from**; those minima need not come from the
same endpoint. The selected route can cost more, and additional provider fees
are outside these token rates. These are provider prices, not personal spending,
quota balances, or estimates of a particular request's cost.

The website is the caller and the existing public Gateway catalog is the receiver;
Gateway must supply sourced metadata for the reference facts to appear. Browser tests
substitute catalogs for deterministic filtering, failure, and identity cases.
Rollout verification also loads the deployed page against the real public Gateway
without intercepting that request. No API key or paid inference is needed.

## Accessibility checks

After building, run `bun run preview:cloudflare`, then
`uv run --with playwright python tests/accessibility_browser.py`. CI runs this
alongside the keyboard and form journeys. Axe checks the rendered pages and
expanded tool/model states against WCAG A/AA rules, with representative mobile
views. It does not certify conformance or replace testing with assistive
technology. The scanner is a development dependency, not a website script.
