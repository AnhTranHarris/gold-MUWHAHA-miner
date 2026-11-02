import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from h1v2_geometry import NAMES,extract_raw_geometry

def test_fast_grid_retains_intraminute_extreme_order():
 t=np.array([0,30,60,90,120,150],np.int64)
 bx=np.array([100,100.2,100,100.1,100,100.1]);by=np.array([100,99.8,100,99.9,100,100.1]);
 x=extract_raw_geometry(t,bx,bx+.2,np.array([5]))
 y=extract_raw_geometry(t,by,by+.2,np.array([5]))
 assert x.shape==(1,99) and y.shape==(1,99)
 assert not np.array_equal(x,y)
 assert 'first_extreme_250ms' in NAMES

def test_fast_grid_never_uses_future_same_ms_quote():
 t=np.array([0,250,500,500,750],np.int64)
 b=np.array([100.,100.1,100.0,102.,100.]);a=b+.2
 x=extract_raw_geometry(t,b,a,np.array([2]))
 b2=b.copy();b2[3]=-100.;y=extract_raw_geometry(t,b2,b2+.2,np.array([2]))
 np.testing.assert_array_equal(x,y)

def test_multiple_horizons_including_30s_and_60s():
 for h in [250,500,1000,5000,15000,30000,45000,60000,300000]:
  assert f'first_extreme_{h}ms' in NAMES
