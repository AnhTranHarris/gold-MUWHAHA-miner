"""Adversarial whole-system tests: no actual trading results are represented."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from htf_ticklab.research_guard import ResearchGuardError, check_plan
from htf_ticklab.source_registry import REGISTERED
from htf_ticklab.system_guard import (
    SCHEMA, attest_artifacts, scenarios, verify_lineage, verify_system_plan,
    verify_system_result,
)

COIN = "XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz"
DUK = "XAUUSD_DUKAS_2026_01_ticks.csv.gz"
BASE="ca4b58aec597174b6f6d18ab2f36cba6836e4f4c"
CHANGED="b"*40


def original_plan():
    return json.loads((Path(__file__).parent.parent / 'governance/EXPERIMENT_PLAN_EXAMPLE.json').read_text())


def lineage():
    src = lambda key, name: {"id":key, "kind":"source", "parents":[],"filename":name,
                              "broker":REGISTERED[name].broker,"sha256":REGISTERED[name].sha256}
    node=lambda id,kind,parents: {"id":id,"kind":kind,"parents":parents,
                                  "artifact_sha256":"a"*64, "code_commit":BASE}
    return {"schema":SCHEMA,"nodes":[
        src("coinexx",COIN),src("dukascopy",DUK),
        node("utc", "transform",["coinexx","dukascopy"]),
        node("mechanism","hypothesis",["utc"]),
        node("test","experiment",["mechanism"]),
        node("res","result",["test"]),
        node("gate","decision",["res"]),
        node("ea","build",["gate"])]}


def plan():
    p1 = original_plan(); line = lineage()
    bp=["SESSION_ROUTER_V1","SHARED_RISK_V1"]
    cp=["SESSION_ROUTER_V2","SHARED_RISK_V1"]
    p={"schema":SCHEMA,"experiment_id":p1["experiment_id"],
       "v1_plan_sha256":check_plan(p1),"lineage_sha256":verify_lineage(line),
       "baseline_system_commit":BASE,"candidate_system_commit":CHANGED,
       "baseline_components":bp,"candidate_components":cp,
       "comparison_unit":"complete_account_portfolio",
       "execution_accounting":"shared_margin_shared_cash_chronological",
       "baseline_candidate_same_source_windows":True,
       "baseline_candidate_same_cost_model":True,
       "required_scenarios":sorted(scenarios(p1)),
       "investor_mandate":"XAU-HTF-INV-001 v1.0","investor_weights":None,
       "research_stage":"integrated_research_only",
       "system_mechanism":"Session router selects signals from two groups using completed bars.",
       "interaction_risk":"An active trade may block a second entry via shared margin constraints.",
       "reason_for_integration":"Reduced adverse session exposure and better account survivability.",
       "component_ablation":"Compare full EA versions with/without the router, not profits added.",
       "next_build_milestone":"Integrate conditional routing into independently built HTF EA.",
       "success_measure":"Greater full account survival and stable after-cost performance.",
       "negative_path":"Try different session-exposure allocation with unchanged costs."}
    return p1,line,p


def metrics(net=20,dd=5,ruin=0):
    return {"net_profit":net,"gross_loss":12,"max_equity_drawdown_pct":dd,
            "max_equity_drawdown_usd":5, "profit_factor":1.8,
            "completed_trades":40,"win_rate":0.6,"win_loss_ratio":1.5,
            "margin_calls":0,"stop_outs":0,"ruin_events":ruin,
            "positive_days":2,"negative_days":1,"positive_weeks":1,"negative_weeks":0,
            "positive_months":1,"negative_months":0,"positive_eligible_hours":9,
            "eligible_hours":15,"volume_days_in_band":0,"active_days":3}


def result(v1,p,line):
    records={}
    for key in p["required_scenarios"]:
        records[key]={"baseline_components":p["baseline_components"],
                      "candidate_components":p["candidate_components"],
                      "input_digest":"c"*64,"execution_config_digest":"d"*64,
                      "period_coverage":"all_eligible_intervals",
                      "baseline":{**metrics(net=20),"run_artifact_sha256":"e"*64,
                                  "trade_ledger_sha256":"f"*64},
                      "candidate":{**metrics(net=21),"run_artifact_sha256":"1"*64,
                                   "trade_ledger_sha256":"2"*64}}
    return {"schema":SCHEMA,"experiment_id":p["experiment_id"],
            "frozen_system_plan_sha256":verify_system_plan(v1,p,line),
            "evaluation_scope":"whole_integrated_EA","status":"research_only",
            "investor_approved":False,"live_ready":False,"scenarios":records,
            "independent_component_diagnostics_used_for_promotion":False,
            "interaction_findings":"Simulated accounting shares margin across candidate subsystems.",
            "constructive_next_step":"Verify at longer execution delays and try S30 filter.",
            "proposed_decision":"advance_integrated_research",
            "continuation":{"next_experiment_id":"HTF-0002-v1",
                            "next_build_action":"Implement S30 state gating within shared risk engine.",
                            "stopping_rule":"Retire after three independent full-system tests show no utility.",
                            "if_negative_option":"Investigate execution expiry.",
                            "if_positive_option":"Validate on the other broker and further lag scenarios.",
                            "recovery_link":"Drive experiment archive file ID to be filled upon actual results.",
                            "handoff_sha256":"a"*64}}


def blocked(fn, phrase):
    with pytest.raises(ResearchGuardError,match=phrase):fn()


def test_lineage_complete():
    assert len(verify_lineage(lineage()))==64

def test_lineage_reject_unapproved_source():
    g=lineage(); g["nodes"][0]["filename"]="FOREIGN.csv.gz"
    blocked(lambda:verify_lineage(g),"foreign/unverified")

def test_lineage_reject_missing_parent():
    g=lineage();g["nodes"][-1]["parents"]=["gone"]
    blocked(lambda:verify_lineage(g),"missing parent")

def test_lineage_reject_cycle():
    g=lineage();g["nodes"][3]["parents"]=["mechanism"]
    blocked(lambda:verify_lineage(g),"lineage cycle")

def test_lineage_reject_duplicate_ids():
    g=lineage();g["nodes"].append(copy.deepcopy(g["nodes"][0]))
    blocked(lambda:verify_lineage(g),"duplicate/empty")

def test_lineage_reject_no_result():
    g=lineage();g["nodes"]=[x for x in g["nodes"] if x["kind"]!="result"]
    blocked(lambda:verify_lineage(g),"missing parent|invalid lineage edge")

def test_plan_complete():
    v,l,p=plan(); assert len(verify_system_plan(v,p,l))==64

def test_plan_reject_component_only():
    v,l,p=plan();p["comparison_unit"]="candidate_standalone"
    blocked(lambda:verify_system_plan(v,p,l),"single candidate")

def test_plan_reject_fake_profit_sum():
    v,l,p=plan();p["execution_accounting"]="sum_of_standalone_results"
    blocked(lambda:verify_system_plan(v,p,l),"cannot be summed")

def test_plan_reject_different_windows():
    v,l,p=plan();p["baseline_candidate_same_source_windows"]=False
    blocked(lambda:verify_system_plan(v,p,l),"share source windows")

def test_plan_reject_unfair_cost_model():
    v,l,p=plan();p["baseline_candidate_same_cost_model"]=False
    blocked(lambda:verify_system_plan(v,p,l),"execution-cost")

def test_plan_reject_missing_capital_or_broker_scenario():
    v,l,p=plan();p["required_scenarios"].pop()
    blocked(lambda:verify_system_plan(v,p,l),"missing broker/capital/latency")

def test_plan_reject_duplicate_scenario():
    v,l,p=plan();p["required_scenarios"].append(p["required_scenarios"][0])
    blocked(lambda:verify_system_plan(v,p,l),"duplicate scenarios")

def test_plan_reject_arbitrary_investor_weight():
    v,l,p=plan();p["investor_weights"]={"net":.9}
    blocked(lambda:verify_system_plan(v,p,l),"unapproved weights")

def test_plan_reject_no_build_change():
    v,l,p=plan();p["candidate_components"]=p["baseline_components"]
    blocked(lambda:verify_system_plan(v,p,l),"identical/duplicate")

def test_plan_reject_modified_lineage():
    v,l,p=plan();l["nodes"][4]["artifact_sha256"]="b"*64
    blocked(lambda:verify_system_plan(v,p,l),"lineage digest mismatch")

def test_result_complete():
    v,l,p=plan();a=verify_system_result(v,p,l,result(v,p,l))
    assert a["scenarios_checked"]==12 and a["risk_breaches"]==[]

def test_result_reject_standalone_promotion():
    v,l,p=plan();r=result(v,p,l);r["independent_component_diagnostics_used_for_promotion"]=True
    blocked(lambda:verify_system_result(v,p,l,r),"standalone candidate")

def test_result_reject_missing_broker_scenario():
    v,l,p=plan();r=result(v,p,l);r["scenarios"].pop(next(iter(r["scenarios"])))
    blocked(lambda:verify_system_result(v,p,l,r),"incomplete whole-EA")

def test_result_reject_cherry_picking():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["period_coverage"]="winners_only"
    blocked(lambda:verify_system_result(v,p,l,r),"cherry-picked")

def test_result_reject_decorrelated_components():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["baseline_components"]=["OTHER"]
    blocked(lambda:verify_system_result(v,p,l,r),"component mix mismatch")

def test_result_reject_undisclosed_margin_calls():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["candidate"]["margin_calls"]=1
    blocked(lambda:verify_system_result(v,p,l,r),"survivability breach")

def test_result_reject_account_ruin():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["candidate"]["ruin_events"]=1
    blocked(lambda:verify_system_result(v,p,l,r),"survivability breach")

def test_result_reject_no_system_improvement():
    v,l,p=plan();r=result(v,p,l)
    for record in r["scenarios"].values():record["candidate"]["net_profit"]=20
    blocked(lambda:verify_system_result(v,p,l,r),"no paired system-level improvement")

def test_result_reject_self_certification():
    v,l,p=plan();r=result(v,p,l);r["investor_approved"]=True
    blocked(lambda:verify_system_result(v,p,l,r),"self-certification")

def test_result_reject_forged_plan_hash():
    v,l,p=plan();r=result(v,p,l);r["frozen_system_plan_sha256"]="0"*64
    blocked(lambda:verify_system_result(v,p,l,r),"system plan mutated")

def test_result_reject_missing_portfolio_metric():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["baseline"].pop("max_equity_drawdown_pct")
    blocked(lambda:verify_system_result(v,p,l,r),"missing")

def test_result_reject_nan():
    v,l,p=plan();r=result(v,p,l);next(iter(r["scenarios"].values()))["candidate"]["net_profit"]=float("nan")
    blocked(lambda:verify_system_result(v,p,l,r),"invalid")

def test_result_safely_records_negative_research():
    v,l,p=plan();r=result(v,p,l)
    r["status"]="requires_repair";r["proposed_decision"]="repair"
    for rec in r["scenarios"].values():rec["candidate"]["net_profit"]=-10
    assert verify_system_result(v,p,l,r)["improvement_scenarios"]==0

def test_artifact_attestation_real_hash(tmp_path):
    p=tmp_path/"proof.json";p.write_text("{}")
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    assert attest_artifacts(tmp_path,[{"path":"proof.json","sha256":h}])["artifacts_verified"]==1

def test_artifact_attestation_reject_renamed_content(tmp_path):
    p=tmp_path/"proof.json";p.write_text("old")
    h=hashlib.sha256(p.read_bytes()).hexdigest();p.write_text("new")
    blocked(lambda:attest_artifacts(tmp_path,[{"path":"proof.json","sha256":h}]),"mismatch")

def test_artifact_attestation_reject_path_escape(tmp_path):
    outside=tmp_path.parent/"outside.txt";outside.write_text("do not accept")
    try:
        blocked(lambda:attest_artifacts(tmp_path,[{"path":"../outside.txt","sha256":hashlib.sha256(outside.read_bytes()).hexdigest()}]),"escapes")
    finally: outside.unlink()


def test_result_reject_missing_handoff():
    v,l,p=plan();r=result(v,p,l);r["continuation"].pop("handoff_sha256")
    blocked(lambda:verify_system_result(v,p,l,r),"missing hashed continuation")


def test_result_reject_repeating_same_experiment():
    v,l,p=plan();r=result(v,p,l);r["continuation"]["next_experiment_id"]=p["experiment_id"]
    blocked(lambda:verify_system_result(v,p,l,r),"anti-loop")


def test_result_reject_missing_build_step():
    v,l,p=plan();r=result(v,p,l);r["continuation"]["next_build_action"]=""
    blocked(lambda:verify_system_result(v,p,l,r),"missing continuation")


def test_synergy_claim_requires_four_integrated_arms():
    v,l,p=plan();r=result(v,p,l);r["interaction_claimed"]=True
    blocked(lambda:verify_system_result(v,p,l,r),"synergy claims require four")


def test_synergy_rejects_four_arms_with_identical_component_mix():
    v,l,p=plan();r=result(v,p,l);r["interaction_claimed"]=True
    for rec in r["scenarios"].values():
        rec["interaction_arms"]={key:{"components":["SAME"],"metrics":metrics(),
                 "run_artifact_sha256":"3"*64,"trade_ledger_sha256":"4"*64}
                 for key in ("base","with_A","with_B","with_A_and_B")}
    blocked(lambda:verify_system_result(v,p,l,r),"four different EA builds")


def test_paired_delta_only_across_independent_scenarios():
    v,l,p=plan();r=result(v,p,l)
    observed=verify_system_result(v,p,l,r)
    assert observed["paired_net_delta_range_usd"]==[1,1]
    assert observed["paired_equity_drawdown_pct_delta_range"]==[0,0]
