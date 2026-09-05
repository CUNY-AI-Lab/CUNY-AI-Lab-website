"""Check rendered WCAG A/AA rules; keyboard journeys live in the page suites.

This is not a WCAG certification. Identity, analytics and Turnstile are outside
the static-site boundary and are disabled here; no live application is sent.
"""

import json
import os
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")


def check_accessibility(page: Page, label: str) -> None:
    page.add_script_tag(path=str(ROOT / "node_modules/axe-core/axe.min.js"))
    violations = page.evaluate("""async () => {
        const result = await axe.run({runOnly: {type: 'tag', values:
            ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']}});
        return result.violations.map(v => ({rule: v.id, help: v.helpUrl,
            nodes: v.nodes.map(n => ({target: n.target, reason: n.failureSummary}))}));
    }""")
    assert not violations, f"{label}: {json.dumps(violations, indent=2)}"


def main() -> None:
    routes = sorted("/" + str(path.relative_to(ROOT / "dist")).removesuffix("index.html")
                    for path in (ROOT / "dist").rglob("index.html"))
    assert routes, "Build the website before running browser checks"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            # Reduced motion also keeps scans out of intermediate fade-in frames.
            context = browser.new_context(reduced_motion="reduce")
            context.route("https://tools.ailab.gc.cuny.edu/**", lambda route: route.fulfill(status=401, body=""))
            context.route("https://www.googletagmanager.com/**", lambda route: route.abort())
            context.route("https://challenges.cloudflare.com/**", lambda route: route.abort())
            page = context.new_page()
            for width, paths in ((1440, routes), (390, ["/", "/tools/", "/models/", "/models/guide/", "/request-access/?kind=class", "/docs/api-keys/"])):
                page.set_viewport_size({"width": width, "height": 1000})
                for path in paths:
                    page.goto(BASE_URL + path, wait_until="networkidle")
                    check_accessibility(page, f"{width}px {path}")
                print(f"PASS axe WCAG A/AA: {len(paths)} routes at {width}px", flush=True)
            page.goto(BASE_URL + "/models/", wait_until="networkidle")
            details = page.get_by_role("button", name="Show model details")
            for _ in range(details.count()):
                details.first.click()
            check_accessibility(page, "expanded model details")
            page.goto(BASE_URL + "/tools/", wait_until="networkidle")
            for category in ("media", "assistants", "working-with-ai", "model-access"):
                page.get_by_label("Category", exact=True).select_option(category)
                check_accessibility(page, f"tools: {category}")
            print("PASS axe WCAG A/AA: expanded models and tool categories")
            page.goto(BASE_URL + "/docs/api-keys/", wait_until="networkidle")
            page.get_by_role("link", name="Send a chat request", exact=True).press("Enter")
            heading = page.get_by_role("heading", name="Send a chat request", exact=True)
            assert heading.bounding_box()["y"] >= page.locator("header").bounding_box()["height"]
            example = page.get_by_role("region", name="Send a chat request").locator("pre")
            example.focus()
            example.press("ArrowRight")
            page.wait_for_function("document.activeElement.scrollLeft > 0")
            print("PASS keyboard scroll and unobscured API example navigation")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
