"""R04 regression suite: source custody, exact fee, R03 noninterference and frozen-learner prefix causality."""
import os
import csv,gzip,hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
import pandas as pd
R=Path(__file__).parent;P=Path(os.environ.get('R9_R03_FOLDER','/mnt/data/r9_jan_r03'))
RAW=Path('/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz')
PIN='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
class TestR04(unittest.TestCase):
 def test_immutable_source_and_booked_account(self):
  self.assertEqual(sha(RAW),PIN)
  m=pd.read_csv(os.environ.get('R9_REFERENCE_MANIFEST','/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv'))
  self.assertEqual(len(m),27980);self.assertEqual(int((m.original_booked_net_usd>0).sum()),24368)
  self.assertEqual(round(m.original_booked_net_usd.sum(),2),41520.82)
 def test_unmodified_r03_fee0_baseline_byte_parity(self):
  self.assertEqual(sha(P/'r03_repro_profit_v02.csv'),sha(R/'r04_meta_0.csv'))
  b=pd.read_csv(R/'r04_meta_0.csv')
  self.assertEqual(len(b),37052)
  self.assertEqual(int((b.net_quote_cents>2).sum()),24529)
  self.assertEqual(int((b.net_quote_cents-2).sum()),-906788)
 def test_all_fullmonth_results_fee_book_no_hindsight(self):
  j=json.loads((R/'r04_grade_results.json').read_text())
  for row in j['full_results']:
   f=pd.read_csv(R/row['name'])
   self.assertEqual(len(f),row['positions'])
   c=f.net_quote_cents-2
   self.assertEqual(int(c.sum()),round(row['cash_net_usd']*100))
   self.assertEqual(int((c>0).sum()),row['fee_positive'])
   self.assertEqual(int((f.exit_ordinal>f.entry_ordinal).sum()),len(f))
  sources=(R/'r04_meta_replay.cpp').read_text()+(R/'r04_quoteordinal_competing_exit.cpp').read_text()
  for forbidden in ('teacher_best_net','original_booked_net','reference_manifest','entry_ref_sec','exit_ref_sec'):
   self.assertNotIn(forbidden,sources)
 def test_learner_source_risk_feature_parity(self):
  with gzip.open(R/'r04_scores.csv.gz','rt') as f:
   hdr=f.readline().strip().split(',');first=next(csv.DictReader(f,fieldnames=hdr))
  with gzip.open(P/'r03_hazard_predictions.csv.gz','rt') as f:
   h=f.readline().strip().split(',');orig=next(csv.DictReader(f,fieldnames=h))
  for k in h:
   if k in ('f_b','f_s','s_b','s_s'):self.assertAlmostEqual(float(first[k]),float(orig[k]),places=5)
   else:self.assertEqual(first[k],orig[k])
  self.assertTrue(0<=float(first['risk1'])<=1)
  self.assertTrue(0<=float(first['risk2'])<=1)
 def test_future_quote_suffix_noninterference(self):
  with tempfile.TemporaryDirectory() as td:
   paths=[];cut=1767315649000
   for flip in (0,500):
    raw=Path(td)/f'raw{flip}.gz';scores=Path(td)/f'scores{flip}.gz';out=Path(td)/f'out{flip}.csv'
    with gzip.open(raw,'wt') as f,gzip.open(scores,'wt') as g:
     f.write('time,time_msc,bid,ask,last,volume,volume_real,flags\n')
     g.write('sec,ms,bid_c,ask_c,phase,spread_c,f_b,f_s,s_b,s_s,risk1,risk2\n')
     for k in range(76):
      sec=1767315600+k;ms=sec*1000;bid=430000+k*4+(flip if k>=50 else 0);ask=bid+19
      f.write(f'{sec},{ms},{bid/100:.2f},{ask/100:.2f},0,0,0,0\n')
      g.write(f'{sec},{ms},{bid},{ask},{sec%60},19,.99,.01,.01,.99,.99,.99\n')
    p=subprocess.run([str(R/'r04_meta_replay'),str(raw),str(scores),str(out),'--f=.24','--s=.23','--spread=80','--pt=14','--sl=180','--hold=30','--clock=0','--second=1','--opp=1','--meta=.75'],capture_output=True,text=True,check=True)
    with open(out) as fp:paths.append([row for row in csv.DictReader(fp) if int(row['exit_time_msc'])<cut])
   self.assertTrue(len(paths[0])>0)
   self.assertEqual(paths[0],paths[1])
if __name__=='__main__':unittest.main(verbosity=2)
