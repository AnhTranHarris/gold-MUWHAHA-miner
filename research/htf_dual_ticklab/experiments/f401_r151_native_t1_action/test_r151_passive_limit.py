import unittest,numpy as np
from r151_passive_limit import passive_limit_touch
class PassiveTests(unittest.TestCase):
 def test_buy_limit_requires_ask_touch(self):
  t=np.array([1000,2000,3000,4000],dtype=np.int64)
  bid=np.array([1000,900,1000,3200],dtype=np.int32)
  ask=np.array([1200,1100,1200,3400],dtype=np.int32)
  status,pnl,fill,_=passive_limit_touch(t,bid,ask,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),100,5000,2000,800)
  self.assertEqual(int(fill[0]),1);self.assertEqual(int(status[0]),1)
 def test_sell_limit_requires_bid_touch(self):
  t=np.array([1000,2000,3000],dtype=np.int64)
  bid=np.array([2000,2100,0],dtype=np.int32)
  ask=np.array([2200,2300,200],dtype=np.int32)
  status,pnl,fill,_=passive_limit_touch(t,bid,ask,np.array([0],dtype=np.int64),np.array([-1],dtype=np.int8),100,5000,1500,800)
  self.assertEqual(int(fill[0]),1);self.assertEqual(int(status[0]),1)
 def test_expired_limit_not_filled(self):
  t=np.array([1000,8000,9000],dtype=np.int64)
  bid=np.array([1000,0,1000],dtype=np.int32);ask=bid+100
  status,_,fill,_=passive_limit_touch(t,bid,ask,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),100,5000)
  self.assertEqual(int(status[0]),-2);self.assertEqual(int(fill[0]),-1)
 def test_same_millisecond_quote_cannot_fill(self):
  t=np.array([1000,1000,2000,3000],dtype=np.int64)
  bid=np.array([1000,0,900,3000],dtype=np.int32);ask=bid+100
  status,_,fill,_=passive_limit_touch(t,bid,ask,np.array([0],dtype=np.int64),np.array([1],dtype=np.int8),100,5000)
  self.assertEqual(int(fill[0]),2)
if __name__=='__main__':unittest.main()