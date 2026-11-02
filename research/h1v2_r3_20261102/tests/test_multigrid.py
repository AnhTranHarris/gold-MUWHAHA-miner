import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from multigrid_regime_discovery import macro_features,fit_map,evaluate,wilson,GRID_SPECS,dataframe

def test_no_outcome_read_by_macro():
 x=np.zeros((3,100),np.float32);x[:,-1]=.7
 t=np.array([1000000,1000250,1000500],np.int64)
 a=macro_features(x,t)
 assert len(a)>=20 and all(len(v)==3 for v in a.values())
 assert all(np.all(np.isfinite(v)) for v in a.values())
 assert not any('net' in k or 'first_hit' in k for k in a)

def test_strict_side_and_ambiguous_wait():
 df=pd.DataFrame({'g':[1,1,1,1,2,2], 'side':[0,1,0,1,0,1], 'month':['01']*6,
                  'event_id':[0,0,1,1,2,2], 'class':[3,0,3,0,3,3], 'strong':[1,0,1,0,1,1]})
 r=evaluate(df,['g','side'],np.ones(6,bool),np.ones(6,bool),1,'mean:0.8','unit')
 assert r['selected_sampled_events']==2 and r['strong_correct']==2 and r['wrong']==0

def test_unknown_state_fail_closed():
 df=pd.DataFrame({'g':[1,1,2,2], 'side':[0,1,0,1], 'month':['01','01','07','07'],
                  'event_id':[0,0,0,0], 'class':[3,0,3,0], 'strong':[1,0,1,0]})
 mask=np.array([True,True,False,False]);score=~mask
 r=evaluate(df,['g','side'],mask,score,1,'mean:0.8','unseen')
 assert r['selected_sampled_events']==0

def test_wilson_rejects_singletons():
 assert wilson(1,1)<.3 and wilson(8,10)<.8

def test_grids_distinct():
 assert len(GRID_SPECS)==len(set(map(tuple,GRID_SPECS.values())))


def test_leave_one_out_removes_own_future_label():
 df=pd.DataFrame({'g':[1,1,2,2], 'side':[0,1,0,1], 'month':['01']*4,
   'event_id':[0,0,1,1], 'class':[3,0,3,0], 'strong':[1,0,1,0]})
 resub=evaluate(df,['g','side'],np.ones(4,bool),np.ones(4,bool),1,'mean:0.8','resub')
 loo=evaluate(df,['g','side'],np.ones(4,bool),np.ones(4,bool),1,'mean:0.8','loo',leave_one_out=True)
 assert resub['selected_sampled_events']==2 and loo['selected_sampled_events']==0
