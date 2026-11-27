"""Check what search engines see across the whole built site.

Every indexable page must declare itself canonical and appear in the sitemap.
Internal links must name the final address (with its trailing slash), so that
crawlers do not record redirects. Moved pages must have permanent redirects on
both hosts: public/_redirects (Cloudflare) and amplify-redirects.json (Amplify).
"""

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

SITE = "https://ailab.gc.cuny.edu"
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class Page(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.links = []
        self.canonicals = []
        self.noindex = False
        self.refresh = None
        self.feed(file.read_text())

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if tag == "link" and "canonical" in (attr.get("rel") or "").split():
            self.canonicals.append(attr.get("href"))
        if tag == "meta" and attr.get("name") == "robots" and "noindex" in (attr.get("content") or ""):
            self.noindex = True
        if tag == "meta" and (attr.get("http-equiv") or "").lower() == "refresh":
            self.refresh = attr.get("content")


def cloudflare_rules():
    rules = []
    for line in (ROOT / "public/_redirects").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            source, target, status = line.split()
            rules.append((source, target, status))
    return rules


def main():
    pages = {"/" + str(file.relative_to(DIST)).removesuffix("index.html"): Page(file)
             for file in DIST.rglob("*.html")}
    sitemap = {node.text for file in DIST.glob("sitemap-[0-9]*.xml")
               for node in ElementTree.parse(file).findall(".//{*}loc")}
    indexable = {path for path, page in pages.items() if not page.noindex and path != "/404.html"}

    for path in indexable:
        assert pages[path].canonicals == [SITE + path], f"{path}: canonical is {pages[path].canonicals}"
        assert SITE + path in sitemap, f"{path}: missing from sitemap"
    for url in sitemap:
        assert urlsplit(url).path in indexable, f"Sitemap lists {url}, which is not an indexable page"

    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(urljoin(SITE + path, link))
            if url.netloc != urlsplit(SITE).netloc:
                continue
            last = url.path.rsplit("/", 1)[-1]
            assert not url.path or url.path.endswith("/") or "." in last, (
                f"{path} links to {link}; add the trailing slash so crawlers do not record a redirect")

    # Pages that only forward (noindex plus meta refresh) need a real 301 on each host.
    moved = {}
    for path, page in pages.items():
        if page.noindex and page.refresh:
            old_root = "/" + path.strip("/").split("/", 1)[0]
            new_root = page.canonicals[0] if path == old_root + "/" else None
            moved.setdefault(old_root, None)
            if new_root:
                moved[old_root] = new_root
    expected = []
    for old_root, canonical in sorted(moved.items()):
        assert canonical, f"{old_root}/ has no forwarding index page"
        target = urlsplit(canonical)
        if target.netloc == urlsplit(SITE).netloc:
            expected += [(old_root, target.path, "301"), (f"{old_root}/*", f"{target.path}:splat", "301")]
        else:
            # External app shortcuts cover only the root, with either slash spelling.
            expected += [(old_root, canonical, "301"), (f"{old_root}/", canonical, "301")]
    cloudflare = cloudflare_rules()
    assert sorted(cloudflare) == sorted(expected), f"public/_redirects should hold exactly {expected}"

    amplify = json.loads((ROOT / "amplify-redirects.json").read_text())
    assert amplify[-1] == {"source": "/<*>", "target": "/index.html", "status": "404-200"}, (
        "amplify-redirects.json must end with the existing not-found rule")
    translated = [(rule["source"].replace("<*>", "*"), rule["target"].replace("<*>", ":splat"), rule["status"])
                  for rule in amplify[:-1]]
    assert translated == cloudflare, "amplify-redirects.json and public/_redirects disagree"

    print(f"PASS {len(indexable)} indexable pages, {len(sitemap)} sitemap URLs, "
          f"slash-terminated internal links, {len(moved)} moved sections redirected on both hosts")


if __name__ == "__main__":
    main()
