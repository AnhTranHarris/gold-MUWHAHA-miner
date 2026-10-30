"""F401-R149 additive causal Bayesian/NP foresight telemetry, UNAPPROVED.

Runtime observes a parent R148B decision for a NEW unsubmitted intent at the
FIRST verified native t0+[15,16) quote.  The HMM/Kalman/technical state was
published strictly from ticks < decision quote, and the parent score is causal.
The privileged oracle has NO runtime input.  All R149 model outputs are SHADOW
ONLY and cannot alter the parent decision.  Unrecognized brokers fall back.

The input 'causal_state_179' is 159D technical geometry + 20D recursive state.
Training code and exact event-mask receipts are preserved separately.
"""
from __future__ import annotations
import math,pathlib
import numpy as np
import lightgbm as lgb

MODEL_SUFFIX={'coinexx':'FINAL_COINEXX','dukascopy':'FINAL_DUKASCOPY'}
ACTIONS={'VETO_NEW_UNFILLED_ORDER','RELEASE_TO_SEPARATE_EXECUTION_CHECK'}
class R149StateError(RuntimeError):pass

class FrozenR149CausalShadow:
 def __init__(self,model_dir:str|pathlib.Path,broker:str):
  self.broker=broker
  self.models={}
  if broker not in MODEL_SUFFIX:return
  root=pathlib.Path(model_dir);prefix=MODEL_SUFFIX[broker]
  for kind,seeds in [('teacher',(14911,14912)),('rescue',(14921,14922)),('hunter',(14921,14922))]:
   self.models[kind]=[]
   for seed in seeds:
    path=root/f'{prefix}_{kind}_seed{seed}.txt'
    if not path.exists():raise R149StateError(f'missing frozen model: {path.name}')
    booster=lgb.Booster(model_file=str(path))
    n=185 if kind=='teacher' else 186
    if booster.num_feature()!=n:raise R149StateError(f'{kind} feature count {booster.num_feature()} != {n}')
    self.models[kind].append(booster)

 @staticmethod
 def input_features(state179,r24_score,rescue_score,hunter_score,side,decision_ms):
  x=np.asarray(state179,dtype=np.float32)
  if x.shape!=(179,) or not np.isfinite(x).all() or side not in (-1,1):
   raise R149StateError('invalid causal state/side')
  if not math.isfinite(r24_score):raise R149StateError('R24 score invalid')
  h=(int(decision_ms)%86400000)/86400000*2*math.pi
  v=np.concatenate([x,np.asarray([r24_score,
    -1 if rescue_score is None or not np.isfinite(rescue_score) else rescue_score,
    -1 if hunter_score is None or not np.isfinite(hunter_score) else hunter_score,
    side,math.sin(h),math.cos(h)],dtype=np.float32)])
  if v.shape!=(185,):raise R149StateError('vector schema mismatch')
  return v

 def shadow(self,*,parent_action:str,broker:str,t0_ms:int,decision_quote_ms:int,
            first_native_quote_verified:bool,already_filled:bool,
            causal_state_179,r24_score:float,rescue_score:float|None,
            hunter_score:float|None,side:int):
  result={'action':parent_action,'r149_override_active':False,'r149_status':'R148_PARENT_UNCHANGED'}
  if already_filled or parent_action not in ACTIONS:
   return {**result,'r149_reason':'FILLED_OR_NONDECISION_IMMUTABLE'}
  if broker!=self.broker or broker not in MODEL_SUFFIX:
   return {**result,'r149_reason':'UNKNOWN_BROKER_PASSTHROUGH'}
  if not(first_native_quote_verified and t0_ms+15000 <= decision_quote_ms < t0_ms+16000):
   return {**result,'r149_reason':'NO_VERIFIED_NATIVE_DECISION_QUOTE'}
  try:
   x=self.input_features(causal_state_179,r24_score,rescue_score,hunter_score,side,decision_quote_ms)
  except R149StateError:
   return {**result,'r149_reason':'INVALID_CAUSAL_STATE'}
  if not self.models:return {**result,'r149_reason':'NO_FROZEN_MODELS'}
  t=float(np.mean([m.predict(x[None,:],num_threads=1)[0] for m in self.models['teacher']]))
  t=float(np.clip(t,0,1));xx=np.r_[x,np.float32(t)]
  kind='rescue' if parent_action=='VETO_NEW_UNFILLED_ORDER' else 'hunter'
  p=float(np.mean([m.predict(xx[None,:],num_threads=1)[0] for m in self.models[kind]]))
  # No learned decision threshold is authorized by historical diagnostics.
  return {**result,'r149_reason':'TELEMETRY_ONLY_NOT_PROMOTED','teacher_student_score':t,
          'r149_head':kind,'r149_head_probability':p,'research_approval':'UNAPPROVED'}
