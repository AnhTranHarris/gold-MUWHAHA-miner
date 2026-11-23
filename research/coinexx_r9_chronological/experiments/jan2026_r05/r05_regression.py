"""R05 source-integrity, original teacher immutability, chronological score and suffix causality tests."""
from __future__ import annotations
import os,unittest,hashlib,gzip,csv,json,subprocess,tempfile
from pathlib import Path
import numpy as np,pandas as pd,lightgbm as lgb
R=Path(__file__).parent
RAW=Path('/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz')
REF=Path('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
PIN='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'
SOURCE=R/'r05_joint_replay.cpp'

def hashfile(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for ch in iter(lambda:f.read(1<<20),b''):h.update(ch)
 return h.hexdigest()

class R05Tests(unittest.TestCase):
 def test_01_immutable_original_source_and_books(self):
  self.assertEqual(hashfile(RAW),PIN)
  r=pd.read_csv(REF)
  self.assertEqual((len(r),int((r.original_booked_net_usd>0).sum()),round(r.original_booked_net_usd.sum(),2)),(27980,24368,41520.82))
  self.assertEqual((int((r.leg==1).sum()),int((r.leg==2).sum())),(19775,8205))
  self.assertEqual(int(((r.leg==1)&(r.cycle_legs==2)&(r.original_booked_net_usd<0)&(r.cycle_net_usd>0)).sum()),2147)
  a=r[r.leg==1]
  self.assertEqual(int((a.entry_sec%60<=10).sum()),11372)
  self.assertEqual(int((a.entry_sec%60).between(18,28).sum()),7506)
  self.assertEqual(int(((a.entry_sec%60).between(18,28)&(a.original_booked_net_usd>0)).sum()),7504)
  self.assertEqual(int(((a.cycle_legs==2)&(a.entry_sec%60>10)).sum()),0)
 def test_02_cxx_never_reads_frozen_teacher(self):
  s=SOURCE.read_text()
  for banned in ('r9_original_row','original_booked_net_usd','reference_manifest','teacher_best_net','entry_ref_sec','exit_ref_sec'):
   self.assertNotIn(banned,s)
  for needed in ('source raw format','wrong original source quote','Original 0.01 lot','exitmodel.score','rearmmodel.score','passage->score'):
   self.assertIn(needed,s)
 def test_03_forest_export_equals_python(self):
  for name,filename in [('exit','r05_exit_teacher_sample.csv'),('rearm','r05_rearm_teacher_sample.csv'),('competing_passage','r05_exit_teacher_sample.csv')]:
   x=pd.read_csv(R/filename,nrows=10)
   meta=json.loads((R/'r05_fit_receipt.json').read_text()) if name!='competing_passage' else None
   feat=meta[name]['features'] if meta else meta
   booster=lgb.Booster(model_file=str(R/f'r05_{name}_hazard_lgb.txt' if name!='competing_passage' else R/'r05_competing_passage_lgb.txt'))
   with open(R/f'r05_{name}_forest.txt') as f:
    sig=f.readline().split();features=f.readline().split();trees=[]
    for t in range(int(sig[3])):
     n=int(f.readline());trees.append([f.readline().split() for _ in range(n)])
   xx=x[features].to_numpy(dtype=float)
   expected=booster.predict(xx)
   got=[]
   for row in xx:
    score=0.
    for t in trees:
     j=0
     while int(t[j][0])>=0:
      k=int(t[j][0]);j=int(t[j][2] if row[k]<=float(t[j][1]) else t[j][3])
     score+=float(t[j][4])
    got.append(1/(1+np.exp(-score)))
   self.assertLess(float(np.max(abs(expected-np.asarray(got)))),1e-8)
 def test_04_full_month_account_fee_and_source_order(self):
  trial=json.loads((R/'R05_GRADED_JANUARY.json').read_text())
  for v in trial['trials']:
   df=pd.read_csv(R/v['file'])
   self.assertEqual(len(df),v['executed'])
   self.assertTrue(df.entry_ordinal.is_monotonic_increasing)
   self.assertTrue((df.exit_ordinal>df.entry_ordinal).all())
   self.assertTrue((df.exit_ordinal.to_numpy()[:-1]<df.entry_ordinal.to_numpy()[1:]).all())
   self.assertEqual(int((df.net_quote_cents-2!=df.net_cash_cents).sum()),0)
   self.assertEqual(round(df.net_cash_cents.sum()/100,2),v['net_account_usd'])
   self.assertEqual(int((df.net_cash_cents>0).sum()),v['fee_wins'])
  rec=json.loads((R/'r05_joint_mode0_receipt.log').read_text().splitlines()[0]);self.assertEqual((rec['source_ticks'],rec['same_ms'],rec['feature_seconds']),(7699274,413,1652250))
 def test_05_future_quotes_do_not_change_closed_prefix_trades(self):
  cutoff=1767316400000;end=1767316700000
  # A small prefix slice of ORIGINAL January tick/feature/score streams, no new full tick library.
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);results=[]
   for change in (0,500):
    ticks=d/f't_{change}.gz';feature=d/f'f_{change}.gz';scores=d/f's_{change}.gz';book=d/f'b_{change}.csv'
    with gzip.open(RAW,'rt') as src,gzip.open(ticks,'wt') as dst:
     dst.write(src.readline())
     for row in csv.reader(src):
      if not row:continue
      ms=int(row[1]);
      if ms>=end:break
      if ms>=cutoff and change:row[2]=f'{float(row[2])+change/100:.2f}';row[3]=f'{float(row[3])+change/100:.2f}'
      dst.write(','.join(row)+'\n')
    for original,outfile in [(Path('/mnt/data/r9_jan_r03/r03_phase_seconds.csv.gz'),feature),(Path('/mnt/data/r9_jan_r03/r03_hazard_predictions.csv.gz'),scores)]:
     with gzip.open(original,'rt') as src,gzip.open(outfile,'wt') as dst:
      dst.write(src.readline())
      for row in csv.reader(src):
       if not row:continue
       ms=int(row[1]);
       if ms>=end:break
       if ms>=cutoff and change:
        row[2]=str(int(row[2])+change);row[3]=str(int(row[3])+change)
       dst.write(','.join(row)+'\n')
    cmd=[str(R/'r05_joint_replay'),str(ticks),str(feature),str(scores),str(R/'r05_exit_forest.txt'),str(R/'r05_rearm_forest.txt'),str(book),'--f=.01','--s=.01','--mode=0','--e=.2','--r=.2','--stop=180','--hold=30']
    subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=25)
    with open(book) as f:results.append([x for x in csv.DictReader(f) if int(x['exit_time_msc'])<cutoff])
   self.assertTrue(len(results[0])>0)
   self.assertEqual(results[0],results[1])
if __name__=='__main__':unittest.main(verbosity=2)
