"""Fail-closed, dependency-free metadata gate for approved XAUUSD research.

Command examples:
  python -m htf_ticklab.research_guard check-plan path/to/plan.json
  python -m htf_ticklab.research_guard check-result plan.json result.json

It cannot verify arbitrary strategy code or prove historical execution; it verifies
formal source and research-protocol constraints before any score is promoted.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .source_registry import REGISTERED

SCHEMA = "XAU-HTF-GOV-001/1.0"
BASELINE_COMMIT = "ca4b58aec597174b6f6d18ab2f36cba6836e4f4c"
R9_COMMIT = "8729a6345655a7b4ea31facc81982004ee2b8921"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
METRIC_FIELDS = (
    "net_profit", "gross_loss", "max_equity_drawdown_pct", "profit_factor",
    "completed_trades", "win_rate", "win_loss_ratio", "margin_calls", "stop_outs",
)

class ResearchGuardError(ValueError):
    """An experiment violates a required governance or source rule."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ResearchGuardError(message)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_text(payload: dict, *names: str) -> None:
    for name in names:
        require(nonempty(payload.get(name)), f"missing nonempty {name}")


def sha256_json(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf8")
    return hashlib.sha256(canonical).hexdigest()


def parse_utc(s: str) -> datetime:
    require(isinstance(s, str) and s.endswith("Z"), "timestamp must be UTC ISO-8601 ending Z")
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ResearchGuardError(f"malformed UTC timestamp: {s}") from exc
    require(t.tzinfo is not None and t.utcoffset().total_seconds() == 0, "UTC timestamp required")
    return t


def check_plan(p: dict) -> str:
    require(isinstance(p, dict), "plan must be an object")
    require(p.get("schema_version") == SCHEMA, "unsupported governance schema")
    require_text(p, "experiment_id", "goal", "hypothesis", "mechanism", "baseline_description",
                 "candidate_change", "causal_feature_contract", "primary_success_criterion",
                 "disconfirming_observation", "ablation", "negative_control",
                 "repair_path", "retirement_condition", "next_ea_milestone")
    require(p.get("instrument") == "XAUUSD", "only XAUUSD is authorized")
    require(p.get("purpose") == "independent_ea_research", "R9-only clone or unrelated research prohibited")
    require(p.get("r9_reference_commit") == R9_COMMIT, "reference R9 SHA changed/unapproved")
    require(p.get("baseline_code_commit") == BASELINE_COMMIT, "unapproved code provenance baseline")
    require(isinstance(p.get("r9_diagnostic_budget"), int) and
            0 <= p["r9_diagnostic_budget"] <= 3, "R9-only diagnostic budget must be 0..3")
    require(p.get("claims_investor_approval") is False, "cannot self-assert investor approval")
    require(p.get("historical_exposure") == "previously_researched_2026",
            "2026 dataset was previously examined; cannot claim untouched holdout")

    sources = p.get("sources")
    require(isinstance(sources, list) and len(sources) > 0, "missing pinned source list")
    brokers: set[str] = set()
    months: dict[str, set[str]] = {"coinexx": set(), "dukascopy": set()}
    seen: set[str] = set()
    for item in sources:
        require(isinstance(item, dict), "source must be an object")
        name, broker, digest = item.get("filename"), item.get("broker"), item.get("sha256")
        require(isinstance(name, str) and name == Path(name).name, "source must be exact basename")
        require(name not in seen, f"duplicate source {name}")
        seen.add(name)
        pin = REGISTERED.get(name)
        require(pin is not None, f"UNAUTHORIZED source: {name}")
        require(broker == pin.broker and digest == pin.sha256,
                f"source identity/hash mismatch: {name}")
        brokers.add(broker)
        match = re.search(r"2026_(\d\d)_ticks", name)
        require(match is not None, f"unrecognized monthly source name {name}")
        months[broker].add(match.group(1))

    requested = p.get("broker_scope")
    require(requested in ("coinexx", "dukascopy", "cross_broker"), "invalid broker scope")
    if requested == "cross_broker":
        require(brokers == {"coinexx", "dukascopy"}, "cross-broker requires both distinct feeds")
        require(months["coinexx"] == months["dukascopy"],
                "cross-broker must use matching source months")
        require(all(1 <= int(m) <= 7 for m in months["coinexx"]),
                "Jan–Jul only for paired cross-broker evaluation")
    else:
        require(brokers == {requested}, "source broker does not match declared scope")

    e = p.get("evaluation")
    require(isinstance(e, dict), "missing evaluation")
    start = parse_utc(e.get("training_end_utc"))
    check = parse_utc(e.get("evaluation_start_utc"))
    require(start <= check, "temporal leakage: evaluation begins before training ends")
    require(e.get("clock_profile") == ("coinexx_2026_nyclose" if "coinexx" in brokers else "dukascopy_native_utc"),
            "clock profile absent or incorrect")
    require(e.get("unregistered_override") is False,
            "fixture/unregistered override prohibited in scored research")
    require(e.get("timeframe_alignment") == "corrected_utc",
            "source/server clock cannot be used for cross-broker bar alignment")
    require(e.get("quote_execution") == "causal_bid_ask",
            "no synthetic/ex-post entry or look-ahead fills allowed")
    require(e.get("reporting") == ["hour", "day", "week", "month"],
            "must report every hour/day/week/month, in that order")
    delays = e.get("latency_scenarios_ms")
    require(isinstance(delays, list) and len(delays) >= 2 and
            all(isinstance(x, int) and x >= 0 for x in delays) and len(set(delays)) == len(delays),
            "need at least two distinct nonnegative latency scenarios")
    if requested == "cross_broker":
        require(e.get("paired_utc_coverage") is True, "must restrict to matched UTC coverage")
    paths = p.get("constructive_paths")
    require(isinstance(paths, list) and len(paths) >= 2,
            "require at least two constructive, distinct paths")
    for i, path in enumerate(paths):
        require(isinstance(path, dict), f"path {i} must be object")
        require_text(path, "mechanism", "testable_prediction", "if_negative_next_action")
    require(len({x["mechanism"].strip().casefold() for x in paths}) >= 2,
            "constructive paths must be different")
    return sha256_json(p)


def check_result(p: dict, result: dict) -> str:
    plan_sha = check_plan(p)
    require(isinstance(result, dict), "result must be object")
    require(result.get("schema_version") == SCHEMA, "unsupported result schema")
    require(result.get("experiment_id") == p["experiment_id"], "experiment mismatch")
    require(result.get("frozen_plan_sha256") == plan_sha,
            "plan mutated after experiment: result references wrong frozen plan hash")
    require(result.get("classification") in ("promising", "negative", "inconclusive", "blocked"),
            "missing transparent classification")
    require(result.get("decision") in ("explore", "revise", "hold", "retire_mechanism"),
            "decision requires explicit bounded next step; no auto investor approval")
    require_text(result, "evidence_summary", "falsification_summary", "next_experiment",
                 "next_milestone", "limits_and_unknowns")
    require(result.get("investor_approved") is False, "no automated investor approval allowed")
    evidence = result.get("artifacts")
    require(isinstance(evidence, list) and len(evidence) >= 1, "no evidence artifact")
    for item in evidence:
        require(isinstance(item, dict) and nonempty(item.get("name")), "artifact requires name")
        require(isinstance(item.get("sha256"), str) and SHA_RE.fullmatch(item["sha256"]) is not None,
                "artifact requires SHA256 fingerprint")
    m = result.get("broker_metrics")
    require(isinstance(m, dict) and len(m) >= 1, "missing broker metrics")
    expected = (set([p["broker_scope"]]) if p["broker_scope"] != "cross_broker"
                else {"coinexx", "dukascopy"})
    require(set(m) == expected, "must report all and only declared brokers")
    for broker, val in m.items():
        require(isinstance(val, dict), f"invalid {broker} metrics")
        for field in METRIC_FIELDS:
            require(field in val, f"missing {broker} metric {field}")
            v = val[field]
            require(v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)),
                    f"invalid metric {broker}.{field}")
        require(isinstance(val["completed_trades"], int) and val["completed_trades"] >= 0,
                "trades must be nonnegative integer")
        require(isinstance(val["margin_calls"], int) and val["margin_calls"] >= 0,
                "margin calls must be counted")
        require(isinstance(val["stop_outs"], int) and val["stop_outs"] >= 0,
                "stop outs must be counted")
    if result["classification"] == "negative":
        require_text(result, "identified_failure_mode", "safe_remediation")
    if result["decision"] == "retire_mechanism":
        require_text(result, "retirement_evidence", "alternative_mechanism")
    require(result.get("includes_all_periods") is True,
            "refuse result that cherry-picks reporting periods")
    require(result.get("trade_survivability_claim") in ("not_certified", "research_only"),
            "cannot certify no live-account ruin from historic result")
    return sha256_json(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="XAUUSD fail-closed source + constructive research gate")
    parser.add_argument("command", choices=("check-plan", "check-result"))
    parser.add_argument("plan", type=Path)
    parser.add_argument("result", type=Path, nargs="?")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf8"))
        if args.command == "check-plan":
            digest = check_plan(plan)
        else:
            require(args.result is not None, "result JSON path required")
            digest = check_result(plan, json.loads(args.result.read_text(encoding="utf8")))
    except (OSError, json.JSONDecodeError, ResearchGuardError) as exc:
        parser.exit(2, f"GOVERNANCE BLOCKED: {exc}\n")
    print(json.dumps({"status": "validated_metadata_not_trading_certification",
                      "schema": SCHEMA, "sha256": digest}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
