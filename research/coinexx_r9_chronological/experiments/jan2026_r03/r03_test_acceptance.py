"""R03 source/custody, full January replay and future suffix noninterference. Not financial validation."""
from __future__ import annotations
import gzip,hashlib,json,subprocess,tempfile,unittest,csv
from pathlib import Path
import pandas as pd
R=Path(__file__).parent
RAW=Path('/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz')
REF=Path('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
PIN='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'
EXE=R/'r03_phase_replay'
PRED=R/'r03_hazard_predictions.csv.gz'

def file_sha(f):
 h=hashlib.sha256()
 with f.open('rb') as stream:
  for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
 return h.hexdigest()
class CausalR03(unittest.TestCase):
 def test_source_pins(self):
  self.assertEqual(file_sha(RAW),PIN)
  a=pd.read_csv(REF);self.assertEqual(len(a),27980)
  self.assertEqual(int((a.original_booked_net_usd>0).sum()),24368)
  self.assertEqual(int((a.leg==1).sum()),19775)
  self.assertEqual(int((a.leg==2).sum()),8205)
 def test_no_historical_oracle_labels_inside_replay(self):
  src=(R/'r03_phase_replay.cpp').read_text()
  for forbidden in ('original_booked_net','teacher_best_net','27980','reference_manifest','entry_ref_sec','exit_ref_sec'):
   self.assertNotIn(forbidden,src)
  self.assertIn('signal.bid!=q.bid||signal.ask!=q.ask',src)
 def test_january_original_source_whole_replay(self):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'same.csv'
   p=subprocess.run([str(EXE),str(RAW),str(PRED),str(out),'--f=0.24','--s=0.23','--spread=80','--pt=15','--sl=180','--hold=30','--clock=0'],check=True,capture_output=True,text=True,timeout=25)
   d=json.loads(p.stderr.strip().splitlines()[-1]);trades=pd.read_csv(out)
   self.assertEqual((d['source_ticks'],d['same_ms']), (7699274,413))
   self.assertEqual(len(trades),d['trades']);self.assertEqual(int((trades.net_quote_cents>0).sum()),d['positive'])
   self.assertTrue(trades.entry_ordinal.is_monotonic_increasing)
   self.assertTrue((trades.exit_ordinal>trades.entry_ordinal).all())
   self.assertEqual(int(trades.net_quote_cents.sum()),d['net_quote_cents'])
   # Replay must always match its own receipt, not hard-coded original trade labels.
 def test_hindsight_teacher_observation_is_ordered(self):
  a=pd.read_csv(R/'r03_teacher_5sec.csv')
  self.assertEqual(len(a),27980)
  v=a[a.order_respecting==1]
  self.assertEqual(len(v),27974)
  self.assertTrue((v.teacher_exit_ord>v.teacher_entry_ord).all())
  self.assertEqual(int((v.teacher_best_net_c>0).sum()),26305)
  self.assertEqual(int((v.teacher_best_net_c>20).sum()),24863)
  self.assertTrue((v.teacher_exit_ms>=v.teacher_entry_ms).all())
 def test_altered_future_source_cannot_change_past_closed_trades(self):
  with tempfile.TemporaryDirectory() as folder:
   base=Path(folder);cutoff=1767315640000
   results=[]
   for alter in (0,500):
    r=base/f'{alter}.csv.gz';scores=base/f'{alter}.sig.gz';out=base/f'{alter}.res.csv'
    with gzip.open(r,'wt') as raw,gzip.open(scores,'wt') as sig:
     raw.write('time,time_msc,bid,ask,last,volume,volume_real,flags\n')
     sig.write('sec,ms,bid_c,ask_c,phase,spread_c,fb,fs,sb,ss\n')
     for k in range(50):
      sec=1767315610+k;ms=sec*1000
      bidc=400000+(k//2)*15+(alter if k>=30 else 0);askc=bidc+20
      raw.write(f'{sec},{ms},{bidc/100:.2f},{askc/100:.2f},0,0,0,0\n')
      sig.write(f'{sec},{ms},{bidc},{askc},{sec%60},20,{0.92 if k==0 else 0:.2f},0,0,0\n')
    p=subprocess.run([str(EXE),str(r),str(scores),str(out),'--f=.70','--s=.70','--spread=50','--pt=5','--sl=100','--hold=8','--second=0'],capture_output=True,text=True,check=True)
    with out.open() as f:results.append([row for row in csv.DictReader(f) if int(row['exit_time_msc'])<cutoff])
   self.assertGreater(len(results[0]),0)
   self.assertEqual(results[0],results[1])
if __name__=='__main__':unittest.main(verbosity=2)
