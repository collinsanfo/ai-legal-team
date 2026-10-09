"""No network/model calls. Every pack lives in an isolated temporary directory."""
import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_pack import Pack, build_page, publish_problems  # noqa: E402
from validate_evidence import digest, evidence_problems  # noqa: E402


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-pack-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "drafts").mkdir()
        (self.root / "review").mkdir()
        (self.root / "snapshots").mkdir()
        self.cfg = {"jurisdiction": "Example jurisdiction",
                    "required_public_documents": ["terms-of-service.md"],
                    "public": [{"key": "terms", "title": "Terms", "file": "terms-of-service.md"}]}
        self.put("drafts/terms-of-service.md", "# Terms\n\nAn example statement for mechanical testing.\n")
        self.put("snapshots/source.txt", "Fictional primary source for a mechanical test.\n")
        for name in ("owner", "counsel", "product"):
            self.put(f"review/{name}.md", f"Fictional {name} review evidence; never a real approval.\n")
        self.ledger = {"schema_version": 1,
                       "sources": [{"id": "S1", "title": "Fictional test source",
                                    "url": "https://example.invalid/source", "primary": True,
                                    "jurisdiction": "Example jurisdiction",
                                    "retrieved_at": "2000-01-01T12:00:00Z",
                                    "snapshot": self.file_record("snapshots/source.txt")}],
                       "claims": [{"id": "C1", "text": "Fictional test claim", "kind": "legal",
                                   "status": "verified", "decision": "accepted", "source_ids": ["S1"],
                                   "jurisdiction": "Example jurisdiction", "applicability": "Synthetic test only",
                                   "locator": "Section 1"}],
                       "documents": {"terms-of-service.md": {
                           "sha256": digest(self.root / "drafts/terms-of-service.md"), "claim_ids": ["C1"]}}}
        self.attestation = {"schema_version": 1,
                            "required_public_documents": ["terms-of-service.md"],
                            "documents": {"terms-of-service.md": {
                                "sha256": digest(self.root / "drafts/terms-of-service.md")}}, "blockers": []}
        for kind, name in (("owner_approval", "owner"), ("counsel_review", "counsel"),
                           ("product_verification", "product")):
            self.attestation[kind] = {"status": "verified", "reviewer": "Synthetic test reviewer",
                                      "reviewed_at": "2000-01-02T12:00:00Z",
                                      "evidence": [self.file_record(f"review/{name}.md")]}
        self.attestation["counsel_review"]["jurisdiction"] = "Example jurisdiction"
        self.save()

    def put(self, relative, text):
        (self.root / relative).write_text(text, encoding="utf-8", newline="\n")

    def file_record(self, name):
        return {"file": name, "sha256": digest(self.root / name)}

    def save(self, bind_ledger=True):
        self.put("pack.json", json.dumps(self.cfg))
        self.put("evidence-ledger.json", json.dumps(self.ledger))
        if bind_ledger:
            self.attestation["evidence_ledger_sha256"] = digest(self.root / "evidence-ledger.json")
        self.put("release-attestation.json", json.dumps(self.attestation))

    def refresh_documents(self):
        sha = digest(self.root / "drafts/terms-of-service.md")
        self.ledger["documents"]["terms-of-service.md"]["sha256"] = sha
        self.attestation["documents"]["terms-of-service.md"]["sha256"] = sha
        self.save()

    def problems(self):
        return publish_problems(Pack(self.root, self.cfg))

    def assert_problem(self, fragment):
        problems = self.problems()
        self.assertTrue(any(fragment in p for p in problems), f"Expected {fragment!r} in {problems}")

    def cli(self, script, *flags):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / script), str(self.root), *flags],
                              capture_output=True, text=True, check=False)

    def test_valid_records_pass_mechanical_gate(self):
        self.assertEqual(self.problems(), [])
        result = self.cli("build_pack.py", "--page-only", "--check-publish")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("does not authenticate reviewers", result.stdout)
        self.assertNotIn("Ready to publish", result.stdout)

    def test_empty_public_pack_fails(self):
        self.cfg["public"] = []
        self.assert_problem("public document set is empty")

    def test_no_explicit_scope_fails(self):
        self.cfg.pop("required_public_documents")
        self.assert_problem("explicit nonempty required_public_documents")

    def test_required_document_absent_from_discovery_fails(self):
        self.cfg.pop("public")
        self.cfg["required_public_documents"].append("privacy-policy.md")
        self.assert_problem("privacy-policy.md: required public document")

    def test_selected_missing_file_fails(self):
        (self.root / "drafts/terms-of-service.md").unlink()
        self.assert_problem("selected public document missing")

    def test_duplicate_selected_documents_fail(self):
        self.cfg["public"].append(copy.deepcopy(self.cfg["public"][0]))
        self.assert_problem("duplicate files")

    def test_heading_only_document_fails(self):
        self.put("drafts/terms-of-service.md", "# Terms\n\n## Contents\n")
        self.refresh_documents()
        self.assert_problem("public document body is empty")

    def test_draft_formats_fail(self):
        for banner in ("DRAFT", "# DRAFT Terms", "# Privacy policy (draft)", "**Draft for review**",
                       "Version 1 (draft)"):
            with self.subTest(banner=banner):
                self.put("drafts/terms-of-service.md", banner + "\n\nSubstantive example.\n")
                self.refresh_documents()
                self.assert_problem("still carries a draft")

    def test_each_marker_fails_even_lowercase_unclosed(self):
        for kind in ("owner", "counsel", "decision", "app change"):
            with self.subTest(kind=kind):
                self.put("drafts/terms-of-service.md", f"# Terms\n\nExample. [{kind}: unresolved\n")
                self.refresh_documents()
                self.assert_problem("marker(s) left")

    def test_stripped_notes_cannot_hide_markers(self):
        self.cfg["strip_notes_from_public"] = True
        self.put("drafts/terms-of-service.md", "# Terms\n\nExample.\n\n## notes for review\n[COUNSEL: confirm]\n")
        self.refresh_documents()
        self.assert_problem("including review notes")
        build_page(Pack(self.root, self.cfg))
        self.assertNotIn("COUNSEL: confirm", (self.root / "review.html").read_text(encoding="utf-8"))

    def test_notes_only_engineering_blocker_fails(self):
        self.put("drafts/terms-of-service.md", "# Terms\n\nExample.\n\n## Notes for review\n"
                 "### Code changes needed\n1. Implement deletion before making this promise.\n")
        self.refresh_documents()
        self.assert_problem("code changes in review notes")

    def test_completed_notes_checklist_is_permitted_with_review_records(self):
        self.put("drafts/terms-of-service.md", "# Terms\n\nExample.\n\n## Notes for review\n"
                 "### Code changes needed\n- [x] Verified deletion in isolated acceptance evidence.\n")
        self.refresh_documents()
        self.assertEqual(self.problems(), [])

    def test_unchecked_tasks_and_status_placeholders_fail(self):
        for note in ("- [ ] Owner decision", "Needs counsel", "Status: unresolved", "TODO: retention", "TBD"):
            with self.subTest(note=note):
                self.put("drafts/terms-of-service.md", "# Terms\n\nExample.\n\n## Notes\n" + note)
                self.refresh_documents()
                self.assert_problem("unresolved placeholder")

    def test_upstream_owner_decisions_fail(self):
        self.put("owner-decisions-to-confirm.md", "# Owner decisions\n\nChoose the retention period.\n")
        self.assert_problem("upstream decisions or product tasks remain open")

    def test_upstream_completed_tasks_are_permitted(self):
        self.put("known-fix-tasks.md", "# Tasks\n\n- [x] Deletion acceptance evidence recorded.\n")
        self.assertEqual(self.problems(), [])

    def test_open_red_team_row_fails(self):
        self.put("review/red-team-findings.md", "| Document | Issue | Action |\n|---|---|---|\n"
                 "| Terms | Liability scope | needs counsel |\n")
        self.assert_problem("red-team findings: unresolved")

    def test_open_red_team_status_column_fails(self):
        for status in ("open", "pending", "unresolved", "blocked", "needs owner"):
            with self.subTest(status=status):
                self.put("review/red-team-findings.md", "| Document | Issue | Status |\n|---|---|---|\n"
                         f"| Terms | Liability scope | {status} |\n")
                self.assert_problem("red-team findings: unresolved")

    def test_completed_red_team_status_column_is_permitted(self):
        self.put("review/red-team-findings.md", "| Document | Issue | Status |\n|---|---|---|\n"
                 "| Terms | Typographical issue | resolved |\n")
        self.assertEqual(self.problems(), [])

    def test_no_approval_inferred_from_prose(self):
        self.put("drafts/terms-of-service.md", "# Terms\n\nApproved by owner and lawyer.\n")
        self.refresh_documents()
        (self.root / "release-attestation.json").unlink()
        self.assert_problem("release attestation: cannot read")

    def test_all_three_review_roles_are_required(self):
        for kind in ("owner_approval", "counsel_review", "product_verification"):
            with self.subTest(kind=kind):
                record = self.attestation.pop(kind)
                self.save()
                self.assert_problem(f"release {kind}: verified review record missing")
                self.attestation[kind] = record

    def test_pending_review_fails(self):
        self.attestation["counsel_review"]["status"] = "pending"
        self.save()
        self.assert_problem("counsel_review: status must be verified")

    def test_counsel_jurisdiction_mismatch_fails(self):
        self.attestation["counsel_review"]["jurisdiction"] = "Another jurisdiction"
        self.save()
        self.assert_problem("jurisdiction differs")

    def test_unresolved_attestation_blocker_fails(self):
        self.attestation["blockers"] = [{"id": "B1", "status": "open",
                                         "resolution": self.file_record("review/product.md")}]
        self.save()
        self.assert_problem("remains unresolved")

    def test_review_evidence_mutation_invalidates_record(self):
        self.put("review/counsel.md", "Changed evidence.\n")
        self.assert_problem("counsel_review evidence 1: stale file hash")

    def test_document_mutation_invalidates_both_coverage_and_review(self):
        with (self.root / "drafts/terms-of-service.md").open("ab") as handle:
            handle.write(b"New public commitment.\n")
        self.assert_problem("stale document hash")
        self.assert_problem("release document terms-of-service.md: stale file hash")

    def test_line_ending_edit_invalidates_exact_bytes(self):
        path = self.root / "drafts/terms-of-service.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_problem("release document terms-of-service.md: stale file hash")

    def test_notes_only_edit_invalidates_exact_bytes(self):
        with (self.root / "drafts/terms-of-service.md").open("ab") as handle:
            handle.write(b"\n## Notes\nChanged review context.\n")
        self.assert_problem("release document terms-of-service.md: stale file hash")

    def test_ledger_mutation_invalidates_approval_binding(self):
        self.ledger["claims"][0]["locator"] = "Section 2"
        self.save(bind_ledger=False)
        self.assert_problem("release evidence ledger: stale file hash")

    def test_snapshot_mutation_invalidates_source(self):
        self.put("snapshots/source.txt", "Changed source snapshot.\n")
        self.assert_problem("snapshot: stale file hash")

    def test_accepted_unverified_contradicted_or_qualified_claims_fail(self):
        for status in ("unverified", "contradicted", "qualified"):
            with self.subTest(status=status):
                self.ledger["claims"][0]["status"] = status
                self.save()
                self.assert_problem("accepted claim must have verified status")

    def test_secondary_source_cannot_alone_support_accepted_legal_claim(self):
        self.ledger["sources"][0]["primary"] = False
        self.save()
        self.assert_problem("accepted legal claim requires a primary source")

    def test_missing_claim_coverage_fails(self):
        self.ledger["documents"]["terms-of-service.md"]["claim_ids"] = []
        self.save()
        self.assert_problem("nonempty claim_ids coverage")

    def test_held_claim_cannot_be_public_coverage(self):
        self.ledger["claims"][0]["decision"] = "held"
        self.save()
        self.assert_problem("not accepted and verified")

    def test_unknown_source_fails(self):
        self.ledger["claims"][0]["source_ids"] = ["missing"]
        self.save()
        self.assert_problem("unknown source missing")

    def test_timezone_and_future_timestamps_fail(self):
        for stamp in ("2000-01-01", "2999-01-01T00:00:00Z"):
            with self.subTest(stamp=stamp):
                self.ledger["sources"][0]["retrieved_at"] = stamp
                self.save()
                self.assert_problem("retrieved_at must")

    def test_path_traversal_snapshot_is_rejected(self):
        self.ledger["sources"][0]["snapshot"]["file"] = "../outside.txt"
        self.save()
        self.assert_problem("file path leaves the pack")

    def test_nonstring_claim_id_is_rejected_without_crash(self):
        self.ledger["documents"]["terms-of-service.md"]["claim_ids"] = [{}]
        self.save()
        self.assert_problem("nonempty claim_ids coverage")

    def test_standalone_ledger_cli(self):
        result = self.cli("validate_evidence.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.ledger["claims"][0]["status"] = "contradicted"
        self.save()
        result = self.cli("validate_evidence.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_review_build_needs_no_release_records_and_page_only_preserves_polish(self):
        (self.root / "release-attestation.json").unlink()
        (self.root / "evidence-ledger.json").unlink()
        self.put("drafts/questions-for-counsel.md", "# Polished report\n\nKeep this exact text.\n")
        before = (self.root / "drafts/questions-for-counsel.md").read_bytes()
        result = self.cli("build_pack.py", "--page-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / "drafts/questions-for-counsel.md").read_bytes(), before)
        self.assertTrue((self.root / "review.html").is_file())
        result = self.cli("build_pack.py", "--page-only", "--check-publish")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_normal_review_build_still_consolidates_without_release_records(self):
        (self.root / "release-attestation.json").unlink()
        (self.root / "evidence-ledger.json").unlink()
        result = self.cli("build_pack.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "drafts/questions-for-counsel.md").is_file())
        self.assertTrue((self.root / "drafts/app-changes-needed.md").is_file())


if __name__ == "__main__":
    unittest.main()
