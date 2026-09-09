import * as z from 'zod/mini';
import featuredData from '../data/featured-models.json';

const catalogUrl = 'https://tools.ailab.gc.cuny.edu/v1/catalog';
const price = z.number().check(z.nonnegative());
const pricingSchema = z.object({
  currency: z.literal('USD'),
  unit: z.literal('million_tokens'),
  input: price,
  output: price,
  basis: z.enum(['standard', 'starting_at']),
});
const metadataText = z.string().check(z.minLength(1), z.maxLength(512), z.refine(value => value.trim() === value && !Array.from(value).some(character => character < ' ' || character === '\u007f')));
const sourceUrl = z.string().check(z.url(), z.refine(value => {
  if (!URL.canParse(value) || value.trim() !== value || Array.from(value).some(character => character < ' ' || character === '\u007f')) return false;
  const url = new URL(value);
  return url.protocol === 'https:' && url.username === '' && url.password === '';
}));
const specificationsSchema = z.object({
  checked_at: z.iso.datetime({ offset: true }),
  model_url: z.catch(z.optional(sourceUrl), undefined),
  weights: z.catch(z.optional(z.object({ available: z.boolean(), source_url: sourceUrl })), undefined),
  license: z.catch(z.optional(z.object({ name: metadataText, url: sourceUrl, source_url: sourceUrl })), undefined),
  architecture: z.catch(z.optional(z.object({ name: metadataText, source_url: sourceUrl })), undefined),
  size: z.catch(z.optional(z.object({ label: metadataText, basis: z.enum(['advertised', 'checkpoint']), source_url: sourceUrl })), undefined),
});
type Specifications = z.infer<typeof specificationsSchema>;
const offeringSchema = z.object({
  id: z.string().check(z.minLength(1), z.maxLength(512)),
  name: z.string().check(z.minLength(1)),
  provider: z.string().check(z.minLength(1)),
  routing: z.catch(z.optional(z.object({ mode: z.string() })), undefined),
  model_name: z.catch(z.optional(metadataText), undefined),
  specifications: z.catch(z.optional(specificationsSchema), undefined),
  model_group: z.optional(z.string().check(z.minLength(1))),
  capabilities: z.array(z.string()),
  context_length: z.nullable(z.int().check(z.positive())),
  pricing: z.optional(pricingSchema),
});
const catalogSchema = z.object({ object: z.literal('list'), data: z.array(offeringSchema) });
const featuredSchema = z.object({
  updated_at: z.string(),
  models: z.array(z.object({ name: metadataText, note: metadataText, ids: z.array(z.string().check(z.minLength(1))).check(z.minLength(1)) })),
});
const featured = featuredSchema.parse(featuredData);
type Offering = z.infer<typeof offeringSchema>;
const providerNames = new Map([
  ['workers-ai', 'Workers AI'],
  ['openrouter', 'OpenRouter'],
  ['bedrock-mantle', 'Bedrock Mantle'],
]);
const capabilityNames = new Map([
  ['text-generation', 'Text generation'],
  ['automatic-speech-recognition', 'Speech recognition'],
  ['vision', 'Image input'],
  ['function-calling', 'Function calling'],
  ['structured-output', 'Structured output'],
  ['reasoning', 'Reasoning'],
]);
const dollars = new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 6,
});
const integers = new Intl.NumberFormat('en-US');
const list = document.querySelector<HTMLElement>('#models-list');
const featuredSection = document.querySelector<HTMLElement>('#featured-models');
const featuredList = document.querySelector<HTMLElement>('#featured-list');
const status = document.querySelector<HTMLElement>('#catalog-status');
const refresh = document.querySelector<HTMLButtonElement>('#refresh-catalog');
const search = document.querySelector<HTMLInputElement>('#model-search');
const providerFilter = document.querySelector<HTMLSelectElement>('#provider-filter');
const capabilityFilter = document.querySelector<HTMLSelectElement>('#capability-filter');
const count = document.querySelector<HTMLElement>('#results-count');
const empty = document.querySelector<HTMLElement>('#empty-state');
type ModelGroup = { key: string; name: string; offerings: Offering[] };
let groups: ModelGroup[] = [];
let loaded = false;
const modelsPerPage = 12;
let modelPage = 1;

function updatePagination(page: number, total: number, pageSize: number): void {
  const pages = Math.ceil(total / pageSize);
  for (const nav of document.querySelectorAll<HTMLElement>('[data-pagination="all"]')) {
    nav.hidden = pages <= 1;
    const pageStatus = nav.querySelector<HTMLElement>('[data-page-status]');
    if (pageStatus) pageStatus.textContent = total === 0 ? '' : `Page ${page} of ${pages} · ${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, total)} of ${total} models`;
    for (const button of nav.querySelectorAll<HTMLButtonElement>('[data-page-step]')) {
      button.disabled = button.dataset.pageStep === '-1' ? page <= 1 : page >= pages;
    }
  }
}

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text: string, className = ''): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

const iconPaths = new Map([
  ['vision', 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12 M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0'],
  ['reasoning', 'M9 18h6 M9 21h6 M8 14a6 6 0 1 1 8 0c-1 1-1 2-1 3H9c0-1 0-2-1-3'],
  ['function-calling', 'M14 6a5 5 0 0 0-6 6L3 17a3 3 0 0 0 4 4l5-5a5 5 0 0 0 6-6l-3 3-4-4 3-3Z'],
  ['structured-output', 'M8 3H5v6l-2 3 2 3v6h3 M16 3h3v6l2 3-2 3v6h-3 M10 9h4 M10 15h4'],
  ['text-generation', 'M4 4h16v12H8l-4 4V4Z M8 8h8 M8 12h5'],
  ['automatic-speech-recognition', 'M9 5a3 3 0 0 1 6 0v7a3 3 0 0 1-6 0V5Z M5 10v2a7 7 0 0 0 14 0v-2 M12 19v3 M8 22h8'],
  ['long-context', 'M6 3h9l4 4v14H6V3Z M14 3v5h5 M9 12h7 M9 16h7'],
  ['open-weights', 'M7 11V7a5 5 0 0 1 9-3 M5 11h14v10H5V11Z M12 15v3'],
]);

function badge(label: string, icon: string, className = 'capability'): HTMLElement {
  const node = element('span', '', className);
  const pathData = iconPaths.get(icon);
  if (pathData) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '1.7');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathData);
    svg.append(path);
    node.append(svg);
  }
  node.append(document.createTextNode(label));
  return node;
}

function agreedFact<K extends keyof Omit<Specifications, 'checked_at'>>(group: ModelGroup, key: K, identity: (value: NonNullable<Specifications[K]>) => string): { value: NonNullable<Specifications[K]>; checkedAt: string } | undefined {
  const facts = group.offerings.flatMap(offering => {
    const specs = offering.specifications;
    const value = specs?.[key];
    return specs && value !== undefined ? [{ value, checkedAt: specs.checked_at }] : [];
  }).sort((a, b) => Date.parse(a.checkedAt) - Date.parse(b.checkedAt));
  const first = facts[0];
  if (!first || !facts.every(fact => identity(fact.value) === identity(first.value))) return undefined;
  return first;
}

function modelSummary(group: ModelGroup): HTMLElement {
  const summary = element('div', '', 'model-summary');
  const highlights = element('div', '', 'model-highlights');
  const details = element('details', '', 'model-details');
  details.append(element('summary', 'Details and sources'));
  const references = element('div', '', 'model-evidence');
  const dates = new Set<string>();
  function fact(field: string, label: string, sourceUrl: string, checkedAt: string): void {
    const row = element('div', '', 'model-references');
    row.append(element('span', field, 'evidence-label'));
    const link = element('a', label);
    link.href = sourceUrl;
    link.setAttribute('aria-label', field === 'License' ? `Source for ${label}` : label);
    row.append(link, element('span', `Checked ${checkedAt.slice(0, 10)}`, 'specification-date'));
    references.append(row);
    dates.add(checkedAt.slice(0, 10));
  }
  function highlight(label: string, className: string, url?: string): void {
    const item = element('span', '', `model-highlight ${className}`);
    if (url) {
      const link = element('a', label);
      link.href = url;
      item.append(link);
    } else item.textContent = label;
    highlights.append(item);
  }
  const size = agreedFact(group, 'size', value => JSON.stringify([value.label, value.basis]));
  if (size) {
    highlight(size.value.label, 'model-size');
    fact('Size', `${size.value.label} · ${size.value.basis === 'checkpoint' ? 'Checkpoint parameter count' : 'Advertised size'}`, size.value.source_url, size.checkedAt);
  }
  const weights = agreedFact(group, 'weights', value => String(value.available));
  if (weights) {
    const label = weights.value.available ? 'Open weights' : 'Weights not published';
    highlight(label, weights.value.available ? 'model-open' : 'model-closed', weights.value.source_url);
    fact('Weights', label, weights.value.source_url, weights.checkedAt);
  }
  const license = agreedFact(group, 'license', value => JSON.stringify([value.name, value.url]));
  if (license) {
    highlight(license.value.name, 'model-license', license.value.url);
    fact('License', license.value.name, license.value.source_url, license.checkedAt);
  }
  const architecture = agreedFact(group, 'architecture', value => value.name);
  if (architecture) fact('Architecture', architecture.value.name, architecture.value.source_url, architecture.checkedAt);
  const modelUrl = agreedFact(group, 'model_url', value => value);
  if (modelUrl) fact('Reference', 'Model card', modelUrl.value, modelUrl.checkedAt);
  if (references.childElementCount === 0) {
    summary.append(element('p', 'Specifications not published', 'specification-date'));
  } else {
    if (dates.size === 1) references.append(element('p', `Checked ${Array.from(dates)[0]}`, 'specification-date evidence-date'));
    details.append(references);
    summary.append(highlights, details);
  }
  return summary;
}

function formatPrice(value: number): string {
  return value > 0 && value < 0.000001
    ? `$${value.toLocaleString('en-US', { maximumSignificantDigits: 21, useGrouping: false })}`
    : dollars.format(value);
}

function offeringRow(offering: Offering): HTMLElement {
  const row = element('div', '', 'provider-offering');
  const identity = element('div', '', 'offering-identity');
  identity.append(element('h3', providerNames.get(offering.provider) ?? offering.provider, 'provider'));
  const api = element('div', '', 'identity');
  const code = element('code', offering.id);
  const copy = element('button', 'Copy API ID');
  copy.type = 'button';
  copy.setAttribute('aria-label', `Copy API ID ${offering.id}`);
  const result = element('span', '', 'copy-result');
  result.setAttribute('role', 'status');
  result.setAttribute('aria-label', `Copy result for ${offering.id}`);
  copy.addEventListener('click', async () => {
    try {
      if (!('clipboard' in navigator)) throw new Error('clipboard_unavailable');
      await navigator.clipboard.writeText(offering.id);
      result.textContent = 'Copied';
    } catch {
      result.textContent = 'Couldn’t copy. Select the API ID to copy it manually.';
    }
  });
  api.append(code, copy, result);
  identity.append(api);
  const specs = figure('Context limit', offering.context_length === null ? 'Not published' : `${integers.format(offering.context_length)} tokens`);
  const capabilities = element('div', '', 'capabilities');
  for (const capability of offering.capabilities) capabilities.append(badge(capabilityNames.get(capability) ?? capability, capability));
  if (offering.capabilities.length === 0) capabilities.append(element('span', 'Capabilities not published', 'spec-value'));
  if (offering.context_length !== null && offering.context_length >= 100_000) capabilities.append(badge('Long context', 'long-context'));

  const prices = element('div', '', 'offering-prices');
  if (offering.pricing === undefined) {
    prices.append(figure('USD / million tokens', 'Token prices not published'));
  } else {
    const { input, output, basis } = offering.pricing;
    const prefix = basis === 'starting_at' ? 'from ' : '';
    prices.append(figure(`Input ${prefix}`, formatPrice(input)), figure(`Output ${prefix}`, formatPrice(output)), element('p', 'USD per million tokens', 'spec-unit price-unit'));
  }
  row.append(identity, specs, prices, capabilities);
  return row;
}

function figure(label: string, value: string): HTMLElement {
  const node = element('div', '', 'spec');
  node.append(element('p', label.trim(), 'spec-label'), document.createTextNode(' '));
  const line = element('p', '', 'spec-value');
  line.append(element('strong', value));
  node.append(line);
  return node;
}

function groupOfferings(offerings: Offering[]): ModelGroup[] {
  const byKey = new Map<string, Offering[]>();
  for (const offering of offerings) {
    const key = offering.model_group ?? offering.id;
    const existing = byKey.get(key);
    if (existing) existing.push(offering);
    else byKey.set(key, [offering]);
  }
  return Array.from(byKey, ([key, entries]) => {
    const alphabetical = entries.toSorted((a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id));
    const preferred = alphabetical.find(offering => offering.id === key) ?? alphabetical[0];
    if (!preferred) throw new Error('empty_model_group');
    return {
      key,
      name: preferred.model_name ?? alphabetical.find(offering => offering.model_name)?.model_name ?? preferred.name,
      offerings: entries.toSorted((a, b) => (providerNames.get(a.provider) ?? a.provider).localeCompare(providerNames.get(b.provider) ?? b.provider) || a.id.localeCompare(b.id)),
    };
  }).sort((a, b) => a.name.localeCompare(b.name) || a.key.localeCompare(b.key));
}

function modelCard(group: ModelGroup, note?: string): HTMLElement {
  const card = element('article', '', note === undefined ? 'model-card' : 'model-card featured-card');
  card.append(element('h2', group.name));
  if (note !== undefined) card.append(element('p', note, 'featured-note'));
  card.append(modelSummary(group));
  card.append(...group.offerings.map(offeringRow));
  return card;
}

function featuredCards(offerings: Offering[]): HTMLElement[] {
  const byId = new Map(offerings.map(offering => [offering.id, offering]));
  return featured.models.flatMap(entry => {
    const listed = entry.ids.flatMap(id => byId.get(id) ?? []);
    if (listed.length === 0) return [];
    const group: ModelGroup = {
      key: entry.ids[0] ?? entry.name,
      name: entry.name,
      offerings: listed.toSorted((a, b) => (providerNames.get(a.provider) ?? a.provider).localeCompare(providerNames.get(b.provider) ?? b.provider) || a.id.localeCompare(b.id)),
    };
    return [modelCard(group, entry.note)];
  });
}

function applyFilters(): void {
  if (!list || !count || !empty || !loaded) return;
  const query = search?.value.trim().toLocaleLowerCase() ?? '';
  const filtering = query !== '' || Boolean(providerFilter?.value) || Boolean(capabilityFilter?.value);
  if (featuredSection) featuredSection.hidden = filtering || (featuredList?.childElementCount ?? 0) === 0;
  let visibleModels = 0;
  let visibleOfferings = 0;
  const matchingCards: HTMLElement[] = [];
  for (const [index, card] of Array.from(list.children).entries()) {
    const group = groups[index];
    if (!group || !(card instanceof HTMLElement)) continue;
    let matchesInGroup = 0;
    const rows = card.querySelectorAll<HTMLElement>('.provider-offering');
    for (const [offeringIndex, row] of Array.from(rows).entries()) {
      const offering = group.offerings[offeringIndex];
      if (!offering) continue;
      const haystack = [group.name, group.key, offering.name, offering.id, offering.provider, providerNames.get(offering.provider) ?? '', ...offering.capabilities, ...offering.capabilities.map(capability => capabilityNames.get(capability) ?? capability)].join(' ').toLocaleLowerCase();
      const matches = haystack.includes(query) && (!providerFilter?.value || offering.provider === providerFilter.value) && (!capabilityFilter?.value || offering.capabilities.includes(capabilityFilter.value));
      row.hidden = !matches;
      if (matches) matchesInGroup++;
    }
    card.hidden = matchesInGroup === 0;
    if (matchesInGroup > 0) {
      visibleModels++;
      matchingCards.push(card);
    }
    visibleOfferings += matchesInGroup;
  }
  modelPage = Math.min(modelPage, Math.max(1, Math.ceil(visibleModels / modelsPerPage)));
  matchingCards.forEach((card, index) => {
    card.hidden = index < (modelPage - 1) * modelsPerPage || index >= modelPage * modelsPerPage;
  });
  updatePagination(modelPage, visibleModels, modelsPerPage);
  count.textContent = `${visibleModels} model${visibleModels === 1 ? '' : 's'} · ${visibleOfferings} provider offering${visibleOfferings === 1 ? '' : 's'}`;
  empty.hidden = visibleModels > 0;
  empty.textContent = groups.length === 0 ? 'The Gateway catalog currently contains no offerings.' : 'No models match your filters. Clear filters to see all offerings.';
}

function populateFilter(select: HTMLSelectElement | null, values: string[], names: Map<string, string>, all: string): void {
  if (!select) return;
  const previous = select.value;
  const options = [new Option(all, ''), ...values.sort((a, b) => (names.get(a) ?? a).localeCompare(names.get(b) ?? b)).map(value => new Option(names.get(value) ?? value, value))];
  select.replaceChildren(...options);
  select.value = values.includes(previous) ? previous : '';
}

async function refreshCatalog(): Promise<void> {
  if (!refresh || !status || !list || !empty || !count || refresh.disabled) return;
  refresh.disabled = true;
  loaded = false;
  groups = [];
  modelPage = 1;
  updatePagination(modelPage, 0, modelsPerPage);
  list.replaceChildren();
  featuredList?.replaceChildren();
  if (featuredSection) featuredSection.hidden = true;
  count.textContent = '';
  empty.hidden = true;
  status.textContent = 'Loading the live catalog…';
  try {
    const response = await fetch(catalogUrl, {
      credentials: 'omit', cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) throw new Error('catalog_unavailable');
    const catalog = catalogSchema.parse(await response.json());
    if (new Set(catalog.data.map(offering => offering.id)).size !== catalog.data.length) throw new Error('ambiguous_catalog');
    const offerings = catalog.data.filter(offering => offering.routing?.mode !== 'automatic');
    groups = groupOfferings(offerings);
    populateFilter(providerFilter, [...new Set(offerings.map(offering => offering.provider))], providerNames, 'All providers');
    populateFilter(capabilityFilter, [...new Set(offerings.flatMap(offering => offering.capabilities))], capabilityNames, 'All capabilities');
    list.replaceChildren(...groups.map(group => modelCard(group)));
    featuredList?.replaceChildren(...featuredCards(offerings));
    loaded = true;
    applyFilters();
    const checkedAt = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date());
    status.textContent = `Catalog checked at ${checkedAt}. Availability and prices can change.`;
  } catch {
    empty.hidden = false;
    empty.textContent = 'The live catalog is unavailable. Refresh catalog to try again.';
    status.textContent = 'Couldn’t load the Gateway catalog. Availability and prices are unknown.';
  } finally {
    refresh.disabled = false;
  }
}

function resetFiltersPage(): void {
  modelPage = 1;
  applyFilters();
}

for (const nav of document.querySelectorAll<HTMLElement>('[data-pagination="all"]')) {
  for (const button of nav.querySelectorAll<HTMLButtonElement>('[data-page-step]')) {
    button.addEventListener('click', () => {
      if (!loaded || button.disabled) return;
      const step = button.dataset.pageStep === '-1' ? -1 : 1;
      modelPage = Math.max(1, modelPage + step);
      applyFilters();
      const heading = document.querySelector<HTMLElement>('#all-models-heading');
      heading?.focus({ preventScroll: true });
      heading?.scrollIntoView({ block: 'start' });
    });
  }
}

search?.addEventListener('input', resetFiltersPage);
providerFilter?.addEventListener('change', resetFiltersPage);
capabilityFilter?.addEventListener('change', resetFiltersPage);
document.querySelector('#clear-filters')?.addEventListener('click', () => {
  if (search) search.value = '';
  if (providerFilter) providerFilter.value = '';
  if (capabilityFilter) capabilityFilter.value = '';
  resetFiltersPage();
});
refresh?.addEventListener('click', () => void refreshCatalog());
void refreshCatalog();
