"""Aalen-Johansen competing-risk estimator and account-cash utility.

Small, deterministic, auditable alternative to prematurely retraining a 237-
feature classifier. Uses R9 quote-side episodes, NEVER raw future values as
entry features. Input split must be chronological and predeclared.

Target, original protective stop and original timeout are mutually exclusive
first events, with quote gaps / source ends right-censored. Trailing stops
can be profitable. The independent-censoring assumption is NOT guaranteed:
report censor rates and perform sensitivity tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from typing import Iterable

from cash_risk_overlay import (
    Episode, CAUSE_TARGET, CAUSE_STOP, CAUSE_TIMEOUT, CENSORED,
    EVENT_CAUSES,
)

HORIZONS_MS=(1000,3000,5000,10000,15000,20000,30000)
SPREAD_BANDS=(15,25)  # quote price cents, specified before evaluation


def context_key(e: Episode, by: str = "session_spread") -> str:
    """Only as-of entry information, never exit time or a future label."""
    if by=="global":
        return "all"
    if by=="session":
        return f"session_{e.session}"
    if by=="session_spread":
        band=sum(e.entry_spread_cents>x for x in SPREAD_BANDS)
        return f"session_{e.session}_spreadband_{band}"
    if by=="hour":
        return f"source_hour_{e.source_hour:02d}"
    raise ValueError("Unknown predetermined context grouping")


@dataclass(frozen=True)
class Incidence:
    horizon_ms: int
    survival: float
    cause_probability: dict[str,float]
    risk_set_at_horizon: int


def aalen_johansen(rows: Iterable[Episode],
                   horizons: tuple[int,...] = HORIZONS_MS) -> list[Incidence]:
    """Proper competing-risk cumulative incidence under right censoring.

    At each distinct observed event time t: dF_j(t)=S(t-)*dN_j(t)/Y(t).
    Events at same t receive priority before right-censor removals at t;
    same-ms SOURCE ORDINAL ordering is already resolved by the observer.
    """
    ep=list(rows)
    if not horizons or any(h<=0 for h in horizons) or tuple(sorted(horizons))!=horizons:
        raise ValueError("Horizon checkpoints must be positive ascending")
    for x in ep:
        if x.cause not in (*EVENT_CAUSES,*CENSORED) or x.event_time_ms is None:
            raise ValueError("Every episode must have a first cause or explicit censor")
        if not (0<=x.event_time_ms<=horizons[-1]):
            raise ValueError("Event time outside declared 30s observation window")
    time_events:dict[int,dict[str,int]]={}
    for x in ep:
        count=time_events.setdefault(int(x.event_time_ms),{})
        count[x.cause]=count.get(x.cause,0)+1
    risk=len(ep)
    s=1.0
    cif={c:0.0 for c in EVENT_CAUSES}
    timeline=sorted(time_events.items())
    ix=0
    output=[]
    for boundary in horizons:
        while ix<len(timeline) and timeline[ix][0]<=boundary:
            time,cs=timeline[ix]
            d=sum(cs.get(c,0) for c in EVENT_CAUSES)
            cens=sum(cs.get(c,0) for c in CENSORED)
            if risk<d+cens or risk<=0:
                raise ValueError("Risk set depleted unexpectedly")
            for cause in EVENT_CAUSES:
                cif[cause]+=s*cs.get(cause,0)/risk
            s*=1.0-d/risk
            risk-=d+cens
            ix+=1
        output.append(Incidence(boundary,s,dict(cif),risk))
    for item in output:
        if any(p< -1e-10 for p in item.cause_probability.values()):
            raise AssertionError("Invalid negative event probability")
        if abs(sum(item.cause_probability.values())+item.survival-1)>1e-8:
            raise AssertionError("Competing probabilities/survival do not normalize")
    return output


def _avg(values:list[float]) -> float|None:
    return sum(values)/len(values) if values else None


def cash_cvar95(values:list[float]) -> float|None:
    """Observed left-tail account-cash shortfall, in account units."""
    if not values:
        return None
    ordered=sorted(values)
    cut=max(1,ceil(0.05*len(ordered)))
    return max(0.,-sum(ordered[:cut])/cut)


def fit_context_tables(episodes: Iterable[Episode],
                       by: str="session_spread",
                       min_group_count: int=100,
                       risk_lambda: float=0.0,
                       max_censor_fraction: float=0.10) -> dict:
    """Freeze train-only cash incidence and net-payoff means per as-of context.

    Do not infer a realized strategy improvement: the early-goal overlay is
    not a full strategy replay; updated entry occupancy is still missing.
    """
    if (min_group_count<=0 or not isfinite(risk_lambda) or risk_lambda<0
            or not isfinite(max_censor_fraction)
            or max_censor_fraction<0 or max_censor_fraction>=1):
        raise ValueError("Invalid minimum count, downside risk penalty, or censor threshold")
    all_rows=list(episodes)
    groups:dict[str,list[Episode]]={}
    for e in all_rows:
        groups.setdefault(context_key(e,by),[]).append(e)
    result={}
    for key,rows in sorted(groups.items()):
        censor_count=sum(e.cause in CENSORED for e in rows)
        event_payoffs:dict[str,list[float]]={c:[] for c in EVENT_CAUSES}
        for e in rows:
            if e.cause in EVENT_CAUSES and e.overlay_net_cash is not None:
                event_payoffs[e.cause].append(float(e.overlay_net_cash))
        event_means={k:_avg(v) for k,v in event_payoffs.items()}
        final=aalen_johansen(rows)[-1]
        # A cause with zero observations cannot have positive estimated CIF;
        # however explicit None makes missing payoff evidence visible.
        expected=0.0
        for cause,probability in final.cause_probability.items():
            m=event_means[cause]
            if probability>0 and m is None:
                raise ValueError(f"Estimated nonzero incidence without payoff sample: {cause}")
            expected+=probability*(m or 0.0)
        all_observed=[float(e.overlay_net_cash) for e in rows
                      if e.cause in EVENT_CAUSES and e.overlay_net_cash is not None]
        cvar=cash_cvar95(all_observed)
        eligible=(len(rows)>=min_group_count and
                  censor_count/len(rows)<=max_censor_fraction and
                  bool(all_observed))
        result[key]={
            "training_episodes":len(rows),
            "censored_count":censor_count,
            "censored_fraction":censor_count/max(1,len(rows)),
            "train_eligible":eligible,
            "incidence_by_horizon":[{
                "horizon_ms":v.horizon_ms,
                "survival":v.survival,
                "cause_probability":v.cause_probability,
                "observed_risk_set":v.risk_set_at_horizon,
            } for v in aalen_johansen(rows)],
            "mean_account_cash_by_cause":event_means,
            "observed_payoff_cvar95_cash":cvar,
            "estimated_net_cash_per_entry":expected if eligible else None,
            "estimated_risk_adjusted_cash":(
                expected-risk_lambda*(cvar or 0.0)
                if eligible else None
            ),
        }
    return {
        "classification":"TRAIN_ONLY_CAUSAL_QUOTE_OVERLAY_NOT_EXECUTED_ACCOUNT_PNL",
        "context":by,
        "min_group_count":min_group_count,
        "risk_lambda":risk_lambda,
        "max_censor_fraction":max_censor_fraction,
        "horizons_ms":list(HORIZONS_MS),
        "fixed_spread_bands_cents":list(SPREAD_BANDS),
        "total_training_episodes":len(all_rows),
        "groups":result,
    }


def evaluate_frozen_table(table:dict, evaluation:Iterable[Episode]) -> dict:
    """Evaluate risk predictions made only with PRIOR data.

    Predicted U cannot be credited as causal portfolio P&L; we report coverage,
    cash calibration on observed episodes, and outcomes without tuning.
    Censored observations are excluded from observed mean, but NOT ignored:
    report missingness and avoid performance claims if material.
    """
    by=table["context"]
    all_rows=list(evaluation)
    matched=[]
    observed=[]
    missing_group=0
    censored=0
    for e in all_rows:
        row=table["groups"].get(context_key(e,by))
        if row is None or not row["train_eligible"]:
            missing_group+=1
            continue
        v=row["estimated_net_cash_per_entry"]
        if v is None:
            missing_group+=1
            continue
        if e.cause in CENSORED:
            censored+=1
            continue
        if e.overlay_net_cash is None:
            raise ValueError("Uncensored row lacks payoff")
        matched.append(float(v))
        observed.append(float(e.overlay_net_cash))
    abs_error=[abs(a-b) for a,b in zip(matched,observed)]
    return {
        "classification":"CHRONOLOGICAL_HELD_OUT_EVALUATION_IF_SOURCE_SPLIT_VERIFIED",
        "all_evaluation_episodes":len(all_rows),
        "no_pretrained_group_count":missing_group,
        "matched_uncensored_count":len(matched),
        "matched_censored_count":censored,
        "mean_predicted_net_cash":_avg(matched),
        "mean_observed_hypothetical_net_cash":_avg(observed),
        "mean_absolute_net_cash_error":_avg(abs_error),
        "warning":"Event incidence assumes independent censoring; high-AUC model score and on-policy occupancy are not included.",
    }
