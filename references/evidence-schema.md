# Evidence ledger contract (version 1)

The deterministic validator runs locally, reads JSON and hashes files. It makes no model calls and does not fetch sources. It does not determine legal truth, exhaustiveness, applicability, source authenticity or whether a cited passage supports a claim. A researcher collects evidence; a qualified lawyer and product owner assess it.

Run from the repository with the configured Python environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/validate_evidence.py PATH_TO_PACK
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The default is `PACK/evidence-ledger.json`. Override it with `evidence_ledger` in `pack.json`. Paths inside the ledger must be relative to the pack, exist as local files and remain inside the pack after resolution. Public document names are relative to `drafts_dir` (default `drafts`). SHA256 values are lowercase hex hashes of **exact file bytes**, including newline and formatting choices. A changed snapshot or document fails validation even when its prose looks similar.

```json
{
  "schema_version": 1,
  "sources": [
    {
      "id": "S1",
      "title": "The official authority and instrument title",
      "url": "https://official-authority.example/instrument",
      "primary": true,
      "jurisdiction": "The applicable jurisdiction",
      "retrieved_at": "2026-10-09T12:00:00+02:00",
      "snapshot": {"file": "research/snapshots/instrument.txt", "sha256": "REPLACE_WITH_REAL_SHA256"}
    }
  ],
  "claims": [
    {
      "id": "C1",
      "text": "The exact material legal assertion being assessed",
      "kind": "legal",
      "status": "verified",
      "decision": "accepted",
      "jurisdiction": "The applicable jurisdiction",
      "applicability": "Why the authority applies to this operator, feature and release",
      "locator": "Article, section, paragraph or page supporting this assertion",
      "source_ids": ["S1"]
    }
  ],
  "documents": {
    "privacy-policy.md": {"sha256": "REPLACE_WITH_REAL_DOCUMENT_SHA256", "claim_ids": ["C1"]}
  }
}
```

This specimen is deliberately invalid until actual evidence replaces its placeholders. Do not convert fictional examples into release evidence.

Every source needs a unique nonempty `id`, `title`, `url`, boolean `primary`, `jurisdiction`, timezone-aware nonfuture `retrieved_at` and a hashed local `snapshot`. URLs use `https`, `http`, or `repo` (for product repository evidence). Preserve publication/effective dates, versions, quotations, conflicting authorities and retrieval method in the snapshot or additional ledger fields where relevant; the validator does not interpret them. Protect confidential source material and include only the minimal excerpt needed.

Every claim needs a unique nonempty `id`, `text`, `kind` (`legal` or `product`), `status` (`verified`, `unverified`, `contradicted` or `qualified`), `decision` (`accepted`, `held` or `rejected`) and `source_ids` list. An accepted claim must be `verified` and cite at least one known source. An accepted legal claim also needs `jurisdiction`, `applicability`, `locator` and at least one source marked primary. A secondary commentary or repository popularity score cannot alone support an accepted legal claim.

Every selected public document needs a current exact-byte hash and a nonempty list of accepted, verified `claim_ids`. Keep rejected and held claims in the ledger for review history, but exclude them from public document coverage until resolved or removed from the public assertion. The validator checks declared coverage; it cannot detect omitted claims. Trace **all material legal assertions and product promises**, not one token claim per document. Product assertions require implementation/test evidence describing its scope: local browser tests do not prove hosted, native-device or production behavior.

`verified` is a declared review status, not a fact inferred by the script. Hashes detect a mismatch with recorded bytes; they do not authenticate a website, lawyer, reviewer or signature. A source can remain byte-identical while the law changes. Re-check primary authorities and release applicability at human review and repeat the research after material changes.
