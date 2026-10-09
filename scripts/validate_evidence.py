#!/usr/bin/env python3
"""Validate a declared evidence ledger without contacting sources or calling a model.

This checks records and exact local file hashes, not legal truth, claim completeness,
reviewer identity, or whether a retrieved source really supports a claim.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys
from urllib.parse import urlparse


SHA256 = re.compile(r"^[a-f0-9]{64}$")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def local_path(root, name):
    """Resolve a pack-relative file and reject traversal, absolute paths and symlinks outside it."""
    if not nonempty(name):
        raise ValueError("file path must be a nonempty string")
    relative = pathlib.Path(name)
    # Also reject Windows paths when running on a non-Windows host.
    windows = pathlib.PureWindowsPath(name)
    if relative.is_absolute() or windows.drive or windows.root:
        raise ValueError("file path must be pack-relative")
    root = pathlib.Path(root).resolve()
    result = (root / relative).resolve()
    if not result.is_relative_to(root):
        raise ValueError("file path leaves the pack")
    return result


def timestamp_problem(value):
    if not nonempty(value):
        return "must be an ISO 8601 timestamp with a timezone"
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return "must include a timezone"
        if parsed > datetime.datetime.now(datetime.timezone.utc):
            return "must not be in the future"
    except ValueError:
        return "must be an ISO 8601 timestamp with a timezone"
    return None


def file_record_problems(root, record, label):
    if not isinstance(record, dict):
        return [f"{label}: must be a file/hash record"]
    problems = []
    sha = record.get("sha256")
    if not isinstance(sha, str) or not SHA256.fullmatch(sha):
        problems.append(f"{label}: sha256 must be 64 lowercase hexadecimal characters")
    try:
        path = local_path(root, record.get("file"))
        if not path.is_file():
            problems.append(f"{label}: file missing")
        elif isinstance(sha, str) and digest(path) != sha:
            problems.append(f"{label}: stale file hash")
    except (ValueError, OSError) as error:
        problems.append(f"{label}: {error}")
    return problems


def load_json(path, label):
    try:
        value = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            return None, [f"{label}: must be a JSON object"]
        return value, []
    except (OSError, ValueError) as error:
        return None, [f"{label}: cannot read valid JSON ({error})"]


def evidence_problems(root, cfg, public_names):
    """Validate the ledger and its declared coverage for every selected public document."""
    problems = []
    try:
        ledger_path = local_path(root, cfg.get("evidence_ledger", "evidence-ledger.json"))
    except ValueError as error:
        return [f"evidence ledger: {error}"]
    ledger, errors = load_json(ledger_path, "evidence ledger")
    problems.extend(errors)
    if ledger is None:
        return problems
    if type(ledger.get("schema_version")) is not int or ledger["schema_version"] != 1:
        problems.append("evidence ledger: schema_version must be 1")
    sources = ledger.get("sources")
    claims = ledger.get("claims")
    documents = ledger.get("documents")
    if not isinstance(sources, list):
        problems.append("evidence ledger: sources must be a list")
        sources = []
    if not isinstance(claims, list):
        problems.append("evidence ledger: claims must be a list")
        claims = []
    if not isinstance(documents, dict):
        problems.append("evidence ledger: documents must be an object")
        documents = {}
    source_index = {}
    for i, source in enumerate(sources):
        label = f"evidence source {i + 1}"
        if not isinstance(source, dict):
            problems.append(f"{label}: must be an object")
            continue
        ident = source.get("id")
        if not nonempty(ident) or ident in source_index:
            problems.append(f"{label}: id must be nonempty and unique")
        else:
            source_index[ident] = source
        for field in ("title", "jurisdiction"):
            if not nonempty(source.get(field)):
                problems.append(f"{label}: {field} is required")
        uri = source.get("url")
        if not nonempty(uri) or urlparse(uri).scheme not in ("http", "https", "repo"):
            problems.append(f"{label}: url must use http, https or repo")
        if type(source.get("primary")) is not bool:
            problems.append(f"{label}: primary must be a boolean")
        problem = timestamp_problem(source.get("retrieved_at"))
        if problem:
            problems.append(f"{label}: retrieved_at {problem}")
        problems.extend(file_record_problems(root, source.get("snapshot"), f"{label} snapshot"))
    claim_index = {}
    for i, claim in enumerate(claims):
        label = f"evidence claim {i + 1}"
        if not isinstance(claim, dict):
            problems.append(f"{label}: must be an object")
            continue
        ident = claim.get("id")
        if not nonempty(ident) or ident in claim_index:
            problems.append(f"{label}: id must be nonempty and unique")
        else:
            claim_index[ident] = claim
        if not nonempty(claim.get("text")):
            problems.append(f"{label}: text is required")
        if claim.get("kind") not in ("legal", "product"):
            problems.append(f"{label}: kind must be legal or product")
        if claim.get("status") not in ("verified", "unverified", "contradicted", "qualified"):
            problems.append(f"{label}: invalid status")
        if claim.get("decision") not in ("accepted", "held", "rejected"):
            problems.append(f"{label}: invalid decision")
        ids = claim.get("source_ids")
        if not isinstance(ids, list) or any(not nonempty(s) for s in ids):
            problems.append(f"{label}: source_ids must be a list of nonempty strings")
            ids = []
        for source_id in ids:
            if source_id not in source_index:
                problems.append(f"{label}: unknown source {source_id}")
        if claim.get("decision") == "accepted":
            if claim.get("status") != "verified":
                problems.append(f"{label}: accepted claim must have verified status")
            if not ids:
                problems.append(f"{label}: accepted claim must cite evidence")
            if claim.get("kind") == "legal":
                for field in ("jurisdiction", "applicability", "locator"):
                    if not nonempty(claim.get(field)):
                        problems.append(f"{label}: accepted legal claim requires {field}")
                if not any(source_index.get(s, {}).get("primary") is True for s in ids):
                    problems.append(f"{label}: accepted legal claim requires a primary source")
    for name in public_names:
        label = f"evidence document {name}"
        entry = documents.get(name)
        if not isinstance(entry, dict):
            problems.append(f"{label}: coverage record missing")
            continue
        try:
            drafts = local_path(root, cfg.get("drafts_dir", "drafts"))
            path = local_path(drafts, name)
            sha = entry.get("sha256")
            if not isinstance(sha, str) or not SHA256.fullmatch(sha):
                problems.append(f"{label}: valid sha256 is required")
            elif not path.is_file() or digest(path) != sha:
                problems.append(f"{label}: missing document or stale document hash")
        except (ValueError, OSError) as error:
            problems.append(f"{label}: {error}")
        ids = entry.get("claim_ids")
        if not isinstance(ids, list) or not ids or any(not nonempty(c) for c in ids):
            problems.append(f"{label}: nonempty claim_ids coverage is required")
            continue
        for ident in ids:
            claim = claim_index.get(ident)
            if claim is None:
                problems.append(f"{label}: unknown claim {ident}")
            elif claim.get("decision") != "accepted" or claim.get("status") != "verified":
                problems.append(f"{label}: claim {ident} is not accepted and verified")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=pathlib.Path)
    parser.add_argument("--config", type=pathlib.Path)
    args = parser.parse_args()
    root = args.pack.resolve()
    cfg_path = args.config or root / "pack.json"
    cfg, problems = load_json(cfg_path, "pack config")
    if cfg is not None:
        required = cfg.get("required_public_documents")
        if not isinstance(required, list) or not required or any(not nonempty(n) for n in required):
            problems.append("pack config: explicit nonempty required_public_documents is required")
            required = []
        selected = cfg.get("public")
        if selected is not None:
            if not isinstance(selected, list) or any(not isinstance(d, dict) or not nonempty(d.get("file")) for d in selected):
                problems.append("pack config: public must be a list of file records")
                names = required
            else:
                names = [d["file"] for d in selected]
                for name in required:
                    if name not in names:
                        problems.append(f"pack config: required public document not selected: {name}")
        else:
            # Same discovery as build_pack, imported only for this CLI path.
            from build_pack import Pack
            names = [n for _, _, n in Pack(root, cfg).public]
            for name in required:
                if name not in names:
                    problems.append(f"pack config: required public document not selected: {name}")
        problems.extend(evidence_problems(root, cfg, names))
    if problems:
        print("Evidence validation failed:")
        print("\n".join(f"  - {problem}" for problem in problems))
        return 1
    print("Evidence records and local hashes passed; legal support and coverage still require human review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
