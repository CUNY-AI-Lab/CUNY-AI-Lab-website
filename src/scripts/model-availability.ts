import * as z from 'zod/mini';
import modelLinks from '../data/model-gateway-links.json';

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
  provider: z.enum(['workers-ai', 'openrouter', 'bedrock-mantle']),
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
  ['vision', 'Image input'],
  ['function-calling', 'Function calling'],
  ['structured-output', 'Structured output'],
  ['reasoning', 'Reasoning'],
]);
const dollars = new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 6,
});
const integers = new Intl.NumberFormat('en-US');
const panels = Array.from(document.querySelectorAll<HTMLElement>('.model-availability'));
const status = document.querySelector<HTMLElement>('#availability-status');
const refresh = document.querySelector<HTMLButtonElement>('#refresh-availability');

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text: string, className = ''): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

function priceText(offering: Offering): string {
  if (offering.pricing === undefined) return 'Token prices not published';
  const { input, output, basis } = offering.pricing;
  const prefix = basis === 'starting_at' ? 'from ' : '';
  return `Input ${prefix}${formatPrice(input)} · Output ${prefix}${formatPrice(output)} per million tokens`;
}

function formatPrice(value: number): string {
  return value > 0 && value < 0.000001 ? '<$0.000001' : dollars.format(value);
}

function offeringRow(offering: Offering): HTMLLIElement {
  const row = element('li', '', 'border-l-2 border-vibrant-200 pl-3 text-sm');
  const provider = element('h4', providerNames.get(offering.provider) ?? offering.provider, 'font-semibold text-neutral-stone');
  const context = offering.context_length === null
    ? 'Context limit not published'
    : `${integers.format(offering.context_length)}-token context`;
  const capabilities = offering.capabilities.flatMap(capability => {
    const label = capabilityNames.get(capability);
    return label === undefined ? [] : [label];
  });
  const specs = element('p', [context, ...capabilities].join(' · '), 'mt-1 text-gray-600');
  const prices = element('p', priceText(offering), 'mt-1 text-gray-700');
  const identity = element('div', '', 'mt-2 flex flex-wrap items-center gap-2');
  const code = element('code', offering.id, 'min-w-0 break-all rounded bg-gray-100 px-2 py-1 text-xs text-gray-700 select-all');
  const copy = element('button', 'Copy API ID', 'rounded border border-gray-300 bg-white px-2 py-1 text-xs font-medium text-vibrant-600 hover:bg-vibrant-50');
  copy.type = 'button';
  copy.setAttribute('aria-label', `Copy API ID ${offering.id}`);
  const result = element('span', '', 'text-xs text-gray-600');
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
  identity.append(code, copy, result);
  row.append(provider, specs, prices, identity);
  return row;
}

function clearOfferings(message: string): void {
  for (const panel of panels) {
    const messageNode = panel.querySelector<HTMLElement>('.availability-message');
    const details = panel.querySelector<HTMLDetailsElement>('.availability-details');
    const list = panel.querySelector<HTMLUListElement>('.availability-offerings');
    if (messageNode) messageNode.textContent = message;
    if (details) {
      details.hidden = true;
      details.open = false;
    }
    list?.replaceChildren();
  }
}

function renderOfferings(offerings: Offering[]): void {
  for (const panel of panels) {
    const link = modelLinks.find(candidate => candidate.key === panel.dataset.modelKey);
    const matches = link === undefined ? [] : offerings.filter(offering =>
      offering.capabilities.includes('text-generation') &&
      (offering.model_group === link.group || link.ids.includes(offering.id)),
    );
    const messageNode = panel.querySelector<HTMLElement>('.availability-message');
    const details = panel.querySelector<HTMLDetailsElement>('.availability-details');
    const list = panel.querySelector<HTMLUListElement>('.availability-offerings');
    if (!messageNode || !details || !list) continue;
    if (matches.length === 0) {
      messageNode.textContent = 'No current Model API offering';
      continue;
    }
    messageNode.textContent = `${matches.length} Model API offering${matches.length === 1 ? '' : 's'}`;
    list.replaceChildren(...matches.map(offeringRow));
    details.hidden = false;
  }
}

async function refreshAvailability(): Promise<void> {
  if (!refresh || !status || refresh.disabled) return;
  refresh.disabled = true;
  status.textContent = 'Checking Model API availability and prices…';
  clearOfferings('Checking availability…');
  try {
    const response = await fetch(catalogUrl, {
      credentials: 'omit', cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) throw new Error('catalog_unavailable');
    const catalog = catalogSchema.parse(await response.json());
    if (new Set(catalog.data.map(offering => offering.id)).size !== catalog.data.length) {
      throw new Error('ambiguous_catalog');
    }
    renderOfferings(catalog.data);
    const checkedAt = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date());
    status.textContent = `Model API checked at ${checkedAt}. Availability and prices can change.`;
  } catch {
    clearOfferings('Couldn’t check availability');
    status.textContent = 'Couldn’t check Model API availability or prices. You can refresh to try again.';
  } finally {
    refresh.disabled = false;
  }
}

if (refresh) {
  refresh.hidden = false;
  refresh.addEventListener('click', () => void refreshAvailability());
  void refreshAvailability();
}
