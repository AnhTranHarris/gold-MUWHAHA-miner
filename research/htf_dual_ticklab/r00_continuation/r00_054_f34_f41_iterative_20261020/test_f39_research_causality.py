"""Source-native F39 Python unit checks, not MT5 compilation/parity verification."""
import sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data');sys.path.insert(0,str(ROOT))
from f39_source_native_quote import build

def check():
 # deterministic tick stream with both-bid and one-sided flags; repeated quote millisecond.
 n=200;t=np.arange(n,dtype=np.int64)*30+1767308400000
 t[45]=t[44]
 bid=np.zeros(n,dtype=np.float64)+4320.
 ask=np.zeros(n,dtype=np.float64)+4321.
 for k in range(1,n):
  bid[k]=bid[k-1]+(.03 if k%4 else -.05)
  ask[k]=ask[k-1]+(.03 if k%5 else -.04)
 ix=np.array([44,70,109],dtype=np.int64);side=np.array([1,-1,1],dtype=np.int8)
 original=build(t,bid,ask,ix,side)
 badbid=bid.copy();badask=ask.copy();badbid[46:]+=10000.;badask[46:]+=10000.
 mutated=build(t,badbid,badask,ix,side)
 assert np.array_equal(original[0],mutated[0]),'FUTURE_QUOTE_LEAK'
 assert original.shape==(3,30) and np.all(np.isfinite(original))
 one=build(t,bid,ask,np.array([0]),np.array([1],dtype=np.int8))
 assert one[0,3]==1000 and one[0,29]==1000000
 print('PASS future tick mutation; repeated event milliseconds; quote index 0 guard; shape 30; finite outputs')
if __name__=='__main__':check()