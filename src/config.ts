// Site-wide configuration constants.

// Base URL of the CAIL gateway model catalog (public, unauthenticated, CORS *).
// The models page fetches `${CATALOG_URL}` client-side so the list always
// reflects what the gateway actually serves, without a site rebuild.
//
// TODO(production cutover): this points at the DEV worker
// (cail-model-proxy.ailab-452.workers.dev). It must be switched to the
// production gateway hostname when the model proxy goes live. This is the
// single place the catalog endpoint is defined — do not scatter copies.
export const CATALOG_URL =
  'https://cail-model-proxy.ailab-452.workers.dev/v1/catalog';
