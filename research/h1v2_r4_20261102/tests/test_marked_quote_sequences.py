import numpy as np
from marked_quote_sequences import mark_quotes, extract,NAMES

def test_quote_order_same_counts_different_transition():
    t=np.array([0,10,20,30,40,50],np.int64)
    a=np.array([100.2,100.2,100.4,100.4,100.6,100.6]);b=np.array([100.,100.1,100.1,100.2,100.2,100.3])
    m=mark_quotes(b,a);assert np.array_equal(m,np.array([0,1,3,1,3,1]))
    m2=np.array([0,1,1,1,3,3],np.uint8)
    x=extract(t,b,a,[5],m);z=extract(t,b,a,[5],m2)
    assert np.array_equal(x[0,:30],z[0,:30]);assert not np.array_equal(x[0,48:84],z[0,48:84])

def test_asof_future_mutation_and_equal_ms_ordinal():
    t=np.array([0,0,0,0,50,70,90],np.int64)
    b=np.array([100,100.1,100.2,100.1,100.4,100.5,100.6]);a=b+.2
    ix=np.array([1,3],np.int64);base=extract(t,b,a,ix)
    b[4:]+=999;a[4:]+=999
    assert np.array_equal(base,extract(t,b,a,ix))
    assert base[0,-1] < base[1,-1]

def test_feature_shapes_and_directional_mark_classification():
    t=np.arange(7,dtype=np.int64)
    b=np.array([1,1.1,1.1,1,1.1,1,1.]);a=np.array([2,2,2.1,2.1,2.2,2.1,2.])
    assert mark_quotes(b,a).tolist()==[0,1,3,2,5,6,4]
    assert len(NAMES)==92
    assert extract(t,b,a,np.array([3,6])).shape==(2,92)
