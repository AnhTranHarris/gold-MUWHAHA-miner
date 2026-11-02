import numpy as np
from full_population_nested_regime import asof_regime, wilson, N_BINS

def test_raw_past_asof_same_ms_future_mutation():
 t=np.array([0,0,100,1000,1200,1200,2000,3000,3000],np.int64)
 b=np.array([100,100.1,100.1,100.2,100.3,100.1,100.3,100.7,100.8])
 a=b+.2
 ix=np.array([1,3,4,6,7],np.int64)
 orig=asof_regime(t,b,a,ix,chunk=2)
 bb=b.copy();bb[5:]+=200;aa=a.copy();aa[5:]+=200
 out=asof_regime(t,bb,aa,ix[:3],chunk=2)
 assert np.array_equal(orig[:3],out)
 assert orig.shape==(5,) and np.all((orig>=0)&(orig<N_BINS))

def test_historical_window_mutation_affects_asof():
 t=np.arange(150)*1000;b=100+np.arange(150)*.02;a=b+.15
 out=asof_regime(t,b,a,np.array([149]))
 assert 0<=out[0]<N_BINS

def test_wilson():
 x=wilson(np.array([0,80,100]),np.array([100,100,100]));assert x[0]<1e-12 and x[1]<.8 and x[2]>.9

def test_bad_ordinal_or_timestamps():
 t=np.array([0,10,20]);b=np.array([100.,100.,101.]);a=b+.1
 try:asof_regime(t,b,a,np.array([2,1]));assert False
 except ValueError:pass
