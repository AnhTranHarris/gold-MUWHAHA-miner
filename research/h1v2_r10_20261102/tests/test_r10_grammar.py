import numpy as np
import pytest
from r10_order_grammar import grammar,NAMES

def test_same_future_different_past_order():
 # Different within-slot orders ending identically must produce distinct past features.
 ts=np.array([0,30,60,90,120,150],np.int64)
 a=np.array([.2,.2,.2,.2,.2,.2])
 b1=np.array([1.,1.2,1.,1.1,1.,1.1])
 b2=np.array([1.,.8,1.,.9,1.,1.1])
 q=np.array([5],np.int64)
 x=grammar(ts,b1,b1+a,q)[0]
 y=grammar(ts,b2,b2+a,q)[0]
 assert not np.array_equal(x,y)

def test_future_events_do_not_change_prefix():
 ts=np.array([0,10,20,20,21,34],np.int64)
 b=np.array([1.,1.2,1.1,1.3,1.2,1.5]);a=b+.2
 ix=np.array([1,2,3,4],np.int64)
 p=grammar(ts,b,a,ix)
 laterb=np.append(b,[100,-100]);latera=np.append(a,[100.3,-99.7]);later=np.append(ts,[35,35])
 assert np.array_equal(p,grammar(later,laterb,latera,ix))
 assert np.isfinite(p).all()

def test_same_millisecond_ordinal_not_full_bin():
 ts=np.array([0,1,1,1,1,2],np.int64)
 b=np.array([100,100.1,100.2,99.5,100.0,101.]);a=b+.1
 ix=np.array([1,2,3,4,5])
 allx=grammar(ts,b,a,ix)
 assert not np.array_equal(allx[0],allx[1]);assert len(NAMES)==48

def test_invalid_ordinal_rejected():
 ts=np.array([0,1,2],np.int64);b=np.ones(3);a=b+.1
 with pytest.raises(ValueError):grammar(ts,b,a,np.array([2,1]))
