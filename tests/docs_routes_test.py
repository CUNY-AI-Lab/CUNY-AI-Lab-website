"""Check published docs links on every built page, including cached Markdown.

Runs on the production artifact as well as in CI; existing redirect pages can
mask stale internal links by returning HTTP 200.
"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

SITE = "https://ailab.gc.cuny.edu"
DIST = Path(__file__).resolve().parents[1] / "dist"
GUIDES = ("sandbox", "stem-splitter", "systems-mapping")
LEGACY = {f"/{guide}-docs" for guide in GUIDES}


class Page(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.noindex = False
        self.feed(file.read_text())

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if tag == "link" and "canonical" in attr.get("rel", "").split():
            self.canonicals.append(attr.get("href"))
        if tag == "meta" and attr.get("name") == "robots" and "noindex" in attr.get("content", ""):
            self.noindex = True


def main():
    pages = {"/" + str(file.relative_to(DIST)).removesuffix("index.html"): Page(file)
             for file in DIST.rglob("*.html")}
    expected = {"/docs/", "/docs/api-keys/", "/docs/cail-pi/", "/models/guide/"}
    for guide in GUIDES:
        assert f"/docs/{guide}/" in pages
        expected.update(path for path in pages if path.startswith(f"/docs/{guide}/"))
    assert expected <= pages.keys(), f"Missing documentation pages: {expected - pages.keys()}"
    sitemap = {node.text for file in DIST.glob("sitemap-*.xml")
               for node in ElementTree.parse(file).findall(".//{*}loc")}
    for path, page in pages.items():
        if path in expected:
            assert page.canonicals == [SITE + path] and not page.noindex, f"{path}: wrong canonical or robots"
            assert SITE + path in sitemap, f"{path}: missing from sitemap"
        for link in page.links:
            url = urlsplit(urljoin(SITE + path, link))
            if url.netloc != urlsplit(SITE).netloc:
                continue
            root = "/" + url.path.strip("/").split("/", 1)[0]
            assert root not in LEGACY, f"{path} still links to moved address {link}"
            if root == "/docs" or url.path.rstrip("/") == "/models/guide":
                assert url.path in expected, f"{path} links to a noncanonical or missing guide {link}"
    for path in expected:
        parts = path.strip("/").split("/")
        if len(parts) < 2 or parts[1] not in GUIDES:
            continue
        old = path.replace(f"/docs/{parts[1]}/", f"/{parts[1]}-docs/", 1)
        assert pages[old].canonicals == [SITE + path] and pages[old].noindex, f"{old}: wrong canonical or robots"
        assert SITE + old not in sitemap, f"{old}: legacy URL in sitemap"
    print(f"PASS canonical docs, sitemap and discoverable links across {len(pages)} built pages")


if __name__ == "__main__":
    main()
