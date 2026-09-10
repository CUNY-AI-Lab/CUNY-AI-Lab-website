"""Copy the rendered API examples, including clipboard denial and keyboard use."""

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
SCREENSHOTS = os.environ.get("CAIL_UI_SCREENSHOT_DIR")


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        for width in [1280, 375]:
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(f"{BASE_URL}/docs/api-keys/")
            expect(page).to_have_title("API Keys and Model Access - CUNY AI Lab")
            expect(page.get_by_role("heading", name="Use the CAIL Model API", exact=True)).to_be_visible()
            expect(page.locator("article pre")).to_have_count(3)
            for section_id in ["setup-heading", "models-heading", "request-heading"]:
                section = page.locator(f'section[aria-labelledby="{section_id}"]')
                expected = section.locator("pre code").text_content()
                assert expected and "CAIL_API" in expected
                copy = section.get_by_role("button", name="Copy code:")
                copy.press("Enter")
                expect(section.get_by_role("status")).to_have_text("Copied")
                assert page.evaluate("navigator.clipboard.readText()") == expected
                assert page.evaluate("document.documentElement.scrollWidth") <= width
            if SCREENSHOTS:
                page.locator('#setup-heading').scroll_into_view_if_needed()
                page.screenshot(path=str(Path(SCREENSHOTS) / f"api-docs-copy-{width}.png"))

        section = page.locator('section[aria-labelledby="request-heading"]')
        code = section.locator("pre code").text_content()
        for unavailable in [False, True]:
            page.evaluate("""unavailable => {
                if (unavailable) {
                    Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true});
                } else {
                    Object.defineProperty(navigator.clipboard, 'writeText', {
                        value: () => Promise.reject(new DOMException('Blocked for test', 'NotAllowedError')),
                        configurable: true
                    });
                }
            }""", unavailable)
            section.get_by_role("button", name="Copy code:").click()
            expect(section.get_by_role("status")).to_have_text("Couldn’t copy. Select the code and copy it manually.")
            assert page.evaluate("window.getSelection().toString()") == code
            assert page.evaluate("document.documentElement.scrollWidth") <= 375
        assert not errors, errors
        context.close()
        context = browser.new_context(java_script_enabled=False)
        page = context.new_page()
        page.goto(f"{BASE_URL}/docs/api-keys/")
        expect(page.locator("article pre")).to_have_count(3)
        expect(page.get_by_role("button", name="Copy code:")).to_have_count(0)
        browser.close()
    print("API documentation copy checks passed: three examples, keyboard, desktop/mobile, denial, unavailable clipboard, no JavaScript.")


if __name__ == "__main__":
    main()
