"""Check the article importer with synthetic, local-only source material."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/import-tool-guides.py"
spec = importlib.util.spec_from_file_location("tool_guides_importer", SCRIPT)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


class ImportGuidesTest(unittest.TestCase):
    def test_nested_images_keep_paths_and_do_not_collide(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "tools").mkdir()
            (root / "src/data").mkdir(parents=True)
            shutil.copyfile(SCRIPT, root / "tools/import-tool-guides.py")
            for tool in importer.TOOLS:
                source = root / "input" / tool
                source.mkdir(parents=True)
                (source / "index.html").write_text('''<!doctype html><html><body>
                  <header>Old site chrome</header><main>
                  <h1 id="start">A &amp; B</h1><p class="lede">Start <em>here</em>.</p>
                  <p>Keep this sentence.</p><a href="notes.html#shared">Notes</a>
                  <a href="/">Open the app</a>
                  <img src="img/overview.png" alt="Overview">
                  <img src="img/screens/overview.png" alt="Detail">
                  </main><footer>Old site footer</footer></body></html>''')
                for relative, content in (("overview.png", b"flat image"), ("screens/overview.png", b"nested image")):
                    image = root / "assets" / tool / "img" / relative
                    image.parent.mkdir(parents=True, exist_ok=True)
                    image.write_bytes(content)
            subprocess.run([sys.executable, str(root / "tools/import-tool-guides.py"),
                            "--stem-dir", str(root / "input/stem-splitter"),
                            "--systems-dir", str(root / "input/systems-mapping"),
                            "--assets-dir", str(root / "assets"), "--source-label", "synthetic fixture"],
                           check=True, capture_output=True, text=True)
            metadata = json.loads((root / "src/data/tool-docs-pages.json").read_text())
            for tool, app in importer.TOOLS.items():
                article = (root / "src/content/tool-guides" / tool / "index.html").read_text()
                self.assertNotIn("Old site", article)
                self.assertIn("Keep this sentence.", article)
                self.assertIn(f'href="/{tool}-docs/notes/#shared"', article)
                self.assertIn(f'href="{app}/"', article)
                self.assertEqual(metadata[tool]["index"]["title"], "A & B")
                self.assertEqual(metadata[tool]["index"]["description"], "Start here.")
                for relative, content in (("overview.png", b"flat image"), ("screens/overview.png", b"nested image")):
                    self.assertIn(f'src="/images/docs/{tool}/{relative}"', article)
                    self.assertEqual((root / "public/images/docs" / tool / relative).read_bytes(), content)

    def test_images_require_canonical_relative_paths(self):
        for path in ("https://example.com/image.png", "/image.png", "img/../outside.png", "//example.com/image.png"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                importer.adapt_url(path, "stem-splitter", "src")

    def test_article_rejects_active_content(self):
        for content in ('<script>alert(1)</script>', '<img src="img/a.png" alt="a" onerror="alert(1)">', '<iframe src="https://example.com"></iframe>'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                importer.Article("stem-splitter").feed(f"<main>{content}</main>")


if __name__ == "__main__":
    unittest.main()
