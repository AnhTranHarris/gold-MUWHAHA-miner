"""Independent R18 source-result-consistency verifier. No source file edited.
This verifies COMPLETE archived results against source month clock reference and
all selected quote ordinals. It does not establish live causality or cash PnL.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import csv,hashlib,json,zipfile
import numpy as np

ROOT=Path(__file__).resolve().parent
RES=ROOT/'results'
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
MONTHS=('01','02','06','07')
HOURS={'01':744,'02':672,'06':720,'07':744}
QREF={'01':27980,'02':33523,'06':31758,'07':24324}
S1={'01':88233,'02':82027,'06':101889,'07':75928}
CONTRACT='NEW_FIRST_TOUCH_60_BEFORE_ADVERSE'
LANE='R18_ADAPTIVE_UNION_4000'

def sha(p):
 with open(p,'rb') as fh:return hashlib.file_digest(fh,'sha256').hexdigest()

def check(source,month):
 stem=f'R18_{source}_{month}'
 rec=json.loads((RES/f'{stem}_SOURCE_VERIFIED_RECEIPT.json').read_text())
 assert rec['source']==source and rec['month']==month
 assert len(rec['results'])==50
 assert rec['historical_clock_hours_shift']==({'01':-2,'02':-2,'06':-3,'07':-3}[month] if source=='MT5_BROKER_EXPORT' else 0)
 assert rec['original_15F30S_and_new_first_touch_labels_DISTINCT']
 assert rec['hindsight_selected_BUY_SELL_not_live']
 for n,v in rec['output_files'].items():
  f=RES/n
  assert f.stat().st_size==v['bytes'],(n,'bytes')
  assert sha(f)==v['sha256'],(n,'hash')
 rows=rec['results'];metrics={(r['lane'],r['contract']):r for r in rows}
 assert len(metrics)==50
 assert len({r['lane'] for r in rows})==10 and len({r['contract'] for r in rows})==5
 assert {r['original_R9_UTC_ref_count'] for r in rows}=={QREF[month]}
 for r in rows:
  assert r['source_sha256']==rec['original_source_sha256']
  assert r['strict_original_only']==(r['contract']=='ORIGINAL_S1_F15_SAFE30')
 if source=='DUKASCOPY_RAW':assert metrics[('BASE_250_1500','ORIGINAL_S1_F15_SAFE30')]['hindsight_firstTP_selected_onepos']==S1[month]
 # Complete calendar source, not a single headline: full original zero-reference rows.
 qc=defaultdict(lambda:[0,0,0,0,0]) # entries, count passing, count active, sumref, count rows
 with open(RES/f'{stem}_ALL_UTC_QUARTERS.csv',newline='') as f:
  for z in csv.DictReader(f):
   k=z['lane'],z['contract']; v=qc[k];ref=int(z['r9_SYNTH_original_ref']);cnt=int(z['hindsight_selected'])
   assert ref>=0 and cnt>=0
   if ref:v[1]+=cnt>=ref;v[2]+=1
   v[0]+=cnt;v[3]+=ref;v[4]+=1
 hc=defaultdict(lambda:[0,0,0,0,0])
 with open(RES/f'{stem}_ALL_UTC_HOURS.csv',newline='') as f:
  for z in csv.DictReader(f):
   k=z['lane'],z['contract'];v=hc[k];ref=int(z['r9_SYNTH_original_ref_hour']);cnt=int(z['hindsight_selected'])
   if ref:v[1]+=cnt>=ref;v[2]+=1
   v[0]+=cnt;v[3]+=ref;v[4]+=1
 assert len(qc)==len(hc)==50
 npz=RES/f'{stem}_LOSSLESS_SELECTED_ORIGINAL_QUOTE_ORDINALS.npz'
 with np.load(npz,allow_pickle=False) as z:
  assert len(z.files)==150
  for k,r in metrics.items():
   v,w=qc[k],hc[k]
   assert v[4]==4*HOURS[month] and w[4]==HOURS[month],(stem,k,'calendar rows')
   assert v[3]==w[3]==QREF[month],(stem,k,'ref parity')
   assert v[0]==w[0]==r['hindsight_firstTP_selected_onepos'],(stem,k,'count parity')
   assert v[1]==r['15m_quota_met'] and v[2]==r['active_quarters'],(stem,k,'quarter success')
   assert w[1]==r['hourly_quota_met'] and w[2]==r['active_hours'],(stem,k,'hour success')
   prefix=k[0]+'__'+k[1]
   entry=z[prefix+'_entry_ord'];sides=z[prefix+'_side_FUTURE_SELECTED'];exits=z[prefix+'_firstTP_exit_ord']
   assert entry.size==sides.size==exits.size==v[0],(stem,k,'traces parity')
   assert np.all((sides==1)|(sides==-1)),(stem,k,'sides')
   assert np.all((entry>=0)&(entry<rec['raw_quotes'])&(exits<rec['raw_quotes'])&(exits>entry)),(stem,k,'quote ordinal')
  # Strict model honesty: no original strict 15/full30 is relabeled as future-60.
  assert metrics[('BASE_250_1500','ORIGINAL_S1_F15_SAFE30')]['strict_original_only']
 controls={'source':source,'month':month,'raw_quotes':rec['raw_quotes'],
  'source_file_sha256':rec['original_source_sha256'], 'scenario_count':len(metrics),
  'all_original_UTC_quarter_rows':4*HOURS[month], 'all_original_UTC_hour_rows':HOURS[month],
  'all_scenario_quarter_rows':50*4*HOURS[month], 'all_scenario_hour_rows':50*HOURS[month],
  'recorded_q_ref':QREF[month], 'source_all_output_sha_verification':True,
  'all_lossless_quote_ordinals_verified':True,
  'old_strict_base':metrics[('BASE_250_1500','ORIGINAL_S1_F15_SAFE30')],
  'new_adaptive60':metrics[(LANE,CONTRACT)],
  'diagnostic_allobserved60':metrics[('R18_ALL_OBSERVED_4000_DIAGNOSTIC',CONTRACT)]}
 return controls

def main():
 allc=[]
 for feed in SOURCES:
  for mon in MONTHS:
   c=check(feed,mon);allc.append(c)
   r=c['new_adaptive60'];print(feed,mon,'verified 50 complete scenarios;',
    'new adaptive60 selected',r['hindsight_firstTP_selected_onepos'],
    'Q',r['15m_quota_met'],'/',r['active_quarters'],
    'H',r['hourly_quota_met'],'/',r['active_hours'],flush=True)
 out={'label':'R18_FULL_EIGHT_SOURCE_MONTH_INDEPENDENT_CALENDAR_SOURCE_SHA_SELECTED_ORDINAL_VERIFIER',
  'all_eight_pass':True,'source_months':len(allc),'full_distinct_scenarios':8*50,
  'all_source_UTC_quarters':2*11520,'all_source_UTC_hours':2*2880,
  'all_scenario_quarter_rows':50*2*11520,'all_scenario_hour_rows':50*2*2880,
  'no_causal_model_accuracy_or_live_execution_inferred':True,'sources':allc}
 outfile=ROOT/'R18_ALL_EIGHT_INDEPENDENT_SOURCE_RECONCILIATION_RECEIPT.json'
 outfile.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 # Each original 15-minute and hourly failure row of the newly proposed strategy, no omissions.
 for unit,key,origfile in [('QUARTER','utc_quarter','ALL_UTC_QUARTERS'),('HOUR','utc_hour','ALL_UTC_HOURS')]:
  outp=ROOT/f'R18_NEW_ADAPTIVE60_ALL_SOURCE_{unit}_QUOTA_FAILURE_WITNESSES.csv'
  with outp.open('w',newline='') as o:
   writer=None
   for feed in SOURCES:
    for mon in MONTHS:
     with (RES/f'R18_{feed}_{mon}_{origfile}.csv').open(newline='') as f:
      for z in csv.DictReader(f):
       if z['lane']!=LANE or z['contract']!=CONTRACT:continue
       ref=int(z.get('r9_SYNTH_original_ref',z.get('r9_SYNTH_original_ref_hour')))
       cnt=int(z['hindsight_selected'])
       if ref and cnt<ref:
        row={'source':feed,'month':mon,'utc_period':z[key],
         'original_R9_SYNTH_reference':ref,'retrospective_firstTP60_selected':cnt,
         'exact_deficit':ref-cnt,'source_future_selected_not_predictive':True}
        if writer is None:writer=csv.DictWriter(o,fieldnames=list(row));writer.writeheader()
        writer.writerow(row)
  if writer is None:outp.write_text('source,month,utc_period,original_R9_SYNTH_reference,retrospective_firstTP60_selected,exact_deficit,source_future_selected_not_predictive\n')
  print('saved exact failure witness',outp.name,outp.stat().st_size,flush=True)
 print('ALL_EIGHT_CONSISTENCY_TESTS_PASS',flush=True)

if __name__=='__main__': main()
