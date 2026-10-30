"""F401-R150D restored-source-path CCC shadow, with immutable R148B action.

No FILTER08 hindsight teacher, future +30-32 truth or future quote enters inference.
Research-only, UNAPPROVED; no OrderSend or active override. First native quote
and source timestamp prefix must be independently authenticated by parent.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np, lightgbm as lgb
from r150d_live_shadow import R150DPhysicalShadow

# June-only predetermined research thresholds, NEVER authorized live veto/rescue
RESEARCH_CUT={'coinexx':0.11995184049010277,'dukascopy':0.13210355274379265}

class R150DRestoredPathShadow(R150DPhysicalShadow):
    def __init__(self,broker:str,model_dir:str|Path):
        super().__init__(broker,model_dir)
        self.path_guard=None
        if broker in RESEARCH_CUT:
            self.path_guard=lgb.Booster(model_file=str(Path(model_dir)/f'{broker}_T0_RESTORED_57D_PATH_GUARD.txt'))
            if self.path_guard.num_feature()!=370:
                raise ValueError('expected 304D state + 6D parent + 3D physical + 57D t0 prefix')

    def observe_path(self,*,broker:str,parent_action:str,t0_ms:int,
                     decision_ms:int,first_quote_verified:bool,already_filled:bool,
                     original_side:int,source304,parent6,path57,
                     path_prefix_end_exclusive_ms:int)->dict:
        base=super().observe(broker=broker,parent_action=parent_action,
          t0_ms=t0_ms,decision_ms=decision_ms,
          first_quote_verified=first_quote_verified,already_filled=already_filled,
          source304=source304,parent6=parent6,original_side=original_side)
        if base.get('reason')!='TELEMETRY_ONLY' or self.path_guard is None:
            return {**base,'r150d_path_status':'PARENT_ONLY_FALLBACK'}
        if path_prefix_end_exclusive_ms!=t0_ms+15000:
            return {**base,'r150d_path_status':'PATH_PREFIX_PROVENANCE_FAILURE'}
        path=np.asarray(path57,dtype=np.float32)
        if path.shape!=(57,) or not np.isfinite(path).all():
            return {**base,'r150d_path_status':'PATH_STATE_INVALID'}
        q=np.array([base[k] for k in ('action_time_midpoint_favorable_first_prob',
           'action_time_midpoint_adverse_first_prob','action_time_midpoint_censored_prob')],dtype=np.float32)
        X=np.concatenate([np.asarray(source304,dtype=np.float32),
                          np.asarray(parent6,dtype=np.float32),q,path])[None,:]
        score=float(self.path_guard.predict(X,num_threads=1)[0])
        if not np.isfinite(score):return {**base,'r150d_path_status':'SCORE_INVALID'}
        return {**base,'r150d_path_status':'RESEARCH_TELEMETRY_ONLY',
                'hypothetical_ccc_score':score,
                'june_frozen_research_cut':RESEARCH_CUT[broker],
                'hypothetical_rescue':bool(score>=RESEARCH_CUT[broker] and parent_action=='VETO_NEW_UNFILLED_ORDER'),
                'r150d_override_active':False}
