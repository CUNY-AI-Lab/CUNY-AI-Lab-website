"""Browser contract tests for the public model registry filters."""

from __future__ import annotations

import os
from typing import Any

from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
RESTORED_NATIVE_LONG_CONTEXT_MODEL = "DeepSeek-V3.2"
EXISTING_NATIVE_LONG_CONTEXT_MODEL = "Kimi-K2.5"
EXTENDED_ONLY_LONG_CONTEXT_MODEL = "Qwen3-235b"


def assert_equal(actual: Any, expected: Any) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def model_card(page: Page, model_name: str):
    card = page.locator("article.model-card").filter(
        has=page.locator("h3").filter(has_text=model_name)
    )
    assert_equal(card.count(), 1)
    return card


def test_long_context_filter_matches_native_context_contract(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/", wait_until="networkidle")
    filter_button = page.get_by_role("button", name="Filter by long context window")
    filter_button.wait_for()
    filter_button.click()

    assert_equal(filter_button.get_attribute("aria-pressed"), "true")
    for model_name in (
        RESTORED_NATIVE_LONG_CONTEXT_MODEL,
        EXISTING_NATIVE_LONG_CONTEXT_MODEL,
    ):
        assert model_card(page, model_name).is_visible(), model_name

    short_context_card = model_card(page, EXTENDED_ONLY_LONG_CONTEXT_MODEL)
    assert short_context_card.is_hidden()
    visible_models = sum(
        card.is_visible() for card in page.get_by_role("article").all()
    )
    expect(page.get_by_role("status")).to_have_text(f"{visible_models} models")
    assert_equal(
        model_card(page, RESTORED_NATIVE_LONG_CONTEXT_MODEL)
        .get_by_role(
            "img",
            name="Long Context: Native/default context window of 100K+ tokens",
        )
        .count(),
        1,
    )


def test_license_filters_and_details(page: Page) -> None:
    page.goto(f"{BASE_URL}/models/", wait_until="networkidle")
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
    page.goto(f"{BASE_URL}/models/guide/", wait_until="networkidle")
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
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            test_long_context_filter_matches_native_context_contract(page)
            test_license_filters_and_details(page)
            test_guide_keyboard_navigation(page)
            assert_equal(errors, [])
            context.close()
            print("PASS test_long_context_filter_matches_native_context_contract")
            print("PASS test_license_filters_and_details")
            print("PASS test_guide_keyboard_navigation")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
