"""Local original lineage and past-only invariant smoke tests; not live-profit certification."""
import io,json,sys,zipfile,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from execute_r00_078 import episode_transition_features,old,last_change_ages,source_labels
from native_phase_076d import extract
REF=Path('/mnt/data/xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results')

def test_asof_last_change_prefix():
 ts=np.array([1000,2000,3000,5000,6000],dtype='int64')
 state=np.zeros((5,42),dtype='float32');state[:,16]=[0,1,1,2,2]
 prev=last_change_ages(ts,state,16)
 assert np.allclose(prev,[0,0,1,0,1])
 state2=state.copy();state2[4,16]=5
 assert np.array_equal(last_change_ages(ts,state2,16)[:4],prev[:4])

def test_recovered_source_phase_uses_only_prefix():
 t=np.array([1000,1120,1500,2050,3050,4000,5100],dtype=np.int64)
 bid=np.array([3000,3000.10,3000.35,3000.40,3000.20,3000.45,3000.75],dtype=np.float64)
 ask=bid+.10
 j=np.array([0,1,3,4],dtype=np.int64)
 a,p=extract(t,bid,ask,j)
 b,q=extract(t[:5],bid[:5],ask[:5],j)
 assert np.array_equal(a,b)

def test_sealed_event_identity_and_per_month_scores():
 for b,m in [('coinexx','06'),('dukascopy','07')]:
  with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz') as z,np.load(ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz') as x,np.load(ROOT/'results'/f'R00_078B_{b}_{m}_EVENTS.npz') as y,np.load(ROOT/'results'/f'R00_079_{b}_{m}_EVENTS.npz') as w:
   for arr in [x,y,w]:
    assert np.array_equal(z['ts_ms'],arr['ts_ms'])
    assert np.array_equal(z['quote_index'],arr['quote_index'])
    assert np.array_equal(z['y'],arr['y'])
   assert np.array_equal(z['AGREE_005'],y['INCUMBENT_077'])
   assert np.array_equal(z['AGREE_005'],w['INCUMBENT_077'])

def test_feb_is_selected_before_exposed():
 a=json.loads((ROOT/'results/R00_078_FEB_FROZEN.json').read_text())
 b=json.loads((ROOT/'results/R00_078B_FEB_FROZEN.json').read_text())
 c=json.loads((ROOT/'results/R00_079_FEB_FROZEN.json').read_text())
 assert a['frozen_winner']=='FLIP_010'
 assert b['FEB_frozen_winner']=='078_PRIO_STRONG'
 assert c['selected_Feb']=='PREVIOUS_FUSION_SELECTED'
 assert c['selection_on_Feb_only']
