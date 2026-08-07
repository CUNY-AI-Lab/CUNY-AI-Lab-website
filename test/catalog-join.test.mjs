import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { joinCatalog, validateCatalog } from '../src/lib/catalog-join.mjs';

const LIVE_ID = '@cf/openai/gpt-oss-120b';

function catalogEntry(overrides = {}) {
  return {
    id: 'test/model',
    object: 'model',
    recommended: false,
    tier: 'advanced',
    order: 1,
    status: 'active',
    modality: 'text',
    provider: 'workers-ai',
    upstream_model: 'test/model',
    pricing_known: 'catalog',
    streaming: true,
    sunset: null,
    capabilities: ['text-generation'],
    context_length: 128000,
    registry_url: null,
    ...overrides,
  };
}

function catalogPayload(data) {
  return { object: 'list', data };
}

const editorial = [
  { key: 'gpt-oss-120b', catalog_id: LIVE_ID, status: 'live', display_name: 'gpt-oss-120b' },
  { key: 'deepseek-v3.2', catalog_id: null, status: 'retired', display_name: 'DeepSeek-V3.2' },
];

test('joins a live model to its editorial entry by catalog_id', () => {
  const rows = joinCatalog(
    catalogPayload([catalogEntry({ id: LIVE_ID, upstream_model: LIVE_ID })]),
    editorial,
  );
  assert.equal(rows.length, 1);
  assert.equal(rows[0].editorial.key, 'gpt-oss-120b');
});

test('live model without editorial gets editorial: null (no invention)', () => {
  const rows = joinCatalog(
    catalogPayload([catalogEntry({ id: 'cail/gpt-4.1-nano', upstream_model: 'cail/gpt-4.1-nano', order: 20 })]),
    editorial,
  );
  assert.equal(rows.length, 1);
  assert.equal(rows[0].editorial, null);
});

test('retired editorial entries never appear (catalog decides the list)', () => {
  const rows = joinCatalog(catalogPayload([]), editorial);
  assert.equal(rows.length, 0);
});

test('rows come back in catalog order, ties broken by id', () => {
  const rows = joinCatalog(
    catalogPayload([
      catalogEntry({ id: 'b', upstream_model: 'b', order: 10 }),
      catalogEntry({ id: 'a', upstream_model: 'a', order: 1 }),
      catalogEntry({ id: 'z', upstream_model: 'z', order: 20 }),
      catalogEntry({ id: 'c', upstream_model: 'c', order: 10 }),
    ]),
    [],
  );
  assert.deepEqual(rows.map((r) => r.catalog.id), ['a', 'b', 'c', 'z']);
});

test('malformed payloads throw (fail loud, no partial render)', () => {
  assert.throws(() => validateCatalog(null));
  assert.throws(() => validateCatalog({ object: 'list', data: 'nope' }));
  assert.throws(() => validateCatalog(catalogPayload([catalogEntry({ id: '' })])));
  assert.throws(() => joinCatalog(catalogPayload([catalogEntry({ provider: 'unknown' })]), []));
});

test('valid empty catalogs remain empty instead of becoming a fake model list', () => {
  assert.deepEqual(validateCatalog(catalogPayload([])), []);
  assert.deepEqual(joinCatalog(catalogPayload([]), editorial), []);
});

test('duplicate and oversized catalogs fail before rendering', () => {
  const duplicate = catalogEntry({ id: 'duplicate', upstream_model: 'duplicate' });
  assert.throws(() => validateCatalog(catalogPayload([duplicate, { ...duplicate }])));

  const oversized = Array.from({ length: 2001 }, (_, index) => catalogEntry({
    id: `model/${index}`,
    upstream_model: `model/${index}`,
    order: index,
  }));
  assert.throws(() => validateCatalog(catalogPayload(oversized)));
});

test('catalog contract fields reject wrong types', () => {
  for (const overrides of [
    { status: 1 },
    { order: '1' },
    { capabilities: ['text-generation', 1] },
    { context_length: '128000' },
    { upstream_model: null },
  ]) {
    assert.throws(() => validateCatalog(catalogPayload([catalogEntry(overrides)])));
  }
});

test('renderer-consumed optional metadata rejects whitespace-only strings', () => {
  assert.throws(() => validateCatalog(catalogPayload([catalogEntry({ name: '   ' })])));
  assert.throws(() => validateCatalog(catalogPayload([catalogEntry({ description: '   ' })])));
});

test('site editorial file: every live entry has a catalog_id, retired entries none', () => {
  const registry = JSON.parse(fs.readFileSync(new URL('../src/data/model-registry.json', import.meta.url), 'utf8'));
  for (const entry of registry.models) {
    assert.ok(['live', 'retired'].includes(entry.status), `${entry.key}: status`);
    if (entry.status === 'live') {
      assert.equal(typeof entry.catalog_id, 'string', `${entry.key}: live needs catalog_id`);
    } else {
      assert.equal(entry.catalog_id, null, `${entry.key}: retired must not map`);
    }
  }
  const ids = registry.models.filter((m) => m.catalog_id).map((m) => m.catalog_id);
  assert.equal(new Set(ids).size, ids.length, 'catalog_id values must be unique');
});

test('known stale overlays are removed and the catalog endpoint is canonical', () => {
  const registry = JSON.parse(fs.readFileSync(new URL('../src/data/model-registry.json', import.meta.url), 'utf8'));
  const keys = new Set(registry.models.map((entry) => entry.key));
  assert.equal(keys.has('kimi-k2.5'), false);
  assert.equal(keys.has('glm-5'), false);

  const config = fs.readFileSync(new URL('../src/config.ts', import.meta.url), 'utf8');
  assert.match(config, /https:\/\/cail-model-api\.ailab-452\.workers\.dev\/v1\/catalog/);
  assert.doesNotMatch(config, /cail-model-proxy/);
});

test('models page has bounded cancellation, empty/error states, and no-script text', () => {
  const page = fs.readFileSync(new URL('../src/pages/models.astro', import.meta.url), 'utf8');
  for (const marker of [
    'new AbortController()',
    'requestGeneration',
    'activeRequest.controller.abort()',
    'setTimeout',
    "credentials: 'omit'",
    "cache: 'no-store'",
    'id="models-loading" class="hidden',
    'id="catalog-empty-state"',
    'id="models-error"',
    'The live model catalog needs JavaScript',
  ]) {
    assert.ok(page.includes(marker), `missing models-page marker: ${marker}`);
  }
  assert.match(page, /errorEl\.classList\.add\('hidden'\)/);
  assert.match(page, /errorDetailEl\) errorDetailEl\.textContent = ''/);
});
