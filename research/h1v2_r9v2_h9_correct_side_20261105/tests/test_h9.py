"""Deterministic adversarial tests for new, append-only H9 USD3/5 label extension."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from h9_teacher_january import strict_asof_teacher_extra_target

def f(t,b,stop_val=500,events=None):
    t=np.asarray(t,np.int64); b=np.asarray(b,np.int32); a=b+100
    fills=np.asarray([0],np.int32); events=np.full((1,2,6),-1,np.int32) if events is None else events
    ev=np.asarray(events,np.int32); ev[0,0,4]=1
    return strict_asof_teacher_extra_target(t,b,a,fills,ev,np.asarray([stop_val],np.int32),np.asarray([[True,False]]))

def test_favorable_direct_and_3_then_5():
    out,mae=f([0,100,200,300,400],[10000,11000,13400,15400,15400]);assert out[0,0,0]==2 and out[0,0,1]==3
    assert mae[0,0,0]<=-120

def test_stopped_first_never_recovered():
    out,mae=f([0,100,200,300],[10000,9400,14000,16000]);assert np.all(out==-1)

def test_quote_gap_censors():
    out,mae=f([0,100,15200,15500,15600],[10000,11000,13000,15500,16500]);assert np.all(out==-1)

def test_30s_exit_is_not_strictly_less():
    out,mae=f([0,100,10000,20000,29999,30000],[10000,11000,11000,11000,14000,16000]);assert out[0,0,0]==4 and out[0,0,1]==-1

def test_invalid_spread_stop_reject():
    out,mae=f([0,100,200,300],[10000,11000,14000,16000],stop_val=-1);assert np.all(out==-1)

if __name__=='__main__':
    for n,v in list(globals().items()):
        if n.startswith('test_') and callable(v):v();print('PASS',n)
