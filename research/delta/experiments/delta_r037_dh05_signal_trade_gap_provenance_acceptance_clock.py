"""DELTA R037 DH05 signal/trade-gap provenance + acceptance-clock ownership diagnostic — Checkpoint 09S.

Uses durable fingerprints only. No raw tick data, no threshold fitting, no economic optimization.
This checkpoint quantifies whether preserved Checkpoint-09 failure/reentry-clock profiles exhibit
a structural split by existing acceptance/reversal timeframe categories.

It does NOT unfreeze the current FAILURE_CANDIDATE clock. Any promising router is a challenger
hypothesis requiring a separate causal tick replay before scientific carry-forward.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

TARGET={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
META={
 "A03":{"acceptance_tf":15,"reversal_tf":5},
 "S05":{"acceptance_tf":15,"reversal_tf":5},
 "S06":{"acceptance_tf":5,"reversal_tf":1},
 "S09":{"acceptance_tf":15,"reversal_tf":1},
 "S10":{"acceptance_tf":5,"reversal_tf":5},
 "S16":{"acceptance_tf":15,"reversal_tf":5},
}
POSTQUAL={"A03":192,"S05":9,"S06":651,"S09":11,"S10":227,"S16":7}
CP09={
 "NEUTRAL_CURRENT":{"A03":187,"S05":9,"S06":617,"S09":9,"S10":206,"S16":8},
 "NEUTRAL_WAIT_REENTRY":{"A03":282,"S05":54,"S06":653,"S09":11,"S10":317,"S16":22},
 "STAGE_CURRENT":{"A03":247,"S05":10,"S06":672,"S09":41,"S10":225,"S16":14},
 "STAGE_WAIT_REENTRY":{"A03":393,"S05":86,"S06":717,"S09":89,"S10":383,"S16":38},
}

def score(counts):
    return sum(abs(int(counts[k])-TARGET[k]) for k in TARGET)

def route_acceptance_clock():
    out={}
    for k,m in META.items():
        out[k]=CP09["NEUTRAL_CURRENT"][k] if m["acceptance_tf"]==5 else CP09["NEUTRAL_WAIT_REENTRY"][k]
    return out

def route_clock_topology():
    out={}
    for k,m in META.items():
        if m["acceptance_tf"]==5:
            p="NEUTRAL_CURRENT"
        elif m["reversal_tf"]==5:
            p="NEUTRAL_WAIT_REENTRY"
        else:
            p="STAGE_WAIT_REENTRY"
        out[k]=CP09[p][k]
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    ratios={k:TARGET[k]/POSTQUAL[k] for k in TARGET}
    gaps={k:TARGET[k]-POSTQUAL[k] for k in TARGET}
    groups={5:[],15:[]}
    for k,m in META.items(): groups[m["acceptance_tf"]].append(k)
    acceptance_summary={}
    for tf,ks in groups.items():
        acceptance_summary[str(tf)]={
          "vectors":ks,
          "all_trade_minus_signal_positive":all(gaps[k]>0 for k in ks),
          "all_trade_minus_signal_negative":all(gaps[k]<0 for k in ks),
          "mean_target_to_postqual_signal_ratio":sum(ratios[k] for k in ks)/len(ks),
          "aggregate_abs_gap":sum(abs(gaps[k]) for k in ks),
        }
    r1=route_acceptance_clock(); r2=route_clock_topology()
    out={
      "schema":"delta-r037-dh05-signal-trade-gap-provenance-acceptance-clock-v1",
      "status":"BOUNDED_PROVENANCE_DIAGNOSTIC_COMPLETE_NON_PROMOTING",
      "targets":TARGET,"meta":META,"postqual_signals":POSTQUAL,
      "target_to_signal_ratio":ratios,"target_minus_signal":gaps,
      "acceptance_tf_group_summary":acceptance_summary,
      "checkpoint09_profiles":{p:{"counts":v,"aggregate_abs_error_to_historical_trades":score(v)} for p,v in CP09.items()},
      "predeclared_routers":{
        "ACCEPTANCE_CLOCK_ROUTER":{"rule":"acceptance_tf=5 -> NEUTRAL_CURRENT; acceptance_tf=15 -> NEUTRAL_WAIT_REENTRY","counts":r1,"aggregate_abs_error":score(r1)},
        "CLOCK_TOPOLOGY_ROUTER":{"rule":"acceptance_tf=5 -> NEUTRAL_CURRENT; acceptance_tf=15,reversal_tf=5 -> NEUTRAL_WAIT_REENTRY; acceptance_tf=15,reversal_tf=1 -> STAGE_WAIT_REENTRY","counts":r2,"aggregate_abs_error":score(r2)}
      },
      "comparison":{"09L_best_error":304,"09R_best_error":359,"postqual_raw_signal_gap_error":score(POSTQUAL)},
      "finding":{
        "acceptance_tf_sign_separation":acceptance_summary["15"]["all_trade_minus_signal_positive"] and acceptance_summary["5"]["all_trade_minus_signal_negative"],
        "acceptance_clock_router_material_clue":score(r1)<304,
        "clock_topology_router_material_clue":score(r2)<304,
        "promoted":False,
        "reason":"Checkpoint-09 producer bytes are missing and current FAILURE_CANDIDATE clock remains frozen; any router requires causal raw-tick challenger replay and anti-overfit review."
      },
      "next":"R037_DH05_CONDITIONAL_FAILURE_CLOCK_CHALLENGER_REPLAY_NON_PROMOTING"
    }
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"acceptance_clock_error":score(r1),"clock_topology_error":score(r2),"acceptance_tf_sign_separation":out["finding"]["acceptance_tf_sign_separation"]},separators=(",",":")))

if __name__=="__main__": main()
