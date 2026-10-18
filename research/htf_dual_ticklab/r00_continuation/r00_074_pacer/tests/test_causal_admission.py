from importlib.machinery import SourceFileLoader
from pathlib import Path
import numpy as np
m=SourceFileLoader('selector',str(Path(__file__).resolve().parents[1]/'src/selective_074.py')).load_module()

def test_prefix_invariance_and_no_y_dependency():
 t=np.array([100,101,200,1000,1800000,1800200,3599000,3600000,3600100,3600200,4200000,7200000],dtype=np.int64)
 p=np.array([0,.2,.0,.3,.0,.1,.1,.2,.9,.1,.01,.0],dtype=float)
 for quota in (2,3,130):
  full=m.emit_mask(t,p,quota,.15,1)
  for n in range(1,len(t)+1):
   np.testing.assert_array_equal(m.emit_mask(t[:n],p[:n],quota,.15,1),full[:n])
  assert full.sum()<=quota*3
