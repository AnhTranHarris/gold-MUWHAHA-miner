"""R150B late-UTC autonomous versus teacher-assisted telemetry.

SOURCE-EXACT UNAPPROVED RESEARCH. R148B parent may never be modified here.
No current truth, no future label, no historical FILTER08 oracle argument.
Models are frozen R150B Jan/Feb weights; no release/veto thresholds are active.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import lightgbm as lgb
from r150b_eventtime import causal_marks

class R150BShadow:
 def __init__(self, directory: str|Path, broker: str):
  self.broker=broker;self.models={}
  if broker not in ('coinexx','dukascopy'):return
  root=Path(directory)
  self.residual=lgb.Booster(model_file=str(root/f'{broker}_RESIDUAL.txt'))
  if self.residual.num_feature()!=211:raise ValueError('R150B latent schema mismatch')
  for teacher in (0,1):
   for h in ('rescue','neutral','opposite'):
    mod=lgb.Booster(model_file=str(root/f'{broker}_E1_T{teacher}_{h}.txt'))
    if mod.num_feature()!=211+teacher:raise ValueError('R150B head schema mismatch')
    self.models[(teacher,h)]=mod

 def observe(self,*,parent_action:str,broker:str,t0_ms:int,decision_quote_ms:int,
             first_source_quote_verified:bool,already_filled:bool,side:int,
             r149_causal_state_179,native_quote_times,native_bid,native_ask)->dict:
  """Return research telemetry; never submit or cancel orders."""
  result={'action':parent_action,'r150b_override_active':False,
          'r150b_status':'UNAPPROVED_TELEMETRY_ONLY'}
  if already_filled:return {**result,'reason':'FILLED_PARENT_IMMUTABLE'}
  if broker!=self.broker or not self.models:
   return {**result,'reason':'UNKNOWN_BROKER_PARENT_FALLBACK'}
  if not(first_source_quote_verified and t0_ms+15000<=decision_quote_ms<t0_ms+16000):
   return {**result,'reason':'MISSING_EXACT_SOURCE_DECISION_QUOTE'}
  if not(21<=((t0_ms//3600000)%24)<=23) or side not in (-1,1):
   return {**result,'reason':'NOT_LATE_SESSION_OR_INVALID_SIDE'}
  x179=np.asarray(r149_causal_state_179,dtype=np.float32)
  if x179.shape!=(179,) or not np.isfinite(x179).all():
   return {**result,'reason':'MISSING_CAUSAL_STATE'}
  t=np.asarray(native_quote_times,dtype=np.int64)
  b=np.asarray(native_bid,dtype=np.int64);a=np.asarray(native_ask,dtype=np.int64)
  if len(t)!=len(b) or len(t)!=len(a) or len(t)<34 or np.any(np.diff(t)<0) or np.any(a<b):
   return {**result,'reason':'INVALID_NATIVE_QUOTE_PREFIX'}
  marks,valid=causal_marks(t,b,a,np.asarray([decision_quote_ms],np.int64),np.asarray([side],np.int8))
  if not valid[0]:return {**result,'reason':'INSUFFICIENT_REAL_QUOTE_PREFIX'}
  x=np.r_[x179,marks[0]].reshape(1,211)
  try:
   latent=float(self.residual.predict(x,num_threads=1)[0]);z=np.column_stack([x,np.asarray([latent],np.float32)])
   scores={}
   for teacher in (0,1):
    inp=z if teacher else x
    scores['teacher_assisted' if teacher else 'teacher_free']={
     h:float(self.models[(teacher,h)].predict(inp,num_threads=1)[0])
     for h in ('rescue','neutral','opposite')}
  except (ValueError,RuntimeError) as exc:return {**result,'reason':'INFERENCE_FAILURE_PARENT_FALLBACK','error_type':type(exc).__name__}
  return {**result,'reason':'RESEARCH_SHADOW_NO_THRESHOLD','score_teacher_residual':latent,
          'heads':scores,'decision_quote_ms':decision_quote_ms}
