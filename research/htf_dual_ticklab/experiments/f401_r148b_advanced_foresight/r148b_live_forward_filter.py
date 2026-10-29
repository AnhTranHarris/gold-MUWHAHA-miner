"""F401-R148B research-only forward-shadow candidate for FILTER08 M-DK-01.

Causal inference contract:
- active base is exact frozen F401-R24 new-unfilled-order shadow;
- current/future original truth is NOT an inference input;
- R148B uses only the exact R24 component tensor plus the 153D R120/R147
  causal state available at the same t0+15 decision clock;
- FILTER08 hindsight is used only to train a teacher-student latent model offline;
  no FILTER08 teacher score/mask is accepted by this runtime API;
- already-filled t0 orders are immutable;
- unknown/OOD source state and risk-monitor breaches fall back to R24.

This is Python forward-shadow code, not an OrderSend implementation or G07/G08/G09 pass.
"""
from __future__ import annotations
from pathlib import Path
import json, math
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from f401_r24_broker_cooperative_shadow import FrozenR24TwoBrokerShadow

THRESHOLDS={
    'coinexx': {'rescue':0.8021619915962219,'hunter':0.9432624578475952},
    'dukascopy': {'rescue':0.7198813557624817,'hunter':0.9287385344505310},
}

class R148ContractError(RuntimeError): pass

def apply_r148b_policy(*, base_action:str, rescue_score:float|None, hunter_score:float|None,
                       broker:str, override_enabled:bool=True)->tuple[str,str]:
    """Pure policy combiner. Does not accept truth or future outcome."""
    if broker not in THRESHOLDS: return base_action,'UNKNOWN_BROKER_R24_FALLBACK'
    if not override_enabled: return base_action,'R148_OVERRIDE_DISABLED_R24_FALLBACK'
    cfg=THRESHOLDS[broker]
    if base_action=='VETO_NEW_UNFILLED_ORDER':
        if rescue_score is None or not np.isfinite(rescue_score): return base_action,'INVALID_RESCUE_SCORE_R24_FALLBACK'
        if rescue_score>=cfg['rescue']: return 'RELEASE_TO_SEPARATE_EXECUTION_CHECK','R148_RESCUE'
        return base_action,'R24_VETO_RETAINED'
    if base_action=='RELEASE_TO_SEPARATE_EXECUTION_CHECK':
        if hunter_score is None or not np.isfinite(hunter_score): return base_action,'INVALID_HUNTER_SCORE_R24_FALLBACK'
        if hunter_score>=cfg['hunter']: return 'VETO_NEW_UNFILLED_ORDER','R148_RESIDUAL_HUNTER'
        return base_action,'R24_RELEASE_RETAINED'
    return base_action,'NONDECISION_R24_PASSTHROUGH'

class MaturedRiskMonitor:
    """Causal demo safety monitor: only already-matured past labels may update it."""
    def __init__(self,min_correct:int=2000,max_correct_veto_rate:float=0.022,z:float=2.576):
        self.min_correct=int(min_correct); self.max_rate=float(max_correct_veto_rate); self.z=float(z)
        self.correct_seen=0; self.correct_vetoed=0
    def observe_matured(self,*,original_correct:bool,candidate_veto:bool):
        if original_correct:
            self.correct_seen+=1
            self.correct_vetoed+=int(bool(candidate_veto))
    def upper_wilson(self)->float:
        n=self.correct_seen
        if n==0:return 1.0
        p=self.correct_vetoed/n;z=self.z;den=1+z*z/n
        center=(p+z*z/(2*n))/den
        rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        return min(1.0,center+rad)
    @property
    def override_allowed(self)->bool:
        return self.correct_seen<self.min_correct or self.upper_wilson()<=self.max_rate

class R148BAdvancedForesightFilter(FrozenR24TwoBrokerShadow):
    N_COMMON=153
    N_COMPONENTS=15
    def __init__(self,r24_folder:str|Path,r148_folder:str|Path,*,broker:str,domain_guard:bool=True):
        super().__init__(r24_folder,broker=broker)
        self.r148=Path(r148_folder);self.domain_guard=bool(domain_guard)
        self.teacher_lgb=lgb.Booster(model_file=str(self.r148/f'R148_{broker}_FILTER08_TEACHER_STUDENT_LGB.txt'))
        self.teacher_xgb=xgb.XGBRegressor();self.teacher_xgb.load_model(self.r148/f'R148_{broker}_FILTER08_TEACHER_STUDENT_XGB.json')
        self.rescue_lgb=lgb.Booster(model_file=str(self.r148/f'R148B_{broker}_R_LGB.txt'))
        self.hunter_lgb=lgb.Booster(model_file=str(self.r148/f'R148B_{broker}_H_LGB.txt'))
        self.rescue_xgb=xgb.XGBClassifier();self.rescue_xgb.load_model(self.r148/f'R148B_{broker}_R_XGB.json')
        self.hunter_xgb=xgb.XGBClassifier();self.hunter_xgb.load_model(self.r148/f'R148B_{broker}_H_XGB.json')
        for mod,n in ((self.teacher_lgb,168),(self.rescue_lgb,169),(self.hunter_lgb,169)):
            if mod.num_feature()!=n: raise R148ContractError(f'model schema mismatch expected {n}')
        d=json.loads((self.r148/'R148_DOMAIN_FINGERPRINT.json').read_text())[broker]
        self.domain_mean=np.asarray(d['mean'],np.float32);self.domain_std=np.asarray(d['std'],np.float32)
        self.domain_cut=float(d['ood_mean_sq_z_clip25_q999'])
        if self.domain_mean.shape!=(153,) or self.domain_std.shape!=(153,):raise R148ContractError('domain schema mismatch')
        self.risk_monitor=MaturedRiskMonitor()

    def _components(self,*,t0:int,decision_msc:int,original_side:int,base_r16:bool,
                    opposite:float,neutral:float,right_guard:float,valid_native_quote:bool=True)->np.ndarray:
        x=self.feature_vector(t0=t0,decision_msc=decision_msc,original_side=original_side,
                              base_r16=base_r16,opposite=opposite,neutral=neutral,
                              right_guard=right_guard,valid_native_quote=valid_native_quote)
        heads=np.asarray([np.float32(h.predict(x,num_threads=1)[0]) for h in self.models],np.float32)
        g02=np.float32(self.guard.predict(x,num_threads=1)[0]);up=np.float32(heads.mean(dtype=np.float32))
        baseline=np.float32(up*np.clip(np.float32(1)-self.guard_mult*g02,np.float32(0),np.float32(1)))
        gx=np.asarray([np.float32(h.predict(x,num_threads=1)[0]) for h in self.r24_models],np.float32)
        if self.broker=='coinexx':
            risk=np.float32(np.clip(baseline-self.cx_guard_amp*np.max(gx),0,1))
        else:risk=baseline
        return np.asarray([risk,up,baseline,*heads,g02,*gx,np.float32(opposite),np.float32(neutral),np.float32(right_guard),np.float32(base_r16)],np.float32)

    def _domain_score(self,common:np.ndarray)->float:
        z=(common-self.domain_mean)/self.domain_std
        return float(np.mean(np.minimum(z*z,np.float32(25.0))))

    @staticmethod
    def _geom(a:float,b:float)->float:
        return float(math.sqrt(max(0.0,min(1.0,a))*max(0.0,min(1.0,b))))

    def decision(self,*,common_state_153,broker:str,t0:int,decision_msc:int,source_quote_msc:int,
                 original_side:int,original_quote_ordinal:int,source_quote_ordinal_reconciled:bool,
                 first_genuine_native_quote_verified:bool,base_r16:bool,opposite:float,neutral:float,
                 right_guard:float,already_filled:bool,valid_native_quote:bool=True)->dict:
        base=super().shadow_decision(broker=broker,t0=t0,decision_msc=decision_msc,source_quote_msc=source_quote_msc,
             original_side=original_side,original_quote_ordinal=original_quote_ordinal,
             source_quote_ordinal_reconciled=source_quote_ordinal_reconciled,
             first_genuine_native_quote_verified=first_genuine_native_quote_verified,
             base_r16=base_r16,opposite=opposite,neutral=neutral,right_guard=right_guard,
             already_filled=already_filled,valid_native_quote=valid_native_quote)
        if base.get('action') not in ('VETO_NEW_UNFILLED_ORDER','RELEASE_TO_SEPARATE_EXECUTION_CHECK'):
            return {**base,'r148_mode':'R24_PASSTHROUGH_NONDECISION'}
        common=np.asarray(common_state_153,np.float32)
        if common.shape!=(153,) or not np.isfinite(common).all():
            return {**base,'r148_mode':'R24_FALLBACK_INVALID_COMMON_STATE'}
        comp=self._components(t0=t0,decision_msc=decision_msc,original_side=original_side,base_r16=base_r16,
                              opposite=opposite,neutral=neutral,right_guard=right_guard,valid_native_quote=valid_native_quote)
        if abs(float(comp[0])-float(base['score']))>2e-6:raise R148ContractError('R24 component reproduction drift')
        dscore=self._domain_score(common)
        if self.domain_guard and dscore>self.domain_cut:
            return {**base,'r148_mode':'R24_FALLBACK_OOD','r148_domain_score':dscore,'r148_domain_cut':self.domain_cut}
        z168=np.concatenate([comp,common]).astype(np.float32).reshape(1,-1)
        ts=self._geom(float(self.teacher_lgb.predict(z168,num_threads=1)[0]),float(self.teacher_xgb.predict(z168)[0]))
        z169=np.concatenate([z168[0],np.asarray([ts],np.float32)]).reshape(1,-1)
        rescue=hunter=None
        if base['action']=='VETO_NEW_UNFILLED_ORDER':
            rescue=self._geom(float(self.rescue_lgb.predict(z169,num_threads=1)[0]),float(self.rescue_xgb.predict_proba(z169)[0,1]))
        else:
            hunter=self._geom(float(self.hunter_lgb.predict(z169,num_threads=1)[0]),float(self.hunter_xgb.predict_proba(z169)[0,1]))
        action,reason=apply_r148b_policy(base_action=base['action'],rescue_score=rescue,hunter_score=hunter,
                                         broker=self.broker,override_enabled=self.risk_monitor.override_allowed)
        return {**base,'action':action,'r148_mode':'R148B_FROZEN_FORWARD_SHADOW','r148_reason':reason,
                'r148_teacher_student':ts,'r148_rescue_score':rescue,'r148_hunter_score':hunter,
                'r148_domain_score':dscore,'r148_domain_cut':self.domain_cut,
                'r148_risk_monitor_upper':self.risk_monitor.upper_wilson(),
                'r148_override_allowed':self.risk_monitor.override_allowed,
                'research_status':'UNAPPROVED_NO_ORDERSEND'}
