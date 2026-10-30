"""F401-R150D teacher-free physical continuation / CCC shadow.

Unapproved research. The ONLY action authority is the pre-existing frozen R148B
parent. All R150D proposals are telemetry until owner approves verified forward
month, MQL5 parity and shared-capital gates. The historical FILTER08 teacher is
neither imported nor accepted in this runtime interface.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import lightgbm as lgb

class CausalClockError(ValueError):pass

class R150DPhysicalShadow:
    def __init__(self, broker: str,model_dir: str|Path):
        self.broker=broker
        if broker not in ('coinexx','dukascopy'):
            self.physics=None;self.guard=None;return
        p=Path(model_dir)
        self.physics=lgb.Booster(model_file=str(p/f'{broker}_T0_PHYSICAL_FP.txt'))
        self.guard=lgb.Booster(model_file=str(p/f'{broker}_T0_SOURCE_PHYSICAL_GUARD.txt'))
        if self.physics.num_feature()!=304 or self.guard.num_feature()!=313:
            raise CausalClockError('schema drift: 304 source, 6 parent, 3 physical')

    @staticmethod
    def validate(*,t0_ms:int,decision_ms:int,first_quote_verified:bool,
                 already_filled:bool,source304,parent6,original_side:int):
        if already_filled:return 'FILLED_IMMUTABLE'
        if not first_quote_verified or not (t0_ms+15000<=decision_ms<t0_ms+16000):
            return 'MISSING_NATIVE_DECISION_QUOTE'
        x=np.asarray(source304,np.float32);p=np.asarray(parent6,np.float32)
        if x.shape!=(304,) or p.shape!=(6,) or not (np.isfinite(x).all() and np.isfinite(p).all()):
            return 'INVALID_SOURCE_STATE'
        if original_side not in (-1,1) or int(p[-1])!=original_side:return 'SIDE_MISMATCH'
        return 'VALID'

    def observe(self,*,broker:str,parent_action:str,t0_ms:int,decision_ms:int,
                first_quote_verified:bool,already_filled:bool,source304,parent6,
                original_side:int)->dict:
        out={'action':parent_action,'r150d_override_active':False,
             'research_status':'UNAPPROVED_PARENT_UNCHANGED'}
        if broker!=self.broker or self.physics is None:
            return {**out,'reason':'UNKNOWN_BROKER_PARENT_FALLBACK'}
        status=self.validate(t0_ms=t0_ms,decision_ms=decision_ms,
         first_quote_verified=first_quote_verified,already_filled=already_filled,
         source304=source304,parent6=parent6,original_side=original_side)
        if status!='VALID':return {**out,'reason':status}
        x=np.asarray(source304,np.float32).reshape(1,-1)
        p=np.asarray(parent6,np.float32).reshape(1,-1)
        phys=np.asarray(self.physics.predict(x,num_threads=1)[0],np.float32)
        if phys.shape!=(3,) or not np.isfinite(phys).all() or abs(float(phys.sum())-1)>1e-4:
            return {**out,'reason':'INVALID_PHYSICAL_POSTERIOR'}
        fp=np.hstack([x,p,phys.reshape(1,-1)]).astype(np.float32)
        cert=float(self.guard.predict(fp,num_threads=1)[0])
        if not np.isfinite(cert):return {**out,'reason':'INVALID_CCC_SCORE'}
        return {**out,'reason':'TELEMETRY_ONLY',
            'action_time_midpoint_favorable_first_prob':float(phys[0]),
            'action_time_midpoint_adverse_first_prob':float(phys[1]),
            'action_time_midpoint_censored_prob':float(phys[2]),
            'correct_continuation_certificate_score':cert}
