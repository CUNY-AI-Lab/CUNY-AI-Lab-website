# AGENTS.md

These are the canonical instructions for working in this repository.

## Commands

```bash
bun install --frozen-lockfile
bun run dev      # Start dev server at localhost:4321
bun run build    # Build production site to ./dist/
bun run preview  # Preview production build locally
bun run lint     # Run Oxlint with the vendored anti-slop profile
bun run check    # Audit dependencies, lint, type-check, and build the site
```

## Lint

`bun run check` starts with the vendored full generic anti-slop profile in
`tools/oxlint/anti-slop/` (`bun run lint`). It covers `.ts`, `.mjs`, `.js`, and
the frontmatter and `<script>` blocks of `.astro` files. Fix findings at the
actual contract or boundary: parse `fetch` responses and form data with
`zod/mini` schemas as `request-access.astro` does (the mini build keeps the
client bundle small) rather than `typeof` checks, and keep DOM feature detection to the `in` operator. Do not add rule
suppressions, evasive wrappers, or generic `SAFETY` comments. Effect-specific
rules stay disabled because this repository has no Effect code.

## Architecture

Astro static site with Tailwind CSS. Production is served at `ailab.gc.cuny.edu`; see Deployment for which host currently serves it. `main` is governed by the `main-ci-required` repository ruleset: it requires the `Website CI` check on an up-to-date branch, and blocks force pushes and branch deletion. The only bypass actor is `smorello87`, who may commit and push straight to `main`. Everyone else — including the other repo admins — must open a pull request and let `Website CI` pass; no formal approval is required, but ask one independent reviewer to look at substantive changes.

Because a bypassed push skips CI, run `bun run build` locally before pushing to `main`, and confirm the deployment afterward (see Deployment) rather than relying on a green check.

## Deployment

- Cloudflare Worker `cail-website` serves the same static `dist/` build at `https://cail-website.ailab-452.workers.dev`. `wrangler.jsonc` has no production routes or application bindings. The serialized `deploy` job publishes current `main` using the repository secret `CLOUDFLARE_API_TOKEN`, then checks the exact serving version and public routes. PR jobs have no deployment credentials and run the existing browser checks against local Wrangler.
- Production remains on AWS Amplify app `d1j8mvw9hg41u1`, which builds `main` from `amplify.yml`. Keep its build aligned with CI. A later, separately authorized domain cutover requires CUNY DNS and Cloudflare zone/route readiness; then remove the obsolete Amplify path. This preview setup does not authorize DNS, plan, or email changes.
- Request-access authentication and intake remain restricted to the canonical website origin. Do not broaden Doorway CORS or identity origins for this preview. Test those interactions locally with the existing explicit fixtures and verify the real flow on the canonical site.
- After a build-toolchain change, verify the deployment that currently serves production succeeded. A passing GitHub check alone does not prove the site deployed.

**Data Layer:**
Pages pull content from two sources:
- `src/content/pages/*.md` — Astro content collections for prose-heavy pages (about, contact). Loaded via `getEntry('pages', 'slug')` with `.render()` for markdown body and `.data` for frontmatter fields.
- `src/data/*.json` — JSON files for structured/list data (team, events, resources, homepage, request-access). Loaded via `fs.readFileSync` in Astro frontmatter:
```javascript
import fs from 'node:fs';
import path from 'node:path';
const jsonPath = path.join(process.cwd(), 'src/data/filename.json');
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
```
- Some pages (tools, guides) have content inline in the `.astro` file rather than in JSON — edit the page directly.
- `src/content/blog/*.md` — Blog posts (Astro content collection). Filename = slug. Rendered by `src/pages/blog/[slug].astro`, listed by `src/pages/blog/index.astro`.
- `src/content/config.ts` — Collection schemas. The `pages` collection is passthrough (flexible frontmatter); the `blog` collection is strict-typed: requires `title`, `description`, `pubDate`, `authors` (string array); optional `tags`, `draft`.

**Key Files:**
- `src/layouts/BaseLayout.astro` - Main layout wrapper (Header, Footer, fonts, favicon)
- `src/components/` - Header.astro, Footer.astro
- `src/pages/` - Route pages (index, about, tools, team, contact, request-access, events, resources, models, guides)
- `src/pages/models.astro` - Live Model API catalog with search and provider/capability filters
- `src/data/featured-models.json` - The registry page's Featured shortlist: `name`, a one-line `note`, and the exact Gateway API `ids` for that model (one per provider route). An entry shows only while at least one of its IDs is in the live catalog, so a retired ID drops out on its own. Update `updated_at` when editing. All other model data comes from Gateway at load time.
- `src/scripts/model-availability.ts` - Public Gateway catalog parsing, filtering, rendering, and API ID copying; present one primary API ID per model, preserve exact provider facts and unknown prices
- `src/pages/models/guide.astro` - Guide to the live registry, factual specifications, and provider token prices
- Gateway owns optional sourced `model_name` and `specifications`; render available facts directly from the catalog, without static identity matching or an allowlist. Malformed optional metadata must not remove valid offerings. Reconcile group facts independently and withhold conflicts.
- `tailwind.config.mjs` - Color palette and theme configuration

**Tailwind Content Scanning:**
The Tailwind content glob includes `.json` files: `'./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue,json}'`. This is required because some JSON data files contain Tailwind class names (e.g., `bg_class` in team.json). If you add Tailwind classes in JSON data, they will be picked up automatically.

**External Tool URLs:**
- Open WebUI: https://chat.ailab.gc.cuny.edu/
- Tools subdomain: https://tools.ailab.gc.cuny.edu/ (asr, alt-text, ocr, agent-studio, site-studio)

**Blog:**
- Staging/publish workflow: commit new posts with `draft: true` and a future `pubDate`; on publish day, flip `draft: false` and push.
- Both `index.astro` and `[slug].astro` filter `!data.draft`, and `rss.xml` excludes drafts — so a `draft: true` post is hidden from the index, its own URL, and the feed. To preview locally, temporarily set `draft: false`.
- Tags are clickable: `src/pages/blog/tags/[tag].astro` builds one archive per unique tag from non-draft posts. Keep tags URL-safe kebab-case because the tag value is used as the route parameter.
- `[slug].astro` gives post images (`.post-content figure img`) a click-to-enlarge lightbox via a native `<dialog>` (Esc/backdrop/button to close). Images are already clickable — don't reinvent it. Top-of-post media uses `<figure>`/`<figcaption>`.

**Color System (tailwind.config.mjs):**
- `vibrant-600` (#3268D8) - Accessible blue links and primary CTA buttons
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
