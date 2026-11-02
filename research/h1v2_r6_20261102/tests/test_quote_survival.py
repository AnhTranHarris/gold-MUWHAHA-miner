import numpy as np
from quote_survival import extract,NAMES

def test_future_mutation_cannot_affect_past_features():
 t=np.array([0,0,50,100,101,200,400,401,500,510,600,620,800,1000],np.int64)
 b=np.array([100,100.1,100.0,100.3,100.2,100.1,100.4,100.3,100.2,100.7,100.6,100.5,100.4,100.3]);a=b+.2
 i=np.array([1,6,10]);z=extract(t,b,a,i);q=b.copy();q[11:]+=50000
 assert np.array_equal(z,extract(t,q,np.where(np.arange(len(a))>=11,q+.2,a),i))
 assert z[0,NAMES.index('has_same_ms_prior')]==1.

def test_quote_order_matters_even_if_same_ohlc():
 t=np.array([0,10,20,30,40],np.int64)
 b=np.array([100.,100.3,99.9,100.2,100.]);a=b+.2
 c=np.array([100.,99.9,100.3,100.2,100.]);
 x=extract(t,b,a,np.array([4]))
 y=extract(t,c,c+.2,np.array([4]))
 assert x.shape[1]>=70 and not np.array_equal(x,y)

def test_equal_ms_future_ordinal_is_unobserved():
 t=np.array([0,10,10,10,11],np.int64)
 b=np.array([10.,10.1,10.2,10.4,10.5]);a=b+.1
 z=extract(t,b,a,np.array([1]));c=b.copy();c[2:]=900.
 assert np.array_equal(z,extract(t,c,c+.1,np.array([1])))
