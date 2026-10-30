"""F401-R150F2 teacher-free physical VOI telemetry only.

No teacher score, original class/truth, future ticks, runtime order action, or
MT5 OrderSend. No parent override even if June-frozen T0 cut is passed.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import math
import numpy as np
import lightgbm as lgb

FROZEN_CUTS={'coinexx': None,'dukascopy': 0.024837782237593725}

@dataclass(frozen=True)
class ShadowObservation:
    parent_action: str
    score: float | None
    would_observe_250ms: bool
    override_active: bool
    status: str

class R150F2CausalVOI:
    def __init__(self, model_dir: str | Path, broker: str):
        self.broker=broker;self.cut=FROZEN_CUTS.get(broker)
        self.model=None
        if broker in FROZEN_CUTS:
            self.model=lgb.Booster(model_file=str(Path(model_dir)/f'R150F2_{broker}_T0_VOI.txt'))
            if self.model.num_feature()!=24:raise ValueError('incorrect T0 source-only input schema')

    def shadow(self, *, broker: str,parent_action: str,t0_ms: int,decision_quote_ms: int,
               verified_first_quote: bool,source_state_published_ms: int,source24,
               already_submitted_or_filled: bool) -> ShadowObservation:
        immutable=ShadowObservation(parent_action,None,False,False,'R148B_PARENT_IMMUTABLE')
        if already_submitted_or_filled:return immutable
        if broker!=self.broker or broker not in FROZEN_CUTS:return immutable
        if not verified_first_quote:return immutable
        if not(t0_ms+15000<=decision_quote_ms<t0_ms+16000):return immutable
        if source_state_published_ms>decision_quote_ms:return immutable
        if parent_action!='VETO_NEW_UNFILLED_ORDER':return immutable
        x=np.asarray(source24,dtype=np.float32)
        if x.shape!=(24,) or not np.isfinite(x).all():return immutable
        s=float(self.model.predict(x[None,:],num_threads=1)[0])
        if not math.isfinite(s):return immutable
        will=self.cut is not None and s>=self.cut
        return ShadowObservation(parent_action,s,bool(will),False,'RESEARCH_TELEMETRY_ONLY_NO_NEW_INTENT')
