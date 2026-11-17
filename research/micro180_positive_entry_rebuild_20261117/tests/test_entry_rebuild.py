import csv
import gzip
import io
import inspect
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
import positive_entry_model as m

class EntryRebuildTests(unittest.TestCase):
 def test_source_teacher_timestamp_and_27_accounting(self):
  if not m.TARGET_ZIP.exists():self.skipTest('original private target archive not present in GitHub CI')
  t=m.load_targets()
  self.assertEqual(len(t),24368)
  self.assertEqual(sum(x['original_cents'] for x in t),4334869)
  self.assertEqual(len({x['uid'] for x in t}),24368)
  self.assertEqual(len(set(x['family'] for x in t)),23)
  self.assertTrue(all(x['sec']//60==x['minute'] for x in t))

 def test_inference_has_no_target_input(self):
  self.assertEqual(list(inspect.signature(m.replay).parameters),['model','days'])
  src=inspect.getsource(m.replay)
  self.assertNotIn('load_targets(',src)
  self.assertNotIn('original_cents',src)
  self.assertNotIn('source_row',src)
  self.assertNotIn("['equote_ms']",src)
  c=(HERE/'src'/'causal_quote_engine.cpp').read_text()
  self.assertNotIn('OrderSend(',c)
  self.assertNotIn('PositionClose(',c)

 def test_entry_comparator_only_source_second_leg_side(self):
  t=[dict(uid='one',sec=1_000,minute=1_000//60,leg=1,side=1,
          family='A1__other',original_cents=250,day='2026-01-02')]
  i=[dict(sec=1002,minute=1000//60,leg=1,side=1)]
  r=m.evaluate_intents(i,t,['2026-01-02'])
  self.assertEqual((r['target_count'],r['matched_exact_second'],r['matched_2second']),(1,0,1))
  i[0]['side']=-1
  self.assertEqual(m.evaluate_intents(i,t,['2026-01-02'])['matched_2second'],0)

 @staticmethod
 def fixture(path:Path,late_adjust=False,alter_logger=False):
  start=1767315600000
  with gzip.open(path,'wt') as f:
   f.write('run_label,time_msc,time,bid,ask,event,source_s1,teacher_label\n')
   for sec in range(27*60):
    ms=start+sec*1000+10
    mid=4320+sec*.003
    if late_adjust and sec>=26*60:mid+=120
    f.write(f'REAL,{ms},2026.01.02 01:00:00,{mid:.5f},{mid+.20:.5f},'
      +('FAKE_WIN,999,SHOULD_NOT_APPEAR' if alter_logger else 'NONE,0,')+'\n')
    if sec%23==0:f.write(f'REAL,{ms},2026.01.02 01:00:00,{mid:.5f},{mid+.20:.5f},NONE,0,\n')

 def test_cpp_prefix_immutable_to_later_ticks_and_logger_labels(self):
  with tempfile.TemporaryDirectory() as d:
   a,b,c=[Path(d)/n for n in ('base.csv.gz','future.csv.gz','labels.csv.gz')]
   self.fixture(a);self.fixture(b,late_adjust=True);self.fixture(c,alter_logger=True)
   out=[]
   for f in (a,b,c):
    cp=subprocess.run([str(m.ENGINE),str(f)],capture_output=True,text=True,check=True)
    out.append(list(csv.DictReader(io.StringIO(cp.stdout))))
   self.assertGreater(len(out[0]),30)
   self.assertEqual(out[0],out[2])
   self.assertEqual(out[0][:10],out[1][:10])
   self.assertGreater(float(out[0][-1]['ret5']),float(out[1][-1]['ret5'])-1000)  # finite
   # Exact one decision snapshot per SOURCE second, despite duplicate timestamp rows.
   sec=[int(r['second']) for r in out[0]]
   self.assertEqual(len(sec),len(set(sec)))
   self.assertTrue(all(x<y for x,y in zip(sec,sec[1:])))

if __name__=='__main__':unittest.main()
