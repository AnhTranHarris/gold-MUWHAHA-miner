"""Preserved ORIGINAL April136A build_events parity, no historical winners."""
import unittest,zipfile,ast
from pathlib import Path
import numpy as np
from v1_grid_native_136a import NativeMinuteRungs136A
ZIP=Path('/mnt/data/GRID0238_CREATOR_48_ACTIVE_H1_VERTICAL_HORIZONTAL_SOURCE_ENGINEERING_UNPROMOTED.zip')
class Original136ATest(unittest.TestCase):
 def test_exact_continuous_source_parity(self):
  if not ZIP.exists():self.skipTest('original GRID0238 source ZIP not available in portable clone')
  with zipfile.ZipFile(ZIP) as z:
   text=z.read('grid0173_accepted_originals/apr_native_markout_136.py').decode()
  tree=ast.parse(text)
  func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build_events')
  func.decorator_list=[]
  ns={'np':np}
  exec(compile(ast.Module(body=[func],type_ignores=[]),'original_136a.py','exec'),ns)
  source=ns['build_events']
  # Original absolute UTC grid research period, one continuous micro-path
  t0=1775001600000+7*3600000
  ms=np.array([t0,t0+500,t0+1000,t0+1500,t0+2000,
               t0+60200,t0+60600,t0+60800,t0+61000,t0+61200],dtype=np.int64)
  midpoint=np.array([3100000,3100040,3100105,3100220,3099970,
                     3100300,3100340,3100420,3100550,3100150],dtype=np.int64)
  hs=np.ones(len(ms),dtype=np.int8)
  ix,d,hr,sig,disp,b10=source(ms,midpoint,hs,hs,hs,hs,np.int64(t0),np.int64(t0+2*60000),50)
  src=[(int(ms[i]),int(dd),int(v)) for i,dd,v in zip(ix,d,disp)]
  g=NativeMinuteRungs136A(step_raw=50,minimum_rung_raw=50,max_quote_gap_ms=60000)
  candidate=[]
  for i,(x,m) in enumerate(zip(ms,midpoint)):
   out=g.on_quote(time_ms=int(x),bid_raw=int(m-50),ask_raw=int(m+50),
      completed_h4_sign=1,completed_h1_sign=1,
      completed_m15_sign=1,completed_m5_sign=1)
   candidate.extend((e.timestamp_ms,e.side,e.rung_raw) for e in out)
  self.assertEqual(candidate,src)
if __name__=='__main__':unittest.main()
