import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from event_graph import classify_marks,extract,WINDOWS_MS,FIELDS

def test_mixed_marks_not_dropped():
 b=np.array([100.,100.1,100.0,100.1])
 a=np.array([100.4,100.3,100.4,100.5])
 assert classify_marks(b,a).tolist()==[0,7,8,5]

def test_genuine_midpoint_order_sensed_even_same_terminal():
 t=np.array([0,10,20,30,40,50],np.int64)
 b1=np.array([100.,100.2,100.0,100.1,100.,100.1])
 b2=np.array([100.,99.8,100.0,99.9,100.,100.1])
 a1=b1+.2;a2=b2+.2
 x=extract(t,b1,a1,np.array([5],np.int64))
 y=extract(t,b2,a2,np.array([5],np.int64))
 assert x.shape==(1,len(WINDOWS_MS)*len(FIELDS))
 assert np.any(x!=y)

def test_future_mutation_cannot_change_previous_ordinal_features():
 t=np.array([0,0,1,1,10,20,25],np.int64)
 b=np.array([100.,100.1,100.2,100.05,100.2,100.5,100.3]);a=b+.2
 orig=extract(t,b,a,np.array([1,2,3,4],np.int64))
 b2=b.copy();a2=a.copy();b2[5:]=[10000,-10000];a2[5:]=b2[5:]+.2
 assert np.array_equal(orig,extract(t,b2,a2,np.array([1,2,3,4],np.int64)))

def test_out_of_order_rejected():
 t=np.array([0,1,2],np.int64);b=np.ones(3);a=b+.1
 with pytest.raises(ValueError):extract(t,b,a,np.array([2,1],np.int64))
