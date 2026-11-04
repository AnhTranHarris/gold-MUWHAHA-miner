import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r20_last46/src')
from r20_spread_hysteretic_stop import independent_paths

def test_entry_exits_full_bid_ask_and_stop_first():
 t=np.array([0,1000,2000,3000,61000],np.int64)
 b=np.array([100000,99800,101500,101500,101500],np.int32)
 a=b+1000
 fill=np.array([0],np.int32)
 tight,e,_=independent_paths(t,b,a,fill,np.array([100],np.int32),0)
 wide,z,n=independent_paths(t,b,a,fill,np.array([500],np.int32),0)
 assert tight[0,0]==0 and e[0,0]==1
 assert wide[0,0]==1 and z[0,0]==2 and n[0,0]>=100

def test_no_unobserved_gap_profit():
 t=np.array([0,1000,19000,20000,21000,62000],np.int64)
 b=np.array([100000,100000,101500,101500,101500,101500],np.int32)
 a=b+1000
 c,e,_=independent_paths(t,b,a,np.array([0],np.int32),np.array([1000],np.int32),0)
 assert c[0,0]==-3 and e[0,0]==-1

def test_source_quote_bid_ask_fee_and_slip_are_paid_both_legs():
 t=np.array([0,1000,2000,62000],np.int64)
 b=np.array([100000,101100,101300,101300],np.int32)
 a=b+1000
 c,e,n=independent_paths(t,b,a,np.array([0],np.int32),np.array([500],np.int32),50)
 assert c[0,0]==1 and e[0,0]==2
 assert n[0,0]==1300-1000-20-100
