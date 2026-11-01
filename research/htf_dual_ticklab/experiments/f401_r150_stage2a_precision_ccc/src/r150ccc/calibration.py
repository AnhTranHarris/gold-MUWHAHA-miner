"""Offline class-safe calibration: maximize CORRECT rescues per BAD re-admission.

Historical class labels are CAL-only; no runtime truth/teacher feedback.
Empirical tail ratios do NOT provide distribution-free guarantees for serial data.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class FrozenCut:
    cut:float|None
    rescued_correct:int
    readmitted_opposite:int
    readmitted_neutral:int
    bad_per_correct:float|None
    n_blocks:int
    status:str


def select_rescue_cut(*,score,truth,utc_ms,valid=None,
                      max_bad_per_correct:float=0.5,min_correct:int=100,
                      min_blocks:int=8,max_worst_block_ratio:float=2.0)->FrozenCut:
    """Predeclared maximum precision at nontrivial original-CORRECT rescue.

    Bootstrap the scarcity of true rare positives via 1-hour blocks. The worst
    supported block BAD/good ratio prevents a small number of episodes from
    masquerading as stable precision. No threshold microgrid, one sorted sweep.
    """
    s=np.asarray(score,dtype=float);y=np.asarray(truth,dtype=int);t=np.asarray(utc_ms,dtype=np.int64)
    if not(len(s)==len(y)==len(t)) or not np.isfinite(s).all() or not np.isin(y,[0,1,2]).all():
        raise ValueError('calibration arrays invalid')
    good=(y==0)
    keep=np.ones(len(s),dtype=bool) if valid is None else np.asarray(valid,dtype=bool)
    if len(keep)!=len(s):raise ValueError('CAL validity lengths')
    order=np.flatnonzero(keep)[np.argsort(-s[keep],kind='stable')]
    if len(order)==0:return FrozenCut(None,0,0,0,None,0,'ABSTAIN_NO_ELIGIBLE')
    classes=y[order]
    gc=np.cumsum(classes==0);bc=np.cumsum(classes!=0)
    op=np.cumsum(classes==1);ne=np.cumsum(classes==2)
    blocks=t[order]//3600000
    # Deterministic single-pass exact risk frontier. Never rescore source or
    # retrain nearby model variants. Class labels are CAL-only.
    unique_hours,inverse_hour=np.unique(blocks,return_inverse=True)
    hour_good=np.zeros(len(unique_hours),dtype=np.int32)
    hour_bad=np.zeros(len(unique_hours),dtype=np.int32)
    ends=set(np.r_[np.flatnonzero(np.diff(s[order])!=0),len(order)-1].tolist())
    chosen=None
    for pos in range(len(order)):
        h=int(inverse_hour[pos]);
        if classes[pos]==0:hour_good[h]+=1
        else:hour_bad[h]+=1
        if pos not in ends:continue
        n=int(gc[pos]);bad=int(bc[pos]);
        if n<min_correct or bad>max_bad_per_correct*n:continue
        supported=(hour_good>0)
        nblocks=int(supported.sum())
        if nblocks<min_blocks:continue
        ratios=hour_bad[supported]/hour_good[supported]
        if np.max(ratios)>max_worst_block_ratio:continue
        chosen=(pos,n,bad,int(op[pos]),int(ne[pos]),nblocks)
    if chosen is None:return FrozenCut(None,0,0,0,None,0,'ABSTAIN_NO_PRECISION_TAIL')
    pos,n,bad,o,ne,nb=chosen
    cut=float(s[order[pos]])
    return FrozenCut(cut,n,o,ne,bad/max(n,1),nb,'EMPIRICAL_FROZEN_CAL_ONLY')


def recount(*,q_veto,rescue,truth,eligible):
    q=np.asarray(q_veto,dtype=bool);r=np.asarray(rescue,dtype=bool)
    y=np.asarray(truth,dtype=int);e=np.asarray(eligible,dtype=bool)
    if not(len(q)==len(r)==len(y)==len(e)):raise ValueError('length mismatch')
    if np.any(r&~q) or np.any(r&~e):raise ValueError('rescue outside valid original Q veto')
    original_bad=int(np.sum(q&(y!=0)));original_correct=int(np.sum(q&(y==0)))
    return dict(q_bad=original_bad,q_correct_lost=original_correct,
      correct_rescued=int(np.sum(r&(y==0))),opposite_readmitted=int(np.sum(r&(y==1))),
      neutral_readmitted=int(np.sum(r&(y==2))),
      new_bad=original_bad-int(np.sum(r&(y!=0))),
      new_correct_lost=original_correct-int(np.sum(r&(y==0))))
