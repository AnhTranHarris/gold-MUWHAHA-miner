import numpy as np
from r7_fine_session_multigrid import fine_from_coarse,N_FINE

def test_fine_remaps_coarse_hour_exactly():
 # coarse r=(base*4+session)*3+eff; each hour known already to 6h coarse
 t=np.arange(24,dtype=np.int64)*3600000
 r=np.array([(7*4+h//6)*3+2 for h in range(24)],dtype=np.int32)
 z=fine_from_coarse(r,t)
 assert np.all(z==(7*24+np.arange(24))*3+2) and max(z)<N_FINE

def test_utc_hour_mismatch_fails():
 try:fine_from_coarse(np.array([3]),np.array([19*3600000]));assert False
 except AssertionError:pass
