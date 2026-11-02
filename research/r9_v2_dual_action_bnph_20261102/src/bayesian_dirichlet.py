"""Dual-side hierarchical Bayesian class-prior shrinkage.

CORRECT, INCORRECT, NEUTRAL maintain SEPARATE class probabilities by BUY/SELL.
The prior must be fitted on training chronology only and frozen for calibration
and subsequent checks. Optional market-state strata are keyed by *past-only*
context. No future label or teacher data enters live features.
"""
from __future__ import annotations
import numpy as np

class BayesianSidePriors:
    def __init__(self,alpha=1.):
        self.alpha=float(alpha)
        self.counts=np.zeros((2,3),np.int64)
        self.state_counts={}
    def observe(self,side,class_index,state=None):
        j=0 if side==1 else 1 if side==-1 else None
        if j is None or class_index not in (0,1,2):raise ValueError('side/class')
        self.counts[j,class_index]+=1
        if state is not None:
            if state not in self.state_counts:self.state_counts[state]=np.zeros((2,3),np.int64)
            self.state_counts[state][j,class_index]+=1
    def prior(self,side,state=None,shrink=100.):
        j=0 if side==1 else 1 if side==-1 else None
        if j is None:raise ValueError('side')
        a=self.counts[j]+self.alpha
        global_prior=a/a.sum()
        if state is None or state not in self.state_counts:return global_prior
        local=self.state_counts[state][j]
        # Regress sparse regime prior toward full-source historical side prior.
        weights=local+shrink*global_prior
        return weights/weights.sum()
    def shrink_prediction(self,model_three,side,state=None,prior_weight=.10):
        """Partial Bayesian pooling; NOT a calibration guarantee.
        Training must assess this choice on earlier periods, never holdout.
        """
        x=np.asarray(model_three,np.float64)
        if x.shape!=(3,) or not np.isfinite(x).all():raise ValueError('invalid forecast')
        if not 0<=prior_weight<=1:raise ValueError('weight')
        p=self.prior(side,state)
        z=prior_weight*p+(1.-prior_weight)*x
        return z/z.sum()
