"""Browser registry journeys; Gateway responses are substituted explicitly."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, expect, sync_playwright

BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
CATALOG_URL = "https://tools.ailab.gc.cuny.edu/v1/catalog"


def offering(api_id: str, provider: str = "openrouter", **fields: Any) -> dict:
    return {"id": api_id, "name": api_id, "provider": provider,
            "capabilities": ["text-generation", "reasoning", "function-calling"],
            "context_length": 163840, **fields}


def pricing(input_price: float, output_price: float, basis: str = "standard") -> dict:
    return {"currency": "USD", "unit": "million_tokens", "input": input_price,
            "output": output_price, "basis": basis}


SPECS = {
    "checked_at": "2026-09-08T10:00:00Z",
    "model_url": "https://example.org/model",
    "size": {"label": "116.8B", "basis": "checkpoint", "source_url": "https://example.org/size"},
    "architecture": {"name": "MoE", "source_url": "https://example.org/architecture"},
    "weights": {"available": True, "source_url": "https://example.org/weights"},
    "license": {"name": "Apache-2.0", "url": "https://example.org/license", "source_url": "https://example.org/license-evidence"},
}

CATALOG = {"object": "list", "data": [
    offering("deepseek/deepseek-v3.2", name="DeepSeek V3.2", model_group="deepseek/deepseek-v3.2", pricing=pricing(0.2, 0.3)),
    offering("deepseek.v3.2", "bedrock-mantle", name="DeepSeek alternate name", model_group="deepseek/deepseek-v3.2", context_length=None, capabilities=["text-generation"]),
    offering("@cf/openai/gpt-oss-120b", "workers-ai", name="Alternate OSS name", model_name="GPT OSS 120B", specifications=SPECS, model_group="openai/gpt-oss-120b", pricing=pricing(0, 0.000001)),
    offering("openai/gpt-oss-120b", name="Provider-prefixed OSS label", pricing=pricing(0.04, 0.15, "starting_at")),
    offering("google/gemma-4-31b-it", name="Gemma 4 31B", capabilities=["text-generation", "vision"]),
    offering("deepseek/deepseek-v3.2-speciale", name="DeepSeek V3.2 Speciale"),
    offering("future/new-release-2099", name="Previously unseen release"),
    offering("deepseek-embedding", name="DeepSeek Embeddings",
             capabilities=["embeddings"]),
    offering("independent/same-name-a", name="Identical name"),
    offering("independent/same-name-b", name="Identical name"),
    offering("provider/image-route", name="Image generator", capabilities=["text-to-image"], pricing=pricing(0.00000001, 0.1)),
]}


MODEL_COUNT = 9

def stub_catalog(page: Page, payload: Any = CATALOG, *, network_failure: bool = False) -> None:
    page.unroute(CATALOG_URL)
    if network_failure:
        page.route(CATALOG_URL, lambda route: route.abort("failed"))
    else:
        page.route(CATALOG_URL, lambda route: route.fulfill(
            status=200, content_type="application/json", body=json.dumps(payload)))


def expect_checked(page: Page) -> None:
    expect(page.get_by_role("status", name="Catalog status", exact=True)).to_contain_text("Catalog checked at")
    expect(page.get_by_role("button", name="Refresh catalog", exact=True)).to_be_enabled()


def model_card(page: Page, api_id: str):
    return page.locator("#models-list article.model-card").filter(has=page.locator("code").filter(has_text=re.compile("^" + re.escape(api_id) + "$")))


def provider_row(page: Page, api_id: str):
    return page.locator("#models-list .provider-offering").filter(has=page.locator("code").filter(has_text=re.compile("^" + re.escape(api_id) + "$")))


def test_automatic_primary_and_native_facts(page: Page) -> None:
    fixture = json.loads((Path(__file__).parent / "fixtures/gateway-native-offerings.json").read_text())
    catalog = fixture["catalog"]
    stub_catalog(page, catalog)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    rows = page.locator("#models-list .provider-offering")
    native_ids = [row["id"] for row in catalog["data"]]
    expect(rows).to_have_count(len(native_ids))
    before_count = page.locator("#results-count").inner_text()
    before_facts = {api_id: provider_row(page, api_id).inner_text() for api_id in native_ids}
    default = catalog["data"][0]
    automatic_id = "auto/openai/gpt-oss-120b"
    automatic = {**default, "id": automatic_id, "name": "GPT OSS 120B",
                 "routing": {"mode": "automatic", "routes": native_ids}}
    native = [{**row, "duplicate_of": automatic_id} for row in catalog["data"]]
    stub_catalog(page, {"object": "list", "data": [*native, automatic]})
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(rows).to_have_count(len(native_ids))
    expect(page.locator("#results-count")).to_have_text(before_count)
    assert rows.locator("code").all_text_contents() == native_ids
    assert {api_id: provider_row(page, api_id).inner_text() for api_id in native_ids} == before_facts
    card = model_card(page, automatic_id)
    expect(card.get_by_role("button", name="Copy API ID " + automatic_id, exact=True)).to_have_count(1)
    expect(rows.get_by_role("button")).to_have_count(0)
    expect(card.locator(".routing-policy")).to_contain_text("Workers AI → Bedrock Mantle → OpenRouter")
    card.get_by_role("button", name="Copy API ID " + automatic_id, exact=True).click()
    assert page.evaluate("navigator.clipboard.readText()") == automatic_id
    page.get_by_label("Provider", exact=True).select_option("openrouter")
    expect(card.get_by_role("button", name="Copy API ID " + automatic_id, exact=True)).to_be_visible()
    page.get_by_role("button", name="Clear filters", exact=True).click()
    page.get_by_role("searchbox", name="Search models", exact=True).fill("auto/")
    expect(page.locator("#models-list article.model-card:visible")).to_have_count(1)
    # A single verified route does not advertise providers absent from the catalog.
    stub_catalog(page, {"object": "list", "data": [native[0], {**automatic, "routing": {"mode": "automatic", "routes": [native_ids[0]]}}, offering("unseen/new", name="Unknown model"), offering("same-model-embedding", model_group="openai/gpt-oss-120b", capabilities=["embeddings"])]})
    page.get_by_role("button", name="Clear filters", exact=True).click()
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(page.locator("#results-count")).to_have_text("2 models · 3 provider offerings")
    expect(card.locator(".routing-policy")).not_to_contain_text("OpenRouter")
    expect(model_card(page, "unseen/new").get_by_role("button", name="Copy API ID unseen/new", exact=True)).to_be_visible()


def test_catalog_offerings_and_copy(page: Page) -> None:
    stub_catalog(page)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    expect(page.locator("#models-list article.model-card")).to_have_count(MODEL_COUNT)
    expect(page.locator("#models-list .provider-offering")).to_have_count(len(CATALOG["data"]))
    expect(page.locator("#results-count")).to_have_text("9 models · 11 provider offerings")
    for entry in CATALOG["data"]:
        row = provider_row(page, entry["id"])
        expect(row).to_be_visible()
        expect(row.locator("code")).to_have_text(entry["id"])
        provider_name = {"openrouter": "OpenRouter", "workers-ai": "Workers AI", "bedrock-mantle": "Bedrock Mantle"}[entry["provider"]]
        expect(row.get_by_role("heading", name=provider_name, exact=True)).to_be_visible()
    for api_id, title in (("deepseek/deepseek-v3.2", "DeepSeek V3.2"),
                          ("openai/gpt-oss-120b", "GPT OSS 120B")):
        card = model_card(page, api_id)
        expect(card.get_by_role("heading", name=title, exact=True)).to_be_visible()
        expect(card.locator(".provider-offering")).to_have_count(2)
    expect(page.locator("#models-list").get_by_role("heading", name="Identical name", exact=True)).to_have_count(2)
    expect(model_card(page, "deepseek/deepseek-v3.2-speciale").locator(".provider-offering")).to_have_count(1)
    gpt_summary = model_card(page, "openai/gpt-oss-120b").locator(".model-summary")
    expect(gpt_summary.locator(".model-evidence")).to_be_hidden()
    gpt_summary.get_by_text("Details and sources", exact=True).press("Enter")
    expect(gpt_summary.locator(".model-evidence")).to_be_visible()
    expect(gpt_summary).to_contain_text("116.8B · Checkpoint parameter count")
    expect(gpt_summary.get_by_role("link", name="Apache-2.0", exact=True)).to_be_visible()
    expect(gpt_summary.get_by_role("link", name="116.8B · Checkpoint parameter count", exact=True)).to_have_attribute("href", "https://example.org/size")
    expect(gpt_summary.get_by_role("link", name="Source for Apache-2.0", exact=True)).to_have_attribute("href", "https://example.org/license-evidence")
    expect(gpt_summary).to_contain_text("Checked 2026-09-08")
    expect(gpt_summary).not_to_contain_text("active")
    expect(model_card(page, "deepseek/deepseek-v3.2").locator(".model-summary")).to_have_text("Specifications not published")
    expect(model_card(page, "future/new-release-2099").locator(".model-summary")).not_to_contain_text("Size not available")
    native = provider_row(page, "deepseek/deepseek-v3.2")
    expect(native.get_by_text("Reasoning", exact=True)).to_be_visible()
    expect(native.get_by_text("Long context", exact=True)).to_be_visible()
    expect(native.locator(".capability svg").first).to_have_attribute("aria-hidden", "true")
    mantle = provider_row(page, "deepseek.v3.2")
    expect(mantle.get_by_text("Reasoning", exact=True)).to_have_count(0)
    expect(mantle.get_by_text("Long context", exact=True)).to_have_count(0)
    deepseek = provider_row(page, "deepseek/deepseek-v3.2")
    expect(deepseek).to_contain_text("Input $0.20")
    expect(deepseek).to_contain_text("Output $0.30")
    expect(provider_row(page, "deepseek.v3.2")).to_contain_text("Token prices not published")
    expect(provider_row(page, "deepseek.v3.2").get_by_text("Not published", exact=True)).to_be_visible()
    expect(provider_row(page, "@cf/openai/gpt-oss-120b")).to_contain_text("Input $0.00")
    expect(provider_row(page, "@cf/openai/gpt-oss-120b")).to_contain_text("Output $0.000001")
    expect(provider_row(page, "openai/gpt-oss-120b")).to_contain_text("Input from $0.04")
    expect(provider_row(page, "openai/gpt-oss-120b")).to_contain_text("Output from $0.15")
    expect(model_card(page, "provider/image-route")).to_contain_text("$0.00000001")
    page.locator("#models-list").get_by_role("button", name="Copy API ID deepseek/deepseek-v3.2", exact=True).press("Enter")
    expect(page.locator("#models-list").get_by_role("status", name="Copy result for deepseek/deepseek-v3.2", exact=True)).to_have_text("Copied")
    assert page.evaluate("navigator.clipboard.readText()") == "deepseek/deepseek-v3.2"


def test_search_and_combined_filters(page: Page) -> None:
    search = page.get_by_role("searchbox", name="Search models", exact=True)
    for query, expected in (("previously unseen", 1), ("speciale", 1), ("bedrock-mantle", 1), ("embeddings", 1)):
        search.fill(query)
        expect(page.locator("#models-list article.model-card:visible")).to_have_count(expected)
    search.fill("deepseek")
    page.get_by_label("Provider", exact=True).select_option("openrouter")
    page.get_by_label("Capability", exact=True).select_option("text-generation")
    expect(page.locator("#models-list article.model-card:visible")).to_have_count(2)
    expect(page.locator("#results-count")).to_contain_text("2")
    expect(page.locator("#models-list .provider-offering:visible")).to_have_count(2)
    expect(provider_row(page, "deepseek.v3.2")).to_be_hidden()
    search.fill("deepseek")
    page.get_by_label("Provider", exact=True).select_option("bedrock-mantle")
    page.get_by_label("Capability", exact=True).select_option("reasoning")
    expect(page.locator("#models-list article.model-card:visible")).to_have_count(0)
    expect(page.locator("#models-list .provider-offering:visible")).to_have_count(0)
    expect(page.locator("#results-count")).to_have_text("0 models · 0 provider offerings")
    page.get_by_label("Capability", exact=True).select_option("text-generation")
    expect(page.locator("#results-count")).to_have_text("1 model · 1 provider offering")
    expect(provider_row(page, "deepseek.v3.2")).to_be_visible()
    expect(provider_row(page, "deepseek/deepseek-v3.2")).to_be_hidden()
    search.fill("no-such-model")
    expect(page.locator("#models-list article.model-card:visible")).to_have_count(0)
    expect(page.locator("#results-count")).to_contain_text("0")
    expect(page.get_by_text("No models match your filters. Clear filters to see all offerings.", exact=True)).to_be_visible()
    page.get_by_role("button", name="Clear filters", exact=True).press("Enter")
    expect(page.locator("#models-list .provider-offering:visible")).to_have_count(len(CATALOG["data"]))
    expect(search).to_have_value("")
    expect(page.get_by_label("Provider", exact=True)).to_have_value("")
    expect(page.get_by_label("Capability", exact=True)).to_have_value("")
    expect(page.locator("#models-list article.model-card:visible")).to_have_count(MODEL_COUNT)


def test_refresh_empty_failure_retry_and_safe_text(page: Page) -> None:
    refresh = page.get_by_role("button", name="Refresh catalog", exact=True)
    status = page.get_by_role("status", name="Catalog status", exact=True)
    stub_catalog(page, {"object": "list", "data": []})
    refresh.click()
    expect_checked(page)
    expect(page.locator("#models-list article.model-card")).to_have_count(0)
    expect(page.locator("#results-count")).to_contain_text("0")
    expect(page.get_by_text("The Gateway catalog currently contains no offerings.", exact=True)).to_be_visible()
    invalid_price = offering("bad-price", pricing=pricing(-1, 0.3))
    missing_route = offering("auto/missing", routing={"mode": "automatic", "routes": ["absent"]})
    duplicate_route = offering("auto/duplicate", routing={"mode": "automatic", "routes": [CATALOG["data"][0]["id"]] * 2})
    for invalid in ({"object": "list", "data": [missing_route]}, {"object": "list", "data": [CATALOG["data"][0], duplicate_route]}, {"object": "list"}, {"object": "list", "data": [invalid_price]},
                    {"object": "list", "data": [CATALOG["data"][0], CATALOG["data"][0]]}, None):
        stub_catalog(page)
        refresh.click()
        expect_checked(page)
        expect(page.locator("#models-list article.model-card")).to_have_count(MODEL_COUNT)
        stub_catalog(page, invalid, network_failure=invalid is None)
        refresh.click()
        expect(status).to_have_text("Couldn’t load the Gateway catalog. Availability and prices are unknown.")
        expect(page.locator("#models-list article.model-card")).to_have_count(0)
        expect(page.locator("#models-list .provider-offering")).to_have_count(0)
        expect(refresh).to_be_enabled()
    replacement_id = "provider/" + "long-model-id-" * 20
    hostile_name = '<img src=x onerror="window.registryInjected=true">'
    stub_catalog(page, {"object": "list", "data": [offering(replacement_id, name=hostile_name)]})
    refresh.click()
    expect_checked(page)
    expect(page.locator("#models-list article.model-card")).to_have_count(1)
    expect(model_card(page, replacement_id).get_by_role("heading", name=hostile_name, exact=True)).to_be_visible()
    assert page.evaluate("window.registryInjected === undefined")
    expect(page.locator("#models-list article.model-card img")).to_have_count(0)
    expect(page.locator("#models-list article.model-card > .identity code")).to_have_text(replacement_id)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Long model text overflows mobile page"
    bounds = page.locator("#models-list article.model-card > .identity code").bounding_box()
    assert bounds and bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 390
    page.set_viewport_size({"width": 1440, "height": 1000})


def test_optional_metadata_and_conflicts(page: Page) -> None:
    long_license = "license-" + "x" * 130
    long_architecture = "architecture-" + "y" * 130
    entries = [
        offering("provider/one", model_group="shared", model_name="Clean model", specifications=SPECS),
        offering("provider/two", model_group="shared", specifications={**SPECS, "size": {**SPECS["size"], "label": "120B"}}),
        offering("provider/malformed", model_name=42, specifications={**SPECS, "size": {"label": "Fake"}, "license": {**SPECS["license"], "url": "javascript:alert(1)"}, "weights": {"available": False, "source_url": "https://example.org/closed"}}),
        offering("provider/long-metadata", specifications={**SPECS, "license": {**SPECS["license"], "name": long_license}, "architecture": {**SPECS["architecture"], "name": long_architecture}}),
        offering("provider/bad-date", specifications={**SPECS, "checked_at": "yesterday"}),
        offering("provider/advertised", specifications={"checked_at": SPECS["checked_at"], "size": {**SPECS["size"], "label": "120B", "basis": "advertised"}}),
    ]
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    expect(page.locator("#models-list .provider-offering")).to_have_count(6)
    shared = model_card(page, "provider/one")
    expect(shared.get_by_role("heading", name="Clean model", exact=True)).to_be_visible()
    expect(shared.locator(".model-summary")).not_to_contain_text("116.8B")
    expect(shared.locator(".model-summary")).to_contain_text("MoE")
    malformed = model_card(page, "provider/malformed")
    expect(malformed).to_contain_text("Weights not published")
    expect(malformed).to_contain_text("MoE")
    expect(malformed.get_by_role("link", name="Apache-2.0", exact=True)).to_have_count(0)
    expect(model_card(page, "provider/bad-date").locator(".model-summary")).not_to_contain_text("MoE")
    expect(page.locator('a[href^="javascript:"]')).to_have_count(0)
    advertised = model_card(page, "provider/advertised").locator(".model-summary")
    expect(advertised).to_contain_text("120B · Advertised size")
    expect(advertised).not_to_contain_text("Weights not published")
    expect(advertised).not_to_contain_text("Specifications not published")
    page.set_viewport_size({"width": 390, "height": 844})
    long_summary = model_card(page, "provider/long-metadata").locator(".model-summary")
    long_summary.get_by_text("Details and sources", exact=True).press("Enter")
    for label in (long_license, long_architecture):
        link = long_summary.get_by_role("link", name=label, exact=True)
        expect(link).to_be_visible()
        bounds = link.bounding_box()
        assert bounds and bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 390
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Long specification text overflows mobile page"
    page.add_script_tag(path=str(Path("node_modules/axe-core/axe.min.js").resolve()))
    violations = page.evaluate("""async () => (await axe.run('#model-registry', {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}})).violations""")
    assert violations == [], violations
    page.set_viewport_size({"width": 1440, "height": 1000})


def test_featured_models(page: Page) -> None:
    stub_catalog(page)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    featured = page.locator("#featured-models")
    expect(featured).to_be_visible()
    cards = featured.locator("article.featured-card")
    # Only gpt-oss-120b and Gemma 4 31B have IDs in the substituted catalog;
    # every other featured entry has no listed offering and must not render.
    expect(cards).to_have_count(2)
    card = cards.first
    expect(card.get_by_role("heading", name="GPT OSS 120B", exact=True)).to_be_visible()
    expect(card.locator(".featured-note")).to_contain_text("Apache-2.0")
    expect(card.locator(".provider-offering")).to_have_count(2)
    expect(card.locator(".provider-offering code")).to_have_text(["openai/gpt-oss-120b", "@cf/openai/gpt-oss-120b"])
    gemma = cards.nth(1)
    expect(gemma.get_by_role("heading", name="Gemma 4 31B", exact=True)).to_be_visible()
    expect(gemma.locator(".provider-offering")).to_have_count(1)
    expect(page.get_by_role("heading", name="All models", exact=True)).to_be_visible()
    expect(page.locator("#models-list article.model-card")).to_have_count(MODEL_COUNT)
    search = page.get_by_role("searchbox", name="Search models", exact=True)
    search.fill("gpt")
    expect(featured).to_be_hidden()
    search.fill("")
    expect(featured).to_be_visible()
    page.get_by_label("Provider", exact=True).select_option("workers-ai")
    expect(featured).to_be_hidden()
    page.get_by_role("button", name="Clear filters", exact=True).press("Enter")
    expect(featured).to_be_visible()
    stub_catalog(page, {"object": "list", "data": [offering("provider/unfeatured", name="Not featured")]})
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(featured).to_be_hidden()
    expect(cards).to_have_count(0)
    stub_catalog(page, network_failure=True)
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect(page.get_by_role("status", name="Catalog status", exact=True)).to_contain_text("Couldn’t load")
    expect(featured).to_be_hidden()
    stub_catalog(page)


def test_guide(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/guide/", wait_until="domcontentloaded")
    for heading in ("How to use the model registry", "Find a model", "Compare provider offerings", "Read token prices", "Use an API ID"):
        expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="API key guide", exact=True)).to_have_attribute("href", "/docs/api-keys/")
    page.get_by_role("link", name="Browse the model registry", exact=True).press("Enter")
    expect(page).to_have_url(f"{BASE_URL}/models/")
    expect_checked(page)


def test_pagination_and_filter_resets(page: Page) -> None:
    entries = [offering(f"model/{index:02}", name=f"Model {index:02}",
                        model_group=f"model/{index:02}",
                        capabilities=["text-generation"] if index < 24 else ["vision"])
               for index in range(27)]
    entries.append(offering("alternate/12", "workers-ai", name="Model 12",
                            model_group="model/12"))
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    cards = page.locator("#models-list article.model-card:visible")
    top = page.get_by_role("navigation", name="All model pages", exact=True)
    bottom = page.get_by_role("navigation", name="All model pages, bottom", exact=True)
    expect(cards).to_have_count(12)
    expect(page.locator("#results-count")).to_have_text("27 models · 28 provider offerings")
    expect(top).to_contain_text("Page 1 of 3 · 1–12 of 27 models")
    expect(top.get_by_role("button", name="Previous", exact=True)).to_be_disabled()
    seen = cards.locator("h2").all_text_contents()
    bottom.get_by_role("button", name="Next", exact=True).press("Enter")
    expect(page.locator("#all-models-heading")).to_be_focused()
    expect(top).to_contain_text("Page 2 of 3 · 13–24 of 27 models")
    expect(bottom).to_contain_text("Page 2 of 3 · 13–24 of 27 models")
    expect(cards).to_have_count(12)
    expect(model_card(page, "model/12").locator(".provider-offering:visible")).to_have_count(2)
    seen += cards.locator("h2").all_text_contents()
    top.get_by_role("button", name="Next", exact=True).click()
    expect(cards).to_have_count(3)
    expect(top).to_contain_text("Page 3 of 3 · 25–27 of 27 models")
    expect(top.get_by_role("button", name="Next", exact=True)).to_be_disabled()
    expect(bottom.get_by_role("button", name="Next", exact=True)).to_be_disabled()
    seen += cards.locator("h2").all_text_contents()
    assert seen == [f"Model {index:02}" for index in range(27)]
    bottom.get_by_role("button", name="Previous", exact=True).click()
    expect(top).to_contain_text("Page 2 of 3")
    search = page.get_by_role("searchbox", name="Search models", exact=True)
    search.fill("Model 26")
    expect(cards).to_have_count(1)
    expect(model_card(page, "model/26")).to_be_visible()
    expect(top).to_be_hidden()
    search.fill("")
    expect(top).to_contain_text("Page 1 of 3")
    top.get_by_role("button", name="Next", exact=True).click()
    page.get_by_label("Capability", exact=True).select_option("vision")
    expect(cards).to_have_count(3)
    expect(top).to_be_hidden()
    page.get_by_role("button", name="Clear filters", exact=True).click()
    expect(top).to_contain_text("Page 1 of 3")
    top.get_by_role("button", name="Next", exact=True).click()
    page.get_by_label("Provider", exact=True).select_option("workers-ai")
    expect(cards).to_have_count(1)
    expect(page.locator("#models-list .provider-offering:visible")).to_have_count(1)
    expect(top).to_be_hidden()
    page.get_by_role("button", name="Clear filters", exact=True).click()
    top.get_by_role("button", name="Next", exact=True).click()
    search.fill("missing")
    expect(cards).to_have_count(0)
    expect(top).to_be_hidden()
    expect(bottom).to_be_hidden()
    page.get_by_role("button", name="Clear filters", exact=True).click()
    expect(top).to_contain_text("Page 1 of 3")
    top.get_by_role("button", name="Next", exact=True).click()
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(top).to_contain_text("Page 1 of 3")
    page.set_viewport_size({"width": 390, "height": 844})
    top.get_by_role("button", name="Next", exact=True).click()
    expect(top).to_contain_text("Page 2 of 3")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.add_script_tag(path=str(Path("node_modules/axe-core/axe.min.js").resolve()))
    violations = page.evaluate("""async () => (await axe.run('#model-registry', {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}})).violations""")
    assert violations == [], violations
    for payload in ({"object": "list", "data": [entries[0]]}, {"object": "list", "data": []}, None):
        stub_catalog(page, payload, network_failure=payload is None)
        page.get_by_role("button", name="Refresh catalog", exact=True).click()
        if payload is None:
            expect(page.get_by_role("status", name="Catalog status", exact=True)).to_contain_text("Couldn’t load")
        else:
            expect_checked(page)
        expect(top).to_be_hidden()
        expect(bottom).to_be_hidden()
    page.set_viewport_size({"width": 1440, "height": 1000})


def test_featured_unpaginated_and_flash_only_v4(page: Page) -> None:
    featured_data = json.loads(Path("src/data/featured-models.json").read_text())["models"]
    entries = [offering(api_id, name=entry["name"], model_group=entry["ids"][0])
               for entry in featured_data for api_id in entry["ids"]]
    entries.extend([
        offering("deepseek/deepseek-v4-pro-0813", name="DeepSeek V4 Pro 0813"),
        offering("deepseek/deepseek-v4-flash", name="DeepSeek V4 Flash 0423"),
    ])
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    cards = page.locator("#featured-list article.featured-card:visible")
    nav = page.get_by_role("navigation", name="Featured model pages", exact=True)
    expect(cards).to_have_count(8)
    expect(cards.first.get_by_role("heading", name="DeepSeek V4 Flash 0731", exact=True)).to_be_visible()
    expect(cards.first.locator(".provider-offering")).to_have_count(2)
    expect(nav).to_have_count(0)
    assert cards.locator("h2").all_text_contents() == [entry["name"] for entry in featured_data]
    expect(cards.filter(has=page.get_by_role("heading", name=re.compile("V4")))).to_have_count(1)
    expect(model_card(page, "deepseek/deepseek-v4-pro-0813")).to_be_visible()
    expect(model_card(page, "deepseek/deepseek-v4-flash")).to_be_visible()
    page.get_by_role("searchbox", name="Search models", exact=True).fill("Flash")
    expect(page.locator("#featured-models")).to_be_hidden()
    page.get_by_role("button", name="Clear filters", exact=True).click()
    expect(cards).to_have_count(8)
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(cards).to_have_count(8)
    stub_catalog(page, {"object": "list", "data": [offering("moonshotai/kimi-k3", name="Kimi K3")]})
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(cards).to_have_count(1)
    expect(cards.first.get_by_role("heading", name="Kimi K3", exact=True)).to_be_visible()
    expect(nav).to_have_count(0)
    stub_catalog(page)


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 1000},
                                          permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for test in (test_automatic_primary_and_native_facts, test_catalog_offerings_and_copy, test_search_and_combined_filters,
                         test_refresh_empty_failure_retry_and_safe_text, test_optional_metadata_and_conflicts,
                         test_featured_models, test_pagination_and_filter_resets,
                         test_featured_unpaginated_and_flash_only_v4, test_guide):
                test(page)
                print(f"PASS {test.__name__}", flush=True)
            assert errors == [], errors
            context.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
