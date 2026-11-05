#!/usr/bin/env python3
"""Fail-closed entry point for a scoped, privately staged Pages distribution.

Never use build_github_pages_integrated_pilot.py --with-details for upload.
This entry point requires an external, independently trusted signature over an
exact approval receipt BEFORE even creating a candidate. It does not deploy.
The configured public-key fingerprint MUST be controlled outside the branch
being reviewed; matching bytes alone is not proof of reviewer authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import build_github_pages_reviewed_scope as scoped

ROOT = Path(__file__).resolve().parents[1]
HASH = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
MONTH = re.compile(r"^20\d{2}-(0[1-9]|1[0-2])$")
RECEIPT_SCHEMA = "kaigo-independent-distribution-receipt-v1"
INPUTS = ("approvals", "legal", "qa", "qa_meta")


def reject(reason: str):
    raise RuntimeError("PUBLIC_SCOPE_HOLD: " + reason)


def safe_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        reject("missing or linked input")
    return path.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_month(value: str) -> str:
    if not isinstance(value, str) or not MONTH.fullmatch(value):
        reject("invalid target month")
    return value


def approve_preflight(*, source_sha: str, target_month: str,
                      service_id: str, qa_service_code: str, inputs: dict[str, Path],
                      receipt_file: Path, signature_file: Path,
                      trusted_key_file: Path, trusted_key_sha256: str) -> dict:
    """Verify the out-of-repository trust anchor and exact records before build.

    The signer identity/independence and fingerprint must be established by
    the authorized release operator, not supplied or inferred by this script.
    """
    if not SHA.fullmatch(source_sha):
        reject("invalid source commit")
    check_month(target_month)
    if not isinstance(service_id, str) or not re.fullmatch(r"[a-z0-9-]{2,80}", service_id):
        reject("invalid legal service identifier")
    if not isinstance(qa_service_code, str) or not re.fullmatch(r"[A-Za-z0-9_-]{2,40}", qa_service_code):
        reject("invalid Q&A service code")
    if not isinstance(trusted_key_sha256, str) or not HASH.fullmatch(trusted_key_sha256):
        reject("independently pinned key fingerprint absent")
    if set(inputs) != set(INPUTS):
        reject("incomplete source inputs")
    decoded = {}
    observed = {}
    for name in INPUTS:
        raw = safe_file(inputs[name])
        observed[name] = sha256(raw)
        try:
            decoded[name] = json.loads(raw)
        except (ValueError, UnicodeError):
            reject("invalid " + name + " JSON")
    manifest = decoded["approvals"]
    legal, qa, meta = decoded["legal"], decoded["qa"], decoded["qa_meta"]
    if (not isinstance(legal, dict) or not isinstance(legal.get("documents"), list)
            or not isinstance(legal.get("records"), list) or not isinstance(qa, list)
            or not isinstance(meta, dict)):
        reject("invalid source structure")
    def unique_index(rows, label):
        index = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or row["id"] in index:
                reject("invalid or duplicate source identifier in " + label)
            index[row["id"]] = row
        return index
    docs = unique_index(legal["documents"], "documents")
    legal_rows = unique_index(legal["records"], "legal")
    qa_rows = unique_index(qa, "qa")
    if (not isinstance(manifest, dict) or manifest.get("schema") != scoped.SCHEMA
            or manifest.get("purpose") != "PRIVATE_ACCEPTANCE_ONLY"):
        reject("invalid approval manifest")
    entries = manifest.get("approvals")
    if not isinstance(entries, list) or not entries:
        reject("zero approved IDs")
    ids = []
    for entry in entries:
        if not isinstance(entry, dict):
            reject("invalid approval entry")
        if (entry.get("kind") not in ("legal", "qa") or not isinstance(entry.get("id"), str)
                or entry.get("publish_approved") is not True
                or entry.get("state") != scoped.APPROVED):
            reject("unapproved or unknown record")
        if not (entry.get("period_start", "") <= target_month <= entry.get("period_end", "")):
            reject("approval period mismatch")
        if entry["kind"] == "legal":
            if service_id not in entry.get("service_ids", []):
                reject("legal service mismatch")
        elif entry.get("service_code") != qa_service_code:
            reject("Q&A service mismatch")
        row = (legal_rows if entry["kind"] == "legal" else qa_rows).get(entry["id"])
        if row is None or not isinstance(entry.get("row_sha256"), str) or entry["row_sha256"] != scoped.digest(row):
            reject("source row hash or ID mismatch")
        if row.get("period_start") != entry.get("period_start") or row.get("period_end") != entry.get("period_end"):
            reject("source row applicability period mismatch")
        if entry["kind"] == "legal":
            doc = docs.get(row.get("document_id"))
            if (doc is None or entry.get("document_id") != row.get("document_id")
                    or row.get("state") != "REVIEWED_CURRENT"
                    or sorted(row.get("service_ids", [])) != sorted(entry.get("service_ids", []))):
                reject("legal source, document or currentness mismatch")
            if (scoped.source_url(row.get("url")) != entry.get("source_url")
                    or not isinstance(doc.get("title"), str) or not doc["title"].strip()):
                reject("missing legal document or official source")
        else:
            if (meta.get("review_status") != "REVIEWED_SCOPE_ONLY"
                    or row.get("review_state") != "REVIEWED_CURRENT"
                    or row.get("service_code") != entry.get("service_code")
                    or not isinstance(row.get("issued_source"), str)
                    or not row["issued_source"].strip()
                    or scoped.source_url(meta.get("source_workbook")) != entry.get("source_url")):
                reject("unreviewed Q&A or missing official issuance")
        ids.append((entry["kind"], entry["id"]))
    if len(ids) != len(set(ids)):
        reject("duplicate approved IDs")
    # Receipt and signature are private external inputs. No fallback to a
    # manifest-embedded reviewer string or a key supplied by an untrusted PR.
    key = safe_file(trusted_key_file)
    if trusted_key_file.resolve().is_relative_to(ROOT.resolve()):
        reject("trusted public key cannot come from the reviewed checkout")
    if sha256(key) != trusted_key_sha256:
        reject("untrusted signer key")
    raw_receipt = safe_file(receipt_file)
    signature = safe_file(signature_file)
    if not raw_receipt or not signature:
        reject("unsigned approval")
    try:
        receipt = json.loads(raw_receipt)
    except (ValueError, UnicodeError):
        reject("invalid signed receipt")
    if not isinstance(receipt, dict):
        reject("invalid signed receipt")
    if (receipt.get("schema") != RECEIPT_SCHEMA
            or receipt.get("decision") != "APPROVED_FOR_DISTRIBUTION"
            or receipt.get("source_sha") != source_sha
            or receipt.get("target_month") != target_month
            or receipt.get("service_id") != service_id
            or receipt.get("qa_service_code") != qa_service_code
            or receipt.get("source_sha256") != observed
            or receipt.get("approved_ids_sha256") != sha256(json.dumps(
                sorted(ids), ensure_ascii=False, separators=(",", ":")).encode("utf-8"))):
        reject("signed evidence does not bind the exact source and scope")
    reviewer = receipt.get("reviewer_id")
    if (not isinstance(reviewer, str) or not reviewer.strip()
            or not isinstance(receipt.get("authority_reference"), str)
            or len(receipt["authority_reference"].strip()) < 6
            or receipt.get("independent_review") is not True
            or any(entry.get("approved_by") != reviewer for entry in entries)):
        reject("independent reviewer provenance missing")
    try:
        first = date.fromisoformat(receipt["valid_from"])
        last = date.fromisoformat(receipt["expires_on"])
    except (KeyError, ValueError, TypeError):
        reject("invalid receipt validity window")
    if first > date.today() or last < date.today() or first > last:
        reject("approval expired or not yet effective")
    try:
        completed = subprocess.run(
            ["openssl", "dgst", "-sha256", "-verify", str(trusted_key_file),
             "-signature", str(signature_file), str(receipt_file)],
            capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        reject("independent signature verification unavailable")
    if completed.returncode != 0 or completed.stdout.strip() != b"Verified OK":
        reject("invalid independent signature")
    # No names, legal text, manifest or signature bytes are emitted.
    return {"preflight": "SIGNED_SCOPE_INPUTS_MATCHED_NOT_RELEASE_APPROVAL",
            "source_sha": source_sha, "target_month": target_month,
            "service_id": service_id, "approved_ids": len(ids),
            "approved_ids_sha256": receipt["approved_ids_sha256"],
            "receipt_sha256": sha256(raw_receipt)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--target-month", required=True)
    p.add_argument("--service-id", required=True, help="Legal service slug")
    p.add_argument("--qa-service-code", required=True, help="Official Q&A classification code")
    p.add_argument("--approvals", required=True, type=Path)
    p.add_argument("--legal", required=True, type=Path)
    p.add_argument("--qa", required=True, type=Path)
    p.add_argument("--qa-meta", required=True, type=Path)
    p.add_argument("--receipt", required=True, type=Path)
    p.add_argument("--signature", required=True, type=Path)
    p.add_argument("--trusted-key", required=True, type=Path)
    p.add_argument("--trusted-key-sha256", required=True)
    p.add_argument("--private-output", type=Path,
                   help="New temporary directory for a candidate; omitted for preflight-only")
    p.add_argument("--preflight-only", action="store_true")
    args = p.parse_args()
    # Reject unknown checkout / branch bait; this is not a source-SHA assertion
    # that can be satisfied merely by passing a command-line value.
    try:
        actual_sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                    capture_output=True, text=True, timeout=10, check=True).stdout.strip()
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        reject("source checkout SHA not verifiable")
    if actual_sha != args.source_sha:
        reject("source checkout mismatch")
    inputs = {"approvals": args.approvals, "legal": args.legal,
              "qa": args.qa, "qa_meta": args.qa_meta}
    report = approve_preflight(
        source_sha=args.source_sha, target_month=args.target_month,
        service_id=args.service_id, qa_service_code=args.qa_service_code, inputs=inputs,
        receipt_file=args.receipt, signature_file=args.signature,
        trusted_key_file=args.trusted_key,
        trusted_key_sha256=args.trusted_key_sha256)
    if args.preflight_only:
        if args.private_output is not None:
            reject("preflight must not create an output")
    else:
        if args.private_output is None:
            reject("missing private temporary output")
        result = scoped.build(args.approvals, args.legal, args.qa,
                              args.qa_meta, args.private_output,
                              target_month=args.target_month,
                              target_service=args.service_id,
                              target_qa_service=args.qa_service_code)
        report.update({"candidate": "PRIVATE_SCOPE_CANDIDATE_ONLY",
                       "files": result["files"], "html": result["html"],
                       "bytes": result["bytes"], "deploy_approved": False})
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as exc:
        # Only diagnostic codes/reasons, not manifest data or source text.
        raise SystemExit(str(exc))
