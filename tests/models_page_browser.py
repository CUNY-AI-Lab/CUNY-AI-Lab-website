"""Browser contract tests for the public model registry filters."""

from __future__ import annotations

import os
from typing import Any

from playwright.sync_api import Page, sync_playwright


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
    assert_equal(
        model_card(page, RESTORED_NATIVE_LONG_CONTEXT_MODEL)
        .get_by_role(
            "img",
            name="Long Context: Native/default context window of 100K+ tokens",
        )
        .count(),
        1,
    )


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            test_long_context_filter_matches_native_context_contract(page)
            assert_equal(errors, [])
            context.close()
            print("PASS test_long_context_filter_matches_native_context_contract")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
