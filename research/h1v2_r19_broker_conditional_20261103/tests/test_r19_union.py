import numpy as np,sys
sys.path.insert(0,'/mnt/data/h1v2_r19_broker_union/src')
from r19_multi_clock_union import verify_unique_union

def test_union_retains_exact_side_and_lane_provenance():
 ix=np.array([4,2,4,10],np.int32)
 side=np.array([-1,1,-1,1],np.int8)
 lanes=np.array([4,1,8,2],np.uint16)
 u,s,m=verify_unique_union(ix,side,lanes,12)
 assert np.array_equal(u,[2,4,10]);assert np.array_equal(s,[1,-1,1]);assert np.array_equal(m,[1,12,2])

def test_contradictory_future_sides_fail_closed():
 with __import__('pytest').raises(ValueError,match='SIDE_COLLISION'):
  verify_unique_union(np.array([1,1]),np.array([1,-1]),np.array([1,2],np.uint16),3)

def test_no_source_ordinal_outside_original():
 with __import__('pytest').raises(ValueError,match='OUTSIDE'):
  verify_unique_union(np.array([5]),np.array([1]),np.array([1],np.uint16),5)
