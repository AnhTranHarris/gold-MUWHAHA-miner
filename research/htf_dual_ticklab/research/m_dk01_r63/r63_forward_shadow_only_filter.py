"""R63 source-native +25s UNSUBMITTED-intent filter: SHADOW ONLY, not live/demo approved.
Frozen original Coinexx-Jan-first60 1023-leaf 70-tree student, never fitted R24 oracle at inference.
Model file must match SHA256 18d1da0bb91498bb7481de7a5203aa31205cafecad65b4431945ff0becacc890.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import numpy as np

FROZEN_SHA="18d1da0bb91498bb7481de7a5203aa31205cafecad65b4431945ff0becacc890"
FROZEN_CUTOFF=.9657679504539772

@dataclass(frozen=True)
class ShadowDecision:
    action: str
    p_bad: float | None
    reason: str

class ForesightShadowFilter:
    def __init__(self,model_path,sha256=FROZEN_SHA,cutoff=FROZEN_CUTOFF):
        import lightgbm as lgb
        p=Path(model_path)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=sha256:
            raise ValueError("SOURCE MODEL HASH MISMATCH")
        self.model=lgb.Booster(model_file=str(p))
        if self.model.num_feature()!=283:raise ValueError("WRONG SOURCE FEATURE SCHEMA")
        self.cutoff=cutoff
    def evaluate(self,*,t0_ms,side,first_observed_quote_ms,now_ms,max_feature_observed_ms,
                 features,order_ever_submitted):
        if order_ever_submitted:return ShadowDecision("ABSTAIN",None,"submitted order cannot be vetoed retroactively")
        if side not in (-1,1) or first_observed_quote_ms is None:
            return ShadowDecision("ABSTAIN",None,"invalid side or absent real quote")
        if not t0_ms+25000<=first_observed_quote_ms<t0_ms+26000:
            return ShadowDecision("ABSTAIN",None,"no genuine 25s source quote")
        if max_feature_observed_ms is None or max_feature_observed_ms>first_observed_quote_ms or first_observed_quote_ms>now_ms:
            return ShadowDecision("ABSTAIN",None,"causality/source watermark violation")
        if features is None:return ShadowDecision("ABSTAIN",None,"feature unavailable")
        x=np.asarray(features,dtype=np.float32)
        if x.shape!=(283,) or not np.isfinite(x).all():
            return ShadowDecision("ABSTAIN",None,"invalid original feature schema")
        p=float(self.model.predict(x.reshape(1,-1),num_threads=1)[0])
        if not 0<=p<=1:return ShadowDecision("ABSTAIN",None,"invalid model score")
        return ShadowDecision("VETO_SHADOW" if p>=self.cutoff else "PASS_SHADOW",p,"research only")
