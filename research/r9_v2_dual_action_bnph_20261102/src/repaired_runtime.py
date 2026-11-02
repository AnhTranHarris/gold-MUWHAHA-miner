"""Fail-closed runtime policy for the repaired R9 v2 entry architecture."""
from __future__ import annotations
import hashlib
from pathlib import Path
import numpy as np
from decision import Limits,Prediction,OpportunityPrediction,AsymmetricEntryPolicy
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT

def _sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

class RepairedDualPolicy:
    """Independent opportunity/BUY/SELL models plus frozen chronological gates.

    The policy remains research-shadow only unless accept_for_research=True.
    That flag never bypasses probability, opportunity, expected-net or spread gates.
    """
    feature_version=FEATURE_VERSION
    def __init__(self,opportunity_model,buy_model,sell_model,policy_file,accept_for_research=False):
        import lightgbm as lgb
        model_paths=(Path(opportunity_model),Path(buy_model),Path(sell_model))
        self.opportunity=lgb.Booster(model_file=str(model_paths[0]))
        self.buy=lgb.Booster(model_file=str(model_paths[1]));self.sell=lgb.Booster(model_file=str(model_paths[2]))
        with np.load(policy_file) as d:
            version=str(d['feature_version'][0]);count=int(d['feature_count'][0])
            if version!=FEATURE_VERSION or count!=REPAIRED_FEATURE_COUNT:raise ValueError('repaired feature-version mismatch')
            self.prior_counts=d['prior_counts'].astype(np.float64);self.prior_weight=float(d['prior_weight'][0])
            self.opportunity_cutoff=float(d['opportunity_cutoff'][0]);self.side_cutoffs=d['side_cutoffs'].astype(np.float64)
            self.payoff=d['payoff_lcb_bins'].astype(np.float64)
            if 'component_model_sha256' not in d.files or 'component_model_role' not in d.files:
                raise ValueError('policy missing v5 component model identity')
            roles=[str(x) for x in d['component_model_role']]
            if roles!=['opportunity','buy','sell']:raise ValueError('policy component role mismatch')
            expected=[str(x) for x in d['component_model_sha256']]
            actual=[_sha256(p) for p in model_paths]
            if expected!=actual:raise ValueError('policy/component model SHA256 mismatch')
            self.iso={'opp':(d['opp_iso_x'].copy(),d['opp_iso_y'].copy())}
            for j in (0,1):
                for kind in ('correct','wrong'):
                    self.iso[(j,kind)]=(d[f'side{j}_{kind}_iso_x'].copy(),d[f'side{j}_{kind}_iso_y'].copy())
        for mdl in (self.opportunity,self.buy,self.sell):
            if mdl.num_feature()!=REPAIRED_FEATURE_COUNT:raise ValueError('model feature mismatch')
        self.priors=(self.prior_counts+1.)/(self.prior_counts.sum(axis=1,keepdims=True)+3.)
        self.accept_for_research=bool(accept_for_research)
        self.limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.08,min_expected_net=0.,min_opportunity=.80)
        self.selector=AsymmetricEntryPolicy(self.side_cutoffs[0],self.side_cutoffs[1],self.opportunity_cutoff,self.limits)
    @staticmethod
    def _interp(pair,x):return float(np.interp(float(x),pair[0],pair[1]))
    def _side(self,mdl,j,side,x):
        raw=np.asarray(mdl.predict(x.reshape(1,-1),num_threads=1)[0],np.float64)
        raw=(1.-self.prior_weight)*raw+self.prior_weight*self.priors[j];raw/=raw.sum()
        pc=self._interp(self.iso[(j,'correct')],raw[2]);pw=self._interp(self.iso[(j,'wrong')],raw[0])
        excess=max(1.,pc+pw);pc/=excess;pw/=excess;pn=max(0.,1.-pc-pw)
        k=min(self.payoff.shape[1]-1,int(np.clip(pc,0.,1.)*self.payoff.shape[1]))
        return Prediction(side,pc,pw,pn,float(self.payoff[j,k]))
    def evaluate(self,x):
        x=np.asarray(x,np.float32)
        if x.shape!=(REPAIRED_FEATURE_COUNT,) or not np.isfinite(x).all():raise ValueError('repaired runtime feature mismatch')
        po=self._interp(self.iso['opp'],self.opportunity.predict(x.reshape(1,-1),num_threads=1)[0])
        return OpportunityPrediction(po),self._side(self.buy,0,1,x),self._side(self.sell,1,-1,x)
    def action(self,x,spread):
        opp,buy,sell=self.evaluate(x)
        side,reason=self.selector.decide(opp,buy,sell,spread)
        if not self.accept_for_research:return 0,'FAIL_CLOSED_RESEARCH_ONLY'
        return side,reason
