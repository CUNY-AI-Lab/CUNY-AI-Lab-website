"""Adapt reviewed HTML articles to the shared website layout without rewriting prose."""

import argparse
import hashlib
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {
    "stem-splitter": "https://stem-splitter.ailab-452.workers.dev",
    "systems-mapping": "https://systems-mapping.ailab-452.workers.dev",
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def adapt_url(value, tool, attribute):
    url = urlsplit(value)
    if attribute == "src":
        if url.scheme or url.netloc or not url.path.startswith("img/") or ".." in Path(url.path).parts:
            raise ValueError(f"Expected canonical guide image: {value}")
        return urlunsplit(("", "", f"/images/docs/{tool}/{url.path[4:]}", url.query, url.fragment))
    if url.scheme:
        if url.scheme not in {"https", "http", "mailto"}:
            raise ValueError(f"Unsupported article URL: {value}")
        if url.netloc == "ailab.gc.cuny.edu" and url.path.startswith("/sandbox-docs"):
            return urlunsplit(("", "", url.path.rstrip("/") + "/", url.query, url.fragment))
        return value
    if url.netloc or ".." in Path(url.path).parts:
        raise ValueError(f"Unexpected article URL: {value}")
    if url.path.startswith("/"):
        return TOOLS[tool] + value
    if url.path.endswith(".html"):
        page = url.path.removesuffix(".html")
        path = f"/{tool}-docs/" + ("" if page == "index" else page + "/")
        return urlunsplit(("", "", path, url.query, url.fragment))
    if not url.path:
        return value.replace("#main", "#main-content") if value == "#main" else value
    raise ValueError(f"Unmapped article link: {value}")


class Article(HTMLParser):
    def __init__(self, tool):
        super().__init__(convert_charrefs=False)
        self.tool = tool
        self.in_main = False
        self.main_count = 0
        self.capture = None
        self.capture_depth = 0
        self.parts = []
        self.title = []
        self.description = []
        self.heading_id = None
        self.images = set()

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "main":
            if self.in_main:
                raise ValueError("Nested main")
            self.in_main = True
            self.main_count += 1
            return
        if not self.in_main:
            return
        if tag in {"script", "style", "iframe", "object", "embed", "form", "link"} or any(key.startswith("on") for key, _ in attrs):
            raise ValueError(f"Active content is not permitted in guide articles: {tag}")
        if self.capture:
            if tag not in VOID:
                self.capture_depth += 1
            return
        if tag == "h1" or (tag == "p" and "lede" in attr.get("class", "").split()):
            self.capture = "title" if tag == "h1" else "description"
            self.capture_depth = 1
            if tag == "h1":
                self.heading_id = attr.get("id")
            return
        if tag == "img":
            if not attr.get("alt"):
                raise ValueError("Guide images need alternative text")
            self.images.add(urlsplit(attr["src"]).path)
        rewritten = []
        for key, value in attrs:
            if key in {"href", "src"}:
                value = adapt_url(value, self.tool, key)
            rewritten.append(key if value is None else f'{key}="{html.escape(value, quote=True)}"')
        self.parts.append("<" + tag + (" " + " ".join(rewritten) if rewritten else "") + ">")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        elif self.in_main:
            if self.capture:
                self.capture_depth -= 1
                if self.capture_depth == 0:
                    self.capture = None
            elif tag not in VOID:
                self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_main:
            if self.capture:
                getattr(self, self.capture).append(data)
            else:
                self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, data):
        if self.in_main and not self.capture:
            self.parts.append(f"<!--{data}-->")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem-dir", type=Path, required=True)
    parser.add_argument("--systems-dir", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path, required=True)
    parser.add_argument("--source-label", required=True)
    args = parser.parse_args()
    metadata = {}
    hashes = {}
    for tool, source in (("stem-splitter", args.stem_dir), ("systems-mapping", args.systems_dir)):
        pages = sorted(source.glob("*.html"))
        if not pages:
            raise ValueError(f"No reviewed pages in {source}")
        output = ROOT / "src/content/tool-guides" / tool
        output.mkdir(parents=True, exist_ok=True)
        metadata[tool] = {}
        for file in pages:
            if not re.fullmatch(r"[a-z0-9-]+", file.stem):
                raise ValueError(f"Unexpected guide filename: {file.name}")
            content = file.read_text()
            article = Article(tool)
            article.feed(content)
            if article.main_count != 1 or not article.title or not article.description:
                raise ValueError(f"Expected one main, title and introduction: {file.name}")
            title = html.unescape("".join(article.title)).strip()
            description = html.unescape("".join(article.description)).strip()
            metadata[tool][file.stem] = {
                "title": title,
                "description": description,
                "headingId": article.heading_id or f"{tool}-{file.stem}",
            }
            (output / file.name).write_text("".join(article.parts).strip() + "\n")
            hashes[f"{tool}/{file.name}"] = hashlib.sha256(file.read_bytes()).hexdigest()
            for image in article.images:
                source_image = args.assets_dir / tool / image
                destination = ROOT / "public/images/docs" / tool / Path(image).relative_to("img")
                if not source_image.is_file():
                    raise ValueError(f"Missing canonical image: {source_image}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_image, destination)
        expected = {file.name for file in pages}
        for file in output.glob("*.html"):
            if file.name not in expected:
                raise ValueError(f"Stale imported guide needs explicit reconciliation: {file}")
    (ROOT / "src/data/tool-docs-pages.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "src/data/tool-docs-source.json").write_text(json.dumps({"source": args.source_label, "files": hashes}, indent=2) + "\n")
    print(json.dumps({"imported": {tool: len(pages) for tool, pages in metadata.items()}, "source": args.source_label}))


if __name__ == "__main__":
    main()
