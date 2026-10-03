"""DELTA R037 DH05 acceptance-timeframe metadata provenance reconciliation — Checkpoint 09X.

Bounded provenance-only diagnostic. No raw tick data. No numeric retune.

Purpose:
- compare Checkpoint-09S hard-coded metadata against the current committed frozen
  DH05 VECTORS tuple used by causal replays;
- identify exact categorical mismatches;
- recompute the 09S historical count-only routers under corrected live metadata;
- state whether later causal Checkpoint-09T requires reopening.

This does not promote any trading semantic.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

from delta_r037_dh05_runtime_primitives import VECTORS, atomic_write_json

TARGET={"A03":306,"S05":51,"S06":615,"S09":119,"S10":206,"S16":24}
POSTQUAL={"A03":192,"S05":9,"S06":651,"S09":11,"S10":227,"S16":7}
CHECKPOINT09S_META={
 "A03":{"acceptance_tf":15,"reversal_tf":5},
 "S05":{"acceptance_tf":15,"reversal_tf":5},
 "S06":{"acceptance_tf":5,"reversal_tf":1},
 "S09":{"acceptance_tf":15,"reversal_tf":1},
 "S10":{"acceptance_tf":5,"reversal_tf":5},
 "S16":{"acceptance_tf":15,"reversal_tf":5},
}
CP09={
 "NEUTRAL_CURRENT":{"A03":187,"S05":9,"S06":617,"S09":9,"S10":206,"S16":8},
 "NEUTRAL_WAIT_REENTRY":{"A03":282,"S05":54,"S06":653,"S09":11,"S10":317,"S16":22},
 "STAGE_CURRENT":{"A03":247,"S05":10,"S06":672,"S09":41,"S10":225,"S16":14},
 "STAGE_WAIT_REENTRY":{"A03":393,"S05":86,"S06":717,"S09":89,"S10":383,"S16":38},
}

def live_meta():
    # VECTORS tuple:
    # name, acceptance_disp_atr, acceptance_tf, max_failure_age_s,
    # max_probe_age_s, probe_excursion_atr, reclaim_buffer_atr,
    # reversal_disp_atr, reversal_eff_min, reversal_tf
    return {
        v[0]:{"acceptance_tf":int(v[2]),"reversal_tf":int(v[9])}
        for v in VECTORS
    }

def score(counts):
    return sum(abs(int(counts[k])-TARGET[k]) for k in TARGET)

def acceptance_clock(meta):
    return {
        k:(CP09["NEUTRAL_CURRENT"][k] if m["acceptance_tf"]==5
           else CP09["NEUTRAL_WAIT_REENTRY"][k])
        for k,m in meta.items()
    }

def clock_topology(meta):
    out={}
    for k,m in meta.items():
        if m["acceptance_tf"]==5:
            p="NEUTRAL_CURRENT"
        elif m["reversal_tf"]==5:
            p="NEUTRAL_WAIT_REENTRY"
        else:
            p="STAGE_WAIT_REENTRY"
        out[k]=CP09[p][k]
    return out

def group_summary(meta):
    gaps={k:TARGET[k]-POSTQUAL[k] for k in TARGET}
    out={}
    for tf in (5,15):
        ks=[k for k,m in meta.items() if m["acceptance_tf"]==tf]
        vals=[gaps[k] for k in ks]
        out[str(tf)]={
            "vectors":ks,
            "target_minus_postqual_signal":{k:gaps[k] for k in ks},
            "all_positive":all(x>0 for x in vals),
            "all_negative":all(x<0 for x in vals),
        }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    live=live_meta()
    mismatches={}
    for k in TARGET:
        if CHECKPOINT09S_META[k]!=live[k]:
            mismatches[k]={
                "checkpoint09s":CHECKPOINT09S_META[k],
                "live_frozen_vectors":live[k],
            }

    old_a=acceptance_clock(CHECKPOINT09S_META)
    old_t=clock_topology(CHECKPOINT09S_META)
    new_a=acceptance_clock(live)
    new_t=clock_topology(live)
    old_groups=group_summary(CHECKPOINT09S_META)
    new_groups=group_summary(live)

    out={
      "schema":"delta-r037-dh05-acceptance-tf-metadata-provenance-09x-v1",
      "status":"BOUNDED_PROVENANCE_RECONCILIATION_COMPLETE",
      "raw_tick_accessed":False,
      "numeric_vector_retune":False,
      "checkpoint09s_meta":CHECKPOINT09S_META,
      "live_frozen_meta":live,
      "mismatches":mismatches,
      "checkpoint09s_original":{
        "acceptance_clock_counts":old_a,
        "acceptance_clock_error":score(old_a),
        "clock_topology_counts":old_t,
        "clock_topology_error":score(old_t),
        "group_summary":old_groups,
      },
      "corrected_diagnostic":{
        "acceptance_clock_counts":new_a,
        "acceptance_clock_error":score(new_a),
        "clock_topology_counts":new_t,
        "clock_topology_error":score(new_t),
        "group_summary":new_groups,
      },
      "finding":{
        "mismatch_count":len(mismatches),
        "s16_only_mismatch":list(mismatches.keys())==["S16"],
        "perfect_acceptance_tf_sign_separation_survives":bool(
            new_groups["15"]["all_positive"] and new_groups["5"]["all_negative"]
        ),
        "checkpoint09t_requires_reopen":False,
        "reason_09t_stands":"Checkpoint 09T derives categories from the same live frozen VECTORS tuple and causally rejected the router on raw Stage-A ticks; correcting the historical 09S metadata cannot reverse that later causal falsification.",
        "promoted":False,
      },
      "decision":"CORRECT_09S_METADATA_CLAIM_KEEP_09T_CAUSAL_REJECTION",
      "next":"R037_DH05_GENERATOR_RELEASE_TOPOLOGY_PROVENANCE_HARVEST"
    }
    atomic_write_json(args.output,out)
    print(json.dumps({
      "mismatches":mismatches,
      "old_acceptance_error":score(old_a),
      "corrected_acceptance_error":score(new_a),
      "old_topology_error":score(old_t),
      "corrected_topology_error":score(new_t),
      "perfect_sign_separation_survives":out["finding"]["perfect_acceptance_tf_sign_separation_survives"],
      "checkpoint09t_requires_reopen":False
    },separators=(",",":")))

if __name__=="__main__": main()
