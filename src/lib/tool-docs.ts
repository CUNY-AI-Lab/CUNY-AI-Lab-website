import metadata from '../data/tool-docs-pages.json';
import type { ToolGuide } from '../data/tool-docs-navigation';

const articles = import.meta.glob<string>('../content/tool-guides/*/*.html', {
  eager: true,
  query: '?raw',
  import: 'default',
});

export function getToolGuidePaths(guide: ToolGuide) {
  return Object.entries(metadata[guide]).map(([page, data]) => {
    const html = articles[`../content/tool-guides/${guide}/${page}.html`];
    if (!html) throw new Error(`Missing reviewed guide: ${guide}/${page}`);
    return {
      params: { page: page === 'index' ? undefined : page },
      props: { page, data, html },
    };
  });
}
