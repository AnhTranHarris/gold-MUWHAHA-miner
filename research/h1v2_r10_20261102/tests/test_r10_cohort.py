import numpy as np
from r10_full_cohort import replay,wilson_lower

def test_wilson_small_n_is_conservative():
 assert wilson_lower([1],[1])[0]<.3
 assert wilson_lower([90],[100])[0]>.8

def test_single_position_replay_nonoverlap():
 idx=np.array([1,3,10,13]);ends=np.array([[5,6],[4,7],[11,12],[15,14]])
 code=np.array([[1,-1],[1,-1],[-1,1],[1,1]],np.int8)
 pnl=np.array([[.8,-1],[.7,-1],[-.5,.6],[.7,.6]],np.float32)
 s=np.array([0,0,1,0],np.int8)
 q,good,bad,neu,net=replay(np.arange(4),s,idx,ends,pnl,code)
 assert q==3 and good==3 and bad==0 and neu==0
