import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { joinCatalog, validateCatalog } from '../src/lib/catalog-join.mjs';

const editorial = [
  { key: 'glm-5', catalog_id: '@cf/zai-org/glm-5.2', status: 'live', display_name: 'GLM-5' },
  { key: 'deepseek-v3.2', catalog_id: null, status: 'retired', display_name: 'DeepSeek-V3.2' },
];

test('joins a live model to its editorial entry by catalog_id', () => {
  const rows = joinCatalog(
    { object: 'list', data: [{ id: '@cf/zai-org/glm-5.2', order: 1 }] },
    editorial,
  );
  assert.equal(rows.length, 1);
  assert.equal(rows[0].editorial.key, 'glm-5');
});

test('live model without editorial gets editorial: null (no invention)', () => {
  const rows = joinCatalog(
    { object: 'list', data: [{ id: 'cail/gpt-4.1-nano', order: 20 }] },
    editorial,
  );
  assert.equal(rows.length, 1);
  assert.equal(rows[0].editorial, null);
});

test('retired editorial entries never appear (catalog decides the list)', () => {
  const rows = joinCatalog({ object: 'list', data: [] }, editorial);
  assert.equal(rows.length, 0);
});

test('rows come back in catalog order, ties broken by id', () => {
  const rows = joinCatalog(
    {
      data: [
        { id: 'b', order: 10 },
        { id: 'a', order: 1 },
        { id: 'z' }, // no order → sorts last
        { id: 'c', order: 10 },
      ],
    },
    [],
  );
  assert.deepEqual(rows.map((r) => r.catalog.id), ['a', 'b', 'c', 'z']);
});

test('malformed payloads throw (fail loud, no partial render)', () => {
  assert.throws(() => validateCatalog(null));
  assert.throws(() => validateCatalog({ data: 'nope' }));
  assert.throws(() => validateCatalog({ data: [{ name: 'no id' }] }));
  assert.throws(() => joinCatalog({ data: [{ id: '' }] }, []));
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
