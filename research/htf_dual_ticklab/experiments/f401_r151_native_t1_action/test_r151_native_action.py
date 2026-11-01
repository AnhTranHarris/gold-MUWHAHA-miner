import unittest,numpy as np
from r151_native_action import action_t1_index,first_touch
class R151Tests(unittest.TestCase):
 def test_window_and_strict_boundary(self):
  t=np.array([10000,24999,25000,25999,26000,30000],dtype=np.int64)
  np.testing.assert_array_equal(action_t1_index(t,np.array([10000,11000,12000],dtype=np.int64)),[2,4,-1])
 def test_buy_uses_ask_entry_bid_exit(self):
  t=np.array([1000,2000,3000],dtype=np.int64)
  b=np.array([1000,1100,3000],dtype=np.int32);a=np.array([1500,1600,3500],dtype=np.int32)
  out,pnl,_,_=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),1500,800)
  self.assertEqual(int(out[0]),1);self.assertEqual(int(pnl[0]),1500)
 def test_sell_uses_bid_entry_ask_exit(self):
  t=np.array([1000,2000,3000],dtype=np.int64)
  b=np.array([3000,2000,1000],dtype=np.int32);a=np.array([3500,2500,1500],dtype=np.int32)
  out,pnl,_,_=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([-1],dtype=np.int8),1500,800)
  self.assertEqual(int(out[0]),1);self.assertEqual(int(pnl[0]),1500)
 def test_adverse_first_wins_over_later_target(self):
  t=np.array([1000,2000,3000],dtype=np.int64)
  b=np.array([1000,0,3000],dtype=np.int32);a=np.array([1200,200,3200],dtype=np.int32)
  out,_,_,idx=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),1500,800)
  self.assertEqual(int(out[0]),-1);self.assertEqual(int(idx[0]),1)
 def test_no_same_quote_exit(self):
  t=np.array([1000],dtype=np.int64)
  out,_,_,_=first_touch(t,np.array([1000],dtype=np.int32),np.array([1200],dtype=np.int32),np.array([0],dtype=np.int64),np.array([1],dtype=np.int8))
  self.assertEqual(int(out[0]),-9)
 def test_same_millisecond_exit_forbidden(self):
  t=np.array([1000,1000,2000],dtype=np.int64)
  b=np.array([1000,5000,1100],dtype=np.int32);a=b+100
  out,_,_,idx=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),1500,800)
  self.assertEqual(int(out[0]),0);self.assertEqual(int(idx[0]),2)
 def test_missing_intent(self):
  t=np.array([1000,2000],dtype=np.int64)
  out,_,_,_=first_touch(t,np.array([1000,2000],dtype=np.int32),np.array([1100,2100],dtype=np.int32),np.array([-1],dtype=np.int64),np.array([1],dtype=np.int8))
  self.assertEqual(int(out[0]),-9)
 def test_no_future_quote_changes_past_result(self):
  t=np.array([1000,2000,3000,40000],dtype=np.int64)
  b=np.array([1000,1100,1000,50000],dtype=np.int32);a=b+200
  one=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),2000,1500)
  b[-1]=-100000;a[-1]=-99800
  two=first_touch(t,b,a,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),2000,1500)
  self.assertEqual(int(one[0][0]),int(two[0][0]))
if __name__=='__main__':unittest.main()