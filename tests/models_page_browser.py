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
    offering("deepseek-v3.2", name="DeepSeek V3.2", pricing=pricing(0.2, 0.3)),
    offering("gpt-oss-120b", "workers-ai", name="GPT OSS 120B", specifications=SPECS, pricing=pricing(0, 0.000001)),
    offering("gemma-4-31b-it", name="Gemma 4 31B", capabilities=["text-generation", "vision"]),
    offering("deepseek-v3.2-speciale", name="DeepSeek V3.2 Speciale", pricing=pricing(0.04, 0.15, "starting_at")),
    offering("new-release-2099", name="Previously unseen release"),
    offering("deepseek-embedding", name="DeepSeek Embeddings", capabilities=["embeddings"]),
    offering("same-name-a", name="Identical name"),
    offering("same-name-b", name="Identical name"),
    offering("image-route", name="Image generator", capabilities=["text-to-image"], pricing=pricing(0.00000001, 0.1)),
]}
MODEL_COUNT = len(CATALOG["data"])


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


def test_canonical_models_and_copy(page: Page) -> None:
    stub_catalog(page)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    expect(page.locator("article.model-card")).to_have_count(MODEL_COUNT)
    expect(page.get_by_label("Provider", exact=True)).to_have_count(0)
    expect(page.locator("article.model-card code")).to_have_count(MODEL_COUNT)
    expect(page.locator("#results-count")).to_have_text(f"{MODEL_COUNT} models")
    for model in CATALOG["data"]:
        card = model_card(page, model["id"])
        expect(card.get_by_role("heading", name=model["name"], exact=True)).to_be_visible()
        expect(card.locator("code")).to_have_text(model["id"])
        card.get_by_role("button", name=f"Copy API ID {model['id']}", exact=True).press("Enter")
        expect(card.get_by_role("status")).to_have_text("Copied")
        assert page.evaluate("navigator.clipboard.readText()") == model["id"]
    expect(model_card(page, "gpt-oss-120b")).to_contain_text("Input $0.00")
    expect(model_card(page, "gpt-oss-120b")).to_contain_text("Output $0.000001")
    expect(model_card(page, "deepseek-v3.2-speciale")).to_contain_text("Input from $0.04")
    expect(model_card(page, "image-route")).to_contain_text("$0.00000001")
    expect(model_card(page, "new-release-2099")).to_contain_text("Token prices not published")
    summary = model_card(page, "gpt-oss-120b").locator(".model-summary")
    expect(summary).to_contain_text("116.8B")
    summary.get_by_text("Details and sources", exact=True).press("Enter")
    expect(summary.get_by_role("link", name="MoE", exact=True)).to_have_attribute("href", SPECS["architecture"]["source_url"])
    expect(summary).to_contain_text("Checkpoint parameter count")
    featured = page.locator("#featured-models")
    expect(featured.locator("a")).to_have_count(2)
    featured.get_by_role("link", name="GPT OSS 120B", exact=True).click()
    expect(model_card(page, "gpt-oss-120b")).to_be_visible()
    expect(page.locator("article.model-card")).to_have_count(MODEL_COUNT)


def test_search_and_combined_filters(page: Page) -> None:
    search = page.get_by_role("searchbox", name="Search models", exact=True)
    search.fill("deepseek")
    expect(page.locator("article.model-card:visible")).to_have_count(3)
    expect(page.locator("#featured-models")).to_be_hidden()
    page.get_by_label("Capability", exact=True).select_option("embeddings")
    expect(page.locator("article.model-card:visible")).to_have_count(1)
    expect(model_card(page, "deepseek-embedding")).to_be_visible()
    search.fill("speciale")
    expect(page.locator("article.model-card:visible")).to_have_count(0)
    expect(page.get_by_text("No models match your filters. Clear filters to see all models.", exact=True)).to_be_visible()
    page.get_by_role("button", name="Clear filters", exact=True).press("Enter")
    expect(search).to_have_value("")
    expect(page.get_by_label("Capability", exact=True)).to_have_value("")
    expect(page.locator("article.model-card:visible")).to_have_count(MODEL_COUNT)
    expect(page.locator("#featured-models")).to_be_visible()


def test_refresh_empty_failure_retry_and_safe_text(page: Page) -> None:
    refresh = page.get_by_role("button", name="Refresh catalog", exact=True)
    status = page.get_by_role("status", name="Catalog status", exact=True)
    stub_catalog(page, {"object": "list", "data": []})
    refresh.click()
    expect_checked(page)
    expect(page.locator("#models-list article.model-card")).to_have_count(0)
    expect(page.locator("#results-count")).to_contain_text("0")
    expect(page.get_by_text("The Gateway catalog currently contains no models.", exact=True)).to_be_visible()
    invalid_price = offering("bad-price", pricing=pricing(-1, 0.3))
    for invalid in ({"object": "list"}, {"object": "list", "data": [invalid_price]},
                    {"object": "list", "data": [CATALOG["data"][0], CATALOG["data"][0]]}, None):
        stub_catalog(page)
        refresh.click()
        expect_checked(page)
        expect(page.locator("#models-list article.model-card")).to_have_count(MODEL_COUNT)
        stub_catalog(page, invalid, network_failure=invalid is None)
        refresh.click()
        expect(status).to_have_text("Couldn’t load the Gateway catalog. Availability and prices are unknown.")
        expect(page.locator("#models-list article.model-card")).to_have_count(0)
        expect(page.locator("#models-list .model-facts")).to_have_count(0)
        expect(refresh).to_be_enabled()
    replacement_id = "variant-" + "long-model-id-" * 20
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


def test_optional_metadata(page: Page) -> None:
    long_license = "license-" + "x" * 130
    long_architecture = "architecture-" + "y" * 130
    entries = [
        offering("one", model_name="Clean model", specifications=SPECS),
        offering("two", specifications={**SPECS, "size": {**SPECS["size"], "label": "120B"}}),
        offering("malformed", model_name=42, specifications={**SPECS, "size": {"label": "Fake"}, "license": {**SPECS["license"], "url": "javascript:alert(1)"}, "weights": {"available": False, "source_url": "https://example.org/closed"}}),
        offering("long-metadata", specifications={**SPECS, "license": {**SPECS["license"], "name": long_license}, "architecture": {**SPECS["architecture"], "name": long_architecture}}),
        offering("bad-date", specifications={**SPECS, "checked_at": "yesterday"}),
        offering("advertised", specifications={"checked_at": SPECS["checked_at"], "size": {**SPECS["size"], "label": "120B", "basis": "advertised"}}),
    ]
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    expect(page.locator("#models-list .model-facts")).to_have_count(6)
    shared = model_card(page, "one")
    expect(shared.get_by_role("heading", name="Clean model", exact=True)).to_be_visible()
    expect(shared.locator(".model-summary")).to_contain_text("116.8B")
    expect(shared.locator(".model-summary")).to_contain_text("MoE")
    malformed = model_card(page, "malformed")
    expect(malformed).to_contain_text("Weights not published")
    expect(malformed).to_contain_text("MoE")
    expect(malformed.get_by_role("link", name="Apache-2.0", exact=True)).to_have_count(0)
    expect(model_card(page, "bad-date").locator(".model-summary")).not_to_contain_text("MoE")
    expect(page.locator('a[href^="javascript:"]')).to_have_count(0)
    advertised = model_card(page, "advertised").locator(".model-summary")
    expect(advertised).to_contain_text("120B · Advertised size")
    expect(advertised).not_to_contain_text("Weights not published")
    expect(advertised).not_to_contain_text("Specifications not published")
    page.set_viewport_size({"width": 390, "height": 844})
    long_summary = model_card(page, "long-metadata").locator(".model-summary")
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


def test_guide(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/guide/", wait_until="domcontentloaded")
    for heading in ("How to use the model registry", "Find a model", "Compare models", "Read token prices", "Use an API ID"):
        expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="API key guide", exact=True)).to_have_attribute("href", "/docs/api-keys/")
    page.get_by_role("link", name="Browse the model registry", exact=True).press("Enter")
    expect(page).to_have_url(f"{BASE_URL}/models/")
    expect_checked(page)


def test_pagination_and_filter_resets(page: Page) -> None:
    entries = [offering(f"model-{index:02}", name=f"Model {index:02}",
                        capabilities=["text-generation"] if index < 24 else ["vision"])
               for index in range(27)]
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    cards = page.locator("#models-list article.model-card:visible")
    top = page.get_by_role("navigation", name="All model pages", exact=True)
    bottom = page.get_by_role("navigation", name="All model pages, bottom", exact=True)
    expect(cards).to_have_count(12)
    expect(page.locator("#results-count")).to_have_text("27 models")
    expect(top).to_contain_text("Page 1 of 3 · 1–12 of 27 models")
    expect(top.get_by_role("button", name="Previous", exact=True)).to_be_disabled()
    seen = cards.locator("h2").all_text_contents()
    bottom.get_by_role("button", name="Next", exact=True).press("Enter")
    expect(page.locator("#all-models-heading")).to_be_focused()
    expect(top).to_contain_text("Page 2 of 3 · 13–24 of 27 models")
    expect(bottom).to_contain_text("Page 2 of 3 · 13–24 of 27 models")
    expect(cards).to_have_count(12)
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
    expect(model_card(page, "model-26")).to_be_visible()
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


def test_featured_jump_across_pages(page: Page) -> None:
    entries = [offering(f"model-{i:02}", name=f"AAA {i:02}") for i in range(26)]
    entries.append(offering("gpt-oss-120b", name="GPT OSS 120B"))
    stub_catalog(page, {"object": "list", "data": entries})
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    page.locator("#featured-list").get_by_role("link", name="GPT OSS 120B", exact=True).click()
    expect(model_card(page, "gpt-oss-120b")).to_be_visible()
    expect(page.get_by_role("navigation", name="All model pages", exact=True)).to_contain_text("Page 3 of 3")
    expect(page.locator("article.model-card")).to_have_count(27)
    stub_catalog(page, {"object": "list", "data": [offering("unfeatured")]})
    page.get_by_role("button", name="Refresh catalog", exact=True).click()
    expect_checked(page)
    expect(page.locator("#featured-models")).to_be_hidden()
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
            for test in (test_canonical_models_and_copy, test_search_and_combined_filters,
                         test_refresh_empty_failure_retry_and_safe_text, test_optional_metadata,
                         test_pagination_and_filter_resets, test_featured_jump_across_pages, test_guide):
                test(page)
                print(f"PASS {test.__name__}", flush=True)
            assert errors == [], errors
            context.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
