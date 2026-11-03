"""R11 source-exact discrete competing cause and censoring training targets.

Only OFFLINE targets. The returned future event/cause must NEVER be included in
as-of features or at online inference. Original strict labels/exit remain frozen.
"""
from __future__ import annotations
import numpy as np

BOUNDARIES_MS=np.asarray((0,250,1000,3000,5000,15000,30000),np.int32)
CAUSE_NAMES=('CENSORED_OR_NONE','FAVORABLE_FIRST','ADVERSE_FIRST')

def first_passage_risk_sets(first_cause,first_ms,exit_ms,exit_ix,net,
                            boundaries=BOUNDARIES_MS):
    """Right-censored event-exposure and first cause without manufactured wins.

    Shapes original teacher labels [n,2]; bins (lo,hi] each have exposure in
    [0,1]. Censored source-end outcomes get unknown terminal outcome, not BAD.
    The R9 original label `code` is intentionally NOT reconstructed here.
    """
    cause=np.asarray(first_cause,np.int8)
    time=np.asarray(first_ms,np.int32)
    exit_t=np.asarray(exit_ms,np.int32)
    exix=np.asarray(exit_ix,np.int64)
    cash=np.asarray(net,np.float64)
    edges=np.asarray(boundaries,np.int32)
    if cause.ndim!=2 or cause.shape[1]!=2 or not (time.shape==exit_t.shape==exix.shape==cash.shape==cause.shape):
        raise ValueError('original BUY/SELL shape drift')
    if len(edges)<2 or edges[0]!=0 or edges[-1]!=30000 or np.any(np.diff(edges)<=0):
        raise ValueError('invalid elapsed-time horizon')
    if not np.isin(cause,(-1,0,1)).all():
        raise ValueError('invalid original cause')
    valid_exit=(exix>=0)&(exit_t>=0)&np.isfinite(cash)
    if np.any((cause!=0)&(time<0)) or np.any((cause==0)&(time!=-1)):
        raise ValueError('original first-cause/elapsed mismatch')
    if np.any((cause!=0)&(time>30000)):
        raise ValueError('cause after original 30sec horizon')
    if np.any(valid_exit & (exit_t<time)):
        raise ValueError('terminal close before first cause')
    # Source-end unknown exit is NOT assumed negative.  A witnessed first cause
    # still contributes its time-to-event even if the eventual close is unknown.
    observed_event=(cause!=0)&(time>=0)
    known_end=np.where(observed_event,time,np.where(valid_exit,exit_t,0))
    known_end=np.clip(known_end,0,30000)
    K=len(edges)-1
    exposure=np.zeros(cause.shape+(K,),np.float32)
    event=np.zeros(cause.shape+(K,),np.int8)
    for k,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
        exposure[...,k]=np.clip((known_end-lo)/(hi-lo),0,1)
        active=observed_event & (time>lo) & (time<=hi)
        event[...,k]=np.where(active,cause,0).astype(np.int8)
    # Event exactly at t=0 should never arise from original ActivePath.update:
    # any same-timestamp future quote is skipped.
    if np.any(observed_event & (time==0)):
        raise ValueError('ambiguous zero duration first passage')
    original_positive_close=valid_exit&(cash>0)&(exit_t<=30000)
    original_strict=original_positive_close & (cause==1) & (time<=30000)
    return dict(exposure=exposure,event=event,close_observed=valid_exit,
                strict_correct=original_strict,source_end_censored=~valid_exit,
                time_to_event=known_end,interval_edges=edges.copy(),
                scope='OFFLINE_TARGETS_ONLY_NO_RUNTIME_FUTURE_FEATURES')


def finite_outcome_group_stats(groups,net,code,exit_ix,min_support=16):
    """R10 cohort fix: censor explicitly, no NaN-weighted bincount poisoning.

    A group is economically eligible only if it has min_support completed
    source-exact exits and NO censored members by default (fail-closed).
    This is a diagnostic, not a predictor or policy gate.
    """
    g=np.asarray(groups,np.int64)
    money=np.asarray(net,np.float64)
    label=np.asarray(code,np.int8)
    ex=np.asarray(exit_ix,np.int64)
    if not (g.ndim==1 and g.shape==money.shape==label.shape==ex.shape) or np.any(g<0):
        raise ValueError('group/side vector mismatch')
    n=int(g.max()+1) if len(g) else 0
    valid=np.isfinite(money)&(ex>=0)
    gross=np.bincount(g,minlength=n).astype(np.int64)
    complete=np.bincount(g[valid],minlength=n).astype(np.int64)
    censored=gross-complete
    total=np.bincount(g[valid],weights=money[valid],minlength=n)
    mean=np.divide(total,complete,out=np.full(n,np.nan),where=complete>0)
    correct=np.bincount(g[valid&(label==1)],minlength=n).astype(np.int64)
    wrong=np.bincount(g[valid&(label==-1)],minlength=n).astype(np.int64)
    neutral=complete-correct-wrong
    if np.any(neutral<0):raise ValueError('invalid source class')
    eligible=(complete>=min_support)&(censored==0)&(mean>0)
    return dict(total=gross,completed=complete,censored=censored,net_sum=total,
                net_mean=mean,strict_good=correct,wrong=wrong,neutral=neutral,
                economic_eligible=eligible,assumption='CENSORED_GROUP_FAIL_CLOSED')
