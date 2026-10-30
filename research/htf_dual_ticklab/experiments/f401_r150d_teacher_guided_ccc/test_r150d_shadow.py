import sys,inspect,numpy as np
sys.path.insert(0,'/mnt/data/R150D/source')
from r150d_live_shadow import R150DPhysicalShadow

def test_runtime_has_no_teacher_or_truth():
 p=inspect.signature(R150DPhysicalShadow.observe).parameters
 assert all(z not in p for z in ('truth','oracle_score','teacher_score','future_midpoint','fp_actual'))

def test_already_filled_immutable():
 s=R150DPhysicalShadow('unknown','/tmp')
 r=s.observe(broker='unknown',parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=1000,decision_ms=16000,first_quote_verified=True,already_filled=True,source304=np.zeros(304),parent6=np.array([0,0,0,0,0,1]),original_side=1)
 assert r['action']=='VETO_NEW_UNFILLED_ORDER' and not r['r150d_override_active']

def test_missing_quote_rejected():
 assert R150DPhysicalShadow.validate(t0_ms=1000,decision_ms=16999,first_quote_verified=False,already_filled=False,source304=np.zeros(304),parent6=np.array([0,0,0,0,0,1]),original_side=1)=='MISSING_NATIVE_DECISION_QUOTE'

def test_side_mismatch_rejected():
 assert R150DPhysicalShadow.validate(t0_ms=1000,decision_ms=16000,first_quote_verified=True,already_filled=False,source304=np.zeros(304),parent6=np.array([0,0,0,0,0,-1]),original_side=1)=='SIDE_MISMATCH'

def test_shadow_valid_fitted_parent_immutable():
 for broker in ('coinexx',):
  s=R150DPhysicalShadow(broker,'/mnt/data/R150D/models')
  import pathlib
  p=pathlib.Path('/mnt/data/R150C/features/R150C_coinexx_06_WORLD_STATE.npz')
  with np.load(p,allow_pickle=False) as d:
   ix=int(np.where(d['valid'] & d['r148_veto'])[0][0]);t=int(d['t'][ix]);decision=int(d['decision'][ix]);side=int(d['side'][ix]);x=d['X_source'][ix];parent=d['X_parent'][ix]
  r=s.observe(broker=broker,parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=t,decision_ms=decision,first_quote_verified=True,already_filled=False,source304=x,parent6=parent,original_side=side)
  assert r['action']=='VETO_NEW_UNFILLED_ORDER' and not r['r150d_override_active']
  assert 0<=r['correct_continuation_certificate_score']<=1
  assert abs(sum(r[k] for k in ('action_time_midpoint_favorable_first_prob','action_time_midpoint_adverse_first_prob','action_time_midpoint_censored_prob'))-1)<1e-4
