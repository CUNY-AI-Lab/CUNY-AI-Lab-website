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

const MAX_CATALOG_ENTRIES = 2_000;
const CATALOG_PROVIDERS = new Set(['workers-ai', 'openrouter']);
const CATALOG_STATUSES = new Set(['active', 'deprecated', 'retiring']);
const CATALOG_MODALITIES = new Set(['text', 'image']);
const CATALOG_PRICING_STATES = new Set(['catalog', 'verified-live']);
const CONTROL_CHARACTERS = /[\x00-\x1f\x7f]/;

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function validOptionalString(value, maxLength) {
  return value === undefined || (
    typeof value === 'string' &&
    value.length > 0 &&
    value.trim().length > 0 &&
    value.length <= maxLength &&
    !CONTROL_CHARACTERS.test(value)
  );
}

function invalidCatalog(message) {
  throw new Error(`Invalid catalog: ${message}`);
}

/**
 * Validate the public catalog fields consumed by the models page. Throws on
 * anything unusable so malformed or partial responses never render as facts.
 * @param {unknown} payload - parsed JSON from GET {CATALOG_URL}
 * @returns {Array<object>} the catalog model list
 */
export function validateCatalog(payload) {
  if (!isRecord(payload) || payload.object !== 'list' || !Array.isArray(payload.data)) {
    invalidCatalog('expected an object=list envelope with a data array');
  }
  if (payload.data.length > MAX_CATALOG_ENTRIES) {
    invalidCatalog(`data exceeds ${MAX_CATALOG_ENTRIES} entries`);
  }

  const ids = new Set();
  for (const [index, model] of payload.data.entries()) {
    if (!isRecord(model)) invalidCatalog(`entry ${index} is not an object`);
    if (
      model.object !== 'model' ||
      typeof model.id !== 'string' ||
      model.id.length === 0 ||
      model.id.trim().length === 0 ||
      model.id.length > 128 ||
      CONTROL_CHARACTERS.test(model.id)
    ) {
      invalidCatalog(`entry ${index} has an invalid model object or id`);
    }
    if (ids.has(model.id)) invalidCatalog(`duplicate model id: ${model.id}`);
    ids.add(model.id);

    if (!CATALOG_PROVIDERS.has(model.provider)) {
      invalidCatalog(`entry ${index} has an invalid provider`);
    }
    if (!CATALOG_STATUSES.has(model.status)) {
      invalidCatalog(`entry ${index} has an invalid status`);
    }
    if (!Number.isSafeInteger(model.order) || model.order < 0) {
      invalidCatalog(`entry ${index} has an invalid order`);
    }
    if (
      typeof model.upstream_model !== 'string' ||
      model.upstream_model.length === 0 ||
      model.upstream_model.trim().length === 0 ||
      model.upstream_model.length > 128 ||
      CONTROL_CHARACTERS.test(model.upstream_model)
    ) {
      invalidCatalog(`entry ${index} has an invalid upstream_model`);
    }
    if (!Array.isArray(model.capabilities) || model.capabilities.length > 32) {
      invalidCatalog(`entry ${index} has invalid capabilities`);
    }
    const capabilitySet = new Set();
    for (const capability of model.capabilities) {
      if (
        typeof capability !== 'string' ||
        capability.length === 0 ||
        capability.trim().length === 0 ||
        capability.length > 64 ||
        CONTROL_CHARACTERS.test(capability) ||
        capabilitySet.has(capability)
      ) {
        invalidCatalog(`entry ${index} has invalid or duplicate capabilities`);
      }
      capabilitySet.add(capability);
    }
    if (
      model.context_length !== null &&
      (!Number.isSafeInteger(model.context_length) || model.context_length < 1)
    ) {
      invalidCatalog(`entry ${index} has an invalid context_length`);
    }
    if (
      typeof model.recommended !== 'boolean' ||
      !CATALOG_MODALITIES.has(model.modality) ||
      typeof model.streaming !== 'boolean' ||
      !CATALOG_PRICING_STATES.has(model.pricing_known) ||
      !validOptionalString(model.name, 256) ||
      !validOptionalString(model.description, 2_048)
    ) {
      invalidCatalog(`entry ${index} has invalid display metadata`);
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
