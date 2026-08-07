// Site-wide configuration constants.

// Canonical CAIL gateway model catalog endpoint (public, unauthenticated).
// The models page fetches `${CATALOG_URL}` client-side so the list always
// reflects what the gateway actually serves, without a site rebuild.
//
// The gateway's reviewed CORS response-header patch must land before this
// browser-facing endpoint is considered production-ready. Changing this URL
// alone does not claim that the live site can read it cross-origin.
export const CATALOG_URL =
  'https://cail-model-api.ailab-452.workers.dev/v1/catalog';
