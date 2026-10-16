"""Fail-closed, evidence-first project continuity controls. No trading decisions.

This file verifies byte-backed handoff manifests and a hash-chained decision journal.
It cannot independently fetch GitHub/Drive, read ChatGPT conversations, or prove a
human/assistant actually considered a document. External checks stay mandatory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

SCHEMA = "XAU-HTF-CONTINUITY/1.2"
EVIDENCE = {"source_registry", "investor_policy", "source_policy", "governance_policy", "research_artifact", "decision_record", "experiment_plan", "result_receipt", "lineage", "code_state", "recovery_receipt"}
REQUIRED = {"source_registry", "investor_policy", "source_policy", "governance_policy", "research_artifact", "decision_record", "lineage", "code_state"}
EVENT_TYPES = {"source_authorization", "experiment_frozen", "checkpoint_verified", "research_result", "decision", "build_verified", "recovery", "blocked", "continuation"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")

class ContinuityBlocked(ValueError):
    pass

def need(flag: bool, message: str) -> None:
    if not flag:
        raise ContinuityBlocked(message)

def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def sha(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None

def verify_contract(m: dict, *, observed_head: str, artifact_root: Path | None = None) -> str:
    """Check a *continuation* contract. Never grants research/trading certification."""
    need(isinstance(m, dict) and m.get("schema") == SCHEMA, "continuity schema mismatch")
    need(m.get("authority_mode") == "original_artifacts_only", "summaries are not research authority")
    need(m.get("research_action") == "continue_existing_research", "new-chat research reset forbidden")
    need(m.get("project") == "independent_XAUUSD_HTF_EA", "project identity changed")
    need(m.get("branch_rule") == "descendant_of_approved_head", "unapproved main/research branch prohibited")
    need(m.get("policy_stack") == ["XAU-HTF-SRC-002", "XAU-HTF-INV-001/1.0", "XAU-HTF-GOV-001/1.0", "XAU-HTF-SYSTEM/1.1", SCHEMA], "governance laws omitted, reordered or superseded without approval")
    code = m.get("code")
    need(isinstance(code, dict), "missing pinned code state")
    for field in ("approved_branch", "approved_head", "parent_verified_head", "rollback_commit", "source_registry_blob_sha"):
        need(isinstance(code.get(field), str) and bool(code[field]), "missing code." + field)
    for field in ("approved_head", "parent_verified_head", "rollback_commit", "source_registry_blob_sha"):
        need(GIT_SHA.fullmatch(code[field]) is not None, "invalid commit/blob SHA: " + field)
    need(observed_head == code["approved_head"], "live GitHub HEAD diverges from frozen handoff")
    need(code["approved_branch"].startswith("carson/htf-"), "unexpected project branch")
    need(code["approved_branch"] != "main" and code["approved_head"] != code["parent_verified_head"], "fresh main/unchanged ancestry blocked")
    need(code.get("ancestry_verification") == "github_parentage_readback", "GitHub ancestry must be checked independently")
    work = m.get("work")
    need(isinstance(work, dict), "missing active research continuation")
    for k in ("last_verified_activity_id", "last_verified_artifact_sha256", "next_build_action", "next_experiment_id", "next_stop_rule", "blocked_items", "completed_work_reference", "current_stage"):
        need(k in work and work[k] is not None, "missing work." + k)
    need(work["current_stage"] in ("governance", "engineering", "research", "validation", "blocked"), "invalid active research stage")
    need(sha(work["last_verified_artifact_sha256"]), "last artifact digest not pinned")
    need(isinstance(work["next_experiment_id"], str) and work["next_experiment_id"].strip(), "missing next experiment ID")
    need(isinstance(work["next_build_action"], str) and work["next_build_action"].strip(), "missing next build action")
    need(isinstance(work["next_stop_rule"], str) and work["next_stop_rule"].strip(), "missing stopping rule")
    need(isinstance(work["blocked_items"], list), "blocked items must be explicit list")
    need(m.get("on_missing_evidence") == "BLOCK_AND_RECOVER_NOT_RESTART", "must fail closed on lost context")
    need(m.get("summaries_can_direct_research") is False, "self summaries may not direct research")
    need(m.get("standalone_candidate_promotion") is False, "whole-system evaluation required")
    need(m.get("uses_previous_research") is True, "must continue prior research")
    need(m.get("source_expansion_allowed") is False, "unauthorized data expansion")
    journal = m.get("journal")
    need(isinstance(journal, dict) and sha(journal.get("head_digest")), "missing pinned journal head")
    need(type(journal.get("event_count")) is int and journal["event_count"] >= 1, "missing prior research event history")
    artifacts = m.get("evidence")
    need(isinstance(artifacts, list) and len(artifacts) >= len(REQUIRED), "too few original artifact references")
    roles = set()
    paths = set()
    for item in artifacts:
        need(isinstance(item, dict), "invalid evidence record")
        role, path = item.get("role"), item.get("path")
        need(role in EVIDENCE, "unrecognized evidence role")
        need(isinstance(path, str) and bool(path) and not Path(path).is_absolute() and ".." not in Path(path).parts, "unsafe/missing local evidence path")
        need(path not in paths, "duplicate evidence path")
        paths.add(path)
        roles.add(role)
        need(sha(item.get("sha256")), "original artifact missing SHA256")
        need(item.get("provenance") in ("approved_drive", "approved_github", "research_output"), "artifact has unapproved provenance")
        need(item.get("authority") == "source_bytes", "narrative summary substituted for source")
        if artifact_root is not None:
            root = artifact_root.resolve(strict=True)
            candidate = (root / path).resolve(strict=True)
            need(candidate.is_relative_to(root) and candidate.is_file(), "unreadable/escaped artifact")
            need(hashlib.sha256(candidate.read_bytes()).hexdigest() == item["sha256"], "evidence hash mismatch: " + path)
    need(REQUIRED <= roles, "mandatory research roles omitted")
    need(m.get("research_history_status") == "preserved_linked_not_condensed", "research history reduced to a summary")
    return digest(m)

def build_event(seq: int, prev: str | None, kind: str, artifact_sha256: str, action: str) -> dict:
    need(type(seq) is int and seq >= 1, "invalid event seq")
    need(kind in EVENT_TYPES, "unrecognized event type")
    need(sha(artifact_sha256), "event needs actual artifact fingerprint")
    need(isinstance(action, str) and action.strip(), "event needs explicit action")
    if seq == 1:
        need(prev is None, "first event must have null parent")
    else:
        need(sha(prev), "event predecessor SHA invalid")
    record = {"seq": seq, "previous_digest": prev, "kind": kind, "artifact_sha256": artifact_sha256, "action": action}
    return {**record, "digest": digest(record)}

def verify_journal(events: list[dict], *, pinned_head: str | None = None, pinned_count: int | None = None) -> str:
    need(isinstance(events, list) and bool(events), "empty research journal")
    prev = None
    for i, event in enumerate(events, 1):
        need(isinstance(event, dict), "malformed journal event")
        want = build_event(i, prev, event.get("kind"), event.get("artifact_sha256"), event.get("action"))
        need(event == want, "research journal altered or continuity broken")
        prev = want["digest"]
    if pinned_head is not None:
        need(prev == pinned_head, "journal differs from frozen external head")
    if pinned_count is not None:
        need(len(events) == pinned_count, "journal length differs from frozen contract")
    return prev

def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement protects from write interruption; external digest anchors
    # must be maintained in Drive/GitHub to detect unauthorized rewritten history.
    fd, tmp = tempfile.mkstemp(prefix=".continuity-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
            f.write("\n")
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def append_event(path: Path, *, expected_head: str | None, kind: str, artifact_sha256: str, action: str) -> dict:
    events = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    if events:
        head = verify_journal(events)
        need(expected_head is not None and head == expected_head, "append requires externally verified current journal head")
    else:
        need(expected_head is None, "new journal cannot silently supersede pinned history")
    event = build_event(len(events) + 1, events[-1]["digest"] if events else None, kind, artifact_sha256, action)
    atomic_json(path, events + [event])
    return {"event": event, "journal_head": event["digest"], "count": len(events) + 1}

def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="XAUUSD evidence-first anti-amnesia continuity gate")
    sub=parser.add_subparsers(dest="command", required=True)
    c=sub.add_parser("check-handoff"); c.add_argument("contract",type=Path); c.add_argument("--observed-head",required=True); c.add_argument("--artifact-root",type=Path)
    j=sub.add_parser("check-journal");j.add_argument("journal",type=Path);j.add_argument("--pinned-head",required=True);j.add_argument("--pinned-count",type=int,required=True)
    a=sub.add_parser("append-event");a.add_argument("journal",type=Path);a.add_argument("--expected-head");a.add_argument("--kind",required=True);a.add_argument("--artifact-sha256",required=True);a.add_argument("--action",required=True)
    opts=parser.parse_args(argv)
    try:
        if opts.command == "check-handoff":
            p=json.loads(opts.contract.read_text(encoding="utf-8")); out={"handoff_sha256":verify_contract(p,observed_head=opts.observed_head,artifact_root=opts.artifact_root)}
        elif opts.command == "check-journal":
            v=json.loads(opts.journal.read_text(encoding="utf-8")); out={"head":verify_journal(v,pinned_head=opts.pinned_head,pinned_count=opts.pinned_count)}
        else:out=append_event(opts.journal,expected_head=opts.expected_head,kind=opts.kind,artifact_sha256=opts.artifact_sha256,action=opts.action)
    except (OSError, ValueError, KeyError, TypeError) as e:
        parser.exit(2, "CONTINUITY BLOCKED: " + str(e) + "\n")
    print(json.dumps({"status":"verified_metadata_and_local_bytes_not_external_research_certification", **out},sort_keys=True));return 0

if __name__=="__main__":
    raise SystemExit(main())
