"""Fail-closed research process regression tests (no third-party market data)."""
import copy
import json
import pytest

from htf_ticklab.research_guard import (
    BASELINE_COMMIT, R9_COMMIT, SCHEMA, ResearchGuardError,
    check_plan, check_result,
)
from htf_ticklab.source_registry import REGISTERED


def plan():
    names = ["XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz", "XAUUSD_DUKAS_2026_01_ticks.csv.gz"]
    return {
        "schema_version": SCHEMA, "experiment_id": "HTF-0001-v1",
        "instrument": "XAUUSD", "purpose": "independent_ea_research",
        "goal": "Improve post-cost survivability and entry timing with completed S15 bars.",
        "hypothesis": "Low-spread S15 continuation may improve executable signals.",
        "mechanism": "A spread-aware S15 state with completed M5 volatility filter.",
        "baseline_description": "Same feeds/dates, no-trade control and existing impulse demo.",
        "candidate_change": "Gate candidate entries using completed S15 impulse and quoted spread.",
        "causal_feature_contract": "Bar close only on next tick; only current and prior quotes.",
        "primary_success_criterion": "Improves profit and survival relative to same-period baseline.",
        "disconfirming_observation": "Net expectancy declines under 250ms/1000ms delay.",
        "ablation": "Remove completed S15 state, preserving costs and sample.",
        "negative_control": "Randomize signal labels on training period only.",
        "repair_path": "Investigate expiry of delayed entries with cost caps.",
        "retirement_condition": "Multiple causal paired-broker tests negative after predeclared improvements.",
        "next_ea_milestone": "Test a new minimal non-R9 signal subsystem.",
        "r9_reference_commit": R9_COMMIT, "baseline_code_commit": BASELINE_COMMIT,
        "r9_diagnostic_budget": 1, "claims_investor_approval": False,
        "historical_exposure": "previously_researched_2026", "broker_scope": "cross_broker",
        "sources": [{"filename": n, "broker": REGISTERED[n].broker, "sha256": REGISTERED[n].sha256} for n in names],
        "evaluation": {"training_end_utc": "2026-01-15T00:00:00Z",
                       "evaluation_start_utc": "2026-01-16T00:00:00Z",
                       "clock_profile": "coinexx_2026_nyclose", "paired_utc_coverage": True,
                       "timeframe_alignment": "corrected_utc", "quote_execution": "causal_bid_ask",
                       "unregistered_override": False,
                       "latency_scenarios_ms": [0, 250, 1000],
                       "reporting": ["hour", "day", "week", "month"]},
        "constructive_paths": [
            {"mechanism": "S15 continuation", "testable_prediction": "Fewer stale entries", "if_negative_next_action": "Try S30 timing"},
            {"mechanism": "Execution veto", "testable_prediction": "Fewer slippage losses", "if_negative_next_action": "Test spread quantiles"},
        ],
    }


def result(p):
    return {"schema_version": SCHEMA, "experiment_id": p["experiment_id"],
            "frozen_plan_sha256": check_plan(p), "classification": "negative",
            "decision": "revise", "evidence_summary": "All dates and both broker scenarios reported.",
            "falsification_summary": "Costs dominate in adverse execution.",
            "next_experiment": "Shorter signal expiry without additional future data.",
            "next_milestone": "Better independent-EA signal feasibility.",
            "limits_and_unknowns": "Historical demo fill models not verified.",
            "identified_failure_mode": "Latency and spread degrade entry.",
            "safe_remediation": "Spread veto and latency budget.",
            "investor_approved": False, "includes_all_periods": True,
            "trade_survivability_claim": "research_only",
            "artifacts": [{"name": "results.json", "sha256": "a" * 64}],
            "broker_metrics": {broker: {"net_profit": -1.0, "gross_loss": 2.0,
                        "max_equity_drawdown_pct": 5.0, "profit_factor": 0.5,
                        "completed_trades": 10, "win_rate": 0.4, "win_loss_ratio": 0.667,
                        "margin_calls": 0, "stop_outs": 0}
                       for broker in ("coinexx", "dukascopy")}}


def blocked(p, phrase):
    with pytest.raises(ResearchGuardError, match=phrase): check_plan(p)


def test_valid_plan_receipt():
    p = plan()
    assert len(check_plan(p)) == 64
    assert len(check_result(p, result(p))) == 64


def test_reject_other_market_file_even_when_same_filename_pattern():
    p=plan(); p["sources"][0]["filename"]="XAUUSD_MT5_BROKER_2026_10_ticks_ALL.csv.gz"
    blocked(p,"UNAUTHORIZED")


def test_reject_corrupted_hash():
    p=plan(); p["sources"][1]["sha256"] = "f"*64
    blocked(p,"source identity/hash mismatch")


def test_reject_wrong_broker():
    p=plan(); p["sources"][1]["broker"]="coinexx"
    blocked(p,"source identity/hash mismatch")


def test_reject_missing_second_broker():
    p=plan(); p["sources"]=p["sources"][:1]
    blocked(p,"cross-broker requires")


def test_reject_mismatched_months():
    p=plan(); n="XAUUSD_DUKAS_2026_02_ticks.csv.gz"
    p["sources"][1] = {"filename":n,"broker":"dukascopy","sha256":REGISTERED[n].sha256}
    blocked(p,"matching source months")


def test_reject_bad_utc_profile():
    p=plan();p["evaluation"]["clock_profile"]="raw"
    blocked(p,"clock profile")


def test_reject_override():
    p=plan();p["evaluation"]["unregistered_override"]=True
    blocked(p,"override")


def test_reject_lookahead_engine():
    p=plan();p["evaluation"]["quote_execution"]="synthetic_hindsight"
    blocked(p,"no synthetic")


def test_reject_temporal_leakage():
    p=plan();p["evaluation"]["evaluation_start_utc"]="2026-01-01T00:00:00Z"
    blocked(p,"temporal leakage")


def test_reject_false_untouched_holdout():
    p=plan();p["historical_exposure"]="unseen"
    blocked(p,"previously examined")


def test_reject_prove_fail_only_no_constructive_paths():
    p=plan();p["constructive_paths"]=[]
    blocked(p,"two constructive")


def test_reject_excessive_r9_audit_budget():
    p=plan();p["r9_diagnostic_budget"]=20
    blocked(p,"diagnostic budget")


def test_reject_false_investor_approval():
    p=plan();p["claims_investor_approval"]=True
    blocked(p,"self-assert")


def test_reject_result_mutated_plan():
    p=plan();r=result(p);p["candidate_change"]="retroactively altered"
    with pytest.raises(ResearchGuardError,match="plan mutated"):
        check_result(p,r)


def test_reject_result_missing_fail_remedy():
    p=plan();r=result(p);r.pop("safe_remediation")
    with pytest.raises(ResearchGuardError,match="safe_remediation"):
        check_result(p,r)


def test_reject_unreported_broker():
    p=plan();r=result(p);r["broker_metrics"].pop("dukascopy")
    with pytest.raises(ResearchGuardError,match="all and only"):
        check_result(p,r)


def test_reject_cherry_picked_periods():
    p=plan();r=result(p);r["includes_all_periods"]=False
    with pytest.raises(ResearchGuardError,match="cherry-picks"):
        check_result(p,r)


def test_reject_false_certification():
    p=plan();r=result(p);r["trade_survivability_claim"]="certified"
    with pytest.raises(ResearchGuardError,match="cannot certify"):
        check_result(p,r)


def test_reject_invalid_evidence_hash():
    p=plan();r=result(p);r["artifacts"][0]["sha256"]="notahash"
    with pytest.raises(ResearchGuardError,match="SHA256"):
        check_result(p,r)
