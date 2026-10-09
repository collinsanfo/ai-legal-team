# Mechanical release gate

`--check-publish` now fails closed on empty packs, missing scoped documents, draft headings/banners/versions, unresolved markers in **bodies or notes**, unchecked tasks and incomplete declared evidence/review records. Passing this gate is not a legal opinion, publication authorization or proof of lawyer identity or competence.

Normal review builds remain available without release records:

```powershell
.\.venv\Scripts\python.exe scripts/build_pack.py PATH_TO_PACK
.\.venv\Scripts\python.exe scripts/build_pack.py PATH_TO_PACK --page-only
.\.venv\Scripts\python.exe scripts/build_pack.py PATH_TO_PACK --page-only --check-publish
```

`--page-only` preserves existing consolidated Markdown documents. A normal build regenerates the counsel/questions, product changes and research reports, so use `--page-only` when a human has polished them. Both modes write a local review page; neither publishes documents or sends them anywhere.

## Declare the actual release scope

Choose required documents from the feature/jurisdiction review. The checker intentionally has no universal software-document minimum that would imply every app has the same obligations. `required_public_documents` is mandatory, nonempty and unique for release checks. Names are relative to `drafts_dir`:

```json
{
  "jurisdiction": "The reviewed jurisdiction scope",
  "required_public_documents": ["terms-of-service.md", "privacy-policy.md"],
  "release_attestation": "release-attestation.json",
  "evidence_ledger": "evidence-ledger.json"
}
```

Every required file must appear in the selected public set and exist. `public` still explicitly replaces discovered public documents; a required file excluded by that override fails. Every selected public document, including optional selected documents, must have evidence coverage and release hashes. An unknown discovered Markdown file remains public unless its name begins `internal-`. This preserves the existing builder's behavior; review the selected set deliberately.

Resolve `[OWNER]`, `[COUNSEL]`, `[DECISION]` and `[APP CHANGE]` markers, including lowercase or unclosed markers and review-note tables. `strip_notes_from_public: true` changes display only and cannot hide release blockers. Draft-only/heading-only files, `TODO`/`TBD`/`TBC`, unchecked checklists, `needs counsel` and explicit unresolved/pending/blocked statuses fail. Code-change sections in notes must contain only completed checkbox tasks or an explicit `None` / `No changes required` statement. This rule is intentionally conservative: explanatory paragraphs belong in the completed-task evidence or an archived review report.

Current root files `owner-decisions-to-confirm.md`, `known-fix-tasks.md` and `owner-driven-changes.md` must also be empty, explicitly `None` or contain only completed `[x]` checklist tasks (headings allowed). Red-team findings fail if they retain counsel-needed rows, unresolved markers, unchecked tasks or explicit open statuses. Preserve closed history outside these active blocker files and record resolution evidence; deleting a marker alone does not establish the underlying decision.

## Record actual owner, lawyer and product reviews

The default `PACK/release-attestation.json` requires this contract:

```json
{
  "schema_version": 1,
  "required_public_documents": ["terms-of-service.md", "privacy-policy.md"],
  "documents": {
    "terms-of-service.md": {"sha256": "REPLACE_WITH_REAL_SHA256"},
    "privacy-policy.md": {"sha256": "REPLACE_WITH_REAL_SHA256"}
  },
  "evidence_ledger_sha256": "REPLACE_WITH_REAL_LEDGER_SHA256",
  "owner_approval": {
    "status": "verified",
    "reviewer": "Actual responsible owner identity",
    "reviewed_at": "2026-10-09T12:00:00+02:00",
    "evidence": [{"file": "review/owner-approval.md", "sha256": "REPLACE_WITH_REAL_SHA256"}]
  },
  "counsel_review": {
    "status": "verified",
    "reviewer": "Actual qualified lawyer identity",
    "jurisdiction": "The reviewed jurisdiction scope",
    "reviewed_at": "2026-10-09T12:00:00+02:00",
    "evidence": [{"file": "review/counsel-review.md", "sha256": "REPLACE_WITH_REAL_SHA256"}]
  },
  "product_verification": {
    "status": "verified",
    "reviewer": "Actual product verification reviewer identity",
    "reviewed_at": "2026-10-09T12:00:00+02:00",
    "evidence": [{"file": "review/product-verification.md", "sha256": "REPLACE_WITH_REAL_SHA256"}]
  },
  "blockers": []
}
```

Do not fill this with invented names, AI approval, placeholder hashes or presumed counsel signoff. Before making an actual `verified` record, the responsible person must review the exact documents and evidence. Record scope, outcome, remaining limitations, source/version/date and reviewer qualifications in the evidence files; use a confidential identifier if necessary and store identifying records securely.

The attestation scope must equal the configured required list, and its `documents` keys must equal **all selected public files**. SHA256 binds the complete original Markdown bytes, including notes, formatting and line endings. This is stricter than the displayed page: even a notes-only edit invalidates the record. The attestation also binds the exact evidence-ledger bytes, and every review evidence file must match its hash. Review timestamps must include a timezone and not be in the future; counsel jurisdiction must equal the configured jurisdiction string when present.

`blockers` is mandatory even when empty. Every recorded blocker must have a unique `id`, `status: "resolved"` and `resolution: {"file": "review/resolution.md", "sha256": "..."}`. An unresolved status fails. The gate cannot discover unrecorded blockers or verify a declared resolution's substance.

Compute a file's hash without rewriting it:

```powershell
(Get-FileHash -LiteralPath PATH_TO_FILE -Algorithm SHA256).Hash.ToLowerInvariant()
```

Hashes are edit detectors, not cryptographic signatures. Anyone who can edit the pack can alter evidence, hashes and reviewer labels. The script therefore reports only **Mechanical release gate passed**. A qualified lawyer, product owner and actual deployment checks must still establish readiness; no software test here measures legal accuracy or compliance.

## Review HTML and private source excerpts

Python-Markdown preserves raw HTML, so a malicious draft or copied source excerpt could previously place scripts, event handlers or `javascript:` links into the review page. The builder now sanitizes **all** document and inline metadata HTML after Markdown conversion and marker highlighting using pinned [`nh3`](https://pypi.org/project/nh3/) and its maintained [allowlist sanitizer](https://nh3.readthedocs.io/en/latest/).

Normal headings, paragraphs, emphasis, lists, blockquotes, code examples, links, tables and marker colors remain. Script/style payloads, event attributes, SVG/MathML, forms, frames and embedded content are removed. Images are omitted to prevent automatic requests from untrusted private excerpts; link text remains, and ordinary HTTP(S), email, telephone and relative navigation links require the user's action. The review page loads no external fonts and sends no referrer on navigation. A generated Content Security Policy disables scripts and automatic network/resource loading while permitting the trusted local stylesheet and safe table alignment.

The source documents remain plain Markdown and are not rewritten by HTML sanitization. This hardening secures the rendered local review surface; it does not make source Markdown, linked destinations, attachments, or third-party viewers safe. Do not paste generated HTML into a host that rewrites it or assumes the whole pack is trusted. Sanitization does not detect misleading prose, phishing destinations or research prompt injection. Review linked authorities deliberately and protect confidential originals separately. Keep the pinned sanitizer updated after reviewing upstream security releases. Structural regression tests check hostile fragments and metadata, preserve normal formatting, and assert the no-script/no-network page policy; they do not claim exhaustive browser/security coverage.
