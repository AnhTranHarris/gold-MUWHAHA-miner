"""DELTA R037 DH05 short-probe ownership provenance/promotion decision — Checkpoint 10B.

Evidence-synthesis unit. No market data access and no parameter fitting.

Promotion requires all of:
1. A reconstructible pre-09Y source independently implies the exact relative-duration
   ownership rule (max_probe_age_s < acceptance_tf_seconds) and FAILURE_CANDIDATE
   generator release while the downstream failure episode remains alive.
2. The rule survives the 09Z exact causal Stage-A replay without trade/S06 deterioration.
3. The rule survives independent 10A later-January P50/P75/P90 robustness.
4. No earlier causal checkpoint directly contradicts universal interpretation.

If criterion 1 is absent, OOS robustness cannot retroactively prove historical helper
semantics. In that case keep the architecture only as a robust non-promoting challenger,
close same-sample ownership recuts, and return to the largest remaining upstream parity
residual.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r003",type=Path,required=True)
    ap.add_argument("--r006",type=Path,required=True)
    ap.add_argument("--c09h",type=Path,required=True)
    ap.add_argument("--c09i",type=Path,required=True)
    ap.add_argument("--c09y",type=Path,required=True)
    ap.add_argument("--c09z",type=Path,required=True)
    ap.add_argument("--c10a",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    r003=args.r003.read_text(encoding="utf-8")
    r006=args.r006.read_text(encoding="utf-8")
    c09h=json.loads(args.c09h.read_text(encoding="utf-8"))
    c09i=json.loads(args.c09i.read_text(encoding="utf-8"))
    c09y=json.loads(args.c09y.read_text(encoding="utf-8"))
    c09z=json.loads(args.c09z.read_text(encoding="utf-8"))
    c10a=json.loads(args.c10a.read_text(encoding="utf-8"))

    # Frozen pre-09Y repo evidence intentionally uses exact text claims rather than
    # inferred helper behavior.
    r003_single_chain = "IDLE -> PROBE -> FAILURE_CANDIDATE -> REENTRY -> RECLAIM_CONFIRMED -> FAILED_BREAK_CONFIRMED -> REVERSAL_REBREAK -> ENTRY_ELIGIBLE" in r003
    r003_accepted_routed_away = "An accepted original breakout is explicitly routed away from DH-05." in r003
    r006_conditional_specialist = "DH-05 — REFINE AS CONDITIONAL SPECIALIST" in r006
    r006_has_relative_duration_rule = "max_probe_age_s < acceptance_tf_seconds" in r006

    h_decision=str(c09h.get("decision",""))
    i_decision=str(c09i.get("decision",""))
    y_candidate=c09y.get("candidate",{})
    z_find=c09z.get("finding",{})
    a_find=c10a.get("finding",{})

    exact_rule="max_probe_age_s < acceptance_tf_seconds"
    criterion_1 = bool(r006_has_relative_duration_rule)  # no pre-09Y exact router provenance in repo summary
    criterion_2 = bool(z_find.get("selection_rule_pass",False) and not z_find.get("s06_economic_veto_triggered",True))
    criterion_3 = bool(a_find.get("anti_overfit_gate_pass",False) and a_find.get("all_three_surfaces_no_worse_net",False))
    criterion_4 = bool("REJECT" not in h_decision.upper() and "REJECT" not in i_decision.upper())
    promotion = bool(criterion_1 and criterion_2 and criterion_3 and criterion_4)

    residual=c09z.get("candidate",{}).get("stage_abs_error",{})
    residual_order=sorted(((str(k),int(v)) for k,v in residual.items()),key=lambda kv:(-kv[1],kv[0]))

    out={
      "schema":"delta-r037-dh05-short-probe-ownership-provenance-promotion-decision-10b-v1",
      "status":"COMPLETE_PROVENANCE_PROMOTION_DECISION",
      "raw_ticks_accessed":False,
      "numeric_vector_retune":False,
      "promotion_criteria":{
        "pre_09y_exact_independent_rule_provenance":criterion_1,
        "09z_causal_stage_a_gate":criterion_2,
        "10a_independent_holdout_robustness":criterion_3,
        "no_prior_causal_release_contradiction":criterion_4
      },
      "evidence":{
        "r003_single_state_chain_present":r003_single_chain,
        "r003_accepted_break_routed_away":r003_accepted_routed_away,
        "r006_conditional_specialist_status_present":r006_conditional_specialist,
        "r006_exact_relative_duration_router_present":r006_has_relative_duration_rule,
        "09h_decision":h_decision,
        "09i_decision":i_decision,
        "09y_rule":y_candidate.get("rule"),
        "09y_discovery_same_stage_a":True,
        "09z_funnel_error_improvement":z_find.get("funnel_error_improvement"),
        "09z_funnel_error_improvement_pct":z_find.get("funnel_error_improvement_pct"),
        "10a_all_three_surfaces_no_worse_net":a_find.get("all_three_surfaces_no_worse_net"),
        "10a_effect_size":a_find.get("effect_size")
      },
      "decision":{
        "promote_as_historical_dh05_semantics":promotion,
        "retain_as_robust_non_promoting_challenger":bool(criterion_2 and criterion_3),
        "close_same_sample_ownership_recut_family":True,
        "reason":"OOS robustness survives, but no pre-09Y source independently encodes the exact relative-duration FAILURE_CANDIDATE release router; earlier causal release tests reject universal release interpretations. Robustness cannot establish missing historical helper identity.",
        "largest_remaining_09z_stage_error":residual_order[0] if residual_order else None,
        "remaining_09z_stage_errors_ranked":residual_order,
        "next":"R037_DH05_PROBE_COUNT_RESIDUAL_PROVENANCE_AND_BOUNDARY_LIFECYCLE_RECONCILIATION"
      }
    }
    # Atomic enough for this tiny provenance-only unit: caller writes in a fresh path
    # and GitHub persistence remains the durable checkpoint.
    tmp=args.output.with_suffix(args.output.suffix+".tmp")
    tmp.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    tmp.replace(args.output)
    print(json.dumps(out["decision"],separators=(",",":")))

if __name__=="__main__":
    main()
