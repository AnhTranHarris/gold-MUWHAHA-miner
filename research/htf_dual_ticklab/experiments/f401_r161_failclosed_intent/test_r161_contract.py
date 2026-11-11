"""Synthetic contract tests only; no original native-tick claims."""
import unittest
from r161_contract import Quote, Intent, guard_action, first_touch_offline
class Contract(unittest.TestCase):
    def setUp(self):
        self.i=Intent(100000,1);self.p=[Quote(99999,2000,2000.2)]
    def test_submitted_failclosed(self):
        self.assertEqual(guard_action(Intent(100000,1,True),'T1',115000,115000),'ABSTAIN')
    def test_t1_bounds(self):
        self.assertEqual(guard_action(self.i,'T1',115000,115000),'T1')
        self.assertEqual(guard_action(self.i,'T1',116000,116000),'ABSTAIN')
    def test_t2_bounds(self):
        self.assertEqual(guard_action(self.i,'T2',120000,115000),'T2')
        self.assertEqual(guard_action(self.i,'T2',121000,115000),'ABSTAIN')
    def test_limit_requires_eligibility(self):
        self.assertEqual(guard_action(self.i,'LIMIT',115000,115000),'ABSTAIN')
    def test_horizon_exclusive(self):
        self.assertEqual(first_touch_offline(self.i,self.p,[Quote(130000,2002,2002.2)],1,1),'unresolved')
    def test_first_touch(self):
        self.assertEqual(first_touch_offline(self.i,self.p,[Quote(100001,2001.3,2001.5),Quote(100002,1998,1998.2)],1,1),'favorable')
    def test_sell_ask(self):
        self.assertEqual(first_touch_offline(Intent(100000,-1),self.p,[Quote(100001,1998,1998.5)],1,1),'favorable')
    def test_nan_fails(self):
        with self.assertRaises(ValueError): first_touch_offline(self.i,self.p,[Quote(100001,float('nan'),2002)],1,1)
    def test_late_invalid_fails(self):
        with self.assertRaises(ValueError): first_touch_offline(self.i,self.p,[Quote(130001,float('nan'),2002)],1,1)
    def test_prefix_future_forbidden(self):
        with self.assertRaises(ValueError): first_touch_offline(self.i,self.p+[Quote(100000,2000,2000.2)],[],1,1)
    def test_submitted_offline_rejected(self):
        with self.assertRaises(ValueError): first_touch_offline(Intent(100000,1,True),self.p,[],1,1)
if __name__=='__main__': unittest.main()
