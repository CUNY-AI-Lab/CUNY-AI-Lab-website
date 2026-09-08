import * as z from 'zod/mini';

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
  model_group: z.optional(z.string()),
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
let offerings: Offering[] = [];
let loaded = false;

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text: string, className = ''): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

function formatPrice(value: number): string {
  return value > 0 && value < 0.000001
    ? `$${value.toLocaleString('en-US', { maximumSignificantDigits: 21, useGrouping: false })}`
    : dollars.format(value);
}

function offeringRow(offering: Offering): HTMLElement {
  const row = element('article', '', 'model-card');
  const identity = element('div', '', 'offering-identity');
  identity.append(element('p', providerNames.get(offering.provider) ?? offering.provider, 'provider'), element('h2', offering.name));
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
  for (const capability of offering.capabilities) capabilities.append(element('span', capabilityNames.get(capability) ?? capability, 'capability'));
  if (offering.capabilities.length === 0) capabilities.append(element('span', 'Capabilities not published', 'spec-value'));
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

function applyFilters(): void {
  if (!list || !count || !empty || !loaded) return;
  const query = search?.value.trim().toLocaleLowerCase() ?? '';
  let visible = 0;
  for (const [index, row] of Array.from(list.children).entries()) {
    const offering = offerings[index];
    if (!offering || !(row instanceof HTMLElement)) continue;
    const haystack = [offering.name, offering.id, offering.provider, providerNames.get(offering.provider) ?? '', ...offering.capabilities, ...offering.capabilities.map(capability => capabilityNames.get(capability) ?? capability)].join(' ').toLocaleLowerCase();
    const matches = haystack.includes(query) && (!providerFilter?.value || offering.provider === providerFilter.value) && (!capabilityFilter?.value || offering.capabilities.includes(capabilityFilter.value));
    row.hidden = !matches;
    if (matches) visible++;
  }
  count.textContent = `${visible} of ${offerings.length} provider offerings`;
  empty.hidden = visible > 0;
  empty.textContent = offerings.length === 0 ? 'The Gateway catalog currently contains no offerings.' : 'No models match your filters. Clear filters to see all offerings.';
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
  offerings = [];
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
    offerings = catalog.data.sort((a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id));
    populateFilter(providerFilter, [...new Set(offerings.map(offering => offering.provider))], providerNames, 'All providers');
    populateFilter(capabilityFilter, [...new Set(offerings.flatMap(offering => offering.capabilities))], capabilityNames, 'All capabilities');
    list.replaceChildren(...offerings.map(offeringRow));
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
