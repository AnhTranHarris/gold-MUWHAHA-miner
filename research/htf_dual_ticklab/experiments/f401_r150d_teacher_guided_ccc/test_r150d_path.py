import sys, pathlib, inspect, numpy as np
sys.path.insert(0,'/mnt/data/R150D/source')
from r150d_restored_path_shadow import R150DRestoredPathShadow

def test_no_teacher_in_runtime():
 x=inspect.signature(R150DRestoredPathShadow.observe_path).parameters
 assert not any(k in x for k in ('teacher','truth','future','oracle','label'))

def test_brokers_model_schema_and_immutability():
 for b in ('coinexx','dukascopy'):
  s=R150DRestoredPathShadow(b,'/mnt/data/R150D/models')
  assert s.path_guard.num_feature()==370
  p=pathlib.Path('/mnt/data/R150C/features')/f'R150C_{b}_07_WORLD_STATE.npz'
  q=pathlib.Path('/mnt/data/R150D/path')/f'R150D_{b}_07_R147_STRICT_PATH.npz'
  with np.load(p,allow_pickle=False) as d, np.load(q,allow_pickle=False) as e:
   i=int(np.where(d['valid']&d['r148_veto']&e['available'])[0][0]);t=int(d['t'][i]);dd=int(d['decision'][i]);side=int(d['side'][i]);xx=d['X_source'][i];pp=d['X_parent'][i];path=e['X'][i]
  r=s.observe_path(broker=b,parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=t,decision_ms=dd,
    first_quote_verified=True,already_filled=False,original_side=side,source304=xx,parent6=pp,path57=path,
    path_prefix_end_exclusive_ms=t+15000)
  assert r['action']=='VETO_NEW_UNFILLED_ORDER' and r['r150d_override_active'] is False
  assert 0<=r['hypothetical_ccc_score']<=1

def test_wrong_prefix_is_fail_closed():
 b='coinexx';s=R150DRestoredPathShadow(b,'/mnt/data/R150D/models')
 p=pathlib.Path('/mnt/data/R150C/features/R150C_coinexx_07_WORLD_STATE.npz')
 with np.load(p,allow_pickle=False) as d:
  i=int(np.where(d['valid'])[0][0]);t=int(d['t'][i]);dd=int(d['decision'][i]);side=int(d['side'][i]);xx=d['X_source'][i];pp=d['X_parent'][i]
 r=s.observe_path(broker=b,parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=t,decision_ms=dd,first_quote_verified=True,
   already_filled=False,original_side=side,source304=xx,parent6=pp,path57=np.zeros(57),path_prefix_end_exclusive_ms=t+16000)
 assert r['action']=='VETO_NEW_UNFILLED_ORDER' and r['r150d_path_status']=='PATH_PREFIX_PROVENANCE_FAILURE'
