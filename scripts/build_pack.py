#!/usr/bin/env python3
"""Build the consolidated documents and one HTML review page for an AI legal team's pack.

No AI: everything is copied or extracted from the pack's Markdown files, so it costs nothing to rerun.

Usage:
    python scripts/build_pack.py PACK_DIR [--config FILE] [--page-only] [--check-publish]

Writes (unless --page-only):
    <drafts>/questions-for-counsel.md  owner decisions to confirm, the red team's "needs counsel" rows,
                                       every [COUNSEL ...] marker, the memos' "Questions for ..." sections
    <drafts>/app-changes-needed.md     known engineering tasks, changes from the owner's answers, and each
                                       document's "Code changes needed" list (or its [APP CHANGE ...] markers)
    <drafts>/law-research.md           the memos' summaries, "could not verify" lists and sources
Always writes:
    <output>                           every document on one page, markers colour-coded (review.html)

Options:
    --page-only      rebuild the page only; keeps generated documents an AI consolidator has polished
    --check-publish  exit with status 1 unless explicit document scope, evidence and hash-bound
                     owner/counsel/product records pass the mechanical gate (not legal approval).

Which documents: every .md file in the drafts folder. templates/document-catalogue.md gives each standard
file name its title, its place in the order and its audience (public or internal). A file the catalogue
does not know is shown as a public document, or as an internal one if its name starts with "internal-".
The "public" and "internal" lists in pack.json replace what is found.

Config: PACK_DIR/pack.json (see scripts/pack.example.json). Keys are optional for review builds;
release checks require explicit scope, evidence and review records.
    brand, operator, jurisdiction   names used in headings and default text
    lang                            page language (default "en")
    page_title, kicker, heading, lede, meta ([label, value] rows), hub_url, hub_label
    drafts_dir, research_dir, redteam_file, output, catalogue (path to another catalogue)
    public      [{key, title, file}]        replaces the public documents found
    internal    [{key, title, file, scan}]  replaces the internal documents found; scan: true also
                                            collects that document's markers
    research    [{label, file}]             default: every .md file in research_dir
    strip_notes_from_public                 true once approved: public documents show without notes
    required_public_documents               explicit nonempty list of drafts-relative file names
    release_attestation, evidence_ledger     release record paths; see references/publish-gate.md
    accent, accent_dark                     link and heading colour in light and dark mode
    counsel_intro, changes_intro, research_intro
    edits       [{file, find, replace}]     applied to the generated documents after each build
Optional files in PACK_DIR, copied in when present:
    owner-decisions-to-confirm.md, known-fix-tasks.md, owner-driven-changes.md
"""
import argparse
import html
import json
import os
import pathlib
import re
import sys

from validate_evidence import (
    digest, evidence_problems, file_record_problems, load_json, local_path, nonempty,
    timestamp_problem,
)

try:
    import markdown
    import nh3
    from markdown.extensions.toc import slugify
except ImportError:  # pragma: no cover
    sys.exit("Install this script's pinned dependencies with: python -m pip install -r requirements.txt")

CATALOGUE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "document-catalogue.md"
ENTRY = re.compile(r"^### (.+?) \u00b7 `([A-Za-z0-9._-]+\.md)` \u00b7 (public|internal)[ \t]*$", re.M)
FALLBACK_CATALOGUE = [  # used only when the catalogue file cannot be read
    ("Terms of Service", "terms-of-service.md", "public"),
    ("Privacy Policy", "privacy-policy.md", "public"),
    ("Business Terms", "business-terms.md", "public"),
    ("Payments and Refunds", "payments-and-refunds.md", "public"),
    ("Community Guidelines", "community-guidelines.md", "public"),
    ("Prohibited Listings", "prohibited-listings.md", "public"),
    ("AI Features Notice", "ai-features-notice.md", "public"),
    ("Consent Forms", "consent-forms.md", "public"),
    ("Data Map and Retention", "data-map-and-retention.md", "internal"),
]
# Reports written by the team or by this script: always internal, never scanned for markers.
REPORTS_FIRST = [("Questions for Counsel", "questions-for-counsel.md"),
                 ("Decider's Answers", "counsel-answers.md"),
                 ("Product Changes Needed", "app-changes-needed.md")]
REPORTS_LAST = [("Law Research", "law-research.md")]
KINDS = ("OWNER", "COUNSEL", "DECISION", "APP CHANGE")

# Headings the research memos use (see roles/01-law-researcher.md); matched without regard to case.
H_SUMMARY = r"^#{1,4}\s+(.*\s)?summary\b.*$"
H_COUNSEL_Q = r"^#{1,4}\s+questions for counsel\b.*$"
H_OTHER_Q = r"^#{1,4}\s+questions for (?!counsel\b).+$"
H_UNVERIFIED = r"^#{1,4}\s+.*(could not verify|not verified|unverified).*$"
H_SOURCES = r"^#{1,4}\s+(list of\s+)?(primary\s+)?(sources?|source list)\b.*$"
H_CODE_CHANGES = r"^#{2,4}\s+.*code changes needed.*$"
URL = re.compile(r"https?://[^\s)>\]`\"'|]+")


# ---------------------------------------------------------------- text helpers
def read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # the same bytes on every system
        f.write(text)


def read_optional(path):
    path = pathlib.Path(path)
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def split_notes(md):
    """(body, notes): the notes start at the '## Notes ...' heading, if there is one."""
    m = re.search(r"^## Notes\b.*$", md, re.M | re.I)
    return (md[: m.start()], md[m.start():]) if m else (md, "")


def markers(text, kind):
    """Every [KIND ...] marker in text as (position, marker), nested brackets included."""
    found, i = [], 0
    pattern = re.compile(r"\[" + re.escape(kind) + r"(?=[: \]\t\r\n]|$)", re.I)
    while (match := pattern.search(text, i)) is not None:
        j = match.start()
        depth, k = 0, j
        while k < len(text):
            depth += {"[": 1, "]": -1}.get(text[k], 0)
            if depth == 0:
                break
            k += 1
        if depth:  # unclosed: take the rest of the line
            end = text.find("\n", j)
            k = (end if end >= 0 else len(text)) - 1
        found.append((j, text[j: k + 1]))
        i = k + 1
    return found


def marker_text(marker, kind):
    inner = marker[len(kind) + 1:]
    inner = inner[:-1] if inner.endswith("]") else inner
    return inner.lstrip(":").strip()


def heading_before(text, pos):
    hs = list(re.finditer(r"^#{2,4}\s+(.*)$", text[:pos], re.M))
    return hs[-1].group(1).strip() if hs else "Opening"


def sections(text, pattern):
    """[(heading text, section)] for every heading matching pattern; a section runs to the next heading
    of the same or a higher level."""
    out = []
    for m in re.finditer(pattern, text, re.M | re.I):
        line = m.group(0)
        level = len(line) - len(line.lstrip("#"))
        rest = text[m.end():]
        nxt = re.search(r"^#{1,%d}\s" % level, rest, re.M)
        out.append((line.lstrip("#").strip(), line + (rest[: nxt.start()] if nxt else rest)))
    return out


def section(text, pattern):
    found = sections(text, pattern)
    return found[0][1] if found else ""


def body_of(sec):
    return sec.split("\n", 1)[1].strip() if "\n" in sec else ""


def rebase(md, under=2):
    """Move the headings so the highest one sits just below a level-`under` heading."""
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", md, re.M)]
    if not levels:
        return md.strip()
    delta = under + 1 - min(levels)
    return re.sub(r"^(#{1,6})(?=\s)", lambda m: "#" * max(1, min(6, len(m.group(1)) + delta)),
                  md, flags=re.M).strip()


def nest(sec, under=2):
    """A section's content, without its own heading, ready to sit under a level-`under` heading."""
    return rebase(body_of(sec), under)


def marker_list(text, kind):
    """One bullet per distinct marker: '- **Section:** what is needed'."""
    lines, seen = [], set()
    for pos, mk in markers(text, kind):
        key = (heading_before(text, pos), marker_text(mk, kind))
        if key[1] and key not in seen:
            seen.add(key)
            lines.append(f"- **{key[0]}:** {key[1]}")
    return lines


def table_rows(text):
    """(header, cells) for every body row of every Markdown table in text."""
    header = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip().replace("\0", "\\|") for c in
                 line.strip().replace("\\|", "\0").strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif not set("".join(cells)) <= set("-: "):
            yield header, cells


def column(header, names, default):
    for i, h in enumerate(header):
        if any(n in h for n in names):
            return i
    return default


def needs_counsel_rows(text):
    rows = []
    for header, cells in table_rows(text):
        if "needs counsel" not in " ".join(cells).lower():
            continue

        def get(names, default):
            i = column(header, names, default)
            return cells[i] if i < len(cells) else ""

        where, problem, evidence = get(("document", "where"), 2), get(("problem", "issue"), 3), get(("evidence",), 4)
        rows.append(f"- **{where}:** {problem}" + (f" *(Evidence: {evidence})*" if evidence else ""))
    return rows


# ---------------------------------------------------------------- the pack
def load_catalogue(path):
    """[(title, file, audience)] from the catalogue's '### Title · `file.md` · audience' headings."""
    try:
        found = ENTRY.findall(read(path))
    except OSError:
        found = []
    return [(t.strip(), f, a) for t, f, a in found] or list(FALLBACK_CATALOGUE)


def slug(key):
    return re.sub(r"[^a-z0-9-]+", "-", str(key).lower()).strip("-") or "doc"


def doc_key(name):
    return slug(pathlib.PurePosixPath(name).stem)


class Pack:
    def __init__(self, root, cfg):
        self.root, self.cfg = root, cfg
        self.brand = cfg.get("brand", "The product")
        self.drafts = root / cfg.get("drafts_dir", "drafts")
        self.research_dir = root / cfg.get("research_dir", "research")
        self.redteam = root / cfg.get("redteam_file", "review/red-team-findings.md")
        self.output = root / cfg.get("output", "review.html")
        catalogue = load_catalogue(root / cfg["catalogue"] if cfg.get("catalogue") else CATALOGUE)
        public, internal = self.discover(catalogue)
        self.public = [(slug(d["key"]), d["title"], d["file"]) for d in cfg["public"]] \
            if "public" in cfg else public
        self.internal = [(slug(d["key"]), d["title"], d["file"], bool(d.get("scan"))) for d in cfg["internal"]] \
            if "internal" in cfg else internal
        if "research" in cfg:
            memos = [(r.get("label") or pathlib.Path(r["file"]).stem, self.research_dir / r["file"])
                     for r in cfg["research"]]
        else:
            memos = [(p.stem, p) for p in sorted(self.research_dir.glob("*.md"))]
        self.memos = [(label, read(p)) for label, p in memos if p.exists()]

    def discover(self, catalogue):
        """(public, internal) documents in the drafts folder, titled and ordered by the catalogue."""
        reports = {name for _, name in REPORTS_FIRST + REPORTS_LAST}
        present = {p.name for p in self.drafts.glob("*.md")} - reports
        public, internal = [], []
        for title, name, audience in catalogue:
            if name in present:
                present.discard(name)
                (public if audience == "public" else internal).append((title, name))
        for name in sorted(present):
            words = pathlib.Path(name).stem.split("-")
            if words[0] == "internal" and len(words) > 1:
                internal.append((" ".join(words[1:]).capitalize(), name))
            else:
                public.append((" ".join(words).capitalize(), name))
                print(f"note: {name} is not in the catalogue, so it is shown as a public document")
        redteam = pathlib.Path(os.path.relpath(self.redteam, self.drafts)).as_posix()
        return ([(doc_key(n), t, n) for t, n in public],
                [(doc_key(n), t, n, False) for t, n in REPORTS_FIRST]
                + [(doc_key(n), t, n, True) for t, n in internal]
                + [(doc_key(n), t, n, False) for t, n in REPORTS_LAST + [("Red-team Review", redteam)]])

    def scanned(self):
        """(title, path) of every document whose markers are collected: all public, and internal with scan."""
        docs = [(t, self.drafts / f) for _, t, f in self.public]
        docs += [(t, self.drafts / f) for _, t, f, scan in self.internal if scan]
        return [(t, p) for t, p in docs if p.exists()]

    def lawyer(self):
        j = self.cfg.get("jurisdiction")
        return f"a qualified {j} lawyer" if j else "a qualified lawyer"


# ---------------------------------------------------------------- generated documents
def build_counsel(pack):
    out = [pack.cfg.get("counsel_intro") or (
        f"Every question for {pack.lawyer()}, gathered from the drafts, the research and the red-team "
        "review. Send it with the public documents and ask for an answer to each: agree, agree with "
        "changes, or disagree with reasons.")]
    owner = read_optional(pack.root / "owner-decisions-to-confirm.md")
    if owner:
        out += ["## Owner decisions to confirm", rebase(owner)]
    if pack.redteam.exists():
        out += ["## Open points from the red-team review", "\n".join(needs_counsel_rows(read(pack.redteam))) or "- None."]
    marked = []
    for title, path in pack.scanned():
        items = marker_list(split_notes(read(path))[0], "COUNSEL")
        if items:
            marked += [f"### {title}", "\n".join(items)]
    out += ["## Questions marked in each document"] + (marked or ["- None."])
    for label, text in pack.memos:
        sec = section(text, H_COUNSEL_Q)
        if body_of(sec):
            out += [f"## Questions from {label}", nest(sec)]
    for label, text in pack.memos:
        for title, sec in sections(text, H_OTHER_Q):
            if body_of(sec):
                out += [f"## {title}", f"From {label}. Get the answers in writing.", nest(sec)]
    return "\n\n".join(out) + "\n"


def build_changes(pack):
    out = [pack.cfg.get("changes_intro") or (
        "Everything the product must change so the documents are true, gathered from every document. "
        "Ship the items a document depends on before that document is published.")]
    known = read_optional(pack.root / "known-fix-tasks.md")
    if known:
        out += ["## Engineering tasks already raised", rebase(known)]
    owner = read_optional(pack.root / "owner-driven-changes.md")
    if owner:
        out += ["## From the owner's answers", rebase(owner)]
    listed = []
    for title, path in pack.scanned():
        text = read(path)
        body, notes = split_notes(text)
        sec = section(text, H_CODE_CHANGES)
        if not body_of(sec):
            m = re.search(r"^.*code changes needed.*$", notes, re.M | re.I)
            if m:
                rest = notes[m.end():]
                nxt = re.search(r"^#{1,4}\s", rest, re.M)
                sec = m.group(0) + (rest[: nxt.start()] if nxt else rest)
        if body_of(sec):
            listed += [f"### {title}", nest(sec, 3)]
        else:
            items = marker_list(body, "APP CHANGE")
            if items:
                listed += [f"### {title}", "\n".join(items)]
    out += ["## Changes listed in each document"] + (listed or ["- None."])
    return "\n\n".join(out) + "\n"


def build_research(pack):
    out = [pack.cfg.get("research_intro") or (
        "The research behind the drafts, written by AI researchers from primary sources where they could "
        "reach them. It is not legal advice. Each memo gives a confidence level for every finding.")]
    for label, text in pack.memos:
        sec = section(text, H_SUMMARY)
        if body_of(sec):
            out += [f"## {label}", nest(sec)]
    for label, text in pack.memos:
        sec = section(text, H_UNVERIFIED)
        if body_of(sec):
            out += [f"## Could not verify: {label}", nest(sec)]
    for label, text in pack.memos:
        sec = section(text, H_SOURCES)
        if body_of(sec):
            out += [f"## Sources: {label}", nest(sec)]
        else:
            urls = list(dict.fromkeys(u.rstrip(".,;:") for u in URL.findall(text)))
            if urls:
                out += [f"## Sources cited: {label}", "\n".join(f"- <{u}>" for u in urls)]
    return "\n\n".join(out) + "\n"


def apply_edits(pack, name, text):
    for edit in pack.cfg.get("edits", []):
        if edit.get("file") != name:
            continue
        if edit["find"] in text:
            text = text.replace(edit["find"], edit["replace"])
        else:
            print(f"warning: edit for {name} not applied, text not found: {edit['find'][:60]!r}")
    return text


# ---------------------------------------------------------------- HTML page
MARK = re.compile(r"\[(OWNER|COUNSEL|APP CHANGE|DECISION)([^\[\]]*)\]")
MARK_CLASS = {"OWNER": "owner", "COUNSEL": "counsel", "APP CHANGE": "app", "DECISION": "decision"}
LEGEND = (("OWNER", "a fact or choice only the owner can give"),
          ("COUNSEL", "for the lawyer to confirm"),
          ("APP CHANGE", "the product must change first"),
          ("DECISION", "follows one of the owner's decisions"))
COLOR = re.compile(r"^#[0-9a-fA-F]{3,8}$")

# Sanitize every untrusted fragment AFTER Markdown rendering and marker highlighting.
# Raw HTML is accepted by Python-Markdown; escaping config titles alone cannot secure it.
CONTENT_TAGS = {
    "a", "abbr", "b", "blockquote", "br", "code", "dd", "del", "div", "dl", "dt", "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "kbd", "li", "mark", "ol", "p",
    "pre", "s", "samp", "small", "strong", "sub", "sup", "table", "tbody", "td", "tfoot",
    "th", "thead", "tr", "ul",
}
INLINE_TAGS = {
    "a", "abbr", "b", "br", "code", "del", "em", "i", "kbd", "mark", "s", "samp",
    "small", "strong", "sub", "sup",
}
REMOVE_CONTENT = {
    "script", "style", "iframe", "object", "embed", "svg", "math", "form", "template",
    "noscript", "noembed", "noframes", "xmp", "plaintext", "textarea", "title",
}
CONTENT_ATTRIBUTES = {"a": {"href", "title"}, "abbr": {"title"}, "ol": {"start"},
                      "td": {"colspan", "rowspan", "style"}, "th": {"colspan", "rowspan", "style"}}
CONTENT_ATTRIBUTES.update({tag: {"id"} for tag in ("h1", "h2", "h3", "h4", "h5", "h6")})
SAFE_CLASSES = {"div": {"table-wrap"},
                "mark": {"mk", "mk-owner", "mk-counsel", "mk-app", "mk-decision"}}
SAFE_SCHEMES = {"https", "http", "mailto", "tel"}
DOCUMENT_CLEANER = nh3.Cleaner(
    tags=CONTENT_TAGS, clean_content_tags=REMOVE_CONTENT, attributes=CONTENT_ATTRIBUTES,
    allowed_classes=SAFE_CLASSES, url_schemes=SAFE_SCHEMES, strip_comments=True,
    filter_style_properties={"text-align"}, link_rel="noopener noreferrer",
)
INLINE_CLEANER = nh3.Cleaner(
    tags=INLINE_TAGS, clean_content_tags=REMOVE_CONTENT,
    attributes={"a": {"href", "title"}, "abbr": {"title"}}, allowed_classes=SAFE_CLASSES,
    url_schemes=SAFE_SCHEMES, strip_comments=True, link_rel="noopener noreferrer",
)


def highlight(fragment):
    return MARK.sub(lambda m: f'<mark class="mk mk-{MARK_CLASS[m.group(1)]}">[{m.group(1)}{m.group(2)}]</mark>',
                    fragment)


def inline(md):
    """Render a short Markdown string (bold, links, code) without the surrounding paragraph."""
    out = markdown.markdown(str(md)).strip()
    return INLINE_CLEANER.clean(highlight(out))


def to_html(key, md):
    md = re.sub(r"\A\s*#\s+[^\n]*\n", "", md)  # the page shows its own title for each document
    conv = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": lambda v, s: f"{key}-{slugify(v, s)}"}},
    )
    out = conv.convert(rebase(md, 2))
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return DOCUMENT_CLEANER.clean(highlight(out))


CSS = """
:root{--bg:#F6F6F3;--surface:#FFFFFF;--ink:#18181B;--soft:#3F3F46;--muted:#64646C;--line:#E2E2DC;
--accent:__ACCENT__;--accent-tint:color-mix(in srgb,var(--accent) 8%,transparent);--code:rgba(24,24,27,.05);
--owner:#8A4A0C;--owner-bg:rgba(212,106,31,.14);--counsel:#1F4E8C;--counsel-bg:rgba(31,78,140,.12);
--app:#2B7153;--app-bg:rgba(43,113,83,.13);--decision:#5B3A9E;--decision-bg:rgba(91,58,158,.11);
--sans:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--mono:"JetBrains Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121214;--surface:#1C1C20;--ink:#F2F2EE;
--soft:#D4D4D0;--muted:#A1A1A8;--line:#34343A;--accent:__ACCENT_DARK__;--code:rgba(242,242,238,.08);
--owner:#E6B35F;--owner-bg:rgba(229,138,74,.16);--counsel:#8DB8EC;--counsel-bg:rgba(141,184,236,.14);
--app:#69C596;--app-bg:rgba(105,197,150,.14);--decision:#C3A8F0;--decision-bg:rgba(195,168,240,.14);color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121214;--surface:#1C1C20;--ink:#F2F2EE;--soft:#D4D4D0;--muted:#A1A1A8;--line:#34343A;
--accent:__ACCENT_DARK__;--code:rgba(242,242,238,.08);--owner:#E6B35F;--owner-bg:rgba(229,138,74,.16);--counsel:#8DB8EC;
--counsel-bg:rgba(141,184,236,.14);--app:#69C596;--app-bg:rgba(105,197,150,.14);--decision:#C3A8F0;
--decision-bg:rgba(195,168,240,.14);color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.65;-webkit-font-smoothing:antialiased}
.page{max-width:820px;margin:0 auto;padding-inline:16px;padding-block:36px 80px;display:flex;flex-direction:column;gap:40px}
a{color:var(--accent);text-underline-offset:3px;overflow-wrap:anywhere}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
h1,h2,h3,h4,h5,h6{text-wrap:balance;line-height:1.3;margin:0}
.top{display:flex;flex-direction:column;gap:14px}
.kicker{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0}
.top h1{font-size:34px;font-weight:700;letter-spacing:-.015em}
.lede{font-size:18px;color:var(--soft);margin:0;max-width:62ch}
.meta{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;font-size:14px;margin:0;padding-top:14px;border-top:1px solid var(--line)}
.meta dt{color:var(--muted)}.meta dd{margin:0}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:13px;margin:0;padding:0;list-style:none}
.nav{display:flex;flex-direction:column;gap:16px}
.nav h2{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.chips{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:0;padding:0}
.chips a{display:inline-flex;align-items:center;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--surface);
color:var(--ink);text-decoration:none;font-size:14px;font-weight:500;min-height:44px}
.chips a:hover{border-color:var(--accent)}
.doc{border-top:1px solid var(--line);padding-top:28px;display:flex;flex-direction:column;gap:6px;scroll-margin-top:12px}
.doc-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px}
.doc-head h2{font-size:26px;font-weight:700}
.doc-kind{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0}
.back{font-size:14px}
.prose{max-width:72ch;overflow-wrap:break-word}
.prose h3{font-size:20px;margin-top:28px}.prose h4{font-size:17px;margin-top:22px}.prose h5,.prose h6{font-size:15px;margin-top:18px}
.prose p,.prose ul,.prose ol{margin:10px 0}.prose li{margin:4px 0}
.prose code{font-family:var(--mono);font-size:.85em;background:var(--code);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
.prose pre{overflow-x:auto;background:var(--code);padding:12px;border-radius:8px}
.prose pre code{background:none;padding:0}
.prose blockquote{margin:12px 0;padding:8px 14px;border-left:3px solid var(--line);color:var(--soft)}
.table-wrap{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line);min-width:110px}
th{font-weight:600;background:var(--accent-tint)}
tr:last-child td{border-bottom:0}
.mk{border-radius:4px;padding:0 4px;font-size:.92em;font-weight:500}
.mk-owner{background:var(--owner-bg);color:var(--owner)}.mk-counsel{background:var(--counsel-bg);color:var(--counsel)}
.mk-app{background:var(--app-bg);color:var(--app)}.mk-decision{background:var(--decision-bg);color:var(--decision)}
@media (max-width:480px){.top h1{font-size:28px}.lede{font-size:17px}.meta{grid-template-columns:1fr;gap:0}.meta dd{margin-bottom:8px}}
@media print{.nav,.back{display:none}.doc{break-before:page}.page{max-width:none}}
"""


def page(pack, sections_html):
    cfg, brand = pack.cfg, pack.brand
    accent = cfg.get("accent", "") if COLOR.match(cfg.get("accent", "")) else "#3446A8"
    accent_dark = cfg.get("accent_dark", "") if COLOR.match(cfg.get("accent_dark", "")) else "#9AA9F2"
    css = CSS.replace("__ACCENT_DARK__", accent_dark).replace("__ACCENT__", accent)
    groups = (("Public documents", [(k, t, pack.drafts / f) for k, t, f in pack.public]),
              ("Internal: for the owner, the lawyer and engineering",
               [(k, t, pack.drafts / f) for k, t, f, _ in pack.internal]))
    nav = []
    for name, items in groups:
        chips = "".join(f'<li><a href="#{k}">{html.escape(t)}</a></li>' for k, t, p in items if p.exists())
        if chips:
            nav.append(f'<div class="nav-group"><h2>{name}</h2><ul class="chips">{chips}</ul></div>')
    legend = "".join(f'<li><mark class="mk mk-{MARK_CLASS[k]}">[{k}]</mark> {html.escape(d)}</li>' for k, d in LEGEND)
    lede = cfg.get("lede") or (
        f"Drafts prepared by an AI legal team for review by {cfg.get('operator', brand)} and "
        f"{pack.lawyer()}. Nothing here is legal advice.")
    if cfg.get("hub_url"):
        lede += f" Decisions and approvals are tracked in the [{cfg.get('hub_label', 'decisions tracker')}]({cfg['hub_url']})."
    meta = "".join(f"<dt>{html.escape(str(a))}</dt><dd>{inline(b)}</dd>" for a, b in cfg.get("meta", []))
    return f"""<!doctype html>
<html lang="{html.escape(cfg.get('lang', 'en'))}">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; img-src 'none'; font-src 'none'; connect-src 'none'; media-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg.get('page_title', f'{brand} Legal Pack'))}</title>
<style>{css}</style>
</head>
<body>
<div class="page" id="top">
<header class="top">
<p class="kicker">{html.escape(cfg.get('kicker', f'{brand} · Legal pack'))}</p>
<h1>{html.escape(cfg.get('heading', 'Legal documents for review'))}</h1>
<p class="lede">{inline(lede)}</p>
{f'<dl class="meta">{meta}</dl>' if meta else ''}
<ul class="legend">{legend}</ul>
</header>
<nav class="nav" aria-label="Documents">{''.join(nav)}</nav>
{''.join(sections_html)}
</div>
</body>
</html>
"""


def build_page(pack):
    out = []
    strip = bool(pack.cfg.get("strip_notes_from_public"))
    docs = [("Public document", k, t, f, True) for k, t, f in pack.public]
    docs += [("Internal", k, t, f, False) for k, t, f, _ in pack.internal]
    for kind, key, title, name, public in docs:
        path = pack.drafts / name
        if not path.exists():
            continue
        text = read(path)
        if public and strip:
            text = split_notes(text)[0]
        out.append(
            f'<section class="doc" id="{key}"><div class="doc-head"><div><p class="doc-kind">{kind}</p>'
            f'<h2>{html.escape(title)}</h2></div><a class="back" href="#top">Back to top</a></div>'
            f'<div class="prose">{to_html(key, text)}</div></section>')
    write(pack.output, page(pack, out))
    return len(out)


# ---------------------------------------------------------------- checks
def marker_report(pack):
    print("Markers left in document bodies (OWNER / COUNSEL / DECISION / APP CHANGE):")
    for _, path in pack.scanned():
        body = split_notes(read(path))[0]
        counts = " / ".join(str(len(markers(body, k))) for k in KINDS)
        print(f"  {path.name:<36} {counts}")


def tasks_closed(text):
    """Accept only an explicit empty task list or completed checkbox lines, not approval prose."""
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not re.match(r"^\s*#{1,6}\s", line)]
    if not lines:
        return True
    if len(lines) == 1 and re.fullmatch(
        r"(?:[-*]\s*)?(?:none\.?|no (?:code )?changes (?:needed|required)\.?)", lines[0], re.I):
        return True
    return all(re.match(r"^(?:[-*]|\d+[.)])\s+\[[xX]\]\s+", line) for line in lines)


def redteam_open_rows(text):
    """Detect explicit unresolved state in a review table's action/status columns."""
    for header, cells in table_rows(text):
        for i, title in enumerate(header):
            if not any(name in title for name in ("action", "status", "resolution")) or i >= len(cells):
                continue
            value = cells[i].strip("*_ `").lower()
            if re.match(r"^(?:open|unresolved|pending|blocked|todo|tbd|tbc)\b|"
                        r"^needs (?:counsel|owner|decision|app change|engineering)\b", value):
                return True
    return False


def publish_problems(pack):
    problems = []
    names = [name for _, _, name in pack.public]
    required = pack.cfg.get("required_public_documents")
    if not isinstance(required, list) or not required or any(not nonempty(n) for n in required):
        problems.append("pack.json: explicit nonempty required_public_documents scope is required")
        required = []
    if len(required) != len(set(required)):
        problems.append("pack.json: required_public_documents must be unique")
    if not names:
        problems.append("public document set is empty")
    if len(names) != len(set(names)):
        problems.append("public document set contains duplicate files")
    for name in required:
        if name not in names:
            problems.append(f"{name}: required public document not selected or missing")
    for _, _, name in pack.public:
        try:
            drafts = local_path(pack.root, pack.cfg.get("drafts_dir", "drafts"))
            path = local_path(drafts, name)
        except ValueError as error:
            problems.append(f"{name}: {error}")
            continue
        if not path.is_file():
            problems.append(f"{name}: selected public document missing")
            continue
        try:
            text = read(path)
        except (OSError, UnicodeError) as error:
            problems.append(f"{name}: cannot read public document ({error})")
            continue
        body, notes = split_notes(text)
        # A file containing headings alone is not a public document.
        substantive = re.sub(r"^\s*#{1,6}\s+.*$", "", body, flags=re.M).strip()
        if not substantive:
            problems.append(f"{name}: public document body is empty")
        if re.search(r"^\s*(?:#{1,6}\s*|>\s*|[-*]\s*)?(?:\*\*|__)?\s*DRAFT\b|"
                     r"^\s*#{1,6}\s+[^\n]*\bdraft\b|\(\s*draft\s*\)", text, re.M | re.I):
            problems.append(f"{name}: still carries a draft heading, banner or version")
        for kind in KINDS:
            n = len(markers(text, kind))
            if n:
                problems.append(f"{name}: {n} [{kind}] marker(s) left, including review notes")
        if re.search(r"\b(?:TODO|TBD|TBC)\b|^\s*(?:[-*]|\d+[.)])\s+\[ \]|"
                     r"\bneeds counsel\b|\b(?:status|decision)\s*:\s*(?:unresolved|pending|blocked)\b",
                     text, re.M | re.I):
            problems.append(f"{name}: unresolved placeholder, checklist or review status remains")
        for _, sec in sections(notes, H_CODE_CHANGES):
            if not tasks_closed(body_of(sec)):
                problems.append(f"{name}: code changes in review notes lack completed checklist records")
    for filename in ("owner-decisions-to-confirm.md", "known-fix-tasks.md", "owner-driven-changes.md"):
        text = read_optional(pack.root / filename)
        if text and (not tasks_closed(text) or any(markers(text, kind) for kind in KINDS)):
            problems.append(f"{filename}: upstream decisions or product tasks remain open")
    if pack.redteam.is_file():
        text = read(pack.redteam)
        if needs_counsel_rows(text) or redteam_open_rows(text) or any(markers(text, kind) for kind in KINDS) or re.search(
            r"^\s*(?:[-*]|\d+[.)])\s+\[ \]|\b(?:status|action)\s*:\s*(?:open|unresolved|pending|blocked)\b",
            text, re.M | re.I):
            problems.append("red-team findings: unresolved review markers or tasks remain")
    problems.extend(evidence_problems(pack.root, pack.cfg, names))
    problems.extend(attestation_problems(pack, names, required))
    return problems


def attestation_problems(pack, names, required):
    """Check declared approval records. Hashes detect edits; they do not authenticate a signer."""
    problems = []
    try:
        path = local_path(pack.root, pack.cfg.get("release_attestation", "release-attestation.json"))
    except ValueError as error:
        return [f"release attestation: {error}"]
    record, errors = load_json(path, "release attestation")
    problems.extend(errors)
    if record is None:
        return problems
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        problems.append("release attestation: schema_version must be 1")
    if record.get("required_public_documents") != required:
        problems.append("release attestation: required_public_documents differs from pack scope")
    documents = record.get("documents")
    if not isinstance(documents, dict) or set(documents) != set(names):
        problems.append("release attestation: documents must match every selected public file exactly")
        documents = documents if isinstance(documents, dict) else {}
    for name in names:
        entry = documents.get(name)
        if not isinstance(entry, dict):
            problems.append(f"release attestation: document hash missing for {name}")
        else:
            filename = pathlib.Path(pack.cfg.get("drafts_dir", "drafts")) / name
            problems.extend(file_record_problems(pack.root, {"file": filename.as_posix(),
                "sha256": entry.get("sha256")}, f"release document {name}"))
    ledger = {"file": pack.cfg.get("evidence_ledger", "evidence-ledger.json"),
              "sha256": record.get("evidence_ledger_sha256")}
    problems.extend(file_record_problems(pack.root, ledger, "release evidence ledger"))
    for kind in ("owner_approval", "counsel_review", "product_verification"):
        review = record.get(kind)
        label = f"release {kind}"
        if not isinstance(review, dict):
            problems.append(f"{label}: verified review record missing")
            continue
        if review.get("status") != "verified":
            problems.append(f"{label}: status must be verified")
        if not nonempty(review.get("reviewer")):
            problems.append(f"{label}: reviewer identity is required")
        problem = timestamp_problem(review.get("reviewed_at"))
        if problem:
            problems.append(f"{label}: reviewed_at {problem}")
        if kind == "counsel_review":
            if not nonempty(review.get("jurisdiction")):
                problems.append(f"{label}: reviewed jurisdiction is required")
            elif pack.cfg.get("jurisdiction") and review["jurisdiction"] != pack.cfg["jurisdiction"]:
                problems.append(f"{label}: jurisdiction differs from pack configuration")
        evidence = review.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{label}: nonempty evidence file records are required")
        else:
            for i, item in enumerate(evidence):
                problems.extend(file_record_problems(pack.root, item, f"{label} evidence {i + 1}"))
    blockers = record.get("blockers")
    if not isinstance(blockers, list):
        problems.append("release attestation: explicit blockers list is required (empty if none)")
    else:
        ids = set()
        for i, blocker in enumerate(blockers):
            label = f"release blocker {i + 1}"
            if not isinstance(blocker, dict):
                problems.append(f"{label}: must be an object")
                continue
            ident = blocker.get("id")
            if not nonempty(ident) or ident in ids:
                problems.append(f"{label}: nonempty unique id is required")
            else:
                ids.add(ident)
            if blocker.get("status") != "resolved":
                problems.append(f"{label}: remains unresolved")
            problems.extend(file_record_problems(pack.root, blocker.get("resolution"), f"{label} resolution"))
    return problems


def main():
    ap = argparse.ArgumentParser(description="Build an AI legal team's consolidated documents and review page.")
    ap.add_argument("pack", type=pathlib.Path, help="the pack folder")
    ap.add_argument("--config", type=pathlib.Path, help="config file (default: PACK/pack.json)")
    ap.add_argument("--page-only", action="store_true", help="rebuild the page without regenerating documents")
    ap.add_argument("--check-publish", action="store_true", help="exit 1 unless the mechanical release gate passes")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    root = args.pack.resolve()
    if not root.is_dir():
        sys.exit(f"Pack folder not found: {root}")
    cfg_path = args.config or root / "pack.json"
    cfg = json.loads(read(cfg_path)) if cfg_path.exists() else {}
    pack = Pack(root, cfg)
    if not pack.drafts.is_dir():
        sys.exit(f"Drafts folder not found: {pack.drafts}")

    if not args.page_only:
        builders = {"questions-for-counsel.md": build_counsel, "app-changes-needed.md": build_changes}
        if pack.memos:
            builders["law-research.md"] = build_research
        for name, build in builders.items():
            text = apply_edits(pack, name, build(pack))
            write(pack.drafts / name, text)
            print(f"wrote {name} ({len(text)} characters)")
    n = build_page(pack)
    print(f"wrote {pack.output.name} ({n} documents, {pack.output.stat().st_size} bytes)")
    marker_report(pack)

    if args.check_publish:
        problems = publish_problems(pack)
        if problems:
            print("Not ready to publish:")
            print("\n".join(f"  - {p}" for p in problems))
            sys.exit(1)
        print("Mechanical release gate passed: scope, markers, evidence and hash-bound review records checked.")
        print("This does not authenticate reviewers, verify legal correctness or authorize publication.")


if __name__ == "__main__":
    main()
