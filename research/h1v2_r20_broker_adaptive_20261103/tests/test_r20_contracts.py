import sys
from pathlib import Path
import numpy as np
P=Path('/mnt/data/h1v2_r20_last46/src');sys.path.insert(0,str(P))
from r20_residual_quote_hazard import independent_both_sides, exclude_occupied,source_candidates

def test_bidask_cross_includes_spread_and_fee():
 t=np.array([0,1000,2000,31000,62000],dtype=np.int64)
 b=np.array([100000,100050,101200,101200,101200],dtype=np.int32)
 a=np.array([101000,101050,102200,102200,102200],dtype=np.int32)
 code,ends,net=independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
 assert code[0,0]==1 and ends[0,0]==2 and net[0,0]>=100
 assert code[0,1]==0 # sell hits opening ask+0.10 adverse at 1 sec

def test_stop_preempts_profit():
 t=np.array([0,1000,2000,3000,70000],dtype=np.int64)
 b=np.array([100000,99899,101500,101500,101500],dtype=np.int32)
 a=b+1000
 code,ends,net=independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
 assert code[0,0]==0 and ends[0,0]==1 and net[0,0]<0

def test_horizon_clock_is_not_relabeled_as_full60():
 t=np.array([0,14000,25000,31000,61000],dtype=np.int64)
 b=np.array([100000,100050,101200,101200,101200],dtype=np.int32)
 a=b+1000
 c15,e15,_=independent_both_sides(t,b,a,np.array([0],np.int32),0,15000)
 c60,e60,_=independent_both_sides(t,b,a,np.array([0],np.int32),0,60000)
 assert c15[0,0]!=1 and c60[0,0]==1 and e60[0,0]==2

def test_incoming_original_overlap_and_far_future_not_occupied():
 t=np.arange(0,6000,1000,dtype=np.int64)
 candidate=np.array([1,4],np.int32);ex=np.array([2,5],np.int32)
 mask=exclude_occupied(t,candidate,ex,np.array([0,3],np.int32),np.array([2,4],np.int32))
 assert not mask[0] and not mask[1]

