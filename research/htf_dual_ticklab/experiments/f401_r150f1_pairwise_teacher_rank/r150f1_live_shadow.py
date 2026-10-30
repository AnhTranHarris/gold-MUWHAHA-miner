"""F401 R150F1 source-only nonoverriding autonomous T0 candidate.
No teacher, class truth, risk-policy override or OrderSend in inference.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import lightgbm as lgb

ACTIONS={'VETO_NEW_UNFILLED_ORDER','RELEASE_TO_SEPARATE_EXECUTION_CHECK'}
BROKERS={'coinexx','dukascopy'}
class R150F1Shadow:
    def __init__(self, model_dir, broker):
        self.broker=broker
        self.rank=None;self.binary=None
        if broker in BROKERS:
            p=Path(model_dir)
            self.rank=lgb.Booster(model_file=str(p/f'{broker}_T0_ORIGINAL_PAIR_RANK.txt'))
            self.binary=lgb.Booster(model_file=str(p/f'{broker}_T0_ORIGINAL_CLASS.txt'))
            assert self.rank.num_feature()==self.binary.num_feature()==436
    def predict(self, *, broker, parent_action, already_filled, first_quote_verified,
                t0_ms, quote_ms, side, source_state_436, asof_provenance_verified):
        base={'action':parent_action,'r150f1_override_active':False,'research_status':'UNAPPROVED_SHADOW'}
        if already_filled or parent_action not in ACTIONS:
            return {**base,'reason':'FILLED_OR_NONDECISION_IMMUTABLE'}
        if broker!=self.broker or broker not in BROKERS or self.rank is None:
            return {**base,'reason':'UNKNOWN_BROKER_FALLBACK'}
        if not(first_quote_verified and asof_provenance_verified and
                t0_ms+15000<=quote_ms<t0_ms+16000 and side in (-1,1)):
            return {**base,'reason':'INVALID_CAUSAL_SOURCE_CLOCK'}
        x=np.asarray(source_state_436,dtype=np.float32)
        if x.shape!=(436,) or not np.isfinite(x).all():
            return {**base,'reason':'INVALID_STATE_OR_MISSING'}
        a=float(self.rank.predict(x[None],num_threads=1)[0]);b=float(self.binary.predict(x[None],num_threads=1)[0])
        return {**base,'reason':'TEACHER_FREE_T0_TELEMETRY_ONLY',
                't0_pair_rank_score':a,'t0_correct_classifier_score':b,
                't0_fusion_score':(a+b)/2}
