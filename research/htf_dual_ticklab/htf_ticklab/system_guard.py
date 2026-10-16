"""Whole-EA evaluation and research-lineage interlocks, additive to v1.0 guard.

The checks validate evidence envelopes, comparison completeness, lineage and
survivability. They cannot establish that a replay/portfolio ledger is genuine;
promotion remains human-reviewed and is never investor/live certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .research_guard import ResearchGuardError, check_plan, sha256_json
from .source_registry import REGISTERED

SCHEMA = "XAU-HTF-SYSTEM/1.1"
KINDS = {"source", "transform", "hypothesis", "experiment", "result", "decision", "build"}
EDGES = {
    "source": set(), "transform": {"source", "transform"},
    "hypothesis": {"source", "transform", "hypothesis"},
    "experiment": {"hypothesis", "transform"},
    "result": {"experiment"}, "decision": {"result"}, "build": {"decision"},
}
REQUIRED_METRICS = (
    "net_profit", "gross_loss", "max_equity_drawdown_pct", "max_equity_drawdown_usd",
    "profit_factor", "completed_trades", "win_rate", "win_loss_ratio",
    "margin_calls", "stop_outs", "ruin_events", "positive_days", "negative_days",
    "positive_weeks", "negative_weeks", "positive_months", "negative_months",
    "positive_eligible_hours", "eligible_hours", "volume_days_in_band", "active_days",
)
COUNT_FIELDS = {
    "completed_trades", "margin_calls", "stop_outs", "ruin_events", "positive_days",
    "negative_days", "positive_weeks", "negative_weeks", "positive_months",
    "negative_months", "positive_eligible_hours", "eligible_hours", "volume_days_in_band", "active_days",
}
HASH_FIELDS = ("input_digest", "execution_config_digest", "run_artifact_sha256", "trade_ledger_sha256")


def need(predicate: bool, message: str) -> None:
    if not predicate:
        raise ResearchGuardError(message)


def sha(text: Any) -> bool:
    return isinstance(text, str) and len(text) == 64 and all(c in '0123456789abcdef' for c in text)


def git_sha(text: Any) -> bool:
    return isinstance(text, str) and len(text) == 40 and all(c in '0123456789abcdef' for c in text)


def verify_lineage(graph: dict) -> str:
    """Reject orphan records, foreign source datasets, cycles, and broken ancestry."""
    need(isinstance(graph, dict) and graph.get("schema") == SCHEMA, "lineage schema")
    nodes = graph.get("nodes")
    need(isinstance(nodes, list) and nodes, "lineage nodes absent")
    by_id = {}
    for node in nodes:
        need(isinstance(node, dict), "lineage node must be object")
        ident, kind = node.get("id"), node.get("kind")
        need(isinstance(ident, str) and ident and ident not in by_id, "duplicate/empty lineage id")
        need(kind in KINDS, "unknown lineage kind")
        parents = node.get("parents")
        need(isinstance(parents, list) and len(parents) == len(set(parents)), "duplicate/invalid parent links")
        if kind == "source":
            need(parents == [], "source nodes cannot have parents")
            spec = REGISTERED.get(node.get("filename"))
            need(spec is not None and node.get("broker") == spec.broker and node.get("sha256") == spec.sha256,
                 "foreign/unverified lineage source")
        else:
            need(bool(parents), f"orphan lineage node {ident}")
            need(sha(node.get("artifact_sha256")), "lineage artifact SHA256 required")
            need(git_sha(node.get("code_commit")), "lineage code SHA required")
        by_id[ident] = node
    visiting, visited = set(), set()
    def ancestors(ident):
        need(ident in by_id, f"missing ancestor {ident}")
        need(ident not in visiting, "lineage cycle")
        if ident in visited:
            return
        visiting.add(ident)
        node = by_id[ident]
        for pid in node["parents"]:
            need(pid in by_id, f"missing parent {pid}")
            need(by_id[pid]["kind"] in EDGES[node["kind"]], "invalid lineage edge")
            ancestors(pid)
        visiting.remove(ident)
        visited.add(ident)
    for ident in by_id: ancestors(ident)
    need(any(n["kind"] == "source" for n in nodes), "no authorized source ancestor")
    need(any(n["kind"] == "build" for n in nodes), "no implementable EA build lineage")
    need(any(n["kind"] == "result" for n in nodes), "no research result lineage")
    # Every build must reach at least one source through documented causal lineage.
    def roots(ident):
        n = by_id[ident]
        return {ident} if n["kind"] == "source" else set().union(*(roots(p) for p in n["parents"]))
    for node in nodes:
        if node["kind"] == "build":
            need(bool(roots(node["id"])), "build does not descend from authorized source")
    return sha256_json(graph)


def scenarios(v1_plan: dict):
    evaluation = v1_plan["evaluation"]
    delays = evaluation["latency_scenarios_ms"]
    brokers = (["coinexx", "dukascopy"] if v1_plan["broker_scope"] == "cross_broker"
               else [v1_plan["broker_scope"]])
    return {f"{b}|{capital}|{ms}" for b in brokers for capital in (100, 200) for ms in delays}


def verify_system_plan(v1_plan: dict, p: dict, lineage: dict) -> str:
    v1_sha = check_plan(v1_plan)
    line_sha = verify_lineage(lineage)
    need(isinstance(p, dict) and p.get("schema") == SCHEMA, "system plan schema")
    need(p.get("experiment_id") == v1_plan["experiment_id"], "experiment identity changed")
    need(p.get("v1_plan_sha256") == v1_sha, "frozen v1 plan mismatch")
    need(p.get("lineage_sha256") == line_sha, "lineage digest mismatch")
    need(git_sha(p.get("baseline_system_commit")) and git_sha(p.get("candidate_system_commit")),
         "missing full-system commit")
    need(p["baseline_system_commit"] != p["candidate_system_commit"], "same system commit")
    base, new = p.get("baseline_components"), p.get("candidate_components")
    need(isinstance(base, list) and isinstance(new, list) and base and new,
         "full EA component composition required")
    need(all(isinstance(x,str) and x.strip() for x in base + new), "empty component")
    need(len(set(base)) == len(base) and len(set(new)) == len(new) and base != new,
         "identical/duplicate component composition")
    need(p.get("comparison_unit") == "complete_account_portfolio", "single candidate evaluation prohibited")
    need(p.get("execution_accounting") == "shared_margin_shared_cash_chronological",
         "independent strategy profits cannot be summed")
    need(p.get("baseline_candidate_same_source_windows") is True,
         "baseline/candidate must share source windows")
    need(p.get("baseline_candidate_same_cost_model") is True,
         "baseline/candidate must share execution-cost assumptions")
    need(set(p.get("required_scenarios", [])) == scenarios(v1_plan), "missing broker/capital/latency scenario")
    need(len(p["required_scenarios"]) == len(set(p["required_scenarios"])), "duplicate scenarios")
    need(p.get("investor_mandate") == "XAU-HTF-INV-001 v1.0", "investor mandate identity")
    need(p.get("investor_weights") is None, "unapproved weights must remain null")
    need(p.get("research_stage") == "integrated_research_only", "no direct live/demo certification")
    for key in ("system_mechanism", "interaction_risk", "reason_for_integration",
                "component_ablation", "next_build_milestone", "success_measure", "negative_path"):
        need(isinstance(p.get(key),str) and bool(p[key].strip()), "missing system field "+key)
    return sha256_json(p)


def verify_metrics(m: dict, label: str) -> None:
    need(isinstance(m, dict), f"missing whole-EA metrics {label}")
    for name in REQUIRED_METRICS:
        need(name in m, f"missing {label}.{name}")
        val = m[name]
        need(val is None or (type(val) in (int,float) and math.isfinite(val)),
             f"invalid {label}.{name}")
        if name in COUNT_FIELDS:
            need(type(val) is int and val >= 0, f"invalid count {label}.{name}")
    for name in ("margin_calls", "stop_outs", "ruin_events"):
        need(m[name] >= 0, "negative risk incidents")
    need(m["eligible_hours"] >= m["positive_eligible_hours"], "invalid hourly result")
    need(m["active_days"] >= m["volume_days_in_band"], "invalid volume-day result")
    need(m["max_equity_drawdown_pct"] is not None and m["max_equity_drawdown_pct"] >= 0,
         "missing equity drawdown")
    need(m["gross_loss"] is not None and m["gross_loss"] >= 0, "gross loss magnitude required")


def verify_system_result(v1_plan: dict, plan: dict, lineage: dict, result: dict) -> dict:
    plan_sha = verify_system_plan(v1_plan,plan,lineage)
    need(isinstance(result,dict) and result.get("schema") == SCHEMA, "result schema")
    need(result.get("experiment_id") == plan["experiment_id"] and
         result.get("frozen_system_plan_sha256") == plan_sha, "system plan mutated")
    need(result.get("evaluation_scope") == "whole_integrated_EA", "candidate-only result prohibited")
    need(result.get("status") in ("research_only", "requires_repair", "inconclusive"),
         "automatic investor approval forbidden")
    need(result.get("investor_approved") is False and result.get("live_ready") is False,
         "self-certification forbidden")
    records = result.get("scenarios")
    need(isinstance(records,dict) and set(records) == set(plan["required_scenarios"]),
         "incomplete whole-EA scenario matrix")
    improvements, risk_breaches, net_deltas, dd_deltas = 0, [], [], []
    synergy = result.get("interaction_claimed", False)
    need(type(synergy) is bool, "invalid interaction flag")
    for key, record in records.items():
        need(isinstance(record,dict),"bad scenario record")
        need(record.get("baseline_components") == plan["baseline_components"] and
             record.get("candidate_components") == plan["candidate_components"],
             f"component mix mismatch {key}")
        for sha_key in HASH_FIELDS:
            if sha_key == "run_artifact_sha256" or sha_key == "trade_ledger_sha256":
                for arm in ("baseline","candidate"):
                    need(sha(record.get(arm,{}).get(sha_key)), f"missing {arm} evidence digest {key}")
            else:
                need(sha(record.get(sha_key)), f"missing equal-condition digest {key}.{sha_key}")
        b,c = record.get("baseline"),record.get("candidate")
        verify_metrics(b, key+".baseline");verify_metrics(c,key+".candidate")
        need(record.get("period_coverage") == "all_eligible_intervals",
             "cherry-picked period "+key)
        net_deltas.append(c["net_profit"] - b["net_profit"])
        dd_deltas.append(c["max_equity_drawdown_pct"] - b["max_equity_drawdown_pct"])
        if synergy:
            arms = record.get("interaction_arms")
            needed = {"base", "with_A", "with_B", "with_A_and_B"}
            need(isinstance(arms, dict) and set(arms) == needed,
                 "synergy claims require four real integrated system arms")
            signatures = []
            for label, arm in arms.items():
                need(isinstance(arm, dict), "invalid synergy arm")
                parts=arm.get("components")
                need(isinstance(parts,list) and parts, "synergy arm components missing")
                signatures.append(tuple(parts))
                verify_metrics(arm.get("metrics"), key+"."+label)
                need(sha(arm.get("run_artifact_sha256")) and sha(arm.get("trade_ledger_sha256")),
                     "synergy claims need separate whole-account replay evidence")
            need(len(set(signatures)) == 4, "synergy arms must represent four different EA builds")
            need(arms["base"]["components"] == plan["baseline_components"] and
                 arms["with_A_and_B"]["components"] == plan["candidate_components"],
                 "synergy arms must connect to baseline and candidate")
        if any(c[k] != 0 for k in ("margin_calls","stop_outs","ruin_events")):
            risk_breaches.append(key)
        if c["net_profit"] > b["net_profit"] or c["gross_loss"] < b["gross_loss"] or \
           c["max_equity_drawdown_pct"] < b["max_equity_drawdown_pct"]:
            improvements += 1
    need(result.get("independent_component_diagnostics_used_for_promotion") is False,
         "standalone candidate metric cannot grant promotion")
    need(isinstance(result.get("interaction_findings"),str) and result["interaction_findings"].strip(),
         "missing whole-system interaction findings")
    need(isinstance(result.get("constructive_next_step"),str) and result["constructive_next_step"].strip(),
         "missing constructive continuation")
    continuation = result.get("continuation")
    need(isinstance(continuation, dict), "continuation receipt is mandatory")
    for field in ("next_experiment_id", "next_build_action", "stopping_rule",
                  "if_negative_option", "if_positive_option", "recovery_link"):
        need(isinstance(continuation.get(field), str) and continuation[field].strip(),
             "missing continuation." + field)
    need(continuation["next_experiment_id"] != plan["experiment_id"],
         "must version the next experiment (anti-loop)")
    need(sha(continuation.get("handoff_sha256")), "missing hashed continuation handoff")
    if result.get("proposed_decision") == "advance_integrated_research":
        need(not risk_breaches, "survivability breach prevents advancing")
        need(improvements > 0, "no paired system-level improvement")
        need(result["status"] == "research_only", "promotion is research-only")
    else:
        need(result.get("proposed_decision") in ("repair", "hold", "retire_component"),
             "invalid system decision")
    return {"status":"validated_metadata_not_backtest_certification", "plan_sha256":plan_sha,
            "result_sha256":sha256_json(result), "scenarios_checked":len(records),
            "improvement_scenarios":improvements,"risk_breaches":risk_breaches,
            "paired_net_delta_range_usd":[min(net_deltas),max(net_deltas)],
            "paired_equity_drawdown_pct_delta_range":[min(dd_deltas),max(dd_deltas)],
            "note":"Ranges across independent scenario comparisons; never pooled broker returns."}


def attest_artifacts(root: Path, artifacts: list[dict]) -> dict:
    """Content-based evidence proof; designed to fail closed for missing/changed artifacts."""
    root = root.resolve(strict=True)
    need(bool(artifacts) and isinstance(artifacts,list), "missing artifact manifest")
    for artifact in artifacts:
        name, digest = artifact.get("path"), artifact.get("sha256")
        need(isinstance(name,str) and name and sha(digest), "invalid artifact record")
        target = (root / name).resolve(strict=True)
        need(target.is_relative_to(root) and target.is_file(), "artifact path escapes declared root")
        need(hashlib.sha256(target.read_bytes()).hexdigest() == digest, "artifact SHA256 mismatch")
    return {"artifacts_verified":len(artifacts),"status":"content_verified_not_market_certification"}


def main(argv=None):
    ap=argparse.ArgumentParser(description="Whole EA lineage and paired-system research guard")
    subs=ap.add_subparsers(dest="command",required=True)
    lp=subs.add_parser("check-lineage");lp.add_argument("lineage",type=Path)
    pp=subs.add_parser("check-system-plan")
    pp.add_argument("v1_plan",type=Path);pp.add_argument("system_plan",type=Path);pp.add_argument("lineage",type=Path)
    rp=subs.add_parser("check-system-result")
    for arg in ("v1_plan","system_plan","lineage","system_result"):
        rp.add_argument(arg,type=Path)
    ea=subs.add_parser("attest-artifacts");ea.add_argument("root",type=Path);ea.add_argument("manifest",type=Path)
    args=ap.parse_args(argv)
    try:
        data=lambda path:json.loads(path.read_text(encoding="utf8"))
        if args.command=="check-lineage":out={"lineage_sha256":verify_lineage(data(args.lineage))}
        elif args.command=="check-system-plan":
            out={"system_plan_sha256":verify_system_plan(data(args.v1_plan),data(args.system_plan),data(args.lineage))}
        elif args.command=="check-system-result":
            out=verify_system_result(data(args.v1_plan),data(args.system_plan),data(args.lineage),data(args.system_result))
        else:out=attest_artifacts(args.root,data(args.manifest))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        ap.exit(2,f"WHOLE-SYSTEM GOVERNANCE BLOCKED: {exc}\n")
    print(json.dumps(out,sort_keys=True));return 0

if __name__=="__main__":raise SystemExit(main())
