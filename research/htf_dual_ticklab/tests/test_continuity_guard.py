"""v1.2 destructive-state, amnesia and source-substitution regression tests."""
import copy
import hashlib
import json

import pytest

from htf_ticklab.continuity_guard import (
    ContinuityBlocked, REQUIRED, SCHEMA, append_event, build_event,
    verify_contract, verify_journal,
)

HEAD = "a" * 40
PARENT = "b" * 40
EVENT_ARTIFACT = "c" * 64


def fixture(tmp_path):
    root = tmp_path / "evidence"
    root.mkdir()
    evidence=[]
    for role in sorted(REQUIRED):
        p=root / f"{role}.txt"
        p.write_text(f"original verified {role} bytes, not a summary", encoding="utf-8")
        evidence.append({"role":role,"path":p.name,
                         "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                         "provenance":"approved_drive" if role != "code_state" else "approved_github",
                         "authority":"source_bytes"})
    e=build_event(1, None, "checkpoint_verified", EVENT_ARTIFACT, "Verify full backtest source checkpoint")
    m={"schema":SCHEMA,"project":"independent_XAUUSD_HTF_EA",
       "authority_mode":"original_artifacts_only","research_action":"continue_existing_research",
       "branch_rule":"descendant_of_approved_head",
       "policy_stack":["XAU-HTF-SRC-002", "XAU-HTF-INV-001/1.0", "XAU-HTF-GOV-001/1.0", "XAU-HTF-SYSTEM/1.1", SCHEMA],
       "code":{"approved_branch":"carson/htf-governance-continuity-v1.2", "approved_head":HEAD,
               "parent_verified_head":PARENT,"rollback_commit":"d"*40,
               "source_registry_blob_sha":"e"*40,
               "ancestry_verification":"github_parentage_readback"},
       "work":{"last_verified_activity_id":"DEV-1", "last_verified_artifact_sha256":EVENT_ARTIFACT,
               "next_build_action":"Implement shared margin arbitrator", "next_experiment_id":"DEV-2",
               "next_stop_rule":"Stop if margin accounting invariants fail",
               "blocked_items":[],"completed_work_reference":"frozen existing receipts",
               "current_stage":"engineering"},
       "on_missing_evidence":"BLOCK_AND_RECOVER_NOT_RESTART",
       "summaries_can_direct_research":False,"standalone_candidate_promotion":False,
       "uses_previous_research":True,"source_expansion_allowed":False,
       "journal":{"head_digest":e["digest"],"event_count":1},
       "research_history_status":"preserved_linked_not_condensed","evidence":evidence}
    return root,m,[e]


def test_full_byte_backed_handoff_passes(tmp_path):
    root,m,e=fixture(tmp_path)
    assert len(verify_contract(m,observed_head=HEAD,artifact_root=root))==64
    assert verify_journal(e,pinned_head=m["journal"]["head_digest"],pinned_count=1)==e[0]["digest"]


def test_anti_summary_directive(tmp_path):
    root,m,_=fixture(tmp_path)
    m["authority_mode"]="assistant_summary"
    with pytest.raises(ContinuityBlocked,match="summaries"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_no_new_research_reset(tmp_path):
    root,m,_=fixture(tmp_path)
    m["research_action"]="start_new_research"
    with pytest.raises(ContinuityBlocked,match="reset"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_prohibition_of_narrative_authority(tmp_path):
    root,m,_=fixture(tmp_path)
    m["evidence"][0]["authority"]="assistant_recap"
    with pytest.raises(ContinuityBlocked,match="summary"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_unchanged_branch_as_parent_rejected(tmp_path):
    root,m,_=fixture(tmp_path)
    m["code"]["parent_verified_head"]=HEAD
    with pytest.raises(ContinuityBlocked,match="unchanged ancestry"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_head_mismatch_blocks(tmp_path):
    root,m,_=fixture(tmp_path)
    with pytest.raises(ContinuityBlocked,match="HEAD diverges"):
        verify_contract(m,observed_head="f"*40,artifact_root=root)


def test_lost_original_artifact_rejected(tmp_path):
    root,m,_=fixture(tmp_path)
    (root / "research_artifact.txt").unlink()
    with pytest.raises(FileNotFoundError):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_substituted_original_bytes_block(tmp_path):
    root,m,_=fixture(tmp_path)
    (root / "research_artifact.txt").write_text("summary of results")
    with pytest.raises(ContinuityBlocked,match="evidence hash mismatch"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_missing_investor_policy_block(tmp_path):
    root,m,_=fixture(tmp_path)
    m["evidence"]=[x for x in m["evidence"] if x["role"]!="investor_policy"]
    with pytest.raises(ContinuityBlocked,match="too few original artifact references|mandatory research roles"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_missing_law_layer_rejected(tmp_path):
    root,m,_=fixture(tmp_path)
    m["policy_stack"].pop(2)
    with pytest.raises(ContinuityBlocked,match="governance laws"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_empty_next_build_rejected(tmp_path):
    root,m,_=fixture(tmp_path)
    m["work"]["next_build_action"]=" "
    with pytest.raises(ContinuityBlocked,match="next build"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_external_journal_head_tamper_detected(tmp_path):
    _,_,e=fixture(tmp_path)
    with pytest.raises(ContinuityBlocked,match="differs from frozen external"):
        verify_journal(e,pinned_head="e"*64,pinned_count=1)


def test_journal_middle_rewrite_detected(tmp_path):
    _,_,e=fixture(tmp_path)
    second=build_event(2,e[0]["digest"],"research_result","f"*64,"Record full-system test")
    bad=copy.deepcopy([e[0],second])
    bad[0]["action"]="lost past research"
    with pytest.raises(ContinuityBlocked,match="journal altered"):
        verify_journal(bad)


def test_journal_duplicate_reorder_detected(tmp_path):
    _,_,e=fixture(tmp_path)
    second=build_event(2,e[0]["digest"],"decision","f"*64,"Proceed with next controlled build")
    with pytest.raises(ContinuityBlocked,match="research journal altered"):
        verify_journal([second,e[0]])


def test_append_event_preserves_existing_ancestry(tmp_path):
    path=tmp_path / "journal.json"
    a=append_event(path,expected_head=None,kind="checkpoint_verified",artifact_sha256="c"*64,action="Verified source record")
    b=append_event(path,expected_head=a["journal_head"],kind="continuation",artifact_sha256="d"*64,action="Resume the prior build")
    assert b["count"]==2
    assert len(json.loads(path.read_text()))==2
    assert verify_journal(json.loads(path.read_text()),pinned_head=b["journal_head"],pinned_count=2)==b["journal_head"]


def test_append_requires_verified_lease(tmp_path):
    p=tmp_path / "journal.json"
    append_event(p,expected_head=None,kind="decision",artifact_sha256="a"*64,action="Preserve decision")
    with pytest.raises(ContinuityBlocked,match="externally verified"):
        append_event(p,expected_head=None,kind="continuation",artifact_sha256="b"*64,action="Cannot overwrite")


def test_new_journal_rejects_phantom_head(tmp_path):
    with pytest.raises(ContinuityBlocked,match="cannot silently supersede"):
        append_event(tmp_path/"none.json",expected_head="a"*64,kind="recovery",artifact_sha256="b"*64,action="False history")


def test_disallow_main_branch(tmp_path):
    root,m,_=fixture(tmp_path)
    m["code"]["approved_branch"]="main"
    with pytest.raises(ContinuityBlocked,match="unexpected project branch"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_no_silent_source_expansion(tmp_path):
    root,m,_=fixture(tmp_path)
    m["source_expansion_allowed"]=True
    with pytest.raises(ContinuityBlocked,match="unauthorized data expansion"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)


def test_whole_system_gating_preserved(tmp_path):
    root,m,_=fixture(tmp_path)
    m["standalone_candidate_promotion"]=True
    with pytest.raises(ContinuityBlocked,match="whole-system evaluation"):
        verify_contract(m,observed_head=HEAD,artifact_root=root)
