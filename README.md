# CUNY AI Lab website

This repository contains the public website for the CUNY AI Lab. It explains
the Lab's work, links people to available tools, and provides current access
and support information at [ailab.gc.cuny.edu](https://ailab.gc.cuny.edu).

The site is built with Astro and Tailwind CSS. Most editorial content lives in
`src/content` and `src/data`; route-specific presentation lives in `src/pages`.

## Work locally

```bash
bun install --frozen-lockfile
bun run dev
```

Before opening a pull request:

```bash
bun audit --audit-level high
bun run build
```

`bun run preview` serves the completed build locally. Merges to `main` are
published by AWS Amplify after the required review and Website CI pass.
