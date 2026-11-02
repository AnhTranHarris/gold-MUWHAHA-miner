import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from true_quote_horizons import calc,feat_classes,HORIZONS_MS

def test_history_only_not_future_including_same_ms_ordinal():
 t=np.array([0,100,500,1000,1000,300000,301000],np.int64)
 b=np.array([100,101,102,103,200,105,106.],float)
 a=b+.2
 ix=np.array([3,4,6],np.int64)
 q=calc(t,b,a,ix)
 assert q[0,0]==1.0 # 1s current at 103, 500ms anchor at 102
 assert q[1,0]>q[0,0] # same millisecond later quote is distinct and uses itself
 assert np.isnan(q[0,-3]) # 4h never silently fabricated

def test_path_finite_and_no_m1_reconstruct():
 t=np.arange(0,600001,50,dtype=np.int64)
 b=100.0+np.arange(len(t))*.001
 a=b+.1
 z=calc(t,b,a,np.array([10000],np.int64))
 assert z.shape==(1,30)
 assert np.isfinite(z[:,:18]).all()
 assert abs(z[0,0]-.005)<1e-5 # 250ms returns exact earlier asof mid
 assert np.isnan(z[0,-3]) # 4hr not yet available
 assert feat_classes(z)['true_trend_250ms'][0]==1
