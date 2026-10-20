"""Strict timestamp eligibility and future outcome perturbation tests for FILTER13."""
import sys
from pathlib import Path
sys.path.insert(0,'/mnt/data')
import numpy as np
from R00_054_FILTER13_CAUSAL_REGIME_MEMORY import regime_matured

t=np.array([0,5000,20000,32999,33000,33001,65000,66000,68000,100000],dtype=np.int64)
y=np.array([0,1,2,0,1,2,1,1,0,2],np.int8)
ctx=np.array([3,4,5,3,4,5,3,4,5,3],np.int32)
subctx=(ctx%12).astype(np.int32)
a=regime_matured(t,y,ctx,subctx)
assert np.array_equal(a[0],a[1])  # before any matured label
assert np.array_equal(a[1],a[2])
assert np.array_equal(a[2],a[3])
assert not np.array_equal(a[3],a[4])  # first signal matures exactly at 33000ms

# Vary every future outcome; no earlier feature vector may change.
for i in range(len(t)):
    mutate=y.copy();mutate[i:] = (mutate[i:]+1)%3
    b=regime_matured(t,mutate,ctx,subctx)
    assert np.array_equal(a[:i+1],b[:i+1]), (i,"future information leaked")
# Past-only effect: changing earliest class affects only features >= t0+33000.
mutate=y.copy();mutate[0]=2; b=regime_matured(t,mutate,ctx,subctx)
assert np.array_equal(a[:4],b[:4]);assert not np.array_equal(a[4],b[4])
print('FILTER13_NO_FUTURE_TEST_PASS',len(t),'synthetic observed-tick timestamps and all future-label perturbations')
