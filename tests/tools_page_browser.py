"""Browser contract tests for the public tools page.

These checks exercise the rendered page so deep links, keyboard interaction,
and the basic tab-panel accessibility contract stay stable together.
"""

from __future__ import annotations

import os
from typing import Any

from playwright.sync_api import Page, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
EXPECTED_PANELS = ["sandbox", "media", "assistants", "working-with-ai", "model-access"]


def assert_equal(actual: Any, expected: Any) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def load_tools(page: Page, suffix: str = "") -> None:
    page.goto(f"{BASE_URL}/tools/{suffix}", wait_until="domcontentloaded")


def assert_selected_panel(page: Page, panel_id: str) -> None:
    for candidate in EXPECTED_PANELS:
        panel = page.locator(f"#panel-{candidate}")
        assert_equal(panel.is_visible(), candidate == panel_id)

    selected = page.locator(
        f'[role="tab"][aria-controls="panel-{panel_id}"][aria-selected="true"]'
    )
    assert_equal(selected.count(), 1)
    assert_equal(page.locator("#tool-category").input_value(), panel_id)


def test_navigation_is_deterministic(page: Page) -> None:
    load_tools(page)
    assert_selected_panel(page, "sandbox")

    load_tools(page, "#media")
    assert_selected_panel(page, "media")

    page.locator('.sidebar-row[data-panel="assistants"]').click()
    assert page.url.endswith("/tools/#assistants")
    assert_selected_panel(page, "assistants")

    page.set_viewport_size({"width": 390, "height": 844})
    assert not page.locator(".tools-sidebar").is_visible()
    picker = page.locator("#tool-category")
    assert picker.is_visible()
    picker.select_option("model-access")
    assert page.url.endswith("/tools/#model-access")
    assert_selected_panel(page, "model-access")


def test_tabs_and_accessibility_contract(page: Page) -> None:
    load_tools(page)

    tablists = page.locator('[role="tablist"]')
    assert_equal(tablists.count(), 1)
    for index in range(tablists.count()):
        tablist = tablists.nth(index)
        tabs = tablist.locator('[role="tab"]')
        assert_equal(tabs.count(), len(EXPECTED_PANELS))
        assert_equal(tablist.locator('[role="tab"][aria-selected="true"]').count(), 1)
        assert_equal(tablist.locator('[role="tab"][tabindex="0"]').count(), 1)
        for tab_index in range(tabs.count()):
            tab = tabs.nth(tab_index)
            panel_id = tab.get_attribute("aria-controls")
            assert panel_id in {f"panel-{panel}" for panel in EXPECTED_PANELS}
            assert_equal(page.locator(f"#{panel_id}").get_attribute("role"), "tabpanel")

    panels = page.locator('[role="tabpanel"]')
    assert_equal(panels.count(), len(EXPECTED_PANELS))
    for index in range(panels.count()):
        panel = panels.nth(index)
        assert panel.get_attribute("aria-label")

    for svg_index in range(page.locator("svg").count()):
        assert_equal(page.locator("svg").nth(svg_index).get_attribute("aria-hidden"), "true")


def test_media_slider_accessibility(page: Page) -> None:
    load_tools(page, "#media")

    def assert_active_slide(active_index: int) -> None:
        for index in range(3):
            slide = page.locator(f"#slide-{index}")
            is_active = index == active_index
            assert_equal(slide.get_attribute("aria-hidden"), "false" if is_active else "true")
            opacity = slide.evaluate(
                "element => element.style.opacity || getComputedStyle(element).opacity"
            )
            assert_equal(opacity, "1" if is_active else "0")

    assert_active_slide(0)
    page.locator('.slider-dot[data-slide="1"]').click()
    assert_active_slide(1)


def test_mobile_initial_load_does_not_scroll(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    load_tools(page)
    page.wait_for_load_state("networkidle")
    assert_equal(page.evaluate("window.scrollY"), 0)

    page.goto("about:blank")
    load_tools(page, "#media")
    page.wait_for_load_state("networkidle")
    assert_equal(page.evaluate("window.scrollY"), 0)

    # The picker sits directly above the panel, so choosing a category must not scroll either.
    picker = page.locator("#tool-category")
    picker.scroll_into_view_if_needed()
    position = page.evaluate("window.scrollY")
    picker.select_option("assistants")
    assert_selected_panel(page, "assistants")
    # Let a browser-initiated smooth scroll advance before measuring the viewport.
    page.evaluate(
        "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
    )
    assert_equal(page.evaluate("window.scrollY"), position)


def test_keyboard_tab_navigation(page: Page) -> None:
    load_tools(page)
    sidebar_tabs = page.locator('.tools-sidebar [role="tab"]')
    sidebar_tabs.nth(0).focus()
    sidebar_tabs.nth(0).press("ArrowDown")
    assert_equal(page.evaluate("document.activeElement?.dataset.panel"), "media")
    assert_selected_panel(page, "media")

    sidebar_tabs.nth(1).press("End")
    assert_equal(page.evaluate("document.activeElement?.dataset.panel"), "model-access")
    assert_selected_panel(page, "model-access")


def test_header_sign_in_link(page: Page) -> None:
    sign_in_url = "https://tools.ailab.gc.cuny.edu/welcome"
    load_tools(page)
    desktop_link = page.locator("header").get_by_role("link", name="Sign in")
    assert_equal(desktop_link.count(), 1)
    assert desktop_link.is_visible()
    assert_equal(desktop_link.get_attribute("href"), sign_in_url)
    assert desktop_link.get_attribute("target") is None

    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#mobile-menu-button").click()
    mobile_link = page.locator("#mobile-menu").get_by_role("link", name="Sign in")
    assert mobile_link.is_visible()
    assert_equal(mobile_link.get_attribute("href"), sign_in_url)


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            tests = (
                test_navigation_is_deterministic,
                test_tabs_and_accessibility_contract,
                test_media_slider_accessibility,
                test_mobile_initial_load_does_not_scroll,
                test_keyboard_tab_navigation,
                test_header_sign_in_link,
            )
            for test in tests:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
                errors: list[str] = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                test(page)
                assert_equal(errors, [])
                context.close()
                print(f"PASS {test.__name__}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
