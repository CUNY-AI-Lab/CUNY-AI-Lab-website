"""Browser contract tests for the public tools page.

These checks exercise the rendered page so tab order, deep links, outbound
links, and the basic tab-panel accessibility contract stay stable together.
"""

from __future__ import annotations

import os
from typing import Any

from playwright.sync_api import Page, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
EXPECTED_PANELS = ["sandbox", "media", "assistants", "model-access"]
EXPECTED_LINKS = {
    "https://chat.ailab.gc.cuny.edu/",
    "https://tools.ailab.gc.cuny.edu/",
    "https://tools.ailab.gc.cuny.edu/asr/",
    "https://tools.ailab.gc.cuny.edu/alt-text/",
    "https://tools.ailab.gc.cuny.edu/ocr/",
    "https://tools.ailab.gc.cuny.edu/agent-studio/",
    "https://tools.ailab.gc.cuny.edu/site-studio/",
    "https://tools.ailab.gc.cuny.edu/model-access",
    "/models",
    "/request-access/",
}


def assert_equal(actual: Any, expected: Any) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def load_tools(page: Page, suffix: str = "") -> None:
    page.goto(f"{BASE_URL}/tools/{suffix}", wait_until="domcontentloaded")


def tab_order(page: Page, selector: str) -> list[str]:
    return page.locator(selector).evaluate_all(
        "tabs => tabs.map(tab => tab.dataset.panel)"
    )


def assert_selected_panel(page: Page, panel_id: str) -> None:
    for candidate in EXPECTED_PANELS:
        panel = page.locator(f"#panel-{candidate}")
        assert_equal(panel.is_visible(), candidate == panel_id)

    selected = page.locator(
        f'[role="tab"][aria-controls="panel-{panel_id}"][aria-selected="true"]'
    )
    assert_equal(selected.count(), 2)


def ax_image_names(page: Page) -> list[str]:
    cdp = page.context.new_cdp_session(page)
    try:
        tree = cdp.send("Accessibility.getFullAXTree")
    finally:
        cdp.detach()
    return [
        node.get("name", {}).get("value", "")
        for node in tree["nodes"]
        if node.get("role", {}).get("value") == "image"
    ]


def test_navigation_is_deterministic(page: Page) -> None:
    for _ in range(3):
        load_tools(page)
        assert_equal(tab_order(page, ".sidebar-card"), EXPECTED_PANELS)
        assert_equal(tab_order(page, ".mobile-tab"), EXPECTED_PANELS)
        assert_selected_panel(page, "sandbox")

    load_tools(page, "#media")
    assert_selected_panel(page, "media")

    page.locator('.sidebar-card[data-panel="assistants"]').click()
    assert page.url.endswith("/tools/#assistants")
    assert_selected_panel(page, "assistants")

    page.set_viewport_size({"width": 390, "height": 844})
    page.locator('.mobile-tab[data-panel="model-access"]').click()
    assert page.url.endswith("/tools/#model-access")
    assert_selected_panel(page, "model-access")


def test_tabs_links_and_accessibility_contract(page: Page) -> None:
    load_tools(page)

    tablists = page.locator('[role="tablist"]')
    assert_equal(tablists.count(), 2)
    for index in range(tablists.count()):
        tablist = tablists.nth(index)
        tabs = tablist.locator('[role="tab"]')
        assert_equal(tabs.count(), len(EXPECTED_PANELS))
        assert_equal(
            tabs.evaluate_all("tabs => tabs.map(tab => tab.dataset.panel)"),
            EXPECTED_PANELS,
        )
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

    for href in EXPECTED_LINKS:
        assert_equal(page.locator(f'a[href="{href}"]').count() > 0, True)

    body = page.locator("body").inner_text()
    privacy_copy = (
        "Model-provider calls are configured for zero retention; "
        "conversations may still be saved in your Sandbox account."
    )
    assert privacy_copy in body
    assert "Spring 2026" not in body
    assert "Prompts and outputs are never stored" not in body
    assert "no data from prompts or responses is stored" not in body
    assert "Math.random" not in page.locator("body").evaluate("body => body.innerHTML")


def test_media_slider_accessibility(page: Page) -> None:
    load_tools(page, "#media")
    slide_alts = [
        "Demo of Multilingual Transcription Suite - uploading audio and receiving transcript",
        "Image Description tool interface showing alt-text generation",
        "Document OCR tool interface showing text extraction",
    ]

    def assert_active_slide(active_index: int) -> None:
        for index, alt in enumerate(slide_alts):
            slide = page.locator(f"#slide-{index}")
            is_active = index == active_index
            assert_equal(slide.get_attribute("aria-hidden"), "false" if is_active else "true")
            opacity = slide.evaluate(
                "element => element.style.opacity || getComputedStyle(element).opacity"
            )
            assert_equal(opacity, "1" if is_active else "0")

            image_is_exposed = alt in ax_image_names(page)
            assert_equal(image_is_exposed, is_active)

    assert_active_slide(0)
    page.locator('.slider-dot[data-slide="1"]').click()
    assert_active_slide(1)


def test_mobile_initial_load_does_not_scroll(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    page.add_init_script(
        """
        window.__scrollIntoViewCalls = 0;
        Element.prototype.scrollIntoView = function() {
          window.__scrollIntoViewCalls += 1;
        };
        """
    )
    load_tools(page)
    assert_equal(page.evaluate("window.scrollY"), 0)
    assert_equal(page.evaluate("window.__scrollIntoViewCalls"), 0)

    page.goto("about:blank")
    load_tools(page, "#media")
    assert_equal(page.evaluate("window.scrollY"), 0)
    assert_equal(page.evaluate("window.__scrollIntoViewCalls"), 0)

    page.locator('.mobile-tab[data-panel="assistants"]').click()
    assert_equal(page.evaluate("window.__scrollIntoViewCalls"), 1)


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


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            tests = (
                test_navigation_is_deterministic,
                test_tabs_links_and_accessibility_contract,
                test_media_slider_accessibility,
                test_mobile_initial_load_does_not_scroll,
                test_keyboard_tab_navigation,
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
