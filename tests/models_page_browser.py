"""Real-browser registry journeys with the public catalog response substituted."""

from __future__ import annotations

import json
import os
from typing import Any

from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
RESTORED_NATIVE_LONG_CONTEXT_MODEL = "DeepSeek-V3.2"
EXISTING_NATIVE_LONG_CONTEXT_MODEL = "Kimi-K2.5"
CATALOG_URL = "https://tools.ailab.gc.cuny.edu/v1/catalog"
VISIBLE_MODELS = 7



def offering(api_id: str, provider: str = "openrouter", **fields: Any) -> dict:
    return {
        "id": api_id, "provider": provider,
        "capabilities": ["text-generation", "reasoning", "function-calling"],
        "context_length": 163840, **fields,
    }


def pricing(input_price: float, output_price: float, basis: str = "standard") -> dict:
    return {"currency": "USD", "unit": "million_tokens", "input": input_price,
            "output": output_price, "basis": basis}


CATALOG = {"object": "list", "data": [
    offering("deepseek/deepseek-v3.2", pricing=pricing(0.2, 0.3)),
    offering("deepseek.v3.2", "bedrock-mantle", context_length=None),
    offering("@cf/openai/gpt-oss-120b", "workers-ai", pricing=pricing(0, 0.000001)),
    offering("openai/gpt-oss-120b", pricing=pricing(0.04, 0.15, "starting_at")),
    offering("google/gemma-4-31b-it", capabilities=["text-generation", "vision"]),
    # These near names and non-text routes must not attach to reviewed cards.
    offering("deepseek/deepseek-v3.2-speciale"),
    offering("z-ai/glm-5.1"),
    offering("google/gemma-4-26b-a4b-it"),
    offering("qwen/qwen3-235b-a22b"),
    offering("deepseek-embedding", model_group="deepseek/deepseek-v3.2",
             capabilities=["embeddings"]),
]}


def stub_catalog(page: Page, payload: Any = CATALOG, *, network_failure: bool = False) -> None:
    page.unroute(CATALOG_URL)
    if network_failure:
        page.route(CATALOG_URL, lambda route: route.abort("failed"))
    else:
        page.route(CATALOG_URL, lambda route: route.fulfill(
            status=200, content_type="application/json", body=json.dumps(payload)))


def availability(page: Page, name: str):
    return page.get_by_role("region", name=f"Model API offerings for {name}", exact=True)


def expect_checked(page: Page) -> None:
    expect(page.get_by_role("status", name="Availability check", exact=True)).to_contain_text(
        "Model API checked at")
    expect(page.get_by_role("button", name="Refresh availability", exact=True)).to_be_enabled()


def open_offerings(page: Page, name: str):
    panel = availability(page, name)
    panel.locator("summary").click()
    return panel


def test_catalog_offerings_and_copy(page: Page) -> None:
    stub_catalog(page)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    expect(page.locator("article.model-card")).to_have_count(VISIBLE_MODELS)
    expect(page.get_by_role("heading", name="Qwen3-235b", exact=True)).to_have_count(0)
    deepseek = open_offerings(page, "DeepSeek-V3.2")
    expect(deepseek.get_by_role("listitem")).to_have_count(2)
    expect(deepseek.get_by_role("heading", name="OpenRouter", exact=True)).to_be_visible()
    expect(deepseek.get_by_role("heading", name="Bedrock Mantle", exact=True)).to_be_visible()
    expect(deepseek.get_by_text("Input $0.20 · Output $0.30 per million tokens", exact=True)).to_be_visible()
    expect(deepseek.get_by_text("Token prices not published", exact=True)).to_be_visible()
    expect(deepseek.get_by_text("Context limit not published", exact=False)).to_be_visible()
    expect(deepseek.get_by_text("163,840-token context · Reasoning · Function calling", exact=True)).to_be_visible()
    deepseek.get_by_role("button", name="Copy API ID deepseek.v3.2", exact=True).click()
    expect(deepseek.get_by_role("status", name="Copy result for deepseek.v3.2", exact=True)).to_have_text("Copied")
    assert_equal(page.evaluate("navigator.clipboard.readText()"), "deepseek.v3.2")
    gpt = open_offerings(page, "gpt-oss-120b")
    expect(gpt.get_by_text("Input $0.00 · Output $0.000001 per million tokens", exact=True)).to_be_visible()
    expect(gpt.get_by_text("Input from $0.04 · Output from $0.15 per million tokens", exact=True)).to_be_visible()
    gemma = open_offerings(page, "Gemma-4-31b")
    expect(gemma.get_by_text("163,840-token context · Image input", exact=True)).to_be_visible()
    expect(availability(page, "GLM-5").locator(".availability-message")).to_have_text("No current Model API offering")
    expect(page.locator(".availability-offerings code")).to_have_count(5)
    expect(page.locator(".availability-offerings code").filter(has_text="speciale")).to_have_count(0)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Mobile page overflows"
    for code in page.locator(".availability-offerings code:visible").all():
        bounds = code.bounding_box()
        assert bounds and bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 390
    page.set_viewport_size({"width": 1440, "height": 1000})


def test_catalog_refresh_failures_preserve_notes(page: Page) -> None:
    stub_catalog(page)
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    expect_checked(page)
    card = model_card(page, "DeepSeek-V3.2")
    card.get_by_role("button", name="Show model details", exact=True).click()
    notes = card.locator(".details-panel")
    original_notes = notes.inner_text()
    refresh = page.get_by_role("button", name="Refresh availability", exact=True)
    stub_catalog(page, {"object": "list", "data": []})
    refresh.click()
    expect_checked(page)
    expect(availability(page, "DeepSeek-V3.2").locator(".availability-message")).to_have_text("No current Model API offering")
    expect(page.locator(".availability-offerings li")).to_have_count(0)
    invalid_price = offering("deepseek/deepseek-v3.2", pricing=pricing(-1, 0.3))
    for invalid in ({"object": "list"}, {"object": "list", "data": [invalid_price]},
                    {"object": "list", "data": [CATALOG["data"][0], CATALOG["data"][0]]}, None):
        stub_catalog(page)
        refresh.click()
        expect_checked(page)
        expect(page.locator(".availability-offerings li")).to_have_count(5)
        stub_catalog(page, invalid, network_failure=invalid is None)
        refresh.click()
        expect(page.get_by_role("status", name="Availability check", exact=True)).to_have_text(
            "Couldn’t check Model API availability or prices. You can refresh to try again.")
        expect(availability(page, "DeepSeek-V3.2").locator(".availability-message")).to_have_text("Couldn’t check availability")
        expect(page.locator(".availability-offerings li")).to_have_count(0)
        expect(notes).to_be_visible()
        assert_equal(notes.inner_text(), original_notes)
        expect(refresh).to_be_enabled()
    # A group-mapped provider ID can change without retaining the old exact IDs.
    replacement_id = "provider/" + "long-model-id-" * 12
    stub_catalog(page, {"object": "list", "data": [offering(
        replacement_id, model_group="deepseek/deepseek-v3.2")]})
    refresh.click()
    expect_checked(page)
    panel = open_offerings(page, "DeepSeek-V3.2")
    expect(panel.get_by_role("listitem")).to_have_count(1)
    expect(panel.locator("code")).to_have_text(replacement_id)
    expect(page.locator(".availability-offerings code")).to_have_count(1)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Long API ID overflows mobile page"
    page.set_viewport_size({"width": 1440, "height": 1000})


def assert_equal(actual: Any, expected: Any) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def model_card(page: Page, model_name: str):
    card = page.locator("article.model-card").filter(
        has=page.locator("h3").filter(has_text=model_name)
    )
    assert_equal(card.count(), 1)
    return card


def test_long_context_filter_matches_native_context_contract(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    filter_button = page.get_by_role("button", name="Filter by long context window")
    filter_button.wait_for()
    filter_button.click()

    assert_equal(filter_button.get_attribute("aria-pressed"), "true")
    for model_name in (
        RESTORED_NATIVE_LONG_CONTEXT_MODEL,
        EXISTING_NATIVE_LONG_CONTEXT_MODEL,
    ):
        assert model_card(page, model_name).is_visible(), model_name

    expect(page.get_by_role("heading", name="Qwen3-235b", exact=True)).to_have_count(0)
    expect(page.locator("article.model-card")).to_have_count(VISIBLE_MODELS)
    visible_models = sum(
        card.is_visible() for card in page.get_by_role("article").all()
    )
    assert_equal(visible_models, VISIBLE_MODELS)
    expect(page.locator("#results-count")).to_have_text(f"{visible_models} models")
    assert_equal(
        model_card(page, RESTORED_NATIVE_LONG_CONTEXT_MODEL)
        .get_by_role(
            "img",
            name="Long Context: Native/default context window of 100K+ tokens",
        )
        .count(),
        1,
    )

    # Combining native-context and vision filters still excludes text-only cards.
    vision = page.get_by_role("button", name="Filter by vision capability")
    vision.click()
    expect(model_card(page, EXISTING_NATIVE_LONG_CONTEXT_MODEL)).to_be_visible()
    expect(model_card(page, RESTORED_NATIVE_LONG_CONTEXT_MODEL)).to_be_hidden()
    expect(page.locator("#results-count")).to_have_text("3 models")
    vision.click()
    expect(page.locator("#results-count")).to_have_text("7 models")


def test_license_filters_and_details(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
    permissive = page.get_by_role("button", name="Filter by permissive license")
    permissive.click()
    for name in ("DeepSeek-V3.2", "Kimi-K2.5", "Gemma-4-31b"):
        expect(model_card(page, name)).to_be_visible()
    for name in ("Gemma-3-27b", "Llama-3.1-70b-Instruct"):
        expect(model_card(page, name)).to_be_hidden()
    permissive.click()
    # Clickthrough is represented by Open/Gated badges, not a separate filter.
    for name, license_id, badge, family in (
        ("DeepSeek-V3.2", "MIT", "Open", "Permissive"),
        ("Kimi-K2.5", "modified-mit", "Open", "Permissive+"),
        ("Gemma-3-27b", "gemma", "Gated", "Restricted"),
        ("Llama-3.1-70b-Instruct", "llama3.1", "Gated", "Community"),
    ):
        card = model_card(page, name)
        expect(card.get_by_text(license_id, exact=True)).to_be_visible()
        expect(card.get_by_text(badge, exact=True)).to_be_visible()
        card.get_by_role("button", name="Show model details").click()
        expect(card.get_by_text(family, exact=True)).to_be_visible()
        expect(card.get_by_role("link", name="View License")).to_be_visible()
        card.get_by_role("button", name="Hide model details").click()
        expect(card.get_by_role("link", name="View License")).to_be_hidden()


def test_guide_keyboard_navigation(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/guide/", wait_until="domcontentloaded")
    first_section = page.get_by_role("button", name="Using the Filters", exact=True)
    expect(first_section).to_have_attribute("aria-current", "true")
    page.get_by_role("button", name="Next: Reading a Model Card").focus()
    page.keyboard.press("Enter")
    expect(
        page.get_by_role("heading", name="Reading a Model Card", exact=True)
    ).to_be_focused()
    expect(first_section).not_to_have_attribute("aria-current", "true")
    expect(
        page.get_by_role("button", name="Reading a Model Card", exact=True)
    ).to_have_attribute("aria-current", "true")
    page.keyboard.press("Tab")
    expect(page.get_by_role("button", name="Previous", exact=True)).to_be_focused()
    page.keyboard.press("Enter")
    expect(
        page.get_by_role("heading", name="Using the Filters", exact=True)
    ).to_be_focused()
    expect(first_section).to_have_attribute("aria-current", "true")


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 1000},
                                          permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            stub_catalog(page)
            test_long_context_filter_matches_native_context_contract(page)
            test_license_filters_and_details(page)
            test_guide_keyboard_navigation(page)
            test_catalog_offerings_and_copy(page)
            test_catalog_refresh_failures_preserve_notes(page)
            assert_equal(errors, [])
            context.close()
            print("PASS test_long_context_filter_matches_native_context_contract")
            print("PASS test_license_filters_and_details")
            print("PASS test_guide_keyboard_navigation")
            print("PASS test_catalog_offerings_and_copy")
            print("PASS test_catalog_refresh_failures_preserve_notes")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
