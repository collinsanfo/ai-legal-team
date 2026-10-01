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
    --check-publish  exit with status 1 unless every public document is ready to publish: no DRAFT
                     banner and no [OWNER], [COUNSEL], [DECISION] or [APP CHANGE] marker left in its body

Which documents: every .md file in the drafts folder. templates/document-catalogue.md gives each standard
file name its title, its place in the order and its audience (public or internal). A file the catalogue
does not know is shown as a public document, or as an internal one if its name starts with "internal-".
The "public" and "internal" lists in pack.json replace what is found.

Config: PACK_DIR/pack.json (see scripts/pack.example.json). Every key is optional.
    brand, operator, jurisdiction   names used in headings and default text
    lang                            page language (default "en")
    page_title, kicker, heading, lede, meta ([label, value] rows), hub_url, hub_label
    drafts_dir, research_dir, redteam_file, output, catalogue (path to another catalogue)
    public      [{key, title, file}]        replaces the public documents found
    internal    [{key, title, file, scan}]  replaces the internal documents found; scan: true also
                                            collects that document's markers
    research    [{label, file}]             default: every .md file in research_dir
    strip_notes_from_public                 true once approved: public documents show without notes
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

try:
    import markdown
    from markdown.extensions.toc import slugify
except ImportError:  # pragma: no cover
    sys.exit("This script needs python-markdown. Install it with: pip install markdown")

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
    m = re.search(r"^## Notes\b.*$", md, re.M)
    return (md[: m.start()], md[m.start():]) if m else (md, "")


def markers(text, kind):
    """Every [KIND ...] marker in text as (position, marker), nested brackets included."""
    found, i, tag = [], 0, "[" + kind
    while (j := text.find(tag, i)) >= 0:
        after = text[j + len(tag): j + len(tag) + 1]
        if after and after not in ": ]\t":
            i = j + 1  # a longer word, such as [OWNERSHIP
            continue
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


def highlight(fragment):
    return MARK.sub(lambda m: f'<mark class="mk mk-{MARK_CLASS[m.group(1)]}">[{m.group(1)}{m.group(2)}]</mark>',
                    fragment)


def inline(md):
    """Render a short Markdown string (bold, links, code) without the surrounding paragraph."""
    out = markdown.markdown(str(md)).strip()
    return highlight(re.sub(r"\A<p>(.*)</p>\Z", r"\1", out, flags=re.S))


def to_html(key, md):
    md = re.sub(r"\A\s*#\s+[^\n]*\n", "", md)  # the page shows its own title for each document
    conv = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"slugify": lambda v, s: f"{key}-{slugify(v, s)}"}},
    )
    out = conv.convert(rebase(md, 2))
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return highlight(out)


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
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg.get('page_title', f'{brand} Legal Pack'))}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
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


def publish_problems(pack):
    problems = []
    for _, _, name in pack.public:
        path = pack.drafts / name
        if not path.exists():
            continue
        body = split_notes(read(path))[0]
        if re.search(r"\*\*\s*DRAFT\b", body):
            problems.append(f"{name}: still carries the DRAFT banner")
        for kind in KINDS:
            n = len(markers(body, kind))
            if n:
                problems.append(f"{name}: {n} [{kind}] marker(s) left")
    return problems


def main():
    ap = argparse.ArgumentParser(description="Build an AI legal team's consolidated documents and review page.")
    ap.add_argument("pack", type=pathlib.Path, help="the pack folder")
    ap.add_argument("--config", type=pathlib.Path, help="config file (default: PACK/pack.json)")
    ap.add_argument("--page-only", action="store_true", help="rebuild the page without regenerating documents")
    ap.add_argument("--check-publish", action="store_true", help="exit 1 unless public documents are ready to publish")
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
        print("Ready to publish: no banner or markers left in the public documents.")


if __name__ == "__main__":
    main()
