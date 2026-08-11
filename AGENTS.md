# AGENTS.md

This is the public CUNY AI Lab website. Keep claims current, specific, and
understandable to people who are not maintaining the fleet.

## Ground truth

- Use Bun and the checked-in lockfile. The authoritative gate is
  `bun audit --audit-level high && bun run build`.
- Verify public links and product claims against the current deployed service.
  Do not infer availability, storage, retention, or response times.
- Structured content lives in `src/data`, prose in `src/content`, and route
  behavior in `src/pages`. Some pages intentionally keep their content inline.
- The production site is `https://ailab.gc.cuny.edu`; `cunyailab.org` in Astro
  configuration is legacy metadata, not the canonical public address.

## Changes

- Preserve the shared layout, skip link, keyboard behavior, semantic headings,
  visible focus, and sufficient contrast.
- Decorative SVGs stay hidden from assistive technology. Icon-only controls
  need accessible names; disclosure and tab controls need their native ARIA
  state.
- Tailwind scans JSON because data files contain class names. Markdown output
  that needs cross-component styling uses explicit global styles.
- Blog drafts remain excluded from direct routes, indexes, and RSS until
  `draft` is false.

## Release

- Pull requests require Website CI and one independent approval.
- A merge to `main` is published by the existing AWS Amplify integration.
  Do not add a second deployment path or bypass the approval rule.
- After publication, probe the changed routes on the canonical domain and
  confirm that the public copy matches the merged source.
