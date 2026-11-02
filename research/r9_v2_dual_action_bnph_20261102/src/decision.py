"""Side-symmetric three-class Bayes/NP/Hawkes dual-action policy contract.

The exact same market observation produces BUY and SELL probability triples.
No side inherited from original specialist; WAIT is not a disguised third side.
NP calibration is empirically conservative, not an IID NP finite-sample theorem.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Limits:
    min_correct:float=.80
    max_wrong:float=.20
    min_margin:float=.08
    min_expected_net:float=0.
    max_spread:float=1.50
    min_n_calibration:int=150

@dataclass(frozen=True)
class Prediction:
    side:int
    p_correct:float
    p_incorrect:float
    p_neutral:float
    expected_net:float
    hawkes_edge:float=0.

class DualActionPolicy:
    def __init__(self,buy_threshold=1.,sell_threshold=1.,limits=Limits()):
        self.thresholds={1:buy_threshold,-1:sell_threshold}
        self.limits=limits

    def decide(self,buy:Prediction,sell:Prediction,spread:float):
        if buy.side!=1 or sell.side!=-1:raise ValueError('independent BUY+SELL required')
        if not np.isfinite(spread) or spread>self.limits.max_spread:return 0,'SPREAD'
        # Hawkes supports the side's posterior estimate only if it is calibrated;
        # do not add an arbitrary boost to a learned probability.
        margin=buy.p_correct-sell.p_correct
        acceptable=[]
        for p in (buy,sell):
            if p.p_correct<self.limits.min_correct:continue
            if p.p_correct<=self.thresholds[p.side]:continue
            if p.p_incorrect>self.limits.max_wrong:continue
            if p.expected_net<=self.limits.min_expected_net:continue
            if p.side*margin<self.limits.min_margin:continue
            acceptable.append(p)
        if not acceptable:return 0,'INSUFFICIENT_DIRECTIONAL_EVIDENCE'
        winner=max(acceptable,key=lambda p:(p.expected_net,p.p_correct))
        return winner.side,'BUY' if winner.side==1 else 'SELL'


def calibrate_np(scores,y,alpha=.10,min_bad=150):
    """Side-specific empirical bad-entry cutoff, calibration ONLY.

    Use a conservative finite-sample upper bound for observed exceedance,
    NOT an IID population guarantee (overlapping labels are dependent).
    """
    bad=np.asarray(scores)[np.asarray(y)!=2]
    if len(bad)<min_bad:return float('inf'),dict(status='FAIL_CLOSED',bad_n=len(bad))
    bad=np.sort(bad)
    # Empirical 1-alpha rejection cutoff; strict > prevents tie ambiguity.
    index=min(len(bad)-1,int(np.ceil((1-alpha)*len(bad))))
    return float(bad[index]),dict(status='CALIBRATED_RESEARCH_ONLY',bad_n=len(bad),alpha=alpha,
                                  observed_exceedance=float(np.mean(bad>bad[index])))


def select_dual(p,net,alpha_cutoff,limits=Limits()):
    """Vectorized eligibility-first arbitration (research, not an on-policy fill).

    A BUY whose expected net is negative must not mask an independently
    eligible SELL. Ties/ambiguous simultaneously eligible candidates WAIT.
    """
    p=np.asarray(p,dtype=np.float64);net=np.asarray(net,dtype=np.float64)
    cut=np.asarray(alpha_cutoff,dtype=np.float64)
    if p.ndim!=3 or p.shape[1:]!=(2,3) or net.shape!=p.shape[:2] or cut.shape!=(2,):
        raise ValueError('expected n x 2 x 3 probabilities, n x 2 net, two cutoffs')
    pc=p[:,:,2];wrong=p[:,:,0]
    eligible=(np.isfinite(p).all(axis=2)&np.isfinite(net)&np.isfinite(cut)[None,:]
              &(pc>=limits.min_correct)&(wrong<=limits.max_wrong)
              &(net>limits.min_expected_net)&(pc>cut[None,:]))
    act=np.zeros(len(pc),dtype=np.int8)
    one_buy=eligible[:,0]&~eligible[:,1]
    one_sell=eligible[:,1]&~eligible[:,0]
    act[one_buy]=1;act[one_sell]=-1
    both=eligible[:,0]&eligible[:,1]
    clear=both&(np.abs(pc[:,0]-pc[:,1])>=limits.min_margin)
    act[clear&(net[:,0]>net[:,1])]=1
    act[clear&(net[:,1]>net[:,0])]=-1
    # Equal expected nets break ties only when directional confidence separates.
    tie=clear&(net[:,0]==net[:,1])
    act[tie&(pc[:,0]>pc[:,1])]=1
    act[tie&(pc[:,1]>pc[:,0])]=-1
    return act
