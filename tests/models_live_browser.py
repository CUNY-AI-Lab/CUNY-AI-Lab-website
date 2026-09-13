"""Verify the deployed registry against the real public Gateway catalog."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ["CAIL_TEST_BASE"].rstrip("/")
CATALOG_URL = "https://tools.ailab.gc.cuny.edu/v1/catalog"


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page_errors: list[str] = []
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            for attempt in range(2):
                try:
                    with page.expect_response(
                        lambda response: response.url == CATALOG_URL,
                        timeout=20_000,
                    ) as response_info:
                        page.goto(f"{BASE_URL}/models/", wait_until="domcontentloaded")
                    break
                except PlaywrightTimeoutError:
                    if attempt == 1:
                        raise
                    page.wait_for_timeout(2_000)
            response = response_info.value
            expect(page.get_by_role("status", name="Catalog status", exact=True)).to_contain_text(
                "Catalog checked at", timeout=20_000
            )
            assert response.ok, f"Gateway catalog returned HTTP {response.status}"

            allowed_origin = response.headers.get("access-control-allow-origin")
            website_origin = f"{urlsplit(BASE_URL).scheme}://{urlsplit(BASE_URL).netloc}"
            assert allowed_origin in {"*", website_origin}, (
                f"Gateway CORS allows {allowed_origin!r}, expected '*' or {website_origin!r}"
            )

            catalog = response.json()
            assert isinstance(catalog, dict) and catalog.get("object") == "list"
            rows = catalog.get("data")
            assert isinstance(rows, list), "Gateway catalog data is not an array"

            expected = page.evaluate(
                """rows => {
                    const valid = rows.filter(row =>
                        row !== null && typeof row === 'object' && !Array.isArray(row) &&
                        typeof row.id === 'string' && row.id.length >= 1 && row.id.length <= 512 &&
                        typeof row.name === 'string' && row.name.length >= 1 &&
                        Array.isArray(row.capabilities) &&
                        row.capabilities.every(capability => typeof capability === 'string') &&
                        Object.hasOwn(row, 'context_length') &&
                        (row.context_length === null ||
                            (Number.isSafeInteger(row.context_length) && row.context_length > 0))
                    );
                    const counts = new Map();
                    for (const row of valid) counts.set(row.id, (counts.get(row.id) ?? 0) + 1);
                    const unambiguous = valid.filter(row => counts.get(row.id) === 1);
                    const featured = unambiguous
                        .filter(row => row.recommended === true && row.tier === 'recommended' &&
                            Number.isSafeInteger(row.order) && row.order > 0)
                        .toSorted((a, b) => a.order - b.order || a.id.localeCompare(b.id));
                    return {
                        ids: unambiguous.map(row => row.id),
                        featuredIds: featured.map(row => row.id),
                    };
                }""",
                rows,
            )
            expected_ids = expected["ids"]
            assert expected_ids, "Gateway catalog has no usable unambiguous rows"

            rendered_ids = page.locator("#models-list article.model-card code").all_text_contents()
            assert len(rendered_ids) == len(expected_ids)
            assert set(rendered_ids) == set(expected_ids), (
                "Deployed registry rows do not match the live Gateway catalog"
            )

            rendered_featured = page.locator(
                "#featured-list article.featured-card code"
            ).all_text_contents()
            assert rendered_featured == expected["featuredIds"], (
                "Deployed Featured order does not match Gateway recommendation metadata"
            )
            assert page_errors == [], page_errors
            print(
                "PASS deployed model registry loaded the live Gateway catalog, "
                "matched its usable IDs, and followed recommendation metadata",
                flush=True,
            )
        finally:
            browser.close()


if __name__ == "__main__":
    main()
