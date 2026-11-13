import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from signatures import Window,CausalQuotePath

class Tests(unittest.TestCase):
 def test_order_sensitive_area(self):
  p=Window(1000)
  p.add(100,10,0);p.add(200,0,10)
  self.assertEqual(p.area2,100)
  q=Window(1000)
  q.add(100,0,10);q.add(200,10,0)
  self.assertEqual(q.area2,-100)
  self.assertEqual((p.x,p.y),(q.x,q.y))
 def test_sliding_window_inverse(self):
  p=Window(350)
  p.add(100,10,0);p.add(200,0,10);p.add(300,-1,2)
  all_steps=list(p.steps)
  p.add(500,3,-2)
  ref=Window(350)
  for z in all_steps[1:]:ref.add(*z[:3])
  ref.add(500,3,-2)
  self.assertEqual((p.x,p.y,p.area2,p.vb,p.va),(ref.x,ref.y,ref.area2,ref.vb,ref.va))
 def test_equal_ms_retained(self):
  p=CausalQuotePath();p.observe(100,1000,1002);p.observe(100,1001,1002)
  self.assertEqual(len(p.windows[500].steps),1)
  self.assertEqual(p.windows[500].x,1)
 def test_long_gap_resets(self):
  p=CausalQuotePath();p.observe(100,100,110);p.observe(200,102,111)
  p.observe(20000,200,210)
  self.assertEqual(len(p.windows[10000].steps),0)
 def test_unrevised_previous_quote_not_peeking(self):
  p=CausalQuotePath();p.observe(100,100,110);one=p.snapshot(1)
  p.observe(200,101,111);two=p.snapshot(1)
  self.assertEqual(one['w500_events'],0)
  self.assertEqual(two['w500_events'],1)

if __name__=='__main__':unittest.main()
