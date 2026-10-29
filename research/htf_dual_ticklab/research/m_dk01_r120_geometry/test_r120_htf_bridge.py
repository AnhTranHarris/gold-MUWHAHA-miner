import numpy as np
from r120_htf_bridge import make_macro_native

def test_closed_bar_publication():
 # Bar 0 has two ticks, bar 1 has an extraordinary price jump exactly t0 60s.
 t=np.array([100,200,60000,60001,119999,120000,120001],dtype=np.int64)
 b=np.array([100,101,9000,9000,9001,40000,40001],dtype=np.int32);a=b+2
 ev=np.array([60000,60001,119999,120000,120001],dtype=np.int64)
 side=np.ones(len(ev),np.int8)
 x,names,meta=make_macro_native(t,b,a,ev,side)
 # t0=60000 sees only bucket 0, exactly at t0 excluded.
 assert x[0,6]<2 and x[0,0]==0
 # t0=119999, bucket1 is not yet complete, same record as at t0=60000.
 assert np.allclose(x[0,:8],x[2,:8])
 # t0=120000, bucket1 is complete and the high/close changes.
 assert x[3,6]>x[0,6]
 # mutate all source ticks in >= bucket1; at t0=60000 prior state invariant.
 b2=b.copy();b2[t>=60000]+=900000
 y,_,_=make_macro_native(t,b2,b2+2,ev,side)
 assert np.array_equal(x[0],y[0])
 print('PASS HTF completed bars no future mutation, exact boundary, no partial leakage',len(names))
if __name__=='__main__':test_closed_bar_publication()