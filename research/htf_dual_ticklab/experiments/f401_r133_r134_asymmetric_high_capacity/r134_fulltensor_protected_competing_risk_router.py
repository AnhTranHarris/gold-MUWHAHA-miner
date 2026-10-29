"""F401-R134 research-only full-tensor protected competing-risk router.
No trained weights. No live/demo authority. No broker order transmission.
"""
from dataclasses import dataclass
from typing import Mapping,Protocol,Sequence
from math import isfinite
import hashlib,json
HORIZONS_S=(1,2,3,5,8,10,12,15)

class TensorHead(Protocol):
    def predict(self,features:Mapping[str,object],horizon_s:int,expert_key:str)->Mapping[str,float]: ...

@dataclass(frozen=True)
class RiskBudget:
    max_correct_false_veto_rate:float=.008278
    min_bad_correct_odds:float=40.0
    min_bad_lower:float=.90
    max_correct_upper:float=.025
    neutral_weight:float=1.0
    opposite_weight:float=1.0
    def __post_init__(self):
        if not 0<self.max_correct_false_veto_rate<=.008278:raise ValueError('correct-loss cap')
        if self.min_bad_correct_odds<40:raise ValueError('bad/correct evidence')
        if not 0<self.min_bad_lower<=1 or not 0<=self.max_correct_upper<1:raise ValueError('bounds')

@dataclass(frozen=True)
class FrozenCalibration:
    model_sha:str;calibration_sha:str;feature_contract_sha:str
    trained_broker_months:tuple[str,...];selected_broker_months:tuple[str,...]
    def __post_init__(self):
        if not self.model_sha or not self.calibration_sha or not self.feature_contract_sha:raise ValueError('provenance')
        if set(self.trained_broker_months)&set(self.selected_broker_months):raise ValueError('fit/cal overlap')

@dataclass(frozen=True)
class RouterState:
    event_id:int;original_t0_ms:int;decision_asof_ms:int;side:int;broker:str
    session_bucket:int;regime_id:int;f392_base_veto:bool;features_178:Sequence[float]
    source_sha:str;feature_contract_sha:str;original_truth_used:bool=False;order_was_submitted_at_t0:bool=False
    def validate(self):
        if self.side not in (-1,1):raise ValueError('side')
        if self.broker not in ('coinexx','dukascopy'):raise ValueError('broker')
        if self.decision_asof_ms<self.original_t0_ms or self.decision_asof_ms>self.original_t0_ms+20000:raise ValueError('clock')
        if len(self.features_178)!=178 or any(not isfinite(float(x)) for x in self.features_178):raise ValueError('full tensor')
        if self.original_truth_used:raise ValueError('truth leakage')
        if self.order_was_submitted_at_t0:raise ValueError('retroactive veto')
        if not self.source_sha or not self.feature_contract_sha:raise ValueError('provenance')

class ProtectedCompetingRiskRouter:
    def __init__(self,model:TensorHead,frozen:FrozenCalibration,budget:RiskBudget):
        self.model=model;self.frozen=frozen;self.budget=budget
    @staticmethod
    def expert_key(s):return f'{s.broker}|side{s.side:+d}|sess{s.session_bucket}|reg{s.regime_id}'
    def decide(self,s:RouterState,horizon_s:int):
        s.validate()
        if horizon_s not in HORIZONS_S:raise ValueError('horizon')
        if s.feature_contract_sha!=self.frozen.feature_contract_sha:raise ValueError('feature contract')
        p={k:float(v) for k,v in self.model.predict({'x178':tuple(map(float,s.features_178)),'side':s.side,'broker':s.broker,'session_bucket':s.session_bucket,'regime_id':s.regime_id,'asof_ms':s.decision_asof_ms},horizon_s,self.expert_key(s)).items()}
        req=('correct','opposite','neutral','correct_upper','opposite_lower','neutral_lower','support')
        if any(k not in p for k in req):raise ValueError('missing class head')
        if abs(p['correct']+p['opposite']+p['neutral']-1)>1e-5:raise ValueError('not normalized')
        bad_lower=self.budget.opposite_weight*p['opposite_lower']+self.budget.neutral_weight*p['neutral_lower']
        odds=bad_lower/max(p['correct_upper'],1e-12)
        if s.f392_base_veto:
            action='VETO_INTENT';reason='F392_BASE_HUNTER_SHADOW'
        elif bad_lower>=self.budget.min_bad_lower and odds>=self.budget.min_bad_correct_odds and p['correct_upper']<=self.budget.max_correct_upper and p['support']>=.5:
            action='VETO_INTENT';reason='FULL_TENSOR_BAD_LOWER_BOUND_WITH_CORRECT_GUARD'
        elif horizon_s<15:
            action='CONTINUE_OBSERVING';reason='AMBIGUOUS_DO_NOT_GUESS'
        else:
            action='RELEASE_INTENT';reason='CORRECT_PROTECTED_OR_BAD_EVIDENCE_INSUFFICIENT'
        return {'event_id':s.event_id,'action':action,'reason':reason,'horizon_s':horizon_s,'bad_lower':bad_lower,'correct_upper':p['correct_upper'],'bad_correct_lower_odds':odds,'order_sent':False,'original_truth_used':False}

class SequentialVOIController:
    def __init__(self,router):self.router=router
    def run(self,states):
        last=None
        for h in HORIZONS_S:
            if h not in states:continue
            last=self.router.decide(states[h],h)
            if last['action'] in ('VETO_INTENT','RELEASE_INTENT'):return last
        return last or {'action':'EXPIRE_INTENT','order_sent':False}

def feature_contract_sha(names):
    if len(names)!=178:raise ValueError('expected 178 names')
    return hashlib.sha256(json.dumps(list(names),separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
