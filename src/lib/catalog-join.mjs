// Join the LIVE gateway catalog (authority for which models exist and their
// technical facts) with the site-owned editorial overlay in
// src/data/model-registry.json (keyed by catalog_id).
//
// Design rules:
// - The catalog decides WHICH models are listed. Editorial entries with no
//   live counterpart (status "retired" / catalog_id null) are never shown.
// - A live model with no editorial entry is still shown, using only
//   catalog-provided fields (editorial: null → the page renders a
//   "editorial coming soon" card). Nothing is invented.
// - Malformed catalog payloads throw — the page fails loud rather than
//   rendering a wrong or partial list.

/**
 * Validate the catalog payload shape. Throws on anything unusable.
 * @param {unknown} payload - parsed JSON from GET {CATALOG_URL}
 * @returns {Array<object>} the catalog model list
 */
export function validateCatalog(payload) {
  if (!payload || typeof payload !== 'object' || !Array.isArray(payload.data)) {
    throw new Error('Catalog payload is not a {data: [...]} list');
  }
  for (const model of payload.data) {
    if (!model || typeof model !== 'object' || typeof model.id !== 'string' || model.id === '') {
      throw new Error('Catalog entry missing a string id');
    }
  }
  return payload.data;
}

/**
 * Left-join live catalog models to editorial entries by catalog_id.
 * @param {unknown} catalogPayload - parsed JSON from the catalog endpoint
 * @param {Array<object>} editorialModels - entries from model-registry.json
 * @returns {Array<{catalog: object, editorial: object|null}>} one row per
 *   LIVE catalog model, in catalog `order` (then id) order.
 */
export function joinCatalog(catalogPayload, editorialModels) {
  const catalog = validateCatalog(catalogPayload);
  const byCatalogId = new Map();
  for (const entry of editorialModels || []) {
    if (entry && typeof entry.catalog_id === 'string' && entry.catalog_id !== '') {
      byCatalogId.set(entry.catalog_id, entry);
    }
  }
  return catalog
    .slice()
    .sort((a, b) => {
      const ao = typeof a.order === 'number' ? a.order : Number.MAX_SAFE_INTEGER;
      const bo = typeof b.order === 'number' ? b.order : Number.MAX_SAFE_INTEGER;
      return ao - bo || String(a.id).localeCompare(String(b.id));
    })
    .map((model) => ({
      catalog: model,
      editorial: byCatalogId.get(model.id) || null,
    }));
}
