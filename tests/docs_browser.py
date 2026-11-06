"""Exercise the three documentation sets on a local static Worker only.

External requests are blocked. These checks open no application sessions and
send no forms, reports, credentials or model requests.
"""

import json
import os
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from playwright.sync_api import expect, sync_playwright
from accessibility_browser import check_accessibility

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
GUIDES = ("sandbox", "stem-splitter", "systems-mapping")
APP_URLS = {
    "stem-splitter": "https://stem-splitter.ailab-452.workers.dev/",
    "systems-mapping": "https://systems-mapping.ailab-452.workers.dev/",
}


class BuiltPage(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if "id" in attr:
            assert attr["id"] not in self.ids, f"Duplicate ID: {attr['id']}"
            self.ids.add(attr["id"])
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if tag == "img" and attr.get("src"):
            self.links.append(attr["src"])


def check_built_links(routes):
    pages = {}
    checked = set()
    for path in routes:
        document = BuiltPage((ROOT / "dist" / path.lstrip("/") / "index.html").read_text())
        for link in document.links:
            url = urlsplit(urljoin(BASE_URL + path, link))
            if url.netloc != urlsplit(BASE_URL).netloc:
                continue
            target = ROOT / "dist" / unquote(url.path).lstrip("/")
            if target.is_dir():
                target /= "index.html"
            assert target.is_file(), f"{path}: missing local target {link}"
            if url.fragment:
                target_page = pages.setdefault(target, BuiltPage(target.read_text()))
                # The existing Sandbox index redirects legacy article hashes.
                legacy = ROOT / "dist/sandbox-docs" / url.fragment / "index.html"
                legacy_redirect = url.path == "/sandbox-docs/" and legacy.is_file()
                assert unquote(url.fragment) in target_page.ids or legacy_redirect, f"{path}: missing fragment {link}"
            checked.add(url.geturl())
    print(f"PASS local documentation targets: {len(checked)} links and images", flush=True)


def main():
    assert urlsplit(BASE_URL).hostname in {"127.0.0.1", "localhost"}, "Docs tests require a local fixture server"
    routes = sorted("/" + str(file.relative_to(ROOT / "dist")).removesuffix("index.html")
                    for guide in GUIDES for file in (ROOT / "dist" / f"{guide}-docs").rglob("index.html"))
    assert len(routes) == 44, f"Expected the reviewed 44-article scope, found {len(routes)}"
    check_built_links(routes)
    screenshot_dir = os.environ.get("CAIL_DOCS_SCREENSHOTS")
    if screenshot_dir:
        Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(reduced_motion="reduce")
            origin = urlsplit(BASE_URL).netloc
            context.route("**/*", lambda route: route.continue_()
                          if urlsplit(route.request.url).netloc == origin else route.abort())
            page = context.new_page()
            page_errors = []
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            for width in (1440, 390):
                page.set_viewport_size({"width": width, "height": 1000})
                for path in routes:
                    response = page.goto(BASE_URL + path, wait_until="networkidle")
                    assert response.status == 200, f"{path}: HTTP {response.status}"
                    page.evaluate("document.fonts.ready")
                    expect(page.locator("h1")).to_have_count(1)
                    expect(page.locator("main")).to_have_count(1)
                    expect(page.locator('.docs-sidebar [aria-current="page"]')).to_have_attribute("href", path)
                    assert page.locator("#docs-menu").evaluate("element => element.open") == (width >= 768)
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{width}px overflow: {path}"
                    images = page.locator('.sandbox-content img')
                    for image in images.all():
                        image.evaluate("async element => { element.loading = 'eager'; await element.decode(); }")
                        assert image.evaluate("element => element.naturalWidth > 0"), f"Undecodable image: {path}"
                    check_accessibility(page, f"{width}px {path}")
                    if screenshot_dir and path in {f"/{guide}-docs/" for guide in GUIDES}:
                        page.screenshot(path=str(Path(screenshot_dir) / f"{path.strip('/')}-{width}.png"), full_page=True)
                    assert not page_errors, f"{path}: {json.dumps(page_errors)}"
                print(f"PASS rendered docs, images, navigation state and axe WCAG A/AA: {len(routes)} routes at {width}px", flush=True)

            for width in (1440, 390):
                page.set_viewport_size({"width": width, "height": 1000})
                for guide in GUIDES:
                    home = f"/{guide}-docs/"
                    page.goto(BASE_URL + home, wait_until="networkidle")
                    menu = page.locator("#docs-menu")
                    if width < 768:
                        menu.locator("summary").press("Enter")
                        expect(menu.locator("nav")).to_be_visible()
                    menu.get_by_role("link", name="Getting Started", exact=True).press("Enter")
                    expect(page).to_have_url(BASE_URL + home + "getting-started/")
                    if width < 768:
                        assert not menu.evaluate("element => element.open")
                        menu.locator("summary").press("Space")
                    if guide in APP_URLS:
                        expect(menu.get_by_role("link", name="Open the app", exact=True)).to_have_attribute("href", APP_URLS[guide])
                    destination = "stem-splitter" if guide == "sandbox" else "sandbox"
                    menu.locator(f'a[href="/{destination}-docs/"]').press("Enter")
                    expect(page).to_have_url(f"{BASE_URL}/{destination}-docs/")
                print(f"PASS keyboard article and cross-guide navigation: 3 guides at {width}px", flush=True)

            page.goto(BASE_URL + "/sandbox-docs/#student-onboarding")
            expect(page).to_have_url(BASE_URL + "/sandbox-docs/student-onboarding/")
            missing = context.request.get(BASE_URL + "/stem-splitter-docs/not-a-guide/")
            assert missing.status == 404, f"Missing guide returned {missing.status}"
            print("PASS existing Sandbox hash redirect and missing-guide 404", flush=True)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
