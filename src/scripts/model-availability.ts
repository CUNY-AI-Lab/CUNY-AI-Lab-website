import * as z from 'zod/mini';
import modelSpecifications from '../data/model-specifications.json';

const catalogUrl = 'https://tools.ailab.gc.cuny.edu/v1/catalog';
const price = z.number().check(z.nonnegative());
const pricingSchema = z.object({
  currency: z.literal('USD'),
  unit: z.literal('million_tokens'),
  input: price,
  output: price,
  basis: z.enum(['standard', 'starting_at']),
});
const offeringSchema = z.object({
  id: z.string().check(z.minLength(1), z.maxLength(512)),
  name: z.string().check(z.minLength(1)),
  provider: z.string().check(z.minLength(1)),
  model_group: z.optional(z.string().check(z.minLength(1))),
  capabilities: z.array(z.string()),
  context_length: z.nullable(z.int().check(z.positive())),
  pricing: z.optional(pricingSchema),
});
const catalogSchema = z.object({ object: z.literal('list'), data: z.array(offeringSchema) });
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

type ModelSpecification = (typeof modelSpecifications)[number];

function specificationFor(group: ModelGroup): ModelSpecification | undefined {
  const identities = new Set([group.key, ...group.offerings.map(offering => offering.id)]);
  const matches = modelSpecifications.filter(specification => specification.ids.some(id => identities.has(id)));
  const first = matches[0];
  if (!first) return undefined;
  const sameFacts = matches.every(specification => specification.total_b === first.total_b && specification.active_b === first.active_b && specification.architecture === first.architecture && specification.open_weights === first.open_weights && specification.license_id === first.license_id && specification.license_url === first.license_url && specification.source_url === first.source_url && specification.verified_at === first.verified_at);
  return sameFacts ? first : undefined;
}

function modelSummary(group: ModelGroup): HTMLElement {
  const summary = element('div', '', 'model-summary');
  const specification = specificationFor(group);
  if (!specification) {
    summary.append(element('p', 'Size not available · License not available', 'model-size'));
    return summary;
  }
  const { total_b, active_b, architecture, open_weights, license_id, license_url, source_url, verified_at } = specification;
  const size = [`${total_b}B parameters`];
  if (active_b !== null) size.push(`${active_b}B active`);
  size.push(architecture);
  summary.append(element('p', size.join(' · '), 'model-size'));
  const references = element('div', '', 'model-references');
  if (open_weights) references.append(badge('Open weights', 'open-weights', 'weights-badge'));
  const license = element('a', license_id);
  license.href = license_url;
  const source = element('a', 'Model card');
  source.href = source_url;
  references.append(license, source, element('span', `Specs checked ${verified_at}`, 'specification-date'));
  summary.append(references);
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
  const specs = element('div', '');
  specs.append(element('p', 'Context limit', 'spec-label'), element('p', offering.context_length === null ? 'Not published' : `${integers.format(offering.context_length)} tokens`, 'spec-value'));
  const capabilities = element('div', '', 'capabilities');
  for (const capability of offering.capabilities) capabilities.append(badge(capabilityNames.get(capability) ?? capability, capability));
  if (offering.capabilities.length === 0) capabilities.append(element('span', 'Capabilities not published', 'spec-value'));
  if (offering.context_length !== null && offering.context_length >= 100_000) capabilities.append(badge('Long context', 'long-context'));
  specs.append(capabilities);
  const prices = element('div', '');
  prices.append(element('p', 'USD / million tokens', 'spec-label'));
  if (offering.pricing === undefined) {
    prices.append(element('p', 'Token prices not published', 'spec-value'));
  } else {
    const { input, output, basis } = offering.pricing;
    const prefix = basis === 'starting_at' ? 'from ' : '';
    prices.append(element('p', `Input ${prefix}${formatPrice(input)}`, 'spec-value'), element('p', `Output ${prefix}${formatPrice(output)}`, 'spec-value'));
  }
  row.append(identity, specs, prices);
  return row;
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
      name: preferred.name,
      offerings: entries.toSorted((a, b) => (providerNames.get(a.provider) ?? a.provider).localeCompare(providerNames.get(b.provider) ?? b.provider) || a.id.localeCompare(b.id)),
    };
  }).sort((a, b) => a.name.localeCompare(b.name) || a.key.localeCompare(b.key));
}

function modelCard(group: ModelGroup): HTMLElement {
  const card = element('article', '', 'model-card');
  card.append(element('h2', group.name), modelSummary(group));
  card.append(...group.offerings.map(offeringRow));
  return card;
}

function applyFilters(): void {
  if (!list || !count || !empty || !loaded) return;
  const query = search?.value.trim().toLocaleLowerCase() ?? '';
  let visibleModels = 0;
  let visibleOfferings = 0;
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
    if (matchesInGroup > 0) visibleModels++;
    visibleOfferings += matchesInGroup;
  }
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
  list.replaceChildren();
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
    const offerings = catalog.data;
    groups = groupOfferings(offerings);
    populateFilter(providerFilter, [...new Set(offerings.map(offering => offering.provider))], providerNames, 'All providers');
    populateFilter(capabilityFilter, [...new Set(offerings.flatMap(offering => offering.capabilities))], capabilityNames, 'All capabilities');
    list.replaceChildren(...groups.map(modelCard));
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

search?.addEventListener('input', applyFilters);
providerFilter?.addEventListener('change', applyFilters);
capabilityFilter?.addEventListener('change', applyFilters);
document.querySelector('#clear-filters')?.addEventListener('click', () => {
  if (search) search.value = '';
  if (providerFilter) providerFilter.value = '';
  if (capabilityFilter) capabilityFilter.value = '';
  applyFilters();
});
refresh?.addEventListener('click', () => void refreshCatalog());
void refreshCatalog();
