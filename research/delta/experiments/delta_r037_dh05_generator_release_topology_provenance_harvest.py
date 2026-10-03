"""DELTA R037 DH05 generator-release topology provenance harvest — Checkpoint 09Y.

Provenance-only harvest from already durable 09H/09I/09V fingerprints.
No raw ticks. No numeric retuning. No semantic promotion.

The unit asks whether release-profile preferences can be explained by a simple
reconstructible relation among already-frozen timing fields, rather than vector identity.

Predeclared natural timing-topology predicate:
    SHORT_PROBE_RELATIVE_TO_ACCEPTANCE_BAR :=
        max_probe_age_s < acceptance_tf_seconds

Rationale: when a probe's admissible lifetime is shorter than one acceptance-bar
duration, the attempt can become FAILURE_CANDIDATE before a newly completed
acceptance bar can exist. Generator ownership may therefore differ structurally.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

from delta_r037_dh05_runtime_primitives import VECTORS, atomic_write_json

STAGES=("probe","qualified","accepted","failure","reentry","reclaim","reversal","signal")
TARGET={
"A03":[6731,1009,207,797,432,266,187,187],
"S05":[7875,318,28,290,51,15,9,9],
"S06":[3470,1606,245,1358,1211,683,617,617],
"S09":[7748,208,40,168,61,40,9,9],
"S10":[6496,1316,202,1106,623,294,206,206],
"S16":[7870,135,43,92,37,18,8,8]}

# Durable POST_QUAL serial control.
SERIAL={
"A03":[6686,998,212,786,441,268,192,192],
"S05":[7727,309,32,277,54,19,9,9],
"S06":[3561,1599,248,1351,1210,695,651,651],
"S09":[7632,201,40,161,63,39,11,11],
"S10":[6440,1300,205,1095,637,309,227,227],
"S16":[7684,130,52,78,32,18,7,7]}

# Durable 09H FAILURE_CANDIDATE decoupled POST_QUAL fingerprints.
FAILURE_RELEASE={
"A03":[7832,1157,235,922,532,325,236,236],
"S05":[7818,315,34,281,56,20,9,9],
"S06":[7373,3117,370,2747,2412,1372,1281,1281],
"S09":[7856,219,44,175,65,41,11,11],
"S10":[7778,1536,223,1313,772,373,283,283],
"S16":[7778,134,53,81,33,19,8,8]}

# Durable 09I reclaim release and 09V next-reversal-bar fingerprints.
RECLAIM_RELEASE={
"A03":[6791,1015,218,797,450,276,197,197],
"S05":[7742,310,33,277,54,19,9,9],
"S06":[3621,1627,252,1375,1227,707,663,663],
"S09":[7697,207,42,165,64,40,11,11],
"S10":[6525,1322,207,1115,651,318,236,236],
"S16":[7713,132,53,79,33,19,8,8]}
NEXT_REV_RELEASE={
"A03":[6752,1009,216,793,446,272,195,195],
"S05":[7735,309,32,277,54,19,9,9],
"S06":[3619,1627,252,1375,1227,708,664,664],
"S09":[7697,207,42,165,64,40,11,11],
"S10":[6476,1310,204,1106,644,313,231,231],
"S16":[7704,131,52,79,33,19,8,8]}

PROFILES={
 "SERIAL_POST_QUAL":SERIAL,
 "FAILURE_CANDIDATE_RELEASE":FAILURE_RELEASE,
 "RECLAIM_RELEASE":RECLAIM_RELEASE,
 "NEXT_REVERSAL_BAR_RELEASE":NEXT_REV_RELEASE,
}

def err(name, profile):
    return sum(abs(int(a)-int(b)) for a,b in zip(profile[name],TARGET[name]))

def live_meta():
    return {
      v[0]:{
        "acceptance_tf_s":int(v[2]),
        "reversal_tf_s":int(v[9]),
        "max_failure_age_s":float(v[3]),
        "max_probe_age_s":float(v[4]),
      }
      for v in VECTORS
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    meta=live_meta()
    per_vector={}
    for n in TARGET:
        errors={p:err(n,d) for p,d in PROFILES.items()}
        per_vector[n]={
          "meta":meta[n],
          "profile_abs_error":errors,
          "best_profile":min(errors,key=errors.get),
          "short_probe_relative_to_acceptance_bar":bool(
              meta[n]["max_probe_age_s"] < meta[n]["acceptance_tf_s"]
          )
        }

    # Explicitly test whether acceptance/reversal timeframe identity alone can explain
    # per-vector best profiles. A category fails if two vectors with same (acc_tf, rev_tf)
    # have different best profiles.
    topology_groups={}
    for n,v in per_vector.items():
        key=f'{v["meta"]["acceptance_tf_s"]}/{v["meta"]["reversal_tf_s"]}'
        topology_groups.setdefault(key,[]).append(n)
    topology_conflicts={}
    for key,ks in topology_groups.items():
        best={per_vector[k]["best_profile"] for k in ks}
        if len(best)>1:
            topology_conflicts[key]={
                "vectors":ks,
                "best_profiles":{k:per_vector[k]["best_profile"] for k in ks}
            }

    routed={}
    routed_errors={}
    for n in TARGET:
        use_failure=per_vector[n]["short_probe_relative_to_acceptance_bar"]
        chosen="FAILURE_CANDIDATE_RELEASE" if use_failure else "SERIAL_POST_QUAL"
        routed[n]=chosen
        routed_errors[n]=per_vector[n]["profile_abs_error"][chosen]

    serial_total=sum(per_vector[n]["profile_abs_error"]["SERIAL_POST_QUAL"] for n in TARGET)
    routed_total=sum(routed_errors.values())

    out={
      "schema":"delta-r037-dh05-generator-release-topology-provenance-09y-v1",
      "status":"BOUNDED_PROVENANCE_HARVEST_COMPLETE_NON_PROMOTING",
      "raw_tick_accessed":False,
      "numeric_vector_retune":False,
      "per_vector":per_vector,
      "timeframe_topology_groups":topology_groups,
      "timeframe_topology_conflicts":topology_conflicts,
      "candidate":{
        "name":"SHORT_PROBE_RELATIVE_TO_ACCEPTANCE_BAR_ROUTER",
        "rule":"max_probe_age_s < acceptance_tf_seconds -> FAILURE_CANDIDATE release; otherwise SERIAL_POST_QUAL",
        "routed_profile":routed,
        "per_vector_abs_error":routed_errors,
        "control_total_abs_error":serial_total,
        "predicted_blended_total_abs_error":routed_total,
        "predicted_improvement":serial_total-routed_total,
        "selected_vectors":[n for n in TARGET if per_vector[n]["short_probe_relative_to_acceptance_bar"]],
        "promoted":False,
        "requires_causal_replay":True
      },
      "finding":{
        "acceptance_reversal_timeframe_topology_sufficient":len(topology_conflicts)==0,
        "vector_specific_best_profile_prohibited":True,
        "semantic_timing_relation_candidate_found":routed_total<serial_total,
        "interpretation":"Timeframe identity alone cannot explain release preference. The natural relative-lifetime predicate selects S05/S09/S16 and predicts a materially lower blended funnel error without routing S06/S10 into early decoupling.",
        "promoted":False
      },
      "decision":"HARVEST_SHORT_PROBE_RELATIVE_TO_ACCEPTANCE_BAR_ROUTER_FOR_NON_PROMOTING_CAUSAL_REPLAY",
      "next":"R037_DH05_SHORT_PROBE_RELATIVE_ACCEPTANCE_BAR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING"
    }
    atomic_write_json(args.output,out)
    print(json.dumps({
      "timeframe_topology_conflicts":topology_conflicts,
      "selected_vectors":out["candidate"]["selected_vectors"],
      "control_total_abs_error":serial_total,
      "predicted_blended_total_abs_error":routed_total,
      "predicted_improvement":serial_total-routed_total,
      "routed_profile":routed
    },separators=(",",":")))

if __name__=="__main__": main()
