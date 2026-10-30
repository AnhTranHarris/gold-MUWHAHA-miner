import inspect
import numpy as np
import pathlib
from r150e_live_shadow import R150EFullStateShadow
ROOT=pathlib.Path('/mnt/data/R150E/models')
def mk(b='coinexx'):
 return R150EFullStateShadow(b,ROOT)
def state():
 return dict(source304=np.zeros(304,np.float32),parent6=np.zeros(6,np.float32),path57=np.zeros(57,np.float32),htf36=np.zeros(36,np.float32))
def args(**kwargs):
 d=dict(broker='coinexx',parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=1000,decision_ms=16000,
        first_quote_verified=True,already_filled=False,path_prefix_end_exclusive_ms=16000,
        completed_htf_verified=True,**state());d.update(kwargs);return d
def test_no_truth_or_teacher_api():
 sig=inspect.signature(R150EFullStateShadow.observe).parameters
 assert not any(x in sig for x in ('truth','outcome','teacher','future'))
def test_parent_action_immutable():
 o=mk().observe(**args());assert o['action']=='VETO_NEW_UNFILLED_ORDER' and not o['r150e_override_active']
def test_unknown_broker_fallback():
 o=mk().observe(**args(broker='unseen'));assert o['reason']=='UNKNOWN_BROKER_FALLBACK'
def test_filled_immutable():
 o=mk().observe(**args(already_filled=True));assert o['reason']=='FILLED_OR_NONDECISION_IMMUTABLE'
def test_window_exact():
 o=mk().observe(**args(decision_ms=17000));assert 'PROVENANCE' in o['reason']
def test_prefix_authentication():
 o=mk().observe(**args(path_prefix_end_exclusive_ms=15999));assert 'PROVENANCE' in o['reason']
def test_nonfinite_rejected():
 p=state();p['htf36'][0]=np.nan
 o=mk().observe(**args(**p));assert o['reason']=='INVALID_CAUSAL_STATE'
def test_source_feature_alignment():
 import numpy as np
 for broker in ('coinexx','dukascopy'):
  for m in ('01','02','06','07'):
   with np.load(f'/mnt/data/R150C/features/R150C_{broker}_{m}_WORLD_STATE.npz') as s, \
        np.load(f'/mnt/data/R150D/path/R150D_{broker}_{m}_R147_STRICT_PATH.npz') as p, \
        np.load(f'/mnt/data/R150E/features/R150E_{broker}_{m}_R147_DIRECT_HTF_INTER36.npz') as h:
    assert np.array_equal(s['t'],p['t']) and np.array_equal(s['t'],h['t'])
    assert np.array_equal(s['side'],p['side']) and np.array_equal(s['side'],h['side'])
    assert h['X'].shape[1]==36 and len(h['names'])==36
    assert not any('teacher' in k or 'truth' in k for k in h.files)
