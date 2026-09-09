// Keep the published Markdown unchanged and adapt only its rendered HTML.
export default function sandboxDocsLinks(document) {
  if (!document.fileURL?.pathname.includes('/src/content/sandbox-docs/')) return null;
  return {
    name: 'sandbox-docs-links',
    element: {
      filter: ['a', 'pre', 'table'],
      visit(node, context) {
        if (node.tagName === 'a') {
          const match = /^(?:\.\/)?([a-z0-9-]+)\.md([?#].*)?$/.exec(node.properties.href);
          if (match) {
            const [, page, suffix = ''] = match;
            context.setProperty(node, 'href', `/sandbox-docs/${page === 'index' ? '' : `${page}/`}${suffix}`);
          }
        } else {
          // Wide examples and tables can be scrolled with the keyboard.
          context.setProperty(node, 'tabIndex', 0);
        }
      },
    },
  };
}
