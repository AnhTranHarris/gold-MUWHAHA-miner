import unittest
import numpy as np
from r151_native_action import FEATURE_NAMES
from r151_t1_core import action_t1_index
from r120_multiclock_geometry import build_states
from r120_htf_bridge import make_macro_native

class SourceContract(unittest.TestCase):
 def test_feature_names_no_teacher_or_outcome(self):
  self.assertEqual(len(FEATURE_NAMES),100)
  forbidden=('teacher','truth','correct_guard','mature','future','outcome','label','post_t1')
  for name in FEATURE_NAMES:
   self.assertFalse(any(s in name.lower() for s in forbidden),name)
 def test_r120_micro_prefix_suffix_mutation(self):
  t=np.arange(1000,310000,1000,dtype=np.int64)
  bid=(4000000+np.cumsum((np.arange(len(t))%9)-4)).astype(np.int32)
  ask=bid+150
  av=np.ones(len(t),dtype=np.float32)*.01
  bv=np.ones(len(t),dtype=np.float32)*.02
  ev=np.array([63000,125000,180000],dtype=np.int64)
  side=np.array([1,-1,1],dtype=np.int8)
  whole=build_states(t,bid,ask,av,bv,ev,side)
  stop=np.searchsorted(t,ev[-1],side='left')
  clipped=build_states(t[:stop],bid[:stop],ask[:stop],av[:stop],bv[:stop],ev,side)
  np.testing.assert_array_equal(whole,clipped)
 def test_r120_htf_completed_prefix_suffix_mutation(self):
  t=np.arange(1000,3600000,1000,dtype=np.int64)
  bid=(4000000+np.cumsum((np.arange(len(t))%9)-4)).astype(np.int32)
  ask=bid+150
  ev=np.array([126000,360000,901000],dtype=np.int64)
  side=np.array([1,-1,1],dtype=np.int8)
  whole,_,_=make_macro_native(t,bid,ask,ev,side)
  stop=np.searchsorted(t,ev[-1],side='left')
  clipped,_,_=make_macro_native(t[:stop],bid[:stop],ask[:stop],ev,side)
  np.testing.assert_array_equal(whole,clipped)
 def test_unavailable_first_t1_quote(self):
  t=np.array([0,10000,17000,33000],dtype=np.int64)
  np.testing.assert_array_equal(action_t1_index(t,np.array([0,20000],dtype=np.int64)),[-1,-1])
if __name__=='__main__':unittest.main()