"""R11 future-privileged counterfactual H1V2 entry frontier, additive sidecar.

This is a generalized OFFLINE ORACLE, not a causal/online action. It consumes
the original immutable H1V2 30s code/net/exit/first_hit arrays and optionally
restricts candidate entry availability to the v5 shadow gap contract.
Three lexicographic objectives are distinct experiments:
  count: maximize known strict-good nonoverlapping count, tie-break repriced net;
  net: maximize cumulative repriced net, tie-break count;
  occupancy: maximize repriced net minus elapsed-ms opportunity penalty,
             tie-break count.
Only historical outcomes may be read here. No student model may use selected
future schedule members, replay exit ordinals, or this DP value as as-of inputs.
Incremental cost is AFTER the already included $0.02 original research fee;
original strict first-hit event is NOT repriced by this post-hoc adjustment.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class FrontierConfig:
    objective:str="count"
    max_first_hit_ms:int=30_000
    min_repriced_net:float=0.0
    incremental_cost:float=0.0
    occupation_penalty_per_ms:float=0.0

def optimize(entries,code,net,exit_ix,first_ms,exit_ms,
             eligible=None, config:FrontierConfig=FrontierConfig()):
    entries=np.asarray(entries,dtype=np.int64)
    code=np.asarray(code,dtype=np.int8)
    net=np.asarray(net,dtype=np.float64)
    exit_ix=np.asarray(exit_ix,dtype=np.int64)
    first_ms=np.asarray(first_ms,dtype=np.int64)
    exit_ms=np.asarray(exit_ms,dtype=np.int64)
    n=len(entries)
    if config.objective not in ("count","net","occupancy"):raise ValueError("unsupported oracle objective")
    if any(v<0 for v in (config.max_first_hit_ms,config.incremental_cost,config.occupation_penalty_per_ms)):
        raise ValueError("invalid frontier cost or horizon")
    if not(np.isfinite(config.incremental_cost) and np.isfinite(config.occupation_penalty_per_ms)
           and np.isfinite(config.min_repriced_net)):
        raise ValueError("nonfinite configuration")
    if entries.ndim!=1 or np.any(np.diff(entries)<=0):raise ValueError("source ordinals not strictly ordered")
    for x in (code,net,exit_ix,first_ms,exit_ms):
        if x.shape!=(n,2):raise ValueError("paired independent side arrays required")
    if eligible is None:
        allowed=np.ones(n,dtype=np.bool_)
    else:
        allowed=np.asarray(eligible,dtype=np.bool_)
        if allowed.shape!=(n,):raise ValueError("eligibility shape mismatch")
    # Unknown or censored outcomes are always excluded, not silently labeled bad.
    valid=((code==1) & np.isfinite(net) & (exit_ix>entries[:,None])
           & (exit_ms>=0) & (exit_ms<=30_000)
           & (first_ms>=0) & (first_ms<=config.max_first_hit_ms)
           & (net-config.incremental_cost>config.min_repriced_net)
           & allowed[:,None])
    next_eligible=np.full((n,2),n,dtype=np.int64)
    for side in (0,1):
        rows=np.flatnonzero(valid[:,side])
        next_eligible[rows,side]=np.searchsorted(entries,exit_ix[rows,side],side="right")
    count=np.zeros(n+1,dtype=np.int64)
    original_net=np.zeros(n+1,dtype=np.float64)
    repriced_net=np.zeros(n+1,dtype=np.float64)
    occupation_score=np.zeros(n+1,dtype=np.float64)
    selection=np.full(n,-1,dtype=np.int8)
    for i in range(n-1,-1,-1):
        b_count=count[i+1];b_orig=original_net[i+1]
        b_net=repriced_net[i+1];b_occ=occupation_score[i+1];chosen=-1
        for s in (0,1):
            if not valid[i,s]:continue
            j=int(next_eligible[i,s])
            candidate_count=count[j]+1
            candidate_orig=original_net[j]+net[i,s]
            candidate_net=repriced_net[j]+net[i,s]-config.incremental_cost
            candidate_occ=occupation_score[j]+net[i,s]-config.incremental_cost-config.occupation_penalty_per_ms*exit_ms[i,s]
            if config.objective=="count":
                improve=candidate_count>b_count or (candidate_count==b_count and candidate_net>b_net+1e-9)
            elif config.objective=="net":
                improve=candidate_net>b_net+1e-9 or (abs(candidate_net-b_net)<=1e-9 and candidate_count>b_count)
            else:
                improve=candidate_occ>b_occ+1e-9 or (abs(candidate_occ-b_occ)<=1e-9 and candidate_count>b_count)
            if improve:
                b_count=candidate_count;b_orig=candidate_orig;b_net=candidate_net
                b_occ=candidate_occ;chosen=s
        count[i]=b_count;original_net[i]=b_orig;repriced_net[i]=b_net
        occupation_score[i]=b_occ;selection[i]=chosen
    rows=[];sides=[];at=0
    while at<n:
        side=int(selection[at])
        if side<0:at+=1;continue
        rows.append(at);sides.append(1 if side==0 else -1)
        at=int(next_eligible[at,side])
    row=np.asarray(rows,dtype=np.int64);side=np.asarray(sides,dtype=np.int8)
    selected_side=(side==-1).astype(np.int64)
    if len(row)>1 and not np.all(entries[row[1:]]>exit_ix[row[:-1],selected_side[:-1]]):
        raise AssertionError("oracle overlap")
    if len(row)!=count[0]:raise AssertionError("DP count reconstruction drift")
    return row,side,dict(
        objective=config.objective,
        trades=int(count[0]),
        original_research_net=float(original_net[0]),
        repriced_net=float(repriced_net[0]),
        occupancy_adjusted_objective=float(occupation_score[0]),
        original_eligible_count=int(allowed.sum()),
        strict_good_eligible_action_count=int(valid.sum()),
        incremental_cost=float(config.incremental_cost),
        additional_note="future-known scheduling and unchanged original strict-first classification; not prospective strategy",
    )
