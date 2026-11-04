from pathlib import Path
import numpy as np,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from r24s6_survival_frontier import query_extrema,evaluated_horizon,fixed_hold_earliest
sys.path.insert(0,'/mnt/data/h1v2_r24_asof/source')
import r24_firstpass_engine as e

def test_prefix_sorted_fixed_length_exact():
 t=np.array([0,1000,1001,15001,19000,30002],np.int64)
 m=np.array([1,1,1,1,1,1],bool)
 z=fixed_hold_earliest(t,m,15000)
 assert z.tolist()==[True,False,False,True,False,True]

def test_completed_horizon_strict_not_early_target_escape():
 t=np.array([0,1000,2000,12000,15001,30000,31000],np.int64)
 b=np.array([99_900,100_050,100_250,99_780,100_200,100_150,100_100],np.int32)
 a=b+200
 sz,bx,bn,ax,an=e.build_tree(b,a)
 f=np.array([0],np.int32);j=np.array([4],np.int32);cover=np.array([True]);shadow=np.array([1],np.int8)
 valid,safe,tp,hs,ht=evaluated_horizon(t,b,a,f,j,cover,shadow,np.array([100,250],np.int32),sz,bx,bn,ax,an)
 assert valid[0]
 assert safe[0,0,0]==False # fell 120 bid raw below original bid after earlier net TP
 assert safe[1,0,0]==True
 assert tp[0,0,0]==False and tp[1,0,0]==True
 assert hs[0,0]==False and hs[1,0]==True

def test_stop_stress_monotonic():
 t=np.array([0,5000,15000],np.int64)
 b=np.array([100000,99900,100100],np.int32);a=b+50
 size,bx,bn,ax,an=e.build_tree(b,a)
 v,s,tp,h,ht=evaluated_horizon(t,b,a,np.array([0],np.int32),np.array([2],np.int32),np.array([True]),np.array([-1],np.int8),np.array([99,100,101],np.int32),size,bx,bn,ax,an)
 assert (np.diff(s[:,0,0].astype(np.int32))>=0).all()
 assert (np.diff(s[:,0,1].astype(np.int32))>=0).all()

def test_right_censor():
 t=np.array([0,1000,2000],np.int64);b=np.array([100,105,103],np.int32);a=b+1
 size,bx,bn,ax,an=e.build_tree(b,a)
 v,s,tp,h,ht=evaluated_horizon(t,b,a,np.array([0],np.int32),np.array([2],np.int32),np.array([False]),np.array([1],np.int8),np.array([100],np.int32),size,bx,bn,ax,an)
 assert not v[0] and not s.any() and not tp.any()
