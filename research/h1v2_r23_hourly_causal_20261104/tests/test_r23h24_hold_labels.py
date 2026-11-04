import sys
import numpy as np

from r23h24_hold_labels import _labels
from r24_firstpass_engine import build_tree

def test_stop_bid_buy_and_ask_sell_asymmetric():
 t=np.array([0,100,300,1100,15100,15150],dtype=np.int64)
 b=np.array([10000,9990,9890,9890,9890,9890],dtype=np.int32)
 a=np.array([10100,10100,10100,10250,10250,10250],dtype=np.int32)
 size,_,mn,mx,_=build_tree(b,a)
 nextgap=np.full(len(t),len(t),np.int32)
 held,stop,ends=_labels(t,b,a,np.array([0],np.int32),nextgap,size,mn,mx)
 assert held[0,0,0]==0 and stop[0,0,0]==2
 assert held[0,1,0]==0 and stop[0,1,0]==3
 assert ends[0,0]==4

def test_later_same_millisecond_ordinal_is_observed():
 t=np.array([0,0,15000,30000,60000],np.int64)
 b=np.array([1000,850,900,900,900],np.int32); a=np.array([1100,1100,1100,1100,1100],np.int32)
 size,_,mn,mx,_=build_tree(b,a)
 held,stops,_=_labels(t,b,a,np.array([0],np.int32),np.full(len(t),len(t),np.int32),size,mn,mx)
 assert stops[0,0,0]==1 and held[0,0,0]==0

def test_quote_gap_right_censor_not_survival():
 t=np.array([0,1000,20000,30000,60000,80000],np.int64)
 b=np.array([1000]*6,np.int32);a=b+100
 size,_,mn,mx,_=build_tree(b,a)
 nxt=np.array([2,2,6,6,6,6],np.int32)
 held,stops,ends=_labels(t,b,a,np.array([0],np.int32),nxt,size,mn,mx)
 assert held[0,0,0]==2 and held[0,1,0]==2
 assert stops[0,0,0]==-1

def test_unfilled_remains_unfilled():
 t=np.array([0,15000,30000,60000],np.int64);b=np.full(4,1000,np.int32);a=b+100
 size,_,mn,mx,_=build_tree(b,a)
 held,_,_=_labels(t,b,a,np.array([-1],np.int32),np.full(4,4,np.int32),size,mn,mx)
 assert np.all(held==3)
