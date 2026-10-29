"""F401-R147 research-only foresight wrapper around the frozen R24 core.

The active decision is deliberately unchanged R24. New R147 source-only models are
shadow observers only because broker-heldout audits did not earn promotion.
All decisions apply only to a NEW order that is still unfilled at the first genuine
native quote in t0+[15s,16s). No current/future truth is accepted by this API.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import lightgbm as lgb

class R147ContractError(RuntimeError): pass

class R147ForesightFilter:
    N_COMMON=153
    def __init__(self, r24_core, *, universal_model: str|Path|None=None,
                 meta_model: str|Path|None=None):
        self.r24=r24_core
        self.universal=lgb.Booster(model_file=str(universal_model)) if universal_model else None
        self.meta=lgb.Booster(model_file=str(meta_model)) if meta_model else None
        if self.universal is not None and self.universal.num_feature()!=self.N_COMMON:
            raise R147ContractError('universal model schema mismatch')
        if self.meta is not None and self.meta.num_feature()!=self.N_COMMON+1:
            raise R147ContractError('meta model schema mismatch')

    @staticmethod
    def _common(x):
        x=np.asarray(x,dtype=np.float32)
        if x.shape!=(R147ForesightFilter.N_COMMON,) or not np.isfinite(x).all():
            raise R147ContractError('153D causal common state required')
        return x

    def decision(self, *, common_state_153, r24_frozen_score: float|None=None, **r24_kwargs):
        base=self.r24.shadow_decision(**r24_kwargs)
        x=self._common(common_state_153)
        shadow={}
        if self.universal is not None:
            shadow['universal_sourceonly_bad_probability']=float(self.universal.predict(x.reshape(1,-1),num_threads=1)[0])
        if self.meta is not None:
            if r24_frozen_score is None or not np.isfinite(r24_frozen_score):
                raise R147ContractError('finite frozen R24 score required for meta observer')
            xm=np.r_[np.float32(r24_frozen_score),x].astype(np.float32)
            shadow['r24_multitrend_meta_bad_probability']=float(self.meta.predict(xm.reshape(1,-1),num_threads=1)[0])
        return {**base,'r147_mode':'FROZEN_R24_CORE__R147_OBSERVERS_SHADOW_ONLY',
                'r147_shadow':shadow,'r147_override_active':False}
