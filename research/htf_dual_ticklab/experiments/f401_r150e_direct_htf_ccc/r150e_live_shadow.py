"""F401-R150E shadow-only full causal HTF/ordered-path CCC.

RESEARCH-ONLY; never overrides frozen R148B. Source prefixes must be authenticated
by the upstream R120/R147/R149 publishers. No original truth, teacher score,
post-decision future result or live filled-order modification in inference.

Input 403D = frozen R150C 304D source + R150D 57D strict t0->15s path
+ R150E 36D completed-HTF/cross-scale + frozen causal parent 6D.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import lightgbm as lgb

# June-selected cut under EXACT prior R150D comparability rule; NOT live policy.
RESEARCH_CUT={'coinexx':0.1279180757701397,'dukascopy':0.12218549020588404}
_ACTIONS={'VETO_NEW_UNFILLED_ORDER','RELEASE_TO_SEPARATE_EXECUTION_CHECK'}

class R150EFullStateShadow:
    def __init__(self, broker:str, model_dir:str|Path):
        self.broker=broker
        self.models=[]
        if broker not in RESEARCH_CUT:return
        for seed in (15071,15073):
            mdl=lgb.Booster(model_file=str(Path(model_dir)/f'{broker}_T0_DIRECT_HTF_CCC_seed{seed}.txt'))
            if mdl.num_feature()!=403:raise ValueError('R150E schema drift, expected 403D')
            self.models.append(mdl)

    def observe(self,*, broker:str,parent_action:str,t0_ms:int,decision_ms:int,
                first_quote_verified:bool,already_filled:bool,
                source304,parent6,path57,htf36,
                path_prefix_end_exclusive_ms:int,completed_htf_verified:bool)->dict:
        out={'action':parent_action,'r150e_override_active':False,'status':'UNAPPROVED_TELEMETRY_ONLY'}
        if already_filled or parent_action not in _ACTIONS:
            return {**out,'reason':'FILLED_OR_NONDECISION_IMMUTABLE'}
        if broker!=self.broker or broker not in RESEARCH_CUT:
            return {**out,'reason':'UNKNOWN_BROKER_FALLBACK'}
        if not (first_quote_verified and completed_htf_verified and
                t0_ms+15000<=decision_ms<t0_ms+16000 and
                path_prefix_end_exclusive_ms==t0_ms+15000):
            return {**out,'reason':'BAD_CLOCK_OR_PUBLISHER_PROVENANCE'}
        blocks=[np.asarray(x,dtype=np.float32) for x in (source304,path57,htf36,parent6)]
        if [b.shape for b in blocks]!=[(304,),(57,),(36,),(6,)]:
            return {**out,'reason':'BAD_FEATURE_SCHEMA'}
        if not all(np.isfinite(b).all() for b in blocks):
            return {**out,'reason':'INVALID_CAUSAL_STATE'}
        x=np.concatenate(blocks)[None,:]
        score=float(np.mean([m.predict(x,num_threads=1)[0] for m in self.models]))
        if not np.isfinite(score):return {**out,'reason':'NONFINITE_SCORE'}
        return {**out,'reason':'TELEMETRY_ONLY','hypothetical_ccc_score':score,
                'june_frozen_cut':RESEARCH_CUT[broker],
                'hypothetical_rescue':bool(parent_action=='VETO_NEW_UNFILLED_ORDER' and
                                           score>=RESEARCH_CUT[broker])}
